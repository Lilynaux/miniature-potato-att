#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

source ~/opt/anaconda3/bin/activate Tools

cd "$SCRIPT_DIR"

python app.py