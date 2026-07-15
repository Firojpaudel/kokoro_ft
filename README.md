# Kokoro-82M Nepali Fine-Tuning Pipeline

This repository contains the structured workflow and preprocessing pipeline to fine-tune `hexgrad/Kokoro-82M` for Nepali. 

### Attribution & Sources
This codebase includes and adapts components from the following projects:
1. **kikiri-tts**: Cloned and adapted from the community-reverse-engineered training pipeline at [semidark/kikiri-tts](https://github.com/semidark/kikiri-tts).
2. **StyleTTS2**: Integrated patched StyleTTS2 training modules from [semidark/StyleTTS2](https://github.com/semidark/StyleTTS2) (forked/submodule of [yl4579/StyleTTS2](https://github.com/yl4579/StyleTTS2)).
3. **Kokoro**: Integrated Kokoro model adaptation code from [hexgrad/kokoro](https://github.com/hexgrad/kokoro).

---

## 1. Directory Structure

```
/home/oem/wiseyak_backup/firojpaudel/kokoro_ft/
├── kikiri-tts/                  # git clone of semidark/kikiri-tts (training code + submodules)
├── data/
│   ├── raw/                     # original dataset manifests
│   ├── audio_24k/               # resampled, mono, 24kHz wav files
│   └── manifests/
│       ├── train.jsonl          # train dataset mapping
│       ├── val.jsonl            # validation dataset mapping
│       ├── train.txt            # StyleTTS2 format list
│       ├── val.txt              # StyleTTS2 format list
│       └── stats.json           # overall dataset statistics
├── checkpoints/
│   ├── stage1_base/             # stage 1 base checkpoints
│   └── stage2_voice/            # stage 2 single-speaker checkpoints
├── logs/
│   ├── stage1_train.log         # logs for stage 1
│   └── stage2_train.log         # logs for stage 2
├── configs/
│   ├── stage1.yaml              # stage 1 training config
│   └── stage2.yaml              # stage 2 training config
├── pyproject.toml               # uv project file
├── uv.lock                      # uv lockfile
├── scripts/
│   ├── 01_inspect_dataset.py    # inspect dataset stats
│   ├── 02_prepare_manifests.py  # resample and prepare lists
│   ├── 03_phonemize.py          # misaki G2P phonemizer
│   ├── 04_validate_phonemes.py  # side-by-side verification
│   ├── train_stage1.sh          # stage 1 launcher (tmux)
│   ├── train_stage2.sh          # stage 2 launcher (tmux)
│   └── generate_eval_samples.py # inference sample generator
└── README.md                    # this documentation
```

---

## 2. Environment Setup

All dependencies are managed using `uv`.

```bash
# Verify system dependencies
espeak-ng --voices=ne

# Sync dependencies
uv sync

# Configure environment variables
# Copy .env.example to .env and configure your W&B API Key
cp .env.example .env
# Edit .env and paste your actual WANDB_API_KEY
```

---

## 3. Data Processing Workflow

### Step 1: Inspect the Dataset
Analyze target counts, durations, and languages:
```bash
uv run python scripts/01_inspect_dataset.py
```

### Step 2: Prepare the Manifests & Audio
Resample, RMS-normalize loudness, and split the first N records (Nepali subset):
```bash
# Run a quick check with the first 100 samples
uv run python scripts/02_prepare_manifests.py --limit 100

# Process all 28,128 Nepali records
uv run python scripts/02_prepare_manifests.py
```

### Step 3: Phonemization
Phonemize using `misaki`'s espeak-ng Nepali G2P frontend:
```bash
uv run python scripts/03_phonemize.py
```

### Step 4: Validate Phonemes
Generate a sample report to manually check phoneme quality:
```bash
uv run python scripts/04_validate_phonemes.py
# View data/manifests/phoneme_samples.txt to review
```

---

## 4. Fine-Tuning Training

Verify monotonic alignment has been compiled successfully:
```bash
cd kikiri-tts/StyleTTS2/monotonic_align
uv run python setup.py build_ext --inplace
```

### Stage 1: Multi-Speaker Base Adaptation
Run inside a detachable `tmux` session:
```bash
tmux new -s kokoro-stage1
bash scripts/train_stage1.sh 2>&1 | tee -a logs/stage1_train.log
```

### Stage 2: Single-Speaker Refinement
Run inside a detachable `tmux` session:
```bash
tmux new -s kokoro-stage2
bash scripts/train_stage2.sh 2>&1 | tee -a logs/stage2_train.log
```

---

## 5. Evaluation
Generate audio samples for 10 evaluation sentences to monitor progress:
```bash
uv run python scripts/generate_eval_samples.py \
  --model checkpoints/stage1_base/first_stage.pth \
  --voicepack checkpoints/stage1_base/eval_samples/nepali.pt \
  --config configs/stage1.yaml
```
