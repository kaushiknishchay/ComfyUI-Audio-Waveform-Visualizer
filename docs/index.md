# ComfyUI Audio Waveform Visualizer

A suite of custom nodes for ComfyUI designed to generate high-quality audio waveform visualizations. Whether you need a real-time preview on your node or a high-fidelity image for video synthesis, this package provides multiple ways to see your sound.

---

## 📸 Preview

![Preview](./images/demo.png)

---

## 🚀 Features

*   **Real-time Visualization**: See waveforms directly on the ComfyUI canvas.
*   **High-Quality Rendering**: Generate image tensors using Matplotlib or FFmpeg.
*   **Highly Customizable**: Control colors, dimensions, and channel splitting.
*   **Optimized Performance**: Features like data decimation and offscreen buffering ensure a smooth experience.

---

## 🛠 Installation

### 1. Prerequisite: FFmpeg
Required for the `Audio Waveform (FFMPEG)` node. 
*   **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract, and add the `bin` folder to your System PATH.
*   **Linux**: `sudo apt install ffmpeg`
*   **macOS**: `brew install ffmpeg`

### 2. Node Installation
1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```
2. Clone or copy this repository into a folder named `audio-visualizer`.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you are using the Python environment associated with your ComfyUI installation)*
4. Restart ComfyUI.

---

## 🧩 Visualization Methods

This suite provides three specialized nodes to fit different workflows.

### 1. Audio Waveform Visualizer (Frontend Canvas)
Renders a waveform directly on the node's UI using a JavaScript canvas.

*   **Pros**: Extremely fast; zero impact on generation time; responsive to resizing.
*   **Cons**: No image output for other nodes; visualization clears on UI refresh without re-execution.
*   **Key Logic**: Uses an offscreen buffer to maintain performance during UI interaction.

### 2. Audio to Waveform Image (Matplotlib)
Generates a customizable waveform image using the Matplotlib engine.

*   **Pros**: Supports transparency (RGBA); high-quality vector-like rendering; produces a standard `IMAGE` tensor.
*   **Cons**: Slower than the JS visualizer (though optimized via data decimation).
*   **Parameters**:
    *   `width/height`: Output resolution.
    *   `color`: Hex code or named color (e.g., `#3232c8`, `green`).

### 3. Audio Waveform (FFMPEG) (Recommended)
Uses the professional `showwavespic` filter from FFmpeg to create an "Audacity-style" visualization.

*   **Pros**: Shows both **Peak** and **RMS** levels; excellent stereo handling; very robust.
*   **Cons**: Requires FFmpeg installed on the OS.
*   **Parameters**:
    *   `bg_color`: Background color.
    *   `peak_color`: Outer peak waveform color.
    *   `rms_color`: Inner RMS (average volume) waveform color.
    *   `split_channels`: Choose between stereo (stacked) or mono (merged) view.

---

## 🏗 Workflow Examples

You can find an example workflow in the [workflows/](https://github.com/your-username/your-repo/tree/main/workflows) directory of this repository:
*   **AudioWaveform.json**: A comprehensive workflow demonstrating all three visualization methods in action.

To use it:
1.  Download the JSON file.
2.  Drag and drop it into your ComfyUI interface.

---

## 📝 Usage Notes

*   **Input/Output**: All nodes take a standard ComfyUI `AUDIO` input. The image nodes output a standard `IMAGE` tensor compatible with any ComfyUI image node (like `Preview Image` or `Save Image`).
*   **Large Audio Files**: The nodes include automatic decimation (downsampling) to handle long audio files without crashing or slowing down the UI/rendering process.
*   **Accuracy**: For the most precise representation of audio levels, the **FFMPEG node** is highly recommended as it uses professional-grade filters.

---

## ⚖️ License

This project is licensed under the [MIT License](https://github.com/your-username/your-repo/blob/main/LICENSE.md).

---

## 🔗 Connect

*   **Website**: [nkaushik.in](https://nkaushik.in)
*   **Blog**: [blog.nkaushik.in](https://blog.nkaushik.in)


