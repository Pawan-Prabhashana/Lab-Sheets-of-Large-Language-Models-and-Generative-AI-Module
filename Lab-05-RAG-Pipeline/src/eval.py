# eval.py — Group 1: baseline (vector-only) vs hybrid (BM25 + vector + RRF + rerank)
import time
from hybrid_pipeline import baseline_retrieve, hybrid_retrieve, answer

# question | substring marking the RELEVANT chunk | keywords a correct ANSWER contains
EVAL = [
    {"q": "What is the prerequisite for the Operating Systems module?",
     "relevant": "Operating Systems", "answer_kw": ["CS102", "Computer Systems"]},
    {"q": "How many credits is the Final Year Research Project?",
     "relevant": "Final Year Research Project", "answer_kw": ["40"]},
    {"q": "What is the minimum attendance requirement?",
     "relevant": "attendance", "answer_kw": ["80"]},
    {"q": "What mark is required to pass a module?",
     "relevant": "pass a module", "answer_kw": ["40"]},
    {"q": "How many credits are required for an honours degree?",
     "relevant": "360 credits", "answer_kw": ["360"]},
    {"q": "Who is the programme coordinator for Data Science?",
     "relevant": "Fernando", "answer_kw": ["Fernando"]},
    {"q": "What time does the library close on weekdays?",
     "relevant": "library is open", "answer_kw": ["10"]},
    {"q": "What GPA is required for the merit scholarship?",
     "relevant": "merit scholarship", "answer_kw": ["3.7"]},
    {"q": "What is the prerequisite for Machine Learning?",
     "relevant": "Machine Learning", "answer_kw": ["DS202", "Statistics"]},
    {"q": "Which programme includes Mobile Application Development?",
     "relevant": "Mobile Application Development", "answer_kw": ["Software Engineering"]},
    {"q": "How long is the industrial internship?",
     "relevant": "internship", "answer_kw": ["twelve", "12"]},
    {"q": "How many working days are allowed to lodge an exam appeal?",
     "relevant": "academic appeal", "answer_kw": ["ten", "10"]},
]

def first_relevant_rank(docs, marker):
    for i, d in enumerate(docs, start=1):
        if marker.lower() in d.page_content.lower():
            return i
    return None

def baseline5(q):
    return baseline_retrieve(q, k=5)

def hybrid5(q):
    return hybrid_retrieve(q, n_each=10, final_k=5)

def evaluate(retrieve_fn):
    n = len(EVAL)
    recall, rr, correct, ret_lat = 0, 0.0, 0, 0.0
    for item in EVAL:
        t0 = time.time()
        docs = retrieve_fn(item["q"])[:5]
        ret_lat += time.time() - t0          # retrieval latency (the differentiator)
        rank = first_relevant_rank(docs, item["relevant"])
        if rank:
            recall += 1                       # relevant chunk in top-5
            rr += 1.0 / rank                  # reciprocal rank
        ans = answer(item["q"], docs).lower()
        if any(kw.lower() in ans for kw in item["answer_kw"]):
            correct += 1
    return {
        "Recall@5": recall / n,
        "MRR": rr / n,
        "Answer correctness": correct / n,
        "Avg retrieval latency (s)": ret_lat / n,
    }

if __name__ == "__main__":
    print(f"Evaluating on {len(EVAL)} questions...\n")
    print("Running baseline (vector-only)...")
    base = evaluate(baseline5)
    print("Running hybrid (BM25 + vector + RRF + rerank)...")
    hyb = evaluate(hybrid5)

    print(f"\n{'Metric':<28}{'Baseline':>12}{'Hybrid':>12}")
    print("-" * 52)
    for m in base:
        print(f"{m:<28}{base[m]:>12.3f}{hyb[m]:>12.3f}")
