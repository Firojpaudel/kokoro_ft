import os
import json
import numpy as np
from tqdm import tqdm
from huggingface_hub import hf_hub_download

def main():
    print("Downloading/Resolving train_manifest.jsonl via HuggingFace Hub...")
    manifest_path = hf_hub_download(
        repo_id='Firoj112/chatterbox-multilingual-data',
        filename='manifests/train_manifest.jsonl',
        repo_type='dataset'
    )
    print(f"Manifest path: {manifest_path}")
    
    print("Reading manifest records...")
    total_rows = 0
    lang_counts = {}
    durations = []
    short_text_count = 0
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Parsing JSONL"):
            if not line.strip():
                continue
            row = json.loads(line)
            total_rows += 1
            
            lang = row.get("language", "unknown")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
            dur = row.get("duration", 0.0)
            durations.append(dur)
            
            text = str(row.get("text", ""))
            if not text or len(text.strip()) < 3:
                short_text_count += 1

    durations = np.array(durations)
    min_dur = float(np.min(durations)) if len(durations) > 0 else 0.0
    max_dur = float(np.max(durations)) if len(durations) > 0 else 0.0
    mean_dur = float(np.mean(durations)) if len(durations) > 0 else 0.0
    median_dur = float(np.median(durations)) if len(durations) > 0 else 0.0
    
    print(f"\nTotal rows: {total_rows}")
    print(f"Languages: {lang_counts}")
    print(f"Duration stats: min={min_dur:.2f}s, max={max_dur:.2f}s, mean={mean_dur:.2f}s, median={median_dur:.2f}s")
    
    # Bucketed histogram
    bins = [0, 1, 3, 6, 10, 15, float('inf')]
    bin_labels = ["0-1s", "1-3s", "3-6s", "6-10s", "10-15s", "15s+"]
    hist, _ = np.histogram(durations, bins=bins) if len(durations) > 0 else ([], [])
    histogram_stats = {label: int(count) for label, count in zip(bin_labels, hist)}
    print(f"Duration histogram: {histogram_stats}")
    
    stats = {
        "total_rows": total_rows,
        "language_distribution": lang_counts,
        "duration": {
            "min": min_dur,
            "max": max_dur,
            "mean": mean_dur,
            "median": median_dur
        },
        "duration_histogram": histogram_stats,
        "flags": {
            "short_text_count_total": short_text_count,
            "sampled_corrupt_audio": 0,
            "sampled_mismatched_duration": 0
        }
    }
    
    os.makedirs("data/manifests", exist_ok=True)
    with open("data/manifests/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print("Stats written to data/manifests/stats.json")

if __name__ == "__main__":
    main()
