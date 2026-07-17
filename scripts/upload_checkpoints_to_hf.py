import os
from huggingface_hub import HfApi

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

    # Initialize HfApi
    api = HfApi(token=token)
    try:
        user_info = api.whoami()
        username = user_info["name"]
    except Exception as e:
        print(f"Auth failed: {e}")
        return

    # Define model repository id
    repo_id = f"{username}/kokoro-nepali-base-adaptation"
    print(f"Target model repository: {repo_id}")

    # Create the model repository
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="model",
            private=True,
            exist_ok=True
        )
        print(f"Model repository {repo_id} created or already exists.")
    except Exception as e:
        print(f"Error creating repo: {e}")
        return

    base_dir = "/home/oem/wiseyak_backup/firojpaudel/kokoro_ft"
    checkpoints_to_upload = {
        # file_path_locally: path_in_repo
        os.path.join(base_dir, "logs/stage2_voice/epoch_2nd_00002.pth"): "epoch_2nd_00002.pth",
        os.path.join(base_dir, "checkpoints/stage2_voice/nepali_kokoro_epoch3.pth"): "nepali_kokoro_epoch3.pth",
        os.path.join(base_dir, "kikiri-tts/kokoro/voices/nepali_ft.pt"): "voices/nepali_ft.pt",
        os.path.join(base_dir, "configs/stage2.yaml"): "stage2.yaml"
    }

    # Upload checkpoints
    for local_path, repo_path in checkpoints_to_upload.items():
        if os.path.exists(local_path):
            print(f"Uploading {os.path.basename(local_path)} to HF as '{repo_path}'...")
            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=repo_path,
                    repo_id=repo_id,
                    repo_type="model"
                )
                print(f"Successfully uploaded {os.path.basename(local_path)}!")
            except Exception as e:
                print(f"Failed to upload {os.path.basename(local_path)}: {e}")
        else:
            print(f"Warning: File {local_path} not found.")

    print(f"\nCheckpoints successfully uploaded! View your model repo at: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    main()
