# rag_pipeline.py — Lab 5: terminal RAG chat over the university knowledge base
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

CHROMA_DIR = "chroma_db"

# --- Load the vector store + models ---
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})   # top-k retrieval
llm = ChatOllama(model="llama3.2:3b", temperature=0)

# --- Prompt template: structure the query with retrieved context ---
prompt = ChatPromptTemplate.from_template(
    "You are a university assistant. Answer the question using ONLY the context "
    "below. If the answer is not in the context, say you don't have that "
    "information.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Answer:"
)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

def answer(question: str) -> str:
    docs = retriever.invoke(question)          # 1. Retrieve
    context = format_docs(docs)                # 2. Augment
    messages = prompt.format_messages(context=context, question=question)
    return llm.invoke(messages).content        # 3. Generate

if __name__ == "__main__":
    print("University RAG assistant. Type 'exit' to quit.\n")
    while True:
        q = input("Ask a university question (or exit): ")
        if q.strip().lower() in {"exit", "quit"}:
            break
        print(f"\nAnswer: {answer(q)}\n")
