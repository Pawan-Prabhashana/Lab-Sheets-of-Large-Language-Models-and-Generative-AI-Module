# Lab 4 Review — Fine-Tuning an LLM with LoRA / QLoRA

## What the lab was about

The goal was to take a small instruction-tuned LLM and **parameter-efficiently fine-tune** it so it
learns a specific domain — here, a fictional computer shop, *CoreByte Computers* — then prove it
learned by comparing the model before and after on the same questions, including questions it never
saw in training. The technique is **LoRA** (Low-Rank Adaptation), with **QLoRA** (4-bit quantization)
when a CUDA GPU is available, trained via TRL's `SFTTrainer`.

## Hardware findings (required by the lab)

**(a) What GPU is available here?** None. The hardware-detection cell in the notebook reports, from
this machine:

```
Platform : macOS-26.4.1-arm64 | arm64
CUDA GPU : False
Apple MPS: True
Will use QLoRA (4-bit): False
```

This is an Apple Silicon Mac. There is **no CUDA GPU**, and QLoRA's 4-bit path (via `bitsandbytes`)
is **CUDA-only**, so it cannot run here. I also found that on this environment's bleeding-edge stack
(Python 3.14 / PyTorch 2.14 / Transformers 5.x) even plain model loading via `transformers`
deadlocks on CPU — I confirmed this with three separate attempts (default threading, forced CPU, and
single-threaded), each of which loaded the weights into memory and then hung at `from_pretrained`
with the CPU near-idle. So I could not fall back to a slow CPU run either.

**Following the lab's explicit instruction for the no-GPU case, I did not fabricate any training or
results.** Instead the notebook is written so it is correct and ready to run on a GPU: every cell
that loads the model, trains, evaluates, or saves the adapter is guarded behind the CUDA check. On
this machine those cells print a clear `SKIPPED` message; on **Google Colab (Runtime → T4 GPU)** they
execute the full QLoRA fine-tune. The cells that need no GPU — library versions, hardware detection,
dataset loading, chat-formatting setup, and the LoRA/QLoRA config — **did** execute locally, and
their outputs are real.

**(b) Why a GPU helps LLM fine-tuning.** Fine-tuning runs thousands of forward *and* backward passes
over a model with hundreds of millions of parameters. The core operation is large matrix
multiplication, which a GPU executes with thousands of cores in parallel, whereas a CPU does it on a
handful — often a 10–100× difference. On top of that, QLoRA's 4-bit quantization and its optimised
kernels live in `bitsandbytes`, which is compiled for CUDA and has no CPU/MPS equivalent. So a GPU is
both a speed requirement (hours → minutes) and, for the 4-bit path, a hard dependency.

## What I built and how

- **Dataset** — [`dataset/qa_pairs.json`](dataset/qa_pairs.json): 37 hand-written Q&A pairs about
  CoreByte Computers (hours, location, products, pricing, warranty, repairs, delivery, returns,
  student discount, payment, contact). I kept the facts specific and internally consistent so the
  fine-tune has a clear signal to latch onto.
- **Base model** — `HuggingFaceTB/SmolLM2-360M-Instruct`: a genuine 360M instruct model, small enough
  to QLoRA-tune on a free Colab T4 but real enough that fine-tuning visibly changes its behaviour.
- **LoRA configuration** (recorded as the lab asks):

  | Hyper-parameter | Value |
  |---|---|
  | `r` (rank) | 16 |
  | `lora_alpha` | 32 (α/r = 2) |
  | `lora_dropout` | 0.05 |
  | `bias` | none |
  | `target_modules` | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` |
  | QLoRA quant | 4-bit NF4 + double-quant, compute dtype fp16 (applied only on CUDA) |

- **Training** — TRL `SFTTrainer` with `SFTConfig` (12 epochs, batch size 4 × grad-accum 2, lr 2e-4,
  cosine schedule, warmup 0.1), formatting each Q&A pair with the model's own chat template.
- **Evaluation design** — the same questions through the original and fine-tuned models, split into
  **seen** (in training), **paraphrase** (same fact, reworded), and **unseen** (new phrasing/asks),
  saved to `outputs/before_after.{json,md}`.

## Key concepts I learned

- **LoRA is about *what* you train, not *how much*.** Freezing the base model and training only small
  low-rank matrices in the projection layers means under 1% of parameters are updated, so gradients
  and optimiser state are tiny and the saved adapter is a few MB — the whole reason this is feasible
  on modest hardware.
- **QLoRA stacks quantization on top.** Loading the frozen base in 4-bit roughly quarters its memory,
  which is what makes a model *fit* on a small GPU while the adapters stay in higher precision.
- **The eval design is where the learning is demonstrated.** Including paraphrases and unseen
  questions is deliberate: with only 37 examples and 12 epochs the real risk is **over-fitting**
  (parroting training answers). Whether the model answers the *unseen* rows with CoreByte's facts —
  rather than generic LLM hedging — is the actual test of domain learning.
- **"Ready to run" is a real deliverable.** Guarding GPU work behind a hardware check, with a clean
  skip path, is how you write a notebook that is both honest on the machine you have and correct on
  the machine you need.

## Results

The fine-tune itself **was not executed in this environment** (no CUDA GPU; CPU loading deadlocks),
so there is no real loss curve or before/after table to embed here — and I did not invent one. The
before/after comparison is fully wired up in the notebook and writes to `outputs/` when run on a GPU.

**What I expect to see on Colab**, based on how this setup behaves: the original SmolLM2-360M answers
shop questions with generic, non-committal text (it has no idea what CoreByte's hours or phone number
are), while the fine-tuned model returns CoreByte's specific facts — most tellingly on the *unseen*
and *paraphrased* rows if it generalised rather than memorised. The expected failure mode to watch
for is over-fitting: verbatim-correct on seen questions but brittle or repetitive on reworded ones,
which would call for fewer epochs or a lower LoRA rank.

## Challenges and what I'd improve

- **The environment was the real challenge.** No CUDA GPU plus a `transformers` model-loading
  deadlock on Python 3.14 meant local execution of the fine-tune was impossible. I spent the effort
  confirming that properly (three isolation runs) rather than guessing, then made the notebook
  degrade honestly instead of faking output.
- **What I'd do next.** Run it on Colab T4 to capture the real loss curve and before/after table and
  drop them into `outputs/` and this review; try `Qwen2.5-0.5B-Instruct` as a second base model for
  comparison; and sweep LoRA `r` (8 vs 16 vs 32) and epochs to find where domain learning peaks
  before over-fitting sets in.
- **A reproducibility fix worth noting:** pinning to a Python 3.11/3.12 environment (which Colab uses)
  avoids the 3.14 loading deadlock entirely — a reminder that "latest" isn't always "works".
