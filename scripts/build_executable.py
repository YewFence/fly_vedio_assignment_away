from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    platform_suffix = {
        "darwin": "macos",
        "win32": "windows",
    }.get(sys.platform, sys.platform)
    executable_name = f"fly_video_assignment_away-{platform_suffix}"
    entrypoint = Path("src/fly_vedio_assignment_away/__main__.py")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--onefile",
            "--name",
            executable_name,
            str(entrypoint),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
