#!/usr/bin/env sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
venv=${1:-"$repo/.venv"}
case "$venv" in "$repo"/*) ;; *) echo "venv must stay inside repository" >&2; exit 2 ;; esac
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
if [ "${RF_DRY_RUN:-0}" = 1 ]; then
  printf '%s\n' "$python_bin -m venv $venv" "$venv/bin/python -m pip install --no-deps -e $repo"
  exit 0
fi
"$python_bin" -m venv "$venv"
"$venv/bin/python" -m pip install --no-deps -e "$repo"
printf '%s\n' '{"status":"installed","global_config_mutation":false}'
