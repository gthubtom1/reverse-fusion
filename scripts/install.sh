#!/usr/bin/env sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
python_bin=${RF_PYTHON:-}
if [ -z "$python_bin" ]; then
  if command -v python >/dev/null 2>&1; then
    python_bin=python
  elif command -v python3 >/dev/null 2>&1; then
    python_bin=python3
  else
    echo "set RF_PYTHON to a Python 3.11+ launcher" >&2
    exit 2
  fi
fi
venv=${1:-"$repo/.venv"}
venv=$("$python_bin" -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$venv")
if command -v cygpath >/dev/null 2>&1; then venv=$(cygpath -u "$venv"); fi
case "$venv" in "$repo"/*) ;; *) echo "venv must stay inside repository" >&2; exit 2 ;; esac
if [ "${RF_DRY_RUN:-0}" = 1 ]; then
  printf '%s\n' "$python_bin -m venv $venv" "$venv/bin/python -m pip install --no-deps -e $repo"
  exit 0
fi
"$python_bin" -m venv "$venv"
venv_python="$venv/bin/python"
if [ -x "$venv/Scripts/python.exe" ]; then venv_python="$venv/Scripts/python.exe"; fi
"$venv_python" -m pip install --no-deps -e "$repo"
printf '%s\n' '{"status":"package-only","core_deployment":"incomplete","reason":"Native Craft distribution currently qualified on Windows x64; port and verify core before deployment"}'
if [ "${RF_PACKAGE_ONLY:-0}" != 1 ]; then exit 2; fi
