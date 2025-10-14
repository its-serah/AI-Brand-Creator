import torch
from diffusers import StableDiffusionUpscalePipeline

model_id = "stabilityai/stable-diffusion-x4-upscaler"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32
device = "cuda" if torch.cuda.is_available() else "cpu"

print("cuda", torch.cuda.is_available())
pipe = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=dtype)
pipe.to(device)
print("loaded")
