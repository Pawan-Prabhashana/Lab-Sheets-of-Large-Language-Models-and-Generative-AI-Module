# PUSL 3205 — Large Language Models & Generative AI · Lab Portfolio

This repository collects my three lab assignments for the **Large Language Models and Generative AI**
module (BSc Data Science). The module moves from classical NLP up to building a Transformer from
scratch, and these labs trace that arc: a traditional machine-learning sentiment classifier, an
LLM-assisted product-design exercise, and a tiny GPT-style language model trained end to end.

Everything here is **executed and real** — the notebooks were run top to bottom, every plot is
generated from the actual runs, and all reported metrics are captured from those runs (no invented
numbers).

## The labs

| # | Lab | What it is | Key deliverables |
|---|-----|------------|------------------|
| 1 | [Sentiment Analysis](Lab-01-Sentiment-Analysis/) | Traditional ML sentiment classifier on the UCI Amazon/IMDb/Yelp reviews — preprocessing, Bag-of-Words, Logistic Regression vs Linear SVM. | [notebook](Lab-01-Sentiment-Analysis/sentiment_analysis.ipynb) · [review](Lab-01-Sentiment-Analysis/REVIEW.md) · [plots](Lab-01-Sentiment-Analysis/outputs/) |
| 2 | [AI in Everyday Challenges](Lab-02-AI-Everyday-Challenges/) | Product-design task using an LLM as a development partner — *Cadence*, a time companion for the "Busy Student" scenario. | [concept](Lab-02-AI-Everyday-Challenges/product-concept.md) · [HTML mock-up](Lab-02-AI-Everyday-Challenges/mockup/cadence-mockup.html) · [review](Lab-02-AI-Everyday-Challenges/REVIEW.md) |
| 3 | [Tiny Transformer](Lab-03-Tiny-Transformer/) | A decoder-only Transformer built from scratch in PyTorch, trained for next-character prediction on a subset of TinyStories. | [notebook](Lab-03-Tiny-Transformer/tiny_transformer.ipynb) · [review](Lab-03-Tiny-Transformer/REVIEW.md) · [plots](Lab-03-Tiny-Transformer/outputs/) |
| 4 | [LoRA / QLoRA Fine-Tuning](Lab-04-LoRA-FineTuning/) | Parameter-efficient fine-tuning of SmolLM2-360M-Instruct on a custom computer-shop Q&A dataset, with before/after evaluation. **Needs a CUDA GPU** — see note below. | [notebook](Lab-04-LoRA-FineTuning/lora_finetuning.ipynb) · [dataset](Lab-04-LoRA-FineTuning/dataset/qa_pairs.json) · [review](Lab-04-LoRA-FineTuning/REVIEW.md) |

## Tech stack

- **Language:** Python 3
- **Classical ML / NLP:** scikit-learn, NLTK, pandas, NumPy
- **Deep learning:** PyTorch (Transformer implemented from scratch), Hugging Face `datasets`
- **LLM fine-tuning:** Hugging Face `transformers`, PEFT (LoRA/QLoRA), TRL, `accelerate`, `bitsandbytes`
- **Visualisation:** Matplotlib, Seaborn
- **Notebooks:** Jupyter / nbconvert
- **Lab 2 prototype:** self-contained HTML + CSS (no dependencies)

## Overall takeaways

Working from a Bag-of-Words classifier up to a from-scratch Transformer in the same module made the
*reason* for each leap tangible: Lab 1's models are fast and strong but blind to word order, which is
exactly the limitation self-attention removes in Lab 3. Building attention, masking, and positional
embeddings by hand — rather than importing a model — was the part that made LLMs stop feeling like a
black box. And Lab 2 was a useful counterweight: the hardest part of applying an LLM well isn't the
model, it's deciding *where* it belongs in a product and where deterministic logic should stay in
charge.

## How to run

```bash
# from the repo root
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

jupyter notebook                  # then open either .ipynb and Run All
```

Both notebooks are committed **with their outputs already visible**, so you can read them without
running anything. Lab 1 downloads its dataset programmatically; Lab 3 streams a small subset of
TinyStories from Hugging Face — both need an internet connection the first time they run.

**Lab 4 needs a GPU.** The LoRA/QLoRA fine-tune requires a CUDA GPU (QLoRA's 4-bit path is
CUDA-only). It was authored on a Mac with no CUDA GPU, so — per the lab brief — the training/eval
cells are guarded behind a hardware check and were **not executed locally** (no results were
fabricated). To run it for real, open
[`Lab-04-LoRA-FineTuning/lora_finetuning.ipynb`](Lab-04-LoRA-FineTuning/lora_finetuning.ipynb) in
**Google Colab → Runtime → T4 GPU** and Run All. Full detail in that lab's
[REVIEW.md](Lab-04-LoRA-FineTuning/REVIEW.md).

**Notes**
- The `venv/`, downloaded datasets (`data/`), the Hugging Face cache, and Lab 4's training
  checkpoints are git-ignored (see [`.gitignore`](.gitignore)) because they're large and regenerated
  on demand.
- Lab 3's trained checkpoint (`Lab-03-Tiny-Transformer/tiny_transformer.pt`) is small (a few MB) and
  **is** committed, so the model can be reloaded without retraining.
- Lab 4's LoRA adapter is small (a few MB) and is committed **once generated on a GPU**; the base
  model is downloaded from Hugging Face on demand and is not committed.
