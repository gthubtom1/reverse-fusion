#!/usr/bin/env sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
venv=${1:-"$repo/.venv"}
case "$venv" in "$repo"/*) ;; *) echo "venv must stay inside repository" >&2; exit 2 ;; esac
if [ "${RF_DRY_RUN:-0}" = 1 ]; then
  printf '%s\n' "python -m venv $venv" "$venv/bin/python -m pip install --no-deps -e $repo"
  exit 0
fi
python -m venv "$venv"
"$venv/bin/python" -m pip install --no-deps -e "$repo"
printf '%s\n' '{"status":"installed","global_config_mutation":false}'
