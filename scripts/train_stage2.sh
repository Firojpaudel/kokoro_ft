#!/usr/bin/env bash
# scripts/train_stage2.sh
set -euo pipefail

# Move to the training directory
cd "/home/oem/wiseyak_backup/firojpaudel/kokoro_ft/kikiri-tts/StyleTTS2"

export CUDA_VISIBLE_DEVICES=0

# Load environment variables from .env if present
if [ -f ../../.env ]; then
  export $(cat ../../.env | grep -v '^#' | xargs)
fi

# Run Stage 2 training using accelerate launch and pointing to our config, logging to pipeline.log
../../.venv/bin/accelerate launch --mixed_precision bf16 train_second.py --config_path ../../configs/stage2.yaml 2>&1 | tee -a ../../logs/pipeline.log
