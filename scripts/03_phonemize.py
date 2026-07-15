import os
import json
from tqdm import tqdm
from misaki import espeak
import sys

def main():
    print("Initializing Misaki EspeakG2P for Nepali (ne)...")
    try:
        g2p = espeak.EspeakG2P(language="ne")
    except Exception as e:
        print(f"Error initializing phonemizer: {e}")
        sys.exit(1)
        
    # Load Kokoro's symbols to diff against
    try:
        # Add kikiri-tts/StyleTTS2 to path to import kokoro_symbols
        sys.path.append(os.path.abspath("kikiri-tts/StyleTTS2"))
        from kokoro_symbols import symbols as kokoro_symbols
        kokoro_vocab = set(kokoro_symbols)
    except Exception as e:
        print(f"Warning: Could not load kokoro_symbols: {e}. Vocabulary diff will be skipped.")
        kokoro_vocab = set()

    manifest_files = ["train", "val"]
    
    seen_phonemes = set()
    
    for name in manifest_files:
        jsonl_path = f"data/manifests/{name}.jsonl"
        txt_path = f"data/manifests/{name}.txt"
        
        if not os.path.exists(jsonl_path):
            print(f"Manifest {jsonl_path} does not exist. Skipping.")
            continue
            
        print(f"Phonemizing {jsonl_path}...")
        
        updated_rows = []
        txt_lines = []
        
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc=f"G2P {name}"):
                if not line.strip():
                    continue
                row = json.loads(line)
                text = row.get("text", "")
                
                try:
                    phonemes, _ = g2p(text)
                    # Misaki output is IPA phonemes. Let's keep it as is.
                    row["phonemes"] = phonemes
                    
                    # Track symbols
                    for char in phonemes:
                        seen_phonemes.add(char)
                        
                except Exception as e:
                    print(f"Warning: Failed to phonemize '{text}': {e}")
                    row["phonemes"] = ""
                
                # StyleTTS2 format: audio_path|phonemes|speaker
                speaker = str(row.get("speaker", "0"))
                # Ensure relative path from project root (configs/stage1.yaml specifies data_params paths relative to CWD)
                audio_path = row["audio_path"]
                txt_lines.append(f"{audio_path}|{row['phonemes']}|{speaker}")
                updated_rows.append(row)
                
        # Write back updated jsonl
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for r in updated_rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                
        # Write StyleTTS2 txt format
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(txt_lines) + "\n")
            
        print(f"Wrote updated JSONL to {jsonl_path} and text file to {txt_path}")
        
    # Write vocab
    vocab_list = sorted(list(seen_phonemes))
    vocab_path = "data/phoneme_vocab.json"
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab_list, f, indent=2, ensure_ascii=False)
        
    print(f"Discovered {len(vocab_list)} unique phonemes/symbols. Saved to {vocab_path}")
    
    if kokoro_vocab:
        new_symbols = seen_phonemes - kokoro_vocab
        print(f"New symbols not present in Kokoro-82M vocabulary ({len(new_symbols)}):")
        print(sorted(list(new_symbols)))
        print(f"Total symbols covered: {len(seen_phonemes & kokoro_vocab)} / {len(seen_phonemes)}")

if __name__ == "__main__":
    main()
