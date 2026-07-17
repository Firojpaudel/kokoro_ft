import os
import sys
import torch
import gradio as gr
from pathlib import Path

# Configure Gradio to use a local temp directory inside the project to avoid /tmp permission errors
os.environ["GRADIO_TEMP_DIR"] = str(Path(__file__).resolve().parent / "tmp")

# Add kokoro submodule to sys.path
_repo_root = Path(__file__).resolve().parent
_kokoro_submodule = _repo_root / "kikiri-tts" / "kokoro"
if _kokoro_submodule.exists() and str(_kokoro_submodule) not in sys.path:
    sys.path.insert(0, str(_kokoro_submodule))

from kokoro import KModel, KPipeline
import kokoro.pipeline as kp
from text_normalizer import normalize_text
import numpy as np
import re

# Register Nepali dynamically in KPipeline
kp.LANG_CODES['n'] = 'ne'
kp.ALIASES['ne'] = 'n'

# Paths
MODEL_PATH = "checkpoints/stage2_voice/nepali_kokoro_epoch3.pth"
VOICEPACK_PATH = "kikiri-tts/kokoro/voices/nepali_ft.pt"
CONFIG_PATH = "configs/stage2.yaml"

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading KModel on {device}...")
kmodel = KModel(repo_id="hexgrad/Kokoro-82M", config=None, model=MODEL_PATH)
kmodel = kmodel.to(device).eval()

# Load pipeline
pipeline = KPipeline(lang_code="n", repo_id="hexgrad/Kokoro-82M", model=kmodel)
from text_normalizer import NepaliHybridG2P
pipeline.g2p = NepaliHybridG2P()

# Load voicepack
print(f"Loading voicepack: {VOICEPACK_PATH}")
voice = torch.load(VOICEPACK_PATH, map_location="cpu", weights_only=True)

def tts_interface(text, speed):
    if not text.strip():
        return None, "Please enter some text.", ""
    
    try:
        # 1. Normalize the text
        normalized_text = normalize_text(text)
        print("Normalized Text:", normalized_text)
        
        # 2. Chunk text by sentence boundaries (। ? ! . \n)
        chunks = re.split(r'([।?!.\n])', normalized_text)
        
        sentences = []
        current_sentence = ""
        for part in chunks:
            if not part:
                continue
            if part in ['।', '?', '!', '.', '\n']:
                current_sentence += part
                sentences.append(current_sentence.strip())
                current_sentence = ""
            else:
                current_sentence += part
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
            
        sentences = [s for s in sentences if s.strip()]
        
        if not sentences:
            return None, "No text to synthesize.", normalized_text
            
        all_audio = []
        all_phonemes = []
        
        # 0.25-second silence separator
        silence = np.zeros(int(24000 * 0.25), dtype=np.float32)
        
        for idx, sentence in enumerate(sentences):
            print(f"Synthesizing chunk {idx+1}/{len(sentences)}: {sentence}")
            try:
                generator = pipeline(sentence, voice=voice, speed=speed)
                chunk_audio = []
                for gs, ps, audio in generator:
                    if ps:
                        all_phonemes.append(ps)
                    if audio is not None and len(audio) > 0:
                        chunk_audio.append(audio)
                if chunk_audio:
                    all_audio.append(np.concatenate(chunk_audio))
                    if idx < len(sentences) - 1:
                        all_audio.append(silence)
            except Exception as ce:
                print(f"Error processing chunk: {ce}")
                    
        if all_audio:
            combined_audio = np.concatenate(all_audio)
            phonemes_str = " | ".join(all_phonemes)
            return (24000, combined_audio), phonemes_str, normalized_text
        else:
            return None, "Error: No audio was generated.", normalized_text
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"Execution failed: {str(e)}", ""

# Create Gradio app with generic layout and absolutely no emojis
with gr.Blocks() as app:
    gr.Markdown("# Nepali Text-to-Speech Web Interface")
    gr.Markdown("Synthesize speech from Nepali text using the fine-tuned Kokoro model.")
    
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Input Text", 
                value="नमस्ते, यो नेपाली स्वर परीक्षण हो।",
                lines=5
            )
            speed_input = gr.Slider(
                label="Speed", 
                minimum=0.5, 
                maximum=2.0, 
                value=1.0, 
                step=0.1
            )
            submit_btn = gr.Button("Generate Speech", variant="primary")
        
        with gr.Column():
            audio_output = gr.Audio(label="Output Audio")
            normalized_output = gr.Textbox(label="Normalized Text", interactive=False)
            phonemes_output = gr.Textbox(label="Generated Phonemes", interactive=False)
            
    submit_btn.click(
        fn=tts_interface, 
        inputs=[text_input, speed_input], 
        outputs=[audio_output, phonemes_output, normalized_output]
    )

if __name__ == "__main__":
    app.queue().launch(server_name="0.0.0.0", share=True)
