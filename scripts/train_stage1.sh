#!/usr/bin/env bash
# scripts/train_stage1.sh
set -euo pipefail

# Move to the training directory
cd "/home/oem/wiseyak_backup/firojpaudel/kokoro_ft/kikiri-tts/StyleTTS2"

export CUDA_VISIBLE_DEVICES=0

# Load environment variables from .env if present
if [ -f ../../.env ]; then
  export $(cat ../../.env | grep -v '^#' | xargs)
fi

# Run Stage 1 training using accelerate launch and pointing to our config
# Note: we use absolute paths or relative paths correctly.
# The config file path is relative to the directory we run the command from,
# which is kikiri-tts/StyleTTS2, so ../../configs/stage1.yaml
../../.venv/bin/accelerate launch train_first.py --config_path ../../configs/stage1.yaml
