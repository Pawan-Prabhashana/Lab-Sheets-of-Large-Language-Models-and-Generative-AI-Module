# ingest.py — Lab 5: load PDFs, chunk, embed into ChromaDB
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DATA_DIR = Path("data")
CHROMA_DIR = "chroma_db"

def main():
    pdfs = list(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in ./data — add a PDF and retry.")
        return

    docs = []
    for pdf in pdfs:
        print(f"Loading {pdf.name} ...")
        docs.extend(PyMuPDFLoader(str(pdf)).load())
    print(f"Loaded {len(docs)} pages.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Embedding (qwen3-embedding:0.6b) ...")

    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    print(f"Done. Vector store saved to ./{CHROMA_DIR}")

if __name__ == "__main__":
    main()
