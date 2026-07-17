import os
from datasets import Dataset, DatasetDict, Audio

def load_env_manually():
    env_path = "/home/oem/wiseyak_backup/firojpaudel/kokoro_ft/.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()

def main():
    load_env_manually()
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN not found in environment.")
        return

    # Use the local manifests to load the datasets
    base_dir = "/home/oem/wiseyak_backup/firojpaudel/kokoro_ft"
    train_jsonl = os.path.join(base_dir, "data/manifests/train.jsonl")
    val_jsonl = os.path.join(base_dir, "data/manifests/val.jsonl")

    print("Loading train dataset from JSONL...")
    train_dataset = Dataset.from_json(train_jsonl)
    
    print("Loading validation dataset from JSONL...")
    val_dataset = Dataset.from_json(val_jsonl)

    # The jsonl has column "audio_path"
    # We rename "audio_path" to "audio"
    if "audio_path" in train_dataset.column_names:
        train_dataset = train_dataset.rename_column("audio_path", "audio")
    if "audio_path" in val_dataset.column_names:
        val_dataset = val_dataset.rename_column("audio_path", "audio")

    # In the local jsonl, the path is "data/audio_24k/nepali_XXX.wav"
    # Since we are running the script in the kokoro_ft directory, the paths are resolved correctly relative to CWD.
    print("Casting 'audio' column to Audio feature...")
    train_dataset = train_dataset.cast_column("audio", Audio(sampling_rate=24000))
    val_dataset = val_dataset.cast_column("audio", Audio(sampling_rate=24000))

    dataset_dict = DatasetDict({
        "train": train_dataset,
        "validation": val_dataset
    })

    # Push to Hugging Face Hub (this will create Parquet files with embedded audio bytes)
    # This completely solves the "Not supported with pagination yet" issue!
    repo_id = f"Firoj112/nepali-kokoro-ft-data"
    print(f"Pushing DatasetDict to Hugging Face Hub as {repo_id}...")
    dataset_dict.push_to_hub(
        repo_id=repo_id,
        private=True,
        token=token
    )
    print("Dataset successfully pushed! Go check the Hugging Face page now.")

if __name__ == "__main__":
    main()
