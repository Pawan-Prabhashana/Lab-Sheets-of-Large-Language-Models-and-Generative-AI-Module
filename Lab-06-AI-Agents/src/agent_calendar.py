# agent_calendar.py — Part D: agent with calculator + memory + RAG + Google Calendar
import ast, operator, sqlite3, subprocess, os.path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.messages import (HumanMessage, SystemMessage, AIMessage,
                                     ToolMessage)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

llm = ChatOllama(model="llama3.2:3b", temperature=0)
CAL_TZ = "Asia/Colombo"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

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

# ================= GOOGLE CALENDAR SERVICE (cached) =================
_calendar = None
def calendar_service():
    global _calendar
    if _calendar is None:
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as f:
                f.write(creds.to_json())
        _calendar = build("calendar", "v3", credentials=creds)
    return _calendar

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

@tool
def create_calendar_event(title: str, date: str, start_time: str,
                          duration_minutes: int = 60) -> str:
    """Create an event in the user's Google Calendar. 'title' = event name,
    'date' = 'YYYY-MM-DD', 'start_time' = 'HH:MM' in 24-hour local time,
    'duration_minutes' defaults to 60. Use when the user wants to schedule/book/add
    an event or meeting."""
    try:
        svc = calendar_service()
        start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=duration_minutes)
        body = {"summary": title,
                "start": {"dateTime": start.isoformat(), "timeZone": CAL_TZ},
                "end": {"dateTime": end.isoformat(), "timeZone": CAL_TZ}}
        svc.events().insert(calendarId="primary", body=body).execute()
        return f"Event '{title}' created for {date} at {start_time} ({CAL_TZ})."
    except Exception as e:
        return f"Could not create event: {e}"

@tool
def check_schedule(date: str = "") -> str:
    """Check the user's Google Calendar for a given day. 'date' = 'YYYY-MM-DD';
    leave empty for today. Use when the user asks what's on their schedule/calendar."""
    try:
        svc = calendar_service()
        tz = ZoneInfo(CAL_TZ)
        day = (datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=tz)
               if date else datetime.now(tz))
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        items = svc.events().list(calendarId="primary", timeMin=start.isoformat(),
            timeMax=end.isoformat(), singleEvents=True,
            orderBy="startTime").execute().get("items", [])
        if not items:
            return f"No events scheduled for {start.date()}."
        return "\n".join(
            f"{e['start'].get('dateTime', e['start'].get('date'))} - "
            f"{e.get('summary','(no title)')}" for e in items)
    except Exception as e:
        return f"Could not read schedule: {e}"

# ================= MEMORY EXTRACTION =================
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
tools = [calculator, search_student_memory, search_university_knowledge,
         create_calendar_event, check_schedule]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}
short_term = []

def chat(user_message):
    fact = extract_memory(user_message)
    if fact:
        save_memory(fact); print(f"[NEW MEMORY DETECTED]\n[SAVED] {fact}")
    else:
        print("[MEMORY] No new information to save.")

    today = datetime.now(ZoneInfo(CAL_TZ))
    sys = SystemMessage(content=(
        f"You are an intelligent university assistant. Today is "
        f"{today:%A, %Y-%m-%d} in {CAL_TZ}. Tools: calculator (math), "
        "search_student_memory (recall facts the user told you), "
        "search_university_knowledge (university/degree/module facts), "
        "create_calendar_event (schedule an event), check_schedule (read the "
        "calendar). For course/module questions you MUST use "
        "search_university_knowledge. When booking events, convert relative dates "
        "like 'tomorrow' to YYYY-MM-DD using today's date above. Reply in one short "
        "sentence."))
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
            print(f"[TOOL RESULT]    {str(res)[:400]}{'...' if len(str(res))>400 else ''}")
            messages.append(ToolMessage(content=str(res), tool_call_id=call["id"]))
    return "Sorry, I couldn't complete that."

if __name__ == "__main__":
    init_db()
    print("=" * 40)
    print("UNIVERSITY AI AGENT")
    print("CALC | MEMORY | RAG | GOOGLE CALENDAR")
    print("=" * 40)
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        print(f"Agent: {chat(q)}")
