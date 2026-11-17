# agent_memory.py — Part B: student agent with memory (SQLite)
import ast, operator, sqlite3, subprocess
from datetime import datetime
from pathlib import Path

from langchain_ollama import ChatOllama
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
        content TEXT NOT NULL,
        created_at TEXT NOT NULL)""")
    conn.commit(); conn.close()

def save_memory(content: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO memories (content, created_at) VALUES (?, ?)",
                 (content, datetime.now().isoformat()))
    conn.commit(); conn.close()

def all_memories():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT content FROM memories").fetchall()
    conn.close()
    return [r[0] for r in rows]

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
    """Perform an arithmetic calculation, e.g. '15 * 3'."""
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
    """Search previously stored information about the user (their name,
    preferences, field of study, etc.). Use this whenever the user asks about
    something they told you earlier, e.g. 'what is my name?'."""
    mems = all_memories()
    if not mems:
        return "No matching memories found."
    words = [w for w in query.lower().split() if w not in _STOP]
    hits = [m for m in mems if any(w in m.lower() for w in words)]
    return "\n".join(hits) if hits else "No matching memories found."

# ================= MEMORY EXTRACTION (what to save) =================
def extract_memory(user_message: str):
    out = llm.invoke([
        SystemMessage(content=(
            "You extract durable facts worth remembering about the user "
            "(name, field of study, preferences, goals). If the message contains "
            "such a fact, reply with ONE short statement like "
            "\"The user's name is Alex.\" If there is nothing worth saving, reply "
            "with exactly: NONE")),
        HumanMessage(content=user_message),
    ]).content.strip()
    return None if out.upper().startswith("NONE") or not out else out

# ================= AGENT (short-term + working memory) =================
tools = [calculator, search_student_memory]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}
short_term = []   # conversation history for THIS session

def chat(user_message: str) -> str:
    # 1) Long-term: decide whether to save a new fact
    fact = extract_memory(user_message)
    if fact:
        save_memory(fact)
        print(f"[NEW MEMORY DETECTED]\n[SAVED] {fact}")
    else:
        print("[MEMORY] No new information to save.")

    # 2) Working memory = system prompt + short-term history + this message
    sys = SystemMessage(content=(
        "You are an intelligent student assistant with memory. Tools: calculator "
        "(math), search_student_memory (recall stored facts). When the user asks "
        "about anything they told you before (their name, course, preferences), "
        "you MUST call search_student_memory to look it up before answering. "
        "Reply in one short sentence."))
    messages = [sys] + short_term + [HumanMessage(content=user_message)]

    # 3) Agent loop
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
            print(f"[TOOL RESULT]    {res}")
            messages.append(ToolMessage(content=str(res), tool_call_id=call["id"]))
    return "Sorry, I couldn't complete that."

if __name__ == "__main__":
    init_db()
    print("=" * 40)
    print("INTELLIGENT STUDENT AI AGENT")
    print("SHORT-TERM MEMORY | LONG-TERM SQLITE MEMORY | WORKING MEMORY")
    print("=" * 40)
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        print(f"Agent: {chat(q)}")
