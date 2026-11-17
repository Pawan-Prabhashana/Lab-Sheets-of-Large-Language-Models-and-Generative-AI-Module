# From Naive RAG to Intelligent University Knowledge Retrieval
## Group 1, Hybrid Retrieval and Reranking

Report notes for the Lab 05 group activity. These expand into the full technical report.

---

## 1. Background and problem

The baseline is a naive Retrieval-Augmented Generation (RAG) system built with Python, LangChain, ChromaDB, Ollama, and Streamlit. It answers questions over university PDF documents using:

- Fixed-size text chunking (recursive character splitter, 800 chars, 120 overlap)
- Dense vector retrieval (Ollama `qwen3-embedding:0.6b` embeddings in ChromaDB)
- Top-k similarity search (cosine similarity, k = 4)

**Limitation addressed:** pure dense retrieval can rank the most relevant chunk below less relevant ones, and it under-weights exact academic terms such as module codes (CS102, DS202), names, and rare keywords, because those are diluted in the embedding space. This hurts ranking quality (MRR) and, on larger corpora, recall.

## 2. Proposed architecture, hybrid retrieval and reranking

See [`screenshots/hybrid_rag_architecture.png`](screenshots/hybrid_rag_architecture.png). The pipeline:

1. **BM25 (sparse, keyword retrieval)** using `rank_bm25` over tokenised chunks. Catches exact terms and codes that dense retrieval fuzzes over.
2. **Dense vector retrieval**, the existing Chroma and Ollama-embeddings search. Catches meaning and paraphrase.
3. **Reciprocal Rank Fusion (RRF)** merges the two ranked lists with `score = sum(1 / (k + rank))`, k = 60. No score normalisation is needed; it combines rankings, not raw scores.
4. **Cross-encoder reranking** using `cross-encoder/ms-marco-MiniLM-L-6-v2`, which re-scores each fused candidate jointly with the query and returns the final top-k. This is far more precise than bi-encoder similarity, applied only to the shortlist to limit cost.
5. **Generation**, the reranked top-k chunks are passed as context to `llama3.2:3b` with a strict answer-only-from-context prompt.

## 3. Methodology and evaluation setup

- **Corpus:** university handbook (prose, four programmes plus policies), about 9.2k chars, 15 chunks.
- **Evaluation dataset:** 12 questions, each labelled with (a) a marker string that identifies the relevant chunk and (b) keywords a correct answer must contain.
- **Systems compared:** baseline (vector only, top-5) and hybrid (BM25 plus vector, RRF, cross-encoder rerank, top-5).
- **Metrics:** Recall@5, MRR, answer correctness, and average retrieval latency.

## 4. Experimental results

These are the real numbers from running [`src/eval.py`](src/eval.py) (see `screenshots/lab05-eval-hybrid-vs-baseline.png`).

| Metric | Baseline (vector) | Hybrid (BM25 + vector + rerank) |
|--------|:-----------------:|:-------------------------------:|
| Recall@5 | 1.000 | 1.000 |
| MRR | 0.944 | 1.000 |
| Answer correctness | 1.000 | 0.917 |
| Avg retrieval latency (s) | 0.017 | 0.150 |

## 5. Analysis and findings

- **Ranking quality improved (MRR 0.944 to 1.000).** The cross-encoder consistently promotes the single most relevant chunk to rank 1; the baseline occasionally ranked it second. This is the primary benefit of the enhancement.
- **Recall@5 saturated (1.0 for both).** On a small, clean 15-chunk corpus the top-5 already contains the relevant chunk for both systems, so Recall@5 cannot discriminate. It would separate at Recall@1 (where the MRR gap implies hybrid wins) or on a larger, noisier multi-document corpus.
- **Answer correctness essentially tied (1.0 vs 0.917, one question of twelve).** Within measurement noise, not a real regression. Correctness is bounded by the generator, not retrieval, once the right chunk is in context.
- **Latency cost about 9 times (0.017 to 0.150 s).** BM25 scoring plus cross-encoder inference add real cost. This is the central retrieval-quality versus computational-cost trade off.

## 6. Limitations and future work

- Small single-document corpus, so metrics saturate. Evaluate on a larger, multi-source academic corpus with distractor documents.
- Table-heavy pages: PyMuPDF flattens tables, so prerequisite and credit facts in tables can be misread by the generator. Prose extraction mitigated it here.
- Expand the eval set (more questions, multiple relevant chunks per question) and add Recall@1 and Recall@3 for sharper discrimination.
- Tune RRF k, the BM25 and vector candidate counts, and the reranker model; benchmark latency on CPU vs GPU.

## 7. Files

`src/ingest.py`, `src/rag_pipeline.py` (baseline), `src/hybrid_pipeline.py` (enhanced retriever), `src/eval.py` (evaluation), `src/app.py` (Streamlit UI), `data/` (PDF corpus), `requirements.txt`.
