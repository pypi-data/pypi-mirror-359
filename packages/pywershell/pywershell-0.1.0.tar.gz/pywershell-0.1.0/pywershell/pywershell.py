import asyncio
import re
import sqlite3
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

from async_property import AwaitLoader
from loguru import logger as log
from propcache import cached_property

from .debug import get_caller_context


def _ident(s: str) -> str:
    s = s.strip().lstrip("-")
    return re.sub(r"\W+", "_", s).lower().strip("_") or "cmd"

@dataclass(slots=True)
class CMDResult:
    dict: dict[str, list[str]]
    list: list[str]
    str: str
    ns: SimpleNamespace = field(repr=False)

    def __getattr__(self, item):
        if item in {"dict", "list", "str"}:
            return getattr(self, item)
        try:
            return getattr(self.ns, item)
        except AttributeError:
            return getattr(self.ns, _ident(item))

    def __str__(self):
        return self.str

    def __iter__(self):
        return iter(self.list)

    @cached_property
    def flat_str(self):
        """Raw string with literal \\n converted to actual newlines"""
        return self.str.replace('\\n', '\n').strip()

    @property
    def json(self):
        if not self._all_json:
            return None
        return self._all_json[0] if len(self._all_json) == 1 else self._all_json

    @cached_property
    def _all_json(self):
        import json
        import re

        try:
            result = json.loads(self.flat_str)
            return [result] if not isinstance(result, list) else result
        except json.JSONDecodeError:
            json_objects = []
            json_matches = re.finditer(r'\{[^{}]*}', self.flat_str, re.DOTALL)
            for match in json_matches:
                try:
                    obj = json.loads(match.group(0))
                    json_objects.append(obj)
                except json.JSONDecodeError:
                    continue
            return json_objects


# noinspection PyUnresolvedReferences
class PywershellLive(AwaitLoader):
    def __init__(self, path: Path = None, alias: str = None, prefix: str = "", debug: bool = False):
        self.root: Path = Path(__file__).parent or path
        self.prefix: str = prefix
        self.debug: bool = debug
        self.script: Path = self.root / "pywershell.ps1"
        self.session_dir: Path = self.root / "pywershell" / "sessions"
        self.session_name: str = str(uuid.uuid4())
        _ = self.backend
        _ = self.db
        log.debug(f"{self}: Successfully Initialized!")

    def __repr__(self):
        return f"[Pywershell.{self.session_name}]"

    @cached_property
    def backend(self):
        if self.debug: return subprocess.Popen(
            [
                "powershell",
                # "-WindowStyle", "Hidden",
                "-ExecutionPolicy", "Bypass",
                "-File", str(self.script),
                "-Dir", str(self.session_dir),
                "-SessionName", self.session_name,
            ],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
            # text=True,
            # bufsize=1,
            # creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return subprocess.Popen(
            [
                "powershell",
                "-WindowStyle", "Hidden",
                "-ExecutionPolicy", "Bypass",
                "-File", str(self.script),
                "-Dir", str(self.session_dir),
                "-SessionName", self.session_name,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    @cached_property
    def db(self, timeout=55) -> SimpleNamespace:
        start = time.time()
        session_path, db_path = None, None

        while True:
            sessions = sorted(
                self.session_dir.glob(f"*-{self.session_name}"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            if sessions:
                session_path = sessions[0]
                db_path = session_path / "output.db"
                if db_path.exists():
                    break

            if time.time() - start > timeout:
                raise TimeoutError("Timed out waiting for session or output.db")

            time.sleep(0.2)

        return SimpleNamespace(
            session_path=session_path,
            path=db_path
        )

    @cached_property
    def stream(self):
        from .stream import Stream
        return Stream(self)

    # @cached_property
    # def queue_input(self) -> threading.Thread:
    #     def _run():
    #         conn = sqlite3.connect(self.db.path)
    #         cur = conn.cursor()
    #         while True:
    #             try:
    #                 cmd = input("")
    #                 if cmd == "stop":
    #                     log.warning(f"{self}: Stopping live input...")
    #                     break
    #                 cur.execute("INSERT INTO commands (input, ran) VALUES (?, 0)", (cmd,))
    #                 conn.commit()
    #             except (EOFError, KeyboardInterrupt):
    #                 break
    #
    #     return threading.Thread(target=_run, daemon=True)

    def queue(self, cmd, new_window: bool):
        log.debug(f"[Pywershell.{self.db.path.name}]: Queueing command '''{cmd}'''...")
        with sqlite3.connect(self.db.path) as conn:
            conn.execute(
                "INSERT INTO commands (input, ran, new_window) VALUES (?, 0, ?)",
                (cmd, int(new_window))
            )
            conn.commit()

    async def run(self, cmd, **kwargs) -> CMDResult | None:
        prefix: str | None = kwargs.pop("prefix", None)
        log.debug(f"{self}: Received request:\n  - caller={get_caller_context()}\n  - prefix={prefix}\n  - kwargs={kwargs}\n  - {cmd}")
        timeouts = kwargs.pop("timeouts", None)
        new_windows = kwargs.pop("new_windows", None)
        no_cls_prefix = kwargs.pop("no_prefix", False)

        self.stream.start()
        self.stream.clear()
        raw_cmds = [cmd] if isinstance(cmd, str) else cmd
        queued = []
        for r in raw_cmds:
            full = r
            new_window = False
            if new_windows and full in new_windows:
                new_window = new_windows[full]
            if prefix: full = f"{prefix} {full}"
            if not no_cls_prefix: full = f"{self.prefix} {full}"
            if "bash -c" in full:
                log.debug(f"{self}: Bash detected! Wrapping...")
                full = full.replace('bash -c ', "bash -c '", 1).rstrip().rstrip('"') + "'"
            full = full.strip().replace("  ", " ")


            self.queue(full, new_window)

            queued.append(full)
            if timeouts and full in timeouts:
                try: time.sleep(timeouts[full])
                except: pass


        conn = sqlite3.connect(self.db.path)
        cur = conn.cursor()
        results = {}

        for full, raw in zip(queued, raw_cmds):
            lines = []
            while True:
                await asyncio.sleep(0.2)
                cur.execute(
                    "SELECT output FROM logs WHERE input = ? AND streamed = 1 ORDER BY ts",
                    (full,),
                )
                rows = cur.fetchall()
                if not rows:
                    continue
                for (o,) in rows:
                    try:
                        text = o.encode("utf-8").decode("unicode_escape")
                    except Exception:
                        text = o
                    # strip blank lines
                    lines.extend([line for line in text.splitlines() if line.strip()])
                break
            results[raw] = lines

        flat_list  = [line for v in results.values() for line in v]   # list[str]
        joined_str = "\n".join(flat_list)                             # str
        wrapped    = {_ident(k): v for k, v in results.items()}       # per-cmd attr access

        cmd_res = CMDResult(
            dict = results,           # dict[str, list[str]]
            list = flat_list,         # list[str]  ← flattened, iterable
            str  = joined_str,        # str         ← full multiline string
            ns   = SimpleNamespace(**wrapped)
        )
        log.debug(f"{self}: Collected results:\n" + "\n".join(f"{r} → {l}" for r, l in results.items()))
        return cmd_res


async def main():
    pywershell = await PywershellLive()
    pywershell.stream.verbose = False
    await pywershell.run("fdfd", timeouts={"fdfd": 10})
    time.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
