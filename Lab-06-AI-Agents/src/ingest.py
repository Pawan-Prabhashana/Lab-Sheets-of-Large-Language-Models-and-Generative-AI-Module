# ingest.py — table-aware ingestion for the university RAG (Lab 5 RAG, improved)
import fitz  # PyMuPDF
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

DATA_DIR = Path("data")
CHROMA_DIR = "chroma_db"

def table_to_text(table):
    """Turn a detected table into one readable line per row, preserving which
    value belongs to which column (so the model can map Module -> Prerequisite)."""
    rows = table.extract()
    if not rows:
        return ""
    header = [(h or "").strip() for h in rows[0]]
    lines = []
    for r in rows[1:]:
        cells = [(c or "").strip() for c in r]
        pairs = ", ".join(f"{h}: {c}" for h, c in zip(header, cells) if c)
        if pairs:
            lines.append(pairs)
    return "\n".join(lines)

def load_pdf(pdf_path):
    """Extract each page as plain text PLUS any structured tables."""
    doc = fitz.open(pdf_path)
    documents = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_text = page.get_text("text").strip()

        table_texts = []
        try:
            for t in page.find_tables().tables:
                tt = table_to_text(t)
                if tt:
                    table_texts.append(tt)
        except Exception:
            pass  # older PyMuPDF without find_tables -> plain text only

        combined = page_text
        if table_texts:
            combined += "\n\n[TABLE DATA]\n" + "\n\n".join(table_texts)

        documents.append(Document(
            page_content=combined,
            metadata={"source": Path(pdf_path).name, "page": page_index}))
    doc.close()
    return documents

def main():
    pdfs = list(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs in ./data — add a handbook PDF and retry.")
        return

    docs = []
    for pdf in pdfs:
        print(f"Loading {pdf.name} (table-aware) ...")
        docs.extend(load_pdf(str(pdf)))
    print(f"Loaded {len(docs)} pages.")

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150).split_documents(docs)
    print(f"Split into {len(chunks)} chunks. Embedding (qwen3-embedding:0.6b) ...")

    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    print(f"Done. Vector store saved to ./{CHROMA_DIR}")

if __name__ == "__main__":
    main()
