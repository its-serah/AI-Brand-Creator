# Logo Generation & Color-Control Experiments (logo-generation-first-experiments)

This document summarizes experiments with two models focused on **brand/logo creation** and **palette control**:

1) **Logo Diffusion (LogoWizard)** – SD 2.1 fine-tuned on logos  
2) **T2I-Adapter (Color)** – palette conditioning module used with Stable Diffusion

---

## Models

### 1) Logo Diffusion (LogoWizard)
- **Type & Features:** Stable Diffusion 2.1 fine-tuned on logos; optimized for **flat, centered iconography** and clean vector-like shapes.
- **Text/Wordmarks:** Does **not** generate reliably readable text (typical SD limitation). Best for **symbol/icon** generation; wordmarks should be typeset afterward.
- **Prompts:** English prompts recommended (OpenCLIP backbone). Other languages may parse, but **text in the image** won’t be readable.
- **When to use:** Rapid ideation of **icon concepts** aligned with a style (minimal, geometric, monoline, etc.).

### 2) T2I-Adapter (Color)
- **Type & Features:** An auxiliary model that conditions SD generation on an **input color palette image** (or map), enforcing palette adherence.
- **Text/Wordmarks:** Not a text renderer; relies on SD for generation. Great for **brand color compliance**.
- **Prompts:** Used alongside English text prompts to describe subject + style; the **adapter** enforces colors.
- **When to use:** You need **strong color consistency** across outputs (brand palette locking).

---

## Test Setup

- **Inputs:** Style prompts (minimal/ultraflat, geometric), industry tags (e.g., *fashion*, *coffee roastery*), and fixed seeds for reproducibility.
- **Palette Control:** For T2I-Adapter runs, a color palette image was supplied to guide generation.
- **Outputs:**
  - `results_1/` 
  - `results_2/` 


---

## Results Summary

| **Aspect**              | **Logo Diffusion (LogoWizard)**                                             | **T2I-Adapter (Color)**                                                                 |
|------------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| **Icon Quality**       | Strong for flat, centered symbol ideas; good shape abstraction               | Similar base quality (depends on SD checkpoint); color adherence improves brand feel    |
| **Color Fidelity**     | Driven by prompt/seed only                                                   | **High** — adheres to provided palette; excellent for brand-consistent explorations     |
| **Text/Wordmarks**     | Letters not reliably readable; taglines fail                                | Same SD limitation — not suitable for rendering small readable text                     |
| **Style Control**      | Good with prompt engineering (ultraflat, monoline, geometric)                | Good + **palette lock**; ideal when palette is a hard constraint                        |
| **Use-Case Fit**       | Fast symbol ideation and style exploration                                   | **Brand consistency** (color-constrained icon variations)                               |
| **Multilingual**       | Prompts in EN recommended; **image text still unreadable**                   | N/A (adapter); relies on SD text prompts; same text rendering limitations               |

---

## Takeaways

- **Ideation:** Use **Logo Diffusion** to quickly explore icon directions per industry/style (e.g., *fashion*, *coffee roastery*).
- **Brand Consistency:** Use **T2I-Adapter** when you must **enforce brand colors** across many variations.
- **Wordmarks:** Treat them as **typography** work; add text in vector tools (Figma/Illustrator) rather than relying on diffusion output.

---

## File Map

- `results_1/` — outputs from the experiments.
- `results_2/` — expected outputs for the second set


