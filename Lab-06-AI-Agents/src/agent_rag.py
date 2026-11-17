# agent_rag.py — Part C: RAG-powered agent (calculator + memory + RAG)
import ast, operator, sqlite3, subprocess
from datetime import datetime
from pathlib import Path

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import (HumanMessage, SystemMessage, AIMessage,
                                     ToolMessage)

llm = ChatOllama(model="llama3.2:3b", temperature=0)

# ================= LONG-TERM MEMORY (SQLite) =================
DB_PATH = Path("student_memory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL, created_at TEXT NOT NULL)""")
    conn.commit(); conn.close()

def save_memory(content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO memories (content, created_at) VALUES (?, ?)",
                 (content, datetime.now().isoformat()))
    conn.commit(); conn.close()

def all_memories():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT content FROM memories").fetchall()
    conn.close()
    return [r[0] for r in rows]

# ================= RAG VECTOR STORE =================
_embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")
_vectorstore = Chroma(persist_directory="chroma_db", embedding_function=_embeddings)

# ================= TOOLS =================
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}
def _eval(n):
    if isinstance(n, ast.Constant): return n.value
    if isinstance(n, ast.BinOp): return _OPS[type(n.op)](_eval(n.left), _eval(n.right))
    if isinstance(n, ast.UnaryOp): return _OPS[type(n.op)](_eval(n.operand))
    raise ValueError("unsupported expression")

@tool
def calculator(expression: str) -> str:
    """Perform an arithmetic calculation, e.g. '100 / 4'."""
    try:
        result = _eval(ast.parse(expression, mode="eval").body)
    except Exception as e:
        return f"Error: could not evaluate '{expression}' ({e})"
    keys = expression.replace(" ", "")
    subprocess.run(["osascript", "-e",
        f'tell application "Calculator" to activate\ndelay 0.4\n'
        f'tell application "System Events"\nkeystroke "{keys}"\nkeystroke "="\nend tell'],
        check=False, timeout=10)
    return str(result)

_STOP = {"what", "is", "my", "the", "a", "do", "you", "know", "i", "me", "about"}

@tool
def search_student_memory(query: str) -> str:
    """Search stored info about the user (name, course, preferences). Use when the
    user asks about something they told you earlier, e.g. 'what is my name?'."""
    mems = all_memories()
    if not mems:
        return "No matching memories found."
    words = [w for w in query.lower().split() if w not in _STOP]
    hits = [m for m in mems if any(w in m.lower() for w in words)]
    return "\n".join(hits) if hits else "No matching memories found."

@tool
def search_university_knowledge(query: str) -> str:
    """Search the university knowledge base (handbook) for programmes, modules,
    subjects, credits, prerequisites, projects, policies and departments. Use this
    for ANY question about the university or its courses."""
    results = _vectorstore.similarity_search(query, k=3)
    if not results:
        return "No relevant information found in the university knowledge base."
    parts = []
    for d in results:
        src = Path(d.metadata.get("source", "handbook")).name
        page = d.metadata.get("page", "?")
        parts.append(f"[Source: {src}, Page: {page}]\n{d.page_content.strip()}")
    return "\n\n".join(parts)

# ================= MEMORY EXTRACTION (stricter: personal facts only) =================
def extract_memory(user_message):
    out = llm.invoke([
        SystemMessage(content=(
            "Decide if the user's message states a NEW personal fact about "
            "THEMSELVES — their name, their course/degree, their preferences or "
            "goals. If yes, reply with ONE short statement like "
            "\"The user's name is Alex.\" If the message is a question, a command, "
            "a calculation, or general knowledge, reply with exactly: NONE")),
        HumanMessage(content=user_message)]).content.strip()
    return None if out.upper().startswith("NONE") or not out else out

# ================= AGENT =================
tools = [calculator, search_student_memory, search_university_knowledge]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}
short_term = []

def chat(user_message):
    fact = extract_memory(user_message)
    if fact:
        save_memory(fact); print(f"[NEW MEMORY DETECTED]\n[SAVED] {fact}")
    else:
        print("[MEMORY] No new information to save.")

    sys = SystemMessage(content=(
        "You are an intelligent university assistant with three tools: calculator "
        "(math), search_student_memory (recall facts the user told you), and "
        "search_university_knowledge (facts about the university, degrees, modules, "
        "credits, prerequisites). For ANY question about courses/modules/the "
        "university, you MUST call search_university_knowledge and answer only from "
        "its result. Reply in one short, factual sentence."))
    messages = [sys] + short_term + [HumanMessage(content=user_message)]

    for _ in range(5):
        ai = llm_with_tools.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            short_term.append(HumanMessage(content=user_message))
            short_term.append(AIMessage(content=ai.content))
            print("[SHORT-TERM MEMORY] Conversation updated.")
            return ai.content
        for call in ai.tool_calls:
            print(f"[TOOL SELECTED]  {call['name']}")
            print(f"[TOOL ARGUMENTS] {call['args']}")
            res = tool_map[call["name"]].invoke(call["args"])
            print(f"[TOOL RESULT]    {res[:400]}{'...' if len(str(res))>400 else ''}")
            messages.append(ToolMessage(content=str(res), tool_call_id=call["id"]))
    return "Sorry, I couldn't complete that."

if __name__ == "__main__":
    init_db()
    print("=" * 40)
    print("RAG-POWERED UNIVERSITY AI AGENT")
    print("CALCULATOR | MEMORY | RAG KNOWLEDGE")
    print("=" * 40)
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        print(f"Agent: {chat(q)}")
