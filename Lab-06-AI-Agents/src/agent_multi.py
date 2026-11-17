# agent_multi.py — Exercise: multi-tool agent (Ollama + LangChain, macOS)
import ast
import operator
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

llm = ChatOllama(model="llama3.2:3b", temperature=0)

# ---------- Tool 1: Calculator ----------
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}

def _eval(node):
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")

@tool
def calculator(expression: str) -> str:
    """Perform an arithmetic calculation, e.g. '25 * 4' or '(3+4)*2'."""
    try:
        result = _eval(ast.parse(expression, mode="eval").body)
    except Exception as e:
        return f"Error: could not evaluate '{expression}' ({e})"
    keys = expression.replace(" ", "")
    script = f'tell application "Calculator" to activate\ndelay 0.4\ntell application "System Events"\nkeystroke "{keys}"\nkeystroke "="\nend tell'
    subprocess.run(["osascript", "-e", script], check=False, timeout=10)
    return str(result)

# ---------- Tool 2: Date and Time ----------
@tool
def get_datetime() -> str:
    """Return the current date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")

# ---------- Tool 3: Notepad / TextEdit ----------
@tool
def write_note(text: str) -> str:
    """Open the macOS TextEdit app and write the given text into a new document.
    Use when the user wants to open Notepad/TextEdit and write something."""
    safe = text.replace('"', '\\"')
    script = (f'tell application "TextEdit"\nactivate\nmake new document\n'
              f'set text of front document to "{safe}"\nend tell')
    subprocess.run(["osascript", "-e", script], check=False, timeout=10)
    return f"Opened TextEdit and wrote: {text}"

# ---------- Tool 4: File Search ----------
@tool
def search_files(directory: str, extension: str = "") -> str:
    """Search a directory (and subfolders) for files. 'directory' like '~/MSC_AI';
    'extension' optionally filters by type, e.g. 'pdf' or 'txt'."""
    base = Path(directory).expanduser()
    if not base.exists():
        return f"Directory not found: {base}"
    pattern = f"*.{extension}" if extension else "*"
    matches = [str(p) for p in base.rglob(pattern) if p.is_file()]
    return "\n".join(matches) if matches else f"No files matching '{pattern}' in {base}"

# ---------- Tool 5: File Creation ----------
@tool
def create_file(directory: str, filename: str, content: str) -> str:
    """Create a text file with given content. 'directory' like '~/MSC_AI',
    'filename' like 'test.txt', 'content' is the text to write."""
    base = Path(directory).expanduser()
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename
    path.write_text(content)
    return f"Created file: {path}"

# ---------- Tool 6: System Information ----------
@tool
def system_info() -> str:
    """Return the computer's operating system, processor, and memory info."""
    os_name = f"{platform.system()} {platform.mac_ver()[0]}".strip()
    def sysctl(key):
        return subprocess.run(["sysctl", "-n", key], capture_output=True,
                              text=True, timeout=5).stdout.strip()
    try: cpu = sysctl("machdep.cpu.brand_string")
    except Exception: cpu = platform.processor() or platform.machine()
    try: mem = f"{round(int(sysctl('hw.memsize')) / (1024**3))} GB"
    except Exception: mem = "unknown"
    return f"OS: {os_name}\nProcessor: {cpu} ({platform.machine()})\nMemory: {mem}"

# ---------- Register all tools + agent loop ----------
tools = [calculator, get_datetime, write_note, search_files, create_file, system_info]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}

def run_agent(user_query: str) -> str:
    messages = [
        SystemMessage(content=(
            "You are an assistant with tools: calculator (math), get_datetime, "
            "write_note (open TextEdit and write), search_files, create_file, "
            "system_info (computer specs). Pick the single most appropriate tool "
            "for the request. After a tool runs, reply in one short sentence.")),
        HumanMessage(content=user_query),
    ]
    for _ in range(5):
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        if not ai_msg.tool_calls:
            return ai_msg.content
        for call in ai_msg.tool_calls:
            print(f"[TOOL SELECTED]  {call['name']}")
            print(f"[TOOL ARGUMENTS] {call['args']}")
            result = tool_map[call["name"]].invoke(call["args"])
            print(f"[TOOL RESULT]    {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    return "Sorry, I couldn't complete that."

if __name__ == "__main__":
    print("Multi-Tool Agent (Ollama + LangChain). Type 'quit' to exit.")
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        print(f"Agent: {run_agent(q)}")
