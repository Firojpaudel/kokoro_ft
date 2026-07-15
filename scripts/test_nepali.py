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

# Register Nepali dynamically in KPipeline
kp.LANG_CODES['n'] = 'ne'
kp.ALIASES['ne'] = 'n'

def main():
    parser = argparse.ArgumentParser(description="Test inference for fine-tuned Nepali Kokoro model.")
    parser.add_argument("--text", type=str, default="नमस्ते, यो नेपाली स्वर परीक्षण हो।", help="Text to synthesize.")
    parser.add_argument("--model", type=str, required=True, help="Path to converted Kokoro model checkpoint (.pth).")
    parser.add_argument("--voicepack", type=str, required=True, help="Path to voicepack (.pt) file.")
    parser.add_argument("--config", type=str, default="configs/stage1.yaml", help="Path to configs/stage1.yaml.")
    parser.add_argument("--output", type=str, default="test_nepali_output.wav", help="Path to save output wav.")
    parser.add_argument("--device", type=str, default="auto", help="Device to run on (cuda, cpu, auto).")
    args = parser.parse_args()

    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"Device: {device}")
    print(f"Loading model: {args.model}")
    print(f"Loading config: {args.config}")
    
    # Load model
    kmodel = KModel(repo_id="hexgrad/Kokoro-82M", config=args.config, model=args.model)
    kmodel = kmodel.to(device).eval()

    # Load pipeline
    pipeline = KPipeline(lang_code="n", repo_id="hexgrad/Kokoro-82M", model=kmodel)

    print(f"Loading voicepack: {args.voicepack}")
    voice = torch.load(args.voicepack, map_location="cpu", weights_only=True)

    print(f"Synthesizing text: '{args.text}'")
    try:
        generator = pipeline(args.text, voice=voice, speed=1.0)
        all_audio = []
        for gs, ps, audio in generator:
            print(f"Phonemes: '{ps}'")
            all_audio.append(audio)
            
        if all_audio:
            import numpy as np
            combined = np.concatenate(all_audio)
            sf.write(args.output, combined, 24000)
            print(f"Success! Saved synthesized audio to: {args.output}")
        else:
            print("Error: No audio was generated.")
    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    main()
