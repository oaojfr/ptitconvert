#!/usr/bin/env python3
"""
Build the FastAPI backend into standalone binaries using PyInstaller.

Outputs into bin/{macos,win,linux}/backend[.exe]

Usage:
  python scripts/build_backend.py
Requirements:
  pip install pyinstaller
"""
import os
import platform
import shutil
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'backend' / 'server.py'
BIN = ROOT / 'bin'


def run(cmd, cwd=None):
    print('>', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def clean_build_artifacts():
    for d in ['build', 'dist', '__pycache__']:
        p = ROOT / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)


def build_one(target: str):
    clean_build_artifacts()
    name = 'backend'
    exe_suffix = '.exe' if target == 'win' else ''
    run([sys.executable, '-m', 'PyInstaller', '--onefile', '--name', name, str(SERVER)])
    out_src = ROOT / 'dist' / f'{name}{exe_suffix}'
    out_dir = BIN / target
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(out_src), str(out_dir / f'{name}{exe_suffix}'))
    clean_build_artifacts()


def main():
    system = platform.system()
    if system == 'Darwin':
        build_one('macos')
    elif system == 'Windows':
        build_one('win')
    else:
        build_one('linux')
    print('Backend built into', BIN)


if __name__ == '__main__':
    main()
