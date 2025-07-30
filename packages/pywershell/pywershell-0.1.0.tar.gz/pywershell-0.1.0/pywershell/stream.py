import sqlite3
import threading
import time
from functools import cached_property
from typing import Callable

from loguru import logger as log

from .pywershell import PywershellLive


class Stream:
    verbose = False
    lines = []

    def __init__(self, pywershell: PywershellLive):
        self.pywershell: PywershellLive = pywershell
        _ = self.thread

    def __repr__(self):
        return f"[Pywershell.{self.pywershell.session_name}.Stream]"

    def clear(self):
        self.lines = []

    def cache(self, line):
        self.lines.append(line)
        if self.verbose: log.debug(f"{self}: Cached line successfully!")
        self.auto_detect(line)

    on_detect = {}

    def stop_detecting(self, key: str = None, all: bool = None):
        if all: self.on_detect.clear()
        elif key in self.on_detect:
            self.on_detect[key] = None

    def new_detect(self, cue: str, fn: Callable):
        self.on_detect[cue] = fn

    def auto_detect(self, line):
        for cue in self.on_detect:
            fn = self.on_detect[cue]
            self.detect(line, cue, fn)

    def detect(self, line: str, cue: str, fn: Callable):
        if not fn:
            if self.verbose: log.debug(f"{self}: Stopping detect for {cue}, no effect listed.")
            return
        if cue in line:
            fn: Callable = self.on_detect[cue]
            log.debug(f"{self}: Detected {cue}! Running {fn.__name__}!")
            return
        if self.verbose: log.debug(f"{self}: Could not find {cue} in {line}.")

    def start(self):
        time.sleep(1)
        if not self.thread.is_alive():
            self.thread.start()
        if self.verbose: log.debug(f"{self}: Started streaming!")

    @cached_property
    def thread(self) -> threading.Thread:
        def core():
            with sqlite3.connect(self.pywershell.db.path) as conn:
                cur = conn.cursor()
                while True:
                    cur.execute("SELECT id, input, output FROM logs WHERE streamed = 0 ORDER BY id ASC")
                    for _id, cmd, output in cur.fetchall():
                        parsed = str(output).replace(r"\n\n", r"\n").replace(r"\n", "\n")
                        for line in parsed.splitlines():
                            if line == "": continue
                            self.cache(line)
                            log.debug(f"{self}: {line}")
                        cur.execute("UPDATE logs SET streamed = 1 WHERE id = ?", (_id,))
                        conn.commit()
                    time.sleep(0.2)
        return threading.Thread(target=core, daemon=True)