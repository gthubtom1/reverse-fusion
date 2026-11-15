#!/usr/bin/env sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
python_bin=${RF_PYTHON:-}
if [ -z "$python_bin" ]; then
  if command -v python >/dev/null 2>&1; then python_bin=python
  elif command -v python3 >/dev/null 2>&1; then python_bin=python3
  else echo 'set RF_PYTHON to a Python 3.11+ launcher' >&2; exit 2
  fi
fi
venv=${1:-"$repo/.venv"}
venv=$("$python_bin" -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$venv")
if command -v cygpath >/dev/null 2>&1; then venv=$(cygpath -u "$venv"); fi
case "$venv" in "$repo"/*) ;; *) echo "venv must stay inside repository" >&2; exit 2 ;; esac
receipt=$("$python_bin" -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$repo/state/install.json")
if command -v cygpath >/dev/null 2>&1; then receipt=$(cygpath -u "$receipt"); fi
case "$receipt" in "$repo"/*) ;; *) echo "receipt must stay inside repository" >&2; exit 2 ;; esac

if [ -e "$venv" ]; then rm -rf -- "$venv"; fi
if [ -f "$receipt" ]; then rm -f -- "$receipt"; fi
printf '%s\n' '{"status":"uninstalled","global_config_mutation":false}'
