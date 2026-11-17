# PUSL 3205, Large Language Models and Generative AI, Practical Portfolio

This repository is my individual practical portfolio for PUSL 3205. It documents the laboratory sessions for the module, which run from classical NLP up to building and orchestrating LLM systems: traditional machine learning, prompt and product design, a transformer built from scratch, parameter-efficient fine-tuning, Retrieval-Augmented Generation, and tool-using AI agents.

Each lab is documented in its own folder with a README in the required format (Laboratory Session, Objective, Tasks and Implementation, Results and Evidence, Observations, Learning Outcomes), the code or notebooks, and screenshots or results as evidence. All metrics and screenshots are from my own real runs.

## Labs

| # | Lab | What it covers | Link |
|---|-----|----------------|------|
| 01 | Machine Learning | Traditional ML sentiment classifier (Bag of Words, Logistic Regression vs Linear SVM) | [Lab-01-Machine-Learning](Lab-01-Machine-Learning/) |
| 02 | LLM in Everyday Life | Using an LLM as a product-development partner, the Busy Student scenario (Cadence) | [Lab-02-LLM-Everyday-Life](Lab-02-LLM-Everyday-Life/) |
| 03 | Tiny Transformer | A decoder-only Transformer built from scratch in PyTorch, trained on TinyStories | [Lab-03-Tiny-Transformer](Lab-03-Tiny-Transformer/) |
| 04 | Fine-Tune | Parameter-efficient fine-tuning with LoRA and QLoRA (SmolLM2 on a computer-shop dataset) | [Lab-04-Fine-Tune](Lab-04-Fine-Tune/) |
| 05 | RAG Pipeline | Document-grounded QA with LangChain, ChromaDB, Ollama, and Streamlit, plus hybrid retrieval | [Lab-05-RAG-Pipeline](Lab-05-RAG-Pipeline/) |
| 06 | AI Agents | A tool-using agent (calculator, memory, RAG, Google Calendar) and an n8n workflow version | [Lab-06-AI-Agents](Lab-06-AI-Agents/) |
| , | Final Reflection | My reflection across the whole module | [Final-Reflection.md](Final-Reflection.md) |

## Tech stack

- **Languages and core:** Python, Jupyter
- **Classical ML and NLP:** scikit-learn, NLTK, pandas, NumPy
- **Deep learning:** PyTorch (transformer from scratch), Hugging Face `transformers`, `datasets`
- **Fine-tuning:** PEFT (LoRA and QLoRA), TRL, `accelerate`, `bitsandbytes`
- **RAG and agents:** LangChain, ChromaDB, Ollama (Llama 3.2 3B, Qwen3 Embedding 0.6B), Streamlit
- **Workflow automation:** n8n (Docker), Google Calendar, Sheets, and Docs APIs
- **Visualisation:** Matplotlib, Seaborn

## How to run, and what needs a GPU or Ollama

- **Labs 01 and 03** run on CPU. See each lab's README; Python dependencies are in the repo and in each lab.
- **Lab 04** (QLoRA fine-tune) needs a CUDA GPU (for example a free Google Colab T4). The notebook is guarded so it skips the GPU-only cells on a machine without CUDA, and it does not fabricate results.
- **Labs 05 and 06** need **Ollama** running locally with `llama3.2:3b` and `qwen3-embedding:0.6b` pulled, and Lab 06 Part E also uses **Docker** (for n8n). These were run on my machine; the evidence is in each lab's screenshots. Running them again means installing Ollama and the models, which is noted in each README. Secrets such as Google OAuth credentials are not committed; see the Lab 06 README for how to supply your own.

## Overall takeaways

The arc of the module made the reasons for each technique tangible. Lab 01's Bag of Words model is fast but blind to word order, which is exactly the limitation self-attention removes in Lab 03, and building attention and masking by hand is what made LLMs stop feeling like a black box. Labs 04, 05, and 06 then showed the three main ways to make a base model useful for a real task: change its weights (fine-tuning), give it the right documents at answer time (RAG), or let it act through tools (agents). My fuller reflection is in [Final-Reflection.md](Final-Reflection.md).
