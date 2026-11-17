# Lab 04: Fine-Tune

## Laboratory Session

Lab 04, Fine-Tuning an LLM with LoRA and QLoRA. This session parameter-efficiently fine-tunes a small instruction-tuned model on a custom domain (a fictional computer shop) and compares the model before and after.

## Objective

The goal was to take a small instruction-tuned LLM and parameter-efficiently fine-tune it so it learns a specific domain, here the products, pricing, warranty, and policies of a fictional computer shop called CoreByte Computers, then prove it learned by comparing the model before and after on the same questions, including questions it never saw in training. The technique is LoRA (Low-Rank Adaptation) via PEFT, with QLoRA (4-bit quantization) when a CUDA GPU is available, trained with TRL's `SFTTrainer`.

## Tasks and Implementation

The full notebook is [`notebooks/lora_finetuning.ipynb`](notebooks/lora_finetuning.ipynb) and the dataset is [`dataset/qa_pairs.json`](dataset/qa_pairs.json).

1. **Hardware detection.** The notebook checks for a CUDA GPU and records what is available, then branches on it.
2. **Dataset.** I hand wrote 37 question and answer pairs about CoreByte Computers (hours, location, products, pricing, warranty, repairs, delivery, returns, student discount, payment, contact), kept specific and internally consistent so the fine-tune has a clear signal.
3. **Base model.** `HuggingFaceTB/SmolLM2-360M-Instruct`, small enough to QLoRA fine-tune on a free Colab T4 but a real instruct model.
4. **LoRA configuration** (recorded as the lab asks):

   | Hyper-parameter | Value |
   |---|---|
   | r (rank) | 16 |
   | lora_alpha | 32 |
   | lora_dropout | 0.05 |
   | bias | none |
   | target_modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
   | QLoRA quant | 4-bit NF4, double quant, compute dtype fp16 (CUDA only) |
5. **Training** with TRL `SFTTrainer` and `SFTConfig` (12 epochs, batch size 4, gradient accumulation 2, lr 2e-4, cosine schedule), formatting each pair with the model's chat template.
6. **Evaluation**, the same questions through the original and fine-tuned models, split into seen, paraphrase, and unseen, saved to an outputs folder.

## Results and Evidence

The hardware detection cell is the key real evidence from my machine:

```
Platform : macOS, arm64
CUDA GPU : False
Apple MPS: True
Will use QLoRA (4-bit): False
```

This is an Apple Silicon Mac with no CUDA GPU. QLoRA's 4-bit path (via `bitsandbytes`) is CUDA only, so it cannot run here, and on this Python 3.14 build even plain model loading via `transformers` deadlocks (confirmed across three separate attempts). Following the lab's instruction for the no-GPU case, I did not fabricate any training or results. Instead every cell that loads the model, trains, evaluates, or saves is guarded behind the CUDA check. On this machine those cells print a clear "skipped" message; on Google Colab with a T4 GPU they run the full QLoRA fine-tune. The cells that need no GPU (library versions, hardware detection, dataset loading, LoRA config) did execute, and their outputs are real.

Because the fine-tune was not executed here, there is no real loss curve or before and after table to show, and I did not invent one. To produce them, open the notebook in Google Colab (Runtime, then T4 GPU) and Run All; the guarded cells write the loss curve and the comparison table to the outputs folder.

## Observations

- **A GPU is both a speed requirement and, for 4-bit QLoRA, a hard dependency**, because the `bitsandbytes` kernels are CUDA only.
- **LoRA trains well under 1 percent of parameters** by freezing the base model and training small low rank adapters, so the saved adapter is a few MB instead of gigabytes.
- **The evaluation design is where the learning is shown.** Including paraphrases and unseen questions is deliberate: with only 37 examples the real risk is overfitting, and the unseen rows are what reveal whether the model learned the domain or memorised strings.
- The honest challenge was the environment: no CUDA plus a model loading deadlock on this Python build, which I confirmed properly rather than guessing.

## Learning Outcomes

- Understood what LoRA and QLoRA actually change and why they make fine-tuning feasible on modest hardware.
- Learned to build a small, consistent instruction dataset with a clear learnable signal.
- Learned to design a before and after evaluation that tests generalisation, not memorisation.
- Practised writing a notebook that degrades honestly on the hardware I have and runs correctly on the hardware it needs, without fabricating output.
