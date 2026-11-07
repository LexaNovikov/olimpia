"""Собрать приложение для текущей операционной системы."""

import os
from pathlib import Path
import subprocess
import sys


root = Path(__file__).resolve().parent
data_separator = ";" if sys.platform == "win32" else ":"
bundle_mode = "--onedir" if sys.platform == "darwin" else "--onefile"

subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        bundle_mode,
        "--windowed",
        "--name",
        "Olimpia",
        "--hidden-import=openpyxl",
        "--add-data",
        f"{root / 'halls.json'}{data_separator}.",
        str(root / "gui.py"),
    ],
    cwd=root,
    check=True,
)
