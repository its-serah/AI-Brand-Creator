# Stable Diffusion x4 Crisp Upscaler

This part of the project provides a **text-safe, high-resolution upscaler** built on [Stable Diffusion x4 Upscaler](https://huggingface.co/stabilityai/stable-diffusion-x4-upscaler).  
It is tuned to minimize blurring and artifacts when enlarging images that contain **logos, fonts, and thin text**.

---

## Features
- Uses **Stable Diffusion x4 Upscaler** for high-quality super-resolution.  
- Custom prompt / negative prompt setup to avoid hallucinations.  
- **Noise level = 0** -> prevents re-blurring of text.  
- Edge-aware **bilateral + Laplacian sharpening** for crisp, clean text.  
- Three presets for different font weights:
  - `thin` -> for hairline serifs or small UI text  
  - `neutral` ->  for most normal logos & text  
  - `bold` -> for heavy decorative lettering  

---

## Notebook Structure
The notebook is split into two main cells:

1. **Setup Cell (run once per session)**  
   - Installs OpenCV for sharpening.  
   - Loads the `stabilityai/stable-diffusion-x4-upscaler` pipeline.  
   - Defines the `crisp_text_sharpen()` function.

2. **Process Cell (run per image)**  
   - Uploads an image (supports PNG/JPG/JPEG/WEBP/TIFF/BMP).  
   - Runs Stable Diffusion x4 Upscaler with tuned parameters.  
   - Applies sharpening with your chosen preset.  
   - Saves the enhanced output as PNG (`filename_sdx4_<preset>.png`).  

---

## Usage (Google Colab)

1. Clone or copy the notebook into Google Colab.  
2. Run the **Setup Cell** (only once per session).  
3. For each new image:
   - Run the **Process Cell**, upload your file.  
   - Pick a preset (`thin`, `neutral`, `bold`).  
   - Get the enhanced PNG for download.

---

## Key Parameters
- `guidance_scale=0.5` -> keeps edges sharp without hallucinations.  
- `num_inference_steps=36` -> balances quality and runtime.  
- `noise_level=0` -> crucial for preserving text clarity.  
- Sharpen strength (`k`) varies with preset:
  - `thin = 0.20`  
  - `neutral = 0.22`  
  - `bold = 0.28`  

---

