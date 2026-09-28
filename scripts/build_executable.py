from __future__ import annotations

import platform
import subprocess
import sys
import tarfile
from pathlib import Path


def executable_name() -> str:
    os_suffix = {
        "darwin": "macos",
        "win32": "windows",
    }.get(sys.platform, sys.platform)
    machine = platform.machine().lower()
    arch_suffix = {
        "amd64": "x86_64",
        "aarch64": "arm64",
    }.get(machine, machine)
    return f"fly_video_assignment_away-{os_suffix}-{arch_suffix}"


def main() -> None:
    name = executable_name()
    entrypoint = Path("src/fly_video_assignment_away/__main__.py")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--onefile",
            "--name",
            name,
            str(entrypoint),
        ],
        check=True,
    )

    # 浏览器下载的裸二进制没有执行位，tar.gz 能把它带过去；Windows 双击 exe 最省事
    if sys.platform != "win32":
        executable = Path("dist") / name
        tarball = Path("dist") / f"{name}.tar.gz"
        with tarfile.open(tarball, "w:gz") as archive:
            archive.add(executable, arcname=executable.name)
        executable.unlink()


if __name__ == "__main__":
    main()
