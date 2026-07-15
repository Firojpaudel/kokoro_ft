import os
import sys
import argparse
import torch
import soundfile as sf
from pathlib import Path

# Add kokoro submodule to sys.path
_repo_root = Path(__file__).resolve().parent.parent
_kokoro_submodule = _repo_root / "kikiri-tts" / "kokoro"
if _kokoro_submodule.exists() and str(_kokoro_submodule) not in sys.path:
    sys.path.insert(0, str(_kokoro_submodule))

from kokoro import KModel, KPipeline
import kokoro.pipeline as kp

# Register Nepali in KPipeline dynamically
kp.LANG_CODES['n'] = 'ne'
kp.ALIASES['ne'] = 'n'

# Fixed list of evaluation sentences
EVAL_SENTENCES = [
    "सिलगढी जङ्सन स्टेसन अब नयाँ रूपमा सजिनेछ।",
    "नेपाल एक सुन्दर देश हो जहाँ सगरमाथा अवस्थित छ।",
    "तपाईंलाई कस्तो छ? मलाई निकै राम्रो छ।",
    "काठमाडौँ नेपालको राजधानी सहर हो।",
    "आजको मौसम कस्तो छ? के पानी पर्ने सम्भावना छ?",
    "म नेपाली भाषा सिक्दैछु र मलाई यो भाषा मनपर्छ।",
    "यो एउटा लामो वाक्य हो जसको उद्देश्य मोडेलको सिर्जनात्मक क्षमता र लामो समयसम्म टिकिरहने स्वरको गुणस्तर परीक्षण गर्नु हो।",
    "१ २ ३ ४ ५ ६ ७ ८ ९ १०",
    "के तपाईंलाई थाहा छ कि ज्ञान नै सबैभन्दा ठूलो शक्ति हो?",
    "संसारका सबै मानिसहरू स्वतन्त्र र समान अधिकारका साथ जन्मिन्छन्।"
]

def main():
    parser = argparse.ArgumentParser(description="Generate evaluation samples for Nepali TTS.")
    parser.add_argument("--model", type=str, required=True, help="Path to converted Kokoro model weight file (.pth).")
    parser.add_argument("--voicepack", type=str, required=True, help="Path to voicepack file (.pt).")
    parser.add_argument("--config", type=str, default="configs/stage1.yaml", help="Path to model config yaml.")
    parser.add_argument("--output-dir", type=str, default="data/eval_samples", help="Output directory for wav files.")
    parser.add_argument("--device", type=str, default="auto", help="Device to run on (cuda, cpu, auto).")
    args = parser.parse_args()

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"Using device: {device}")
    print(f"Loading model: {args.model}")
    print(f"Loading config: {args.config}")
    
    kmodel = KModel(repo_id="hexgrad/Kokoro-82M", config=args.config, model=args.model)
    kmodel = kmodel.to(device).eval()

    # Instantiate pipeline with 'n' (Nepali)
    pipeline = KPipeline(lang_code="n", repo_id="hexgrad/Kokoro-82M", model=kmodel)

    print(f"Loading voicepack: {args.voicepack}")
    voice = torch.load(args.voicepack, map_location="cpu", weights_only=True)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(EVAL_SENTENCES)} evaluation samples...")
    for idx, sentence in enumerate(EVAL_SENTENCES):
        print(f"[{idx+1}/{len(EVAL_SENTENCES)}] Text: '{sentence}'")
        try:
            generator = pipeline(sentence, voice=voice, speed=1.0)
            all_audio = []
            for gs, ps, audio in generator:
                print(f"  Phonemes: '{ps}'")
                all_audio.append(audio)
            
            if all_audio:
                import numpy as np
                combined = np.concatenate(all_audio)
                wav_path = out_dir / f"eval_{idx+1:02d}.wav"
                sf.write(str(wav_path), combined, 24000)
                print(f"  Saved: {wav_path} ({len(combined)/24000:.1f}s)")
            else:
                print("  WARNING: No audio generated")
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone! Evaluation samples saved to {args.output_dir}/")

if __name__ == "__main__":
    main()
