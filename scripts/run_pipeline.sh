#!/usr/bin/env bash
# scripts/run_pipeline.sh
set -euo pipefail

echo "=== STEP 0: Cleaning codebase ==="
rm -rf data/audio_24k/* data/manifests/*.jsonl data/manifests/*.txt

echo "=== STEP 1: Preparing Manifests & Audio (Full Dataset) ==="
# This will download parquet files sequentially, resample to 24kHz, and save to data/audio_24k/
uv run python scripts/02_prepare_manifests.py

echo "=== STEP 2: Running Phonemizer (Misaki G2P) ==="
uv run python scripts/03_phonemize.py

echo "=== STEP 3: Generating Phoneme Validation Samples ==="
uv run python scripts/04_validate_phonemes.py

echo "=== STEP 4: Starting Stage 1 Training (Base Adaptation) ==="
bash scripts/train_stage1.sh
