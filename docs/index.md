# ComfyUI Audio Waveform Visualizer

Audio waveform visualization nodes for ComfyUI.

---

## Preview

![Preview](./images/demo.png)

---

## Features

*   **Real-time Visualization**: View waveforms directly on the canvas.
*   **Image Generation**: Generate image tensors using Matplotlib or FFmpeg.
*   **Customization**: Control over colors, dimensions, and layout.
*   **Performance**: Optimized for long audio files via downsampling.

---

## Quick Start

### 1. Prerequisite: FFmpeg
Required for the `Audio Waveform (FFMPEG)` node.
*   **Linux**: `sudo apt install ffmpeg`
*   **macOS**: `brew install ffmpeg`
*   **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to PATH.

### 2. Installation
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/kaushiknishchay/ComfyUI-Audio-Waveform-Visualizer audio-visualizer
pip install -r requirements.txt
```

---

## Node Breakdown

### 1. Audio Waveform Visualizer
A high-performance JS-based visualizer for immediate feedback.
- **Output**: `AUDIO` (Pass-through)
- **UI**: Interactive canvas.

### 2. Audio to Waveform Image (Matplotlib)
Generates an image tensor using Matplotlib.
- **Output**: `IMAGE` (RGBA)
- **Customization**: Supports hex colors and custom dimensions.

### 3. Audio Waveform (FFMPEG)
Visualization using FFmpeg filters.
- **Output**: `IMAGE` (RGB)
- **Features**: Peak/RMS visualization, Stereo channel splitting.

---

## Example Workflow

Find the reference workflow in [workflows/AudioWaveform.json](https://github.com/kaushiknishchay/ComfyUI-Audio-Waveform-Visualizer/blob/main/workflows/AudioWaveform.json).

---

## Links
- [GitHub Repository](https://github.com/kaushiknishchay/ComfyUI-Audio-Waveform-Visualizer)
- [Author Website](https://nkaushik.in)
