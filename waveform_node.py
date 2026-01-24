import torch
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend to avoid threading issues
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import os
import subprocess
import tempfile
import soundfile as sf

class AudioToWaveformImage:
    DESCRIPTION = "Generates a waveform image from audio data with optimized performance."

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "width": ("INT", {"default": 512, "min": 128, "max": 2048}),
                "height": ("INT", {"default": 256, "min": 64, "max": 1024}),
                "color": (["green", "#3232c8", "red", "white"], {"default": "#3232c8"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_waveform"
    CATEGORY = "AudioTools"

    def generate_waveform(self, audio, width, height, color):
        # Handle ComfyUI audio format (dict or tuple)
        if isinstance(audio, dict):
            waveform = audio["waveform"]
        else:
            waveform, _ = audio

        # Ensure 2D: [channels, samples]
        if waveform.ndim == 3: # [batch, channels, samples]
            waveform = waveform[0]
        
        # Merge channels to mono for visualization
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0)
        else:
            waveform = waveform[0]
        
        samples = waveform.cpu().numpy()

        # PERFORMANCE IMPROVEMENT: Decimate/Downsample
        # Plotting every sample is slow. We only need a few points per pixel.
        target_points = width * 4 
        if len(samples) > target_points:
            # Calculate the step to get roughly target_points
            step = len(samples) // target_points
            # Use slicing for fast decimation
            samples = samples[::step]

        # Create the plot using Matplotlib
        # Set figure size in inches based on DPI 100
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        fig.patch.set_alpha(0) # Set figure background to transparent
        ax.patch.set_alpha(0)  # Set axes background to transparent
        
        # Plot the waveform
        ax.plot(samples, color=color, linewidth=0.5)
        
        # Remove axes and padding
        ax.axis('off')
        fig.tight_layout(pad=0)

        # Convert plot to PIL Image
        buf = BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0)
        plt.close(fig) # Explicitly close to free memory
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")

        # Convert PIL to ComfyUI Tensor [B, H, W, C]
        img_np = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np)[None, :, :, :] # Shape: [1, H, W, 4]

        return (img_tensor,)

class AudioWaveformVisualizer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
        }

    RETURN_TYPES = ("AUDIO",) # Pass audio through
    FUNCTION = "process_audio"
    CATEGORY = "AudioTools"
    OUTPUT_NODE = True

    def process_audio(self, audio):
        # Handle ComfyUI audio format (dict or tuple)
        if isinstance(audio, dict):
            waveform = audio["waveform"]
        else:
            waveform, _ = audio

        # Ensure 2D: [channels, samples]
        if waveform.ndim == 3: # [batch, channels, samples]
            waveform = waveform[0]
        
        # Merge channels to mono for visualization
        if waveform.shape[0] > 1:
            waveform_mono = torch.mean(waveform, dim=0)
        else:
            waveform_mono = waveform[0]

        # Target ~4000 points for a detailed look that won't choke JS
        target_points = 4000
        num_samples = waveform_mono.shape[-1]
        step = max(1, num_samples // target_points)
        
        # PERFORMANCE: Slice the tensor BEFORE moving to CPU/Numpy
        samples_downsampled = waveform_mono[::step].cpu().numpy()
        
        # Clean data for JS (remove NaNs, clip range)
        samples_downsampled = np.clip(samples_downsampled, -1.0, 1.0)
        samples_downsampled = np.nan_to_num(samples_downsampled)
        peaks = samples_downsampled.tolist()

        # This is the 'message' the JS receives in onExecuted
        return {"ui": {"waveform_peaks": peaks}, "result": ({"waveform": waveform.unsqueeze(0) if waveform.ndim == 2 else waveform, "sample_rate": audio.get("sample_rate", 44100) if isinstance(audio, dict) else audio[1]},)}
        # audio is usually a dict: {"waveform": torch.Tensor, "sample_rate": int}
        # We don't need to transform it much here because the 
        # heavy lifting for visualization happens in the JS frontend.

class AudioWaveformFFMPEG:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "width": ("INT", {"default": 640, "min": 128, "max": 2048}),
                "height": ("INT", {"default": 240, "min": 64, "max": 1024}),
                "bg_color": ("STRING", {"default": "#c0c0c0"}),
                "peak_color": ("STRING", {"default": "#3232c8"}),
                "rms_color": ("STRING", {"default": "#6464dc"}),
                "split_channels": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "AudioTools"

    def generate(self, audio, width, height, bg_color, peak_color, rms_color, split_channels):
        # Handle ComfyUI audio format (dict or tuple)
        if isinstance(audio, dict):
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
        else:
            waveform, sample_rate = audio

        # Ensure 2D: [channels, samples]
        if waveform.ndim == 3: # [batch, channels, samples]
            waveform = waveform[0]
        
        # We use a temporary directory to handle the file I/O for FFmpeg
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "input.wav")
            output_path = os.path.join(tmpdir, "output.png")
            
            # Save audio to temp wav file
            # soundfile expects [samples, channels]
            sf.write(audio_path, waveform.cpu().numpy().T, sample_rate)
            
            size = f"{width}x{height}"
            split = 1 if split_channels else 0
            
            # Construct the filter complex based on the reference command
            filter_complex = (
                f"[0:a] showwavespic=s={size}:split_channels={split}:colors={peak_color}:filter=peak [pk]; "
                f"[0:a] showwavespic=s={size}:split_channels={split}:colors={rms_color} [rms]; "
                f"[pk][rms] overlay=format=auto [nobg]; "
                f"[1:v][nobg] overlay=format=auto"
            )
            
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-i", audio_path,
                "-f", "lavfi", "-i", f"color=c={bg_color}:s={size}",
                "-filter_complex", filter_complex,
                "-frames:v", "1",
                output_path
            ]
            
            subprocess.run(cmd, check=True)
            img = Image.open(output_path).convert("RGB")

        # Convert PIL to ComfyUI Tensor [B, H, W, C]
        img_np = np.array(img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_np)[None, :, :, :]

        return (img_tensor,)

NODE_CLASS_MAPPINGS = {
    "AudioWaveformVisualizer": AudioWaveformVisualizer,
    "AudioToWaveformImage": AudioToWaveformImage,
    "AudioWaveformFFMPEG": AudioWaveformFFMPEG
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AudioWaveformVisualizer": "Audio Waveform Visualizer",
    "AudioToWaveformImage": "Audio to Waveform Image",
    "AudioWaveformFFMPEG": "Audio Waveform (FFMPEG)"
}