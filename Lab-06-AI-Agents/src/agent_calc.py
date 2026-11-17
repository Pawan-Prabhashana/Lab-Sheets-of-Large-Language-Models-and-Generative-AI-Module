# agent_calc.py — Part A: Calculator Agent (Ollama + LangChain, macOS)

# ---- Step 3: Import all the libraries ----
import ast
import operator
import subprocess

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# ---- Step 4: Initialize the LLM (local model via Ollama) ----
llm = ChatOllama(model="llama3.2:3b", temperature=0)

# ---------- helpers for the calculator ----------
# Safe arithmetic evaluator (no raw eval → no code-injection risk)
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def _eval(node):
    if isinstance(node, ast.Constant):          # a number
        return node.value
    if isinstance(node, ast.BinOp):             # left <op> right
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):           # -x, +x
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")

def safe_calc(expression: str):
    return _eval(ast.parse(expression, mode="eval").body)

def show_in_calculator(expression: str):
    """Open macOS Calculator and type the sum (visual only).
    Needs Accessibility permission; fails silently if not granted."""
    keys = expression.replace(" ", "")
    script = f'''
    tell application "Calculator" to activate
    delay 0.4
    tell application "System Events"
        keystroke "{keys}"
        keystroke "="
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=False, timeout=10)
    except Exception:
        pass  # permission not granted — Python result below is still correct

# ---- Step 5: Create the calculator tool ----
@tool
def calculator(expression: str) -> str:
    """Perform an arithmetic calculation. Input is a math expression such as
    '25 * 4', '100 / 5', or '(3 + 4) * 2'. Returns the numeric result."""
    try:
        result = safe_calc(expression)
    except Exception as e:
        return f"Error: could not evaluate '{expression}' ({e})"
    show_in_calculator(expression)   # open Calculator.app for the visual effect
    return str(result)

# ---- Step 6: Register the tool with the LLM ----
tools = [calculator]
llm_with_tools = llm.bind_tools(tools)
tool_map = {t.name: t for t in tools}

# ---- Step 7: Implement the Agent execution loop ----
def run_agent(user_query: str) -> str:
    messages = [
        SystemMessage(content=(
            "You are a helpful assistant. Use the calculator tool for any "
            "arithmetic. After you get a tool result, reply with one short "
            "sentence stating the answer."
        )),
        HumanMessage(content=user_query),
    ]
    for _ in range(5):  # safety cap on tool-calling rounds
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        if not ai_msg.tool_calls:          # no tool needed → final answer
            return ai_msg.content

        for call in ai_msg.tool_calls:
            print(f"[TOOL SELECTED]  {call['name']}")
            print(f"[TOOL ARGUMENTS] {call['args']}")
            result = tool_map[call["name"]].invoke(call["args"])
            print(f"[TOOL RESULT]    {result}")
            messages.append(ToolMessage(content=str(result),
                                        tool_call_id=call["id"]))
    return "Sorry, I couldn't complete that."

# ---- Step 8: Run and test ----
if __name__ == "__main__":
    print("Calculator Agent (Ollama + LangChain). Type 'quit' to exit.")
    while True:
        q = input("\nYou: ")
        if q.strip().lower() in {"quit", "exit"}:
            break
        print(f"Agent: {run_agent(q)}")
