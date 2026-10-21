# Lab 4 outputs

This folder is populated **when the notebook is run on a CUDA GPU** (e.g. Google Colab T4). The
GPU-guarded cells in `lora_finetuning.ipynb` generate:

- `training_loss.png` — the LoRA fine-tuning loss curve.
- `before_after.json` / `before_after.md` — the side-by-side original-vs-fine-tuned comparison table.

They are intentionally **absent here** because this lab was authored on a machine with no CUDA GPU,
and — per the lab sheet — no training outputs were fabricated. See `../REVIEW.md` for the full
explanation.
