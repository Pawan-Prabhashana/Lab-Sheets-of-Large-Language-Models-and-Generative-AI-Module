# app.py — Lab 5 Task: University AI Assistant with PDF upload
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

CHROMA_DIR = "chroma_db"
st.set_page_config(page_title="University AI Assistant", page_icon="🎓")

@st.cache_resource
def get_base():
    embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
    llm = ChatOllama(model="llama3.2:3b", temperature=0)
    prompt = ChatPromptTemplate.from_template(
        "You are a university assistant. Answer the question using ONLY the context "
        "below. If the answer is not in the context, say you don't have that "
        "information.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )
    base_store = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    return embeddings, llm, prompt, base_store

embeddings, llm, prompt, base_store = get_base()

def build_store_from_uploads(files):
    docs = []
    for f in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.getvalue())
            tmp_path = tmp.name
        docs.extend(PyMuPDFLoader(tmp_path).load())
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=120).split_documents(docs)
    return Chroma.from_documents(chunks, embeddings, collection_name="uploaded_docs")

def answer(question, retriever):
    docs = retriever.invoke(question)
    context = "\n\n".join(d.page_content for d in docs)
    messages = prompt.format_messages(context=context, question=question)
    return llm.invoke(messages).content

# ---------- Sidebar: upload your own PDFs ----------
st.sidebar.header("📄 Your documents")
uploaded = st.sidebar.file_uploader("Upload PDF(s)", type="pdf",
                                    accept_multiple_files=True)
if st.sidebar.button("Process uploaded PDFs") and uploaded:
    with st.spinner("Reading and embedding your PDFs..."):
        st.session_state.user_store = build_store_from_uploads(uploaded)
    st.sidebar.success(f"Processed {len(uploaded)} file(s).")

if "user_store" in st.session_state:
    st.sidebar.info("Answering from YOUR uploaded PDFs.")
    if st.sidebar.button("Clear uploads (use handbook)"):
        del st.session_state.user_store
        st.rerun()
else:
    st.sidebar.caption("No uploads — answering from the default handbook.")

# ---------- Main chat ----------
st.title("🎓 University AI Assistant")
st.caption("Ask questions based on university documents")

if "messages" not in st.session_state:
    st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Ask your university question..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    store = st.session_state.get("user_store", base_store)   # uploaded or default
    retriever = store.as_retriever(search_kwargs={"k": 4})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            a = answer(q, retriever)
        st.markdown(a)
    st.session_state.messages.append({"role": "assistant", "content": a})
