import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Custom.AudioWaveform",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "AudioWaveformVisualizer") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                this.size = [400, 360]; // Initial size: 400 width, 360 height
                this.min_size = [200, 360]; // Prevent resizing smaller than the waveform area
            };
            
            nodeType.prototype.onExecuted = function (message) {
                if (message.waveform_peaks) {
                    this.waveformValues = message.waveform_peaks;
                    this.needsRedraw = true; // Flag to trigger high-quality render
                }
            };

            nodeType.prototype.onDrawForeground = function (ctx) {
                if (this.flags.collapsed || !this.waveformValues) return;

                const margin = 5;
                const y = 50; // Start below the title/widgets
                const w = Math.max(64, this.size[0] - (margin * 2));
                const h = Math.max(300, this.size[1] - y - margin); // Minimum height of 300

                // Create or update the offscreen buffer
                if (this.needsRedraw || !this.bufferCanvas || this.bufferCanvas.width !== w || this.bufferCanvas.height !== h) {
                    if (!this.bufferCanvas) this.bufferCanvas = document.createElement('canvas');
                    
                    this.bufferCanvas.width = w;
                    this.bufferCanvas.height = h;
                    const bCtx = this.bufferCanvas.getContext('2d');

                    // Background
                    bCtx.fillStyle = "rgb(37, 36, 36)";
                    bCtx.fillRect(0, 0, w, h);

                    // Draw center line
                    bCtx.strokeStyle = "#333";
                    bCtx.beginPath();
                    bCtx.moveTo(0, h / 2);
                    bCtx.lineTo(w, h / 2);
                    bCtx.stroke();

                    // Draw Waveform onto the BUFFER
                    bCtx.strokeStyle = "#3232c8";
                    bCtx.lineWidth = 1;
                    bCtx.beginPath();

                    // Find the maximum absolute value to normalize the waveform (tight spacing)
                    const maxPeak = Math.max(...this.waveformValues.map(v => Math.abs(v))) || 0.01;
                    const verticalScale = (h / 2) / maxPeak;

                    const step = w / this.waveformValues.length;
                    for (let i = 0; i < this.waveformValues.length; i++) {
                        const vx = i * step;
                        const vy = (h / 2) + (this.waveformValues[i] * verticalScale);
                        if (i === 0) bCtx.moveTo(vx, vy);
                        else bCtx.lineTo(vx, vy);
                    }
                    bCtx.stroke();
                    this.needsRedraw = false;
                }

                // High-performance: Just paint the pre-rendered image
                if (this.bufferCanvas) ctx.drawImage(this.bufferCanvas, margin, y);
            };
        }
    },
});