# hybrid_pipeline.py — Group 1: BM25 + vector + RRF fusion + cross-encoder rerank
import time
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

DATA_DIR = Path("data")

# ---------- Load + chunk once (both retrievers share the SAME chunks) ----------
def load_chunks():
    docs = []
    for pdf in DATA_DIR.glob("*.pdf"):
        docs.extend(PyMuPDFLoader(str(pdf)).load())
    return RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120).split_documents(docs)

chunks = load_chunks()
corpus = [c.page_content for c in chunks]
print(f"Loaded {len(chunks)} chunks.")

# ---------- Vector retriever (semantic) ----------
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
vectorstore = Chroma.from_documents(chunks, embeddings, collection_name="hybrid_vec")

# ---------- BM25 retriever (keyword) ----------
bm25 = BM25Okapi([c.lower().split() for c in corpus])

# ---------- Cross-encoder reranker (downloads ~80MB on first run) ----------
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# ---------- LLM + prompt ----------
llm = ChatOllama(model="llama3.2:3b", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "You are a university assistant. Answer using ONLY the context below. If the "
    "answer isn't there, say you don't have that information.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)

# ---------- Retrieval building blocks ----------
def vector_search(query, k):
    return vectorstore.similarity_search(query, k=k)

def bm25_search(query, k):
    scores = bm25.get_scores(query.lower().split())
    idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [chunks[i] for i in idx]

def rrf_fuse(lists, k=60):
    """Reciprocal Rank Fusion: score = sum(1 / (k + rank)) across lists."""
    scores, by_key = {}, {}
    for results in lists:
        for rank, doc in enumerate(results):
            key = doc.page_content
            by_key[key] = doc
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
    return [by_key[key] for key in sorted(scores, key=scores.get, reverse=True)]

def rerank(query, docs, k):
    pairs = [(query, d.page_content) for d in docs]
    scored = sorted(zip(docs, reranker.predict(pairs)),
                    key=lambda x: x[1], reverse=True)
    return [d for d, _ in scored[:k]]

# ---------- Two retrievers to compare ----------
def baseline_retrieve(query, k=4):
    """Basic RAG: vector-only, no fusion, no rerank."""
    return vector_search(query, k)

def hybrid_retrieve(query, n_each=8, final_k=4):
    """Enhanced: BM25 + vector -> RRF -> rerank."""
    fused = rrf_fuse([vector_search(query, n_each), bm25_search(query, n_each)])
    return rerank(query, fused, final_k)

def answer(query, retrieved):
    context = "\n\n".join(d.page_content for d in retrieved)
    return llm.invoke(prompt.format_messages(context=context, question=query)).content

if __name__ == "__main__":
    print("Hybrid RAG (BM25 + vector + RRF + rerank). Type 'exit' to quit.\n")
    while True:
        q = input("Ask a university question (or exit): ")
        if q.strip().lower() in {"exit", "quit"}:
            break
        t0 = time.time()
        docs = hybrid_retrieve(q)
        ans = answer(q, docs)
        print(f"\nAnswer: {ans}\n(done in {time.time()-t0:.1f}s)\n")
