import os
import sys
import torch
import gradio as gr
from pathlib import Path

# Add kokoro submodule to sys.path
_repo_root = Path(__file__).resolve().parent
_kokoro_submodule = _repo_root / "kikiri-tts" / "kokoro"
if _kokoro_submodule.exists() and str(_kokoro_submodule) not in sys.path:
    sys.path.insert(0, str(_kokoro_submodule))

from kokoro import KModel, KPipeline
import kokoro.pipeline as kp

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

# Load voicepack
print(f"Loading voicepack: {VOICEPACK_PATH}")
voice = torch.load(VOICEPACK_PATH, map_location="cpu", weights_only=True)

def tts_interface(text, speed):
    if not text.strip():
        return None, "Please enter some text."
    
    try:
        generator = pipeline(text, voice=voice, speed=speed)
        all_audio = []
        all_phonemes = []
        
        for gs, ps, audio in generator:
            all_phonemes.append(ps)
            all_audio.append(audio)
            
        if all_audio:
            import numpy as np
            combined_audio = np.concatenate(all_audio)
            phonemes_str = " | ".join(all_phonemes)
            return (24000, combined_audio), phonemes_str
        else:
            return None, "Error: No audio was generated."
    except Exception as e:
        return None, f"Execution failed: {str(e)}"

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
            phonemes_output = gr.Textbox(label="Generated Phonemes", interactive=False)
            
    submit_btn.click(
        fn=tts_interface, 
        inputs=[text_input, speed_input], 
        outputs=[audio_output, phonemes_output]
    )

if __name__ == "__main__":
    app.queue().launch(server_name="0.0.0.0", server_port=7861, share=True)
