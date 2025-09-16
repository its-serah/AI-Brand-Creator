## Logo Upscaling Experiments – Real-ESRGAN vs. Stable Diffusion x4 Upscaler
This repo documents experiments with two pretrained upscaling models — Real-ESRGAN and Stable Diffusion x4 Upscaler — to test how well they handle different types of images relevant to AI Brand Creator (logos, text, symbols, photos).
The goal: evaluate which model is more suitable for integrating into a pipeline where users can input logo prompts, and the system generates clean, scalable outputs.
Models Tested

## 1. Real-ESRGAN (x4)
###Setup: Installed and ran the Real-ESRGAN pretrained model.

### Process: Tested on four main image categories:
Badge (text + symbol)

Hexagon (geometric shape)

Eagle (natural photo)

Wordmark (text logo)

## Results Summary:
Strong on natural images (e.g., eagle feathers sharpened).

Decent on simple graphics but introduced blur on geometric edges.

Weak on text logos → tagline and smaller fonts became unreadable.

## 2. Stable Diffusion x4 Upscaler

## Setup: Used diffusers pipeline (stabilityai/stable-diffusion-x4-upscaler) with prompt guidance.

## Process: Tested on the same set of images + additional mixed logos and font examples:

Badge logos

Geometric shapes

Photos (eagle)

Wordmarks (Google, Vans, Revlon, etc.)

Font styles (Classic, Elegant, Modern, Bold, Informal, Dramatic)

Lion Capital logo & multi-font Brooklyn Urban Style wordmark

Complex emblem (Knights of Columbus)

## Results Summary:

Preserved large text slightly better than ESRGAN but still blurred small fonts.

Painterly effect on gradients (Lion Capital), looks stylish but loses vector crispness.

Script or decorative fonts survived better than thin serif/sans serif.

Complex logos with tiny embedded text still degraded.

## Comparison Table
| **Image Type**         | **Real-ESRGAN (x4)**                              | **Stable Diffusion x4 Upscaler**                              |
|--------------------------|--------------------------------------------------|----------------------------------------------------------------|
| **Badge (text + symbol)** | Outline smoothed, text blurred/unreadable         | Shape preserved, large text okay, small text still degraded      |
| **Geometric Shape**       | Straight edges blurred                            | Edges preserved slightly better but not perfectly crisp           |
| **Photo (Eagle)**          | Excellent – sharp details, feathers clear           | Excellent – also strong on photos                                 |
| **Wordmarks (logos)**      | Letters softened, tagline unreadable                 | Large bold text preserved better, small/thin fonts blurred         |
| **Font Styles**             | Blur across serif & script                              | Decorative/script preserved, serif blurred                            |
| **Complex Emblems**         | Text unreadable                                              | Symbol enhanced but fine emblem text lost                                |



## Key Findings
Real-ESRGAN
 - Best for natural images
 - Struggles with text & geometric precision

Stable Diffusion x4 Upscaler
 - Slightly better for logos with bold or decorative text
 - Adds painterly enhancement to gradients/shapes
 - Still weak with small fonts & vector-sharp logos



## Conclusion – Which Model Fits AI Brand Creator?
For the AI Brand Creator use case (logo generation based on user prompts):
Real-ESRGAN is not ideal for logos, it excels at photos but fails with text.

Stable Diffusion x4 Upscaler is closer to the goal, it reads larger words more correctly, handles decorative styles better, and could be fine-tuned on logo datasets to improve text rendering.


## Recommendation:
Use Stable Diffusion x4 Upscaler as the base model.

Add fine-tuning on a clean logo/text dataset to improve text clarity and vector sharpness.

Combine with font rendering libraries or SVG generation for the final polished logo outputs.

## Next step (future work): 

Fine-tune Stable Diffusion on wordmark + symbol datasets to solve text blurring.
