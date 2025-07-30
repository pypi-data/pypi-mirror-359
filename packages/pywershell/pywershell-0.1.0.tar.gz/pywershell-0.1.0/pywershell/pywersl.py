import asyncio
from functools import cached_property

from async_property import AwaitLoader, async_cached_property
from loguru import logger as log

from .debug import get_caller_context
from .pywershell import PywershellLive, CMDResult


class Debian:
    CHECK = ["--list --quiet", f"-d Debian -- bash -c echo Hello from Debian!"]
    INSTALL = {
        "cmd": "wsl --install Debian",
        "new_windows": {"wsl --install Debian": True},
    }
    POST_INSTALL = [
        "-d Debian -u root -- bash -c 'apt update && apt upgrade -y'",
        "-d Debian -u root -- bash -c 'apt install -y curl wget git unzip zip ca-certificates lsb-release software-properties-common build-essential'",
        "-d Debian -u root -- bash -c 'apt install -y python3 python3-pip python3-venv'",
        "-d Debian -u root -- bash -c 'apt install -y tmux htop neofetch ripgrep fd-find fzf'",
        "-d Debian -u root -- bash -c 'apt install -y docker.io docker-compose && usermod -aG docker $USER'",
        "-d Debian -u root -- bash -c 'echo Post-install complete'",
    ]
    PREFIX = "-d Debian -u root -- bash -c"
    UNINSTALL = ["--unregister Debian"]


class Distro(AwaitLoader):
    def __init__(self, pywersl):
        self.pywersl = pywersl
        self.name = pywersl.distro_str
        self.pywershell: PywershellLive = pywersl.pywershell

    def __repr__(self):
        return f"[Pywersl.{self.name}]"

    @cached_property
    def util(self):
        distro = None
        if self.name == "Debian": distro = Debian()
        if distro is None: raise RuntimeError
        return distro

    @async_cached_property
    async def setup(self):
        out = await self.pywershell.run(self.util.CHECK)
        response = out.str
        if "Hello from Debian!" in response:
            log.success(f"{self}: Successfully initialized {self.name}!")
            return
        elif "There is no distribution with the supplied name" in response:
            cmd = self.util.INSTALL["cmd"]
            new_windows = self.util.INSTALL["new_windows"]
            await self.pywershell.run(cmd, no_prefix=True, new_windows=new_windows)
            await self.pywershell.run(self.util.POST_INSTALL, no_prefix=False)

    async def run(self, cmd: str | list[str], **kwargs) -> CMDResult | None:
        prefix = kwargs.pop("prefix", None)
        log.debug(
            f"{self}: Received request:\n  - caller={get_caller_context()}\n  - prefix={prefix}\n  - kwargs={kwargs}\n  - {cmd}")
        if prefix:
            prefix = f"{self.util.PREFIX} {prefix}"
        else:
            prefix = self.util.PREFIX

        if isinstance(cmd, str): cmd = [cmd]
        cmds = cmd
        log.debug(
            f"{self}: Sent request:\n  - receiver={self.pywershell}\n  - prefix={prefix}\n  - kwargs={kwargs}\n  - {cmd}")
        out = await self.pywershell.run(cmds, prefix=prefix, **kwargs)
        return out

    async def uninstall(self):
        out = await self.pywershell.run(self.util.UNINSTALL)
        if "The operation completed successfully." in out.str:
            log.warning(f"{self}: Successfully uninstalled!")
            return
        raise RuntimeWarning("{self}: Could not uninstall!")


class Pywersl(AwaitLoader):
    """
    Pywershell Windows System for Linux
    """
    instances = {}

    def __init__(self, *, distro: str = "Debian"):
        self.distro_str = distro
        self.pywershell = PywershellLive(alias="WSL", prefix=r"C:\Windows\System32\wsl.exe", debug=True)
        log.success(f"{self}: Initialized successfully!")

    def __repr__(self):
        return f"[Pywersl.{self.distro}]"

    @classmethod
    async def get(cls, distro: str):
        if distro in cls.instances:
            return cls.instances[distro]
        cls.instances[distro] = cls(distro=distro)
        return cls.instances[distro]

    @async_cached_property
    async def version(self):
        cmd = "--version"
        out = await self.pywershell.run(cmd)
        ver: list = out.__getattr__(cmd)
        wsl_vers: str = ver[0]
        item = "WSL version: "
        if not item in wsl_vers: raise RuntimeError
        wsl_vers_num: str = wsl_vers.replace(item, "")
        return wsl_vers_num

    @async_cached_property
    async def distro(self) -> Distro:
        distro: Distro = await Distro(self)
        return distro

    async def run(self, cmd: str | list, **kwargs) -> CMDResult | None:
        prefix = kwargs.pop("prefix", None)
        log.debug(
            f"{self}: Received request:\n  - caller={get_caller_context()}\n  - prefix={prefix}\n  - kwargs={kwargs}\n  - {cmd}")
        cmds = [cmd] if isinstance(cmd, str) else cmd
        full = []
        if prefix:
            prefix = f"{prefix} "
        else:
            prefix = ""
        for c in cmds:
            item = f"{prefix}{c}"
            full.append(item)
        log.debug(
            f"{self}: Sent request:\n  - receiver={self.distro}\n  - prefix={prefix}\n  - kwargs={kwargs}\n  - {cmd}")
        out = await self.distro.run(full, **kwargs)
        return out


# Globally exposed alias
pywersl = Pywersl.get("Debian")


async def debug():
    py = await Pywersl()
    log.debug(py.version)


if __name__ == "__main__":
    asyncio.run(debug())
