import os
import json
import argparse
import numpy as np
import librosa
import soundfile as sf
import datasets
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Prepare manifests and process audio files.")
    parser.add_argument("--limit", type=int, default=0, help="Limit the number of samples to process (0 for no limit).")
    parser.add_argument("--min-duration", type=float, default=0.3, help="Minimum duration in seconds.")
    parser.add_argument("--max-duration", type=float, default=20.0, help="Maximum duration in seconds.")
    parser.add_argument("--val-ratio", type=float, default=0.05, help="Validation set ratio.")
    args = parser.parse_args()

    print("Loading dataset Firoj112/chatterbox-multilingual-data in streaming mode...")
    ds = datasets.load_dataset("Firoj112/chatterbox-multilingual-data", split="train", streaming=True)
    # Disable decoding of the audio column to avoid dependency on torchcodec/libsndfile decoding during streaming
    ds = ds.cast_column("audio", datasets.Audio(decode=False))
    
    # We will process only Nepali records. Since they are the first 28,128 rows,
    # we can stop iterating once we hit the limit or finished all 'ne' rows.
    max_ne_rows = 28128
    limit = args.limit if args.limit > 0 else max_ne_rows
    limit = min(limit, max_ne_rows)
    
    print(f"Targeting to process up to {limit} Nepali (ne) records...")
    
    os.makedirs("data/audio_24k", exist_ok=True)
    os.makedirs("data/manifests", exist_ok=True)
    
    processed_records = []
    
    # Iterator with progress bar
    pbar = tqdm(total=limit, desc="Processing audio")
    
    for idx, row in enumerate(ds):
        if len(processed_records) >= limit or idx >= max_ne_rows:
            break
            
        lang = row.get("language", "")
        if lang != "ne":
            # Just in case, skip non-Nepali
            continue
            
        duration = row.get("duration", 0.0)
        if duration < args.min_duration or duration > args.max_duration:
            continue
            
        text = str(row.get("text", "")).strip()
        if len(text) < 3:
            continue
            
        # Extract audio bytes
        audio_data = row.get("audio", {})
        if not audio_data or "bytes" not in audio_data or audio_data["bytes"] is None:
            continue
            
        try:
            # Load audio using soundfile from bytes
            import io
            audio_bytes = audio_data["bytes"]
            y, sr = sf.read(io.BytesIO(audio_bytes))
            
            # Convert to mono if stereo
            if len(y.shape) > 1:
                y = librosa.to_mono(y.T)
                
            # Resample to 24kHz if needed
            if sr != 24000:
                y = librosa.resample(y, orig_sr=sr, target_sr=24000)
                
            # Normalize loudness: RMS to -20 dBFS
            rms = np.sqrt(np.mean(y**2))
            if rms > 0:
                target_rms = 10 ** (-20 / 20)
                y = y * (target_rms / rms)
                
            # Peak normalization safety: ensure no clipping
            peak = np.max(np.abs(y))
            if peak > 0.99:
                y = y / peak * 0.99
                
            # Write processed WAV file
            filename = f"nepali_{len(processed_records)}.wav"
            filepath = os.path.join("data/audio_24k", filename)
            sf.write(filepath, y, 24000, subtype='PCM_16')
            
            # Save record info
            processed_records.append({
                "audio_path": filepath,
                "text": text,
                "language": "ne",
                "duration": float(len(y) / 24000)
            })
            
            pbar.update(1)
            
        except Exception as e:
            # Print warning but keep going
            print(f"\nWarning: Failed to process record {idx}: {e}")
            continue
            
    pbar.close()
    
    total_processed = len(processed_records)
    print(f"Successfully processed {total_processed} Nepali records.")
    
    if total_processed == 0:
        print("Error: No records were processed. Manifests cannot be created.")
        return
        
    # Split into train and validation
    np.random.seed(42)
    shuffled_indices = np.random.permutation(total_processed)
    val_size = int(total_processed * args.val_ratio)
    
    val_indices = shuffled_indices[:val_size]
    train_indices = shuffled_indices[val_size:]
    
    train_records = [processed_records[i] for i in train_indices]
    val_records = [processed_records[i] for i in val_indices]
    
    # Write JSONL manifests
    train_path = "data/manifests/train.jsonl"
    val_path = "data/manifests/val.jsonl"
    
    with open(train_path, "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    with open(val_path, "w", encoding="utf-8") as f:
        for r in val_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"Manifests created: {len(train_records)} train, {len(val_records)} val.")

if __name__ == "__main__":
    main()
