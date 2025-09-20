#!/usr/bin/env bash
set -euo pipefail
cd /home/ubuntu/arb-bot

# ativa venv
source .venv/bin/activate

# exporta .env (para apps que não usam python-dotenv)
set -a
[ -f .env ] && source .env
set +a

# roda um scan (one-shot). Ajuste parâmetros se quiser.
python -m src.apps.tri_scan --start_qty 1000 --min_edge 0.0005 --fee_bps 10 "$@" \
  >> logs/tri_watch.log 2>&1 || true
