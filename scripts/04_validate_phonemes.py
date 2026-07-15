import os
import json
import random

def main():
    manifest_path = "data/manifests/train.jsonl"
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest {manifest_path} does not exist. Run prepare_manifests and phonemize first.")
        return
        
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    if not records:
        print("No records found in manifest.")
        return
        
    # Sample up to 30 records
    sample_size = min(30, len(records))
    sampled_records = random.sample(records, sample_size)
    
    output_path = "data/manifests/phoneme_samples.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Sampling {sample_size} records for validation...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== PHONEME VALIDATION SAMPLE ===\n\n")
        for idx, r in enumerate(sampled_records):
            f.write(f"Sample {idx+1}:\n")
            f.write(f"Text    : {r.get('text', '')}\n")
            f.write(f"Phonemes: {r.get('phonemes', '')}\n")
            f.write("-" * 50 + "\n")
            
    print(f"Phoneme samples saved to {output_path} for manual inspection.")

if __name__ == "__main__":
    main()
