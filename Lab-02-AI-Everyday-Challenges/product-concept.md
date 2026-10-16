# Cadence — the time companion that turns a messy week into a realistic day

**Lab 2 · AI in Everyday Challenges · Group 5 — The Busy Student**
**PUSL 3205 — Large Language Models and Generative AI**

> Tell it your week in plain words. Get back a day you can actually follow.

---

## 1. Problem framing

The brief for Group 5 is the *Busy Student*: someone balancing lectures, assignments, group
projects, studying, extracurriculars, personal time, and deadlines all at once. When that many
things compete for attention, important tasks slip — not because the student is lazy, but because
they lose **visibility** of what is due, how long it will really take, and when they actually have
time to do it.

From talking through this scenario, three failure points stand out:

1. **Capture friction.** Tasks arrive in messy, spoken form ("the stats report is due Friday, and
   I've got a group meeting Tuesday afternoon"). Traditional planners make you stop and fill in a
   form — due date, category, priority — so most tasks never get logged at all.
2. **No sense of time cost.** A to-do list shows *what* but not *when* or *how long*. A student sees
   "Finish report" next to "Reply to email" as if they were equal, and underestimates the big one
   until the night before.
3. **Plans break and never recover.** Real weeks go sideways. A single missed afternoon makes a
   static plan wrong, and rebuilding it by hand is enough effort that people just abandon the plan.

Existing tools (Google Calendar, Todoist, Notion) are powerful but **passive**: they store what you
type and show it back. They don't *interpret* a brain-dump, *reason* about how to fit the work into
the gaps you have, or *rebuild* the plan when life changes. That reasoning gap is exactly where an
LLM earns its place.

---

## 2. Product name & concept

**Cadence** is a mobile-first study and time companion for university students. Its core loop is
simple:

**Brain-dump → Plan → Adapt.**

- You **brain-dump** everything on your mind in one text box (or voice note) — deadlines, fixed
  classes, vague intentions, all mixed together.
- Cadence's LLM **parses** that into structured tasks (title, course, due date, estimated effort,
  priority) and **schedules** them into the real free gaps around your fixed timetable, producing a
  time-blocked "Today" plan.
- As the day moves — you finish things, fall behind, or something new lands — Cadence **adapts** the
  rest of the week in one tap and tells you, in a sentence, what it changed and why.

The name reflects the goal: not a rigid timetable that shames you when you fall off it, but a
sustainable *rhythm* you can keep. Cadence plans for a realistic student, not an idealised one.

---

## 3. Key features

| # | Feature | What it does | Why it matters |
|---|---------|--------------|----------------|
| 1 | **Natural-language capture** | One box takes a free-text or spoken brain-dump; the LLM extracts tasks, due dates, course tags, and effort estimates. | Removes the form-filling friction that stops students logging tasks in the first place. |
| 2 | **Smart auto-schedule** | Places each task into actual free slots around the fixed timetable, respecting deadlines, estimated durations, and preferred focus hours. | Turns a flat list into an *achievable* time-blocked day, so "what" becomes "when". |
| 3 | **Deadline-aware prioritisation** | Ranks tasks by a blend of due date, grade weight, and remaining effort; surfaces an "At risk" banner when a deadline is mathematically tight. | Makes the big, graded, soon-due work visually dominant instead of equal to trivial tasks. |
| 4 | **Assignment breakdown** | Decomposes a large deliverable ("10-page report") into ordered subtasks and back-plans them from the due date. | Fights last-minute cramming by making a big task start *earlier* and feel smaller. |
| 5 | **One-tap re-plan** | When you mark things done or miss a block, it reshuffles the remaining week and explains the change in plain language. | Keeps the plan alive after the first thing goes wrong — the moment most plans die. |
| 6 | **Daily brief & context nudges** | A morning summary plus timely nudges ("2 free hours this afternoon — good block for the stats report"). | Keeps the plan present without nagging, nudging at the moment a decision is actually made. |

---

## 4. Target user

**Primary:** 2nd- and 3rd-year undergraduates with a fixed lecture/lab timetable *plus* a shifting
load of coursework, group projects, and extracurriculars — students who miss deadlines from poor
visibility and under-estimation, not from not caring.

**Secondary:** first-year students building study habits for the first time, and postgraduate /
part-time students juggling study with work.

**Representative persona — "Dinuki, Year 2 Data Science":** has 14 fixed contact hours a week, three
overlapping assignments, a group project, and a part-time weekend job. She starts most weeks meaning
to get ahead and ends most weeks working past midnight on Thursday. She doesn't need *more*
reminders — she needs something that tells her *what to do right now* and quietly rebuilds the plan
when Tuesday falls apart.

---

## 5. How an LLM powers it

Cadence isn't "a calendar with a chatbot bolted on." The LLM is the reasoning engine behind every
step of the core loop, doing work that rule-based software can't:

- **Parsing unstructured input → structured tasks.** The LLM reads a messy brain-dump and returns
  clean fields: task title, course, due date (resolving relative dates like "next Friday"), an
  effort estimate, and a priority. This is classic LLM information-extraction, and it's what makes
  zero-friction capture possible.
- **Constraint reasoning for scheduling.** Given the fixed timetable, task durations, deadlines, and
  the student's preferred focus windows, the LLM arranges work into the free gaps and produces a
  time-blocked day — then explains the trade-offs it made ("I moved reading to tomorrow so the
  graded report gets today's long afternoon block").
- **Backward planning / decomposition.** Asked to break down a deliverable, the LLM proposes
  sensible subtasks and spreads them across the days before the due date — generative planning, not
  a fixed template.
- **Natural-language explanations and nudges.** Every re-plan and nudge is phrased in friendly,
  specific language, so the student trusts and understands the plan instead of treating it as a
  black box.
- **Conversational re-planning.** The student can push back in plain words ("I'm wiped, make
  tomorrow lighter") and the LLM adjusts the schedule accordingly.

**Where the LLM should *not* run alone:** the actual timetable, reminder timing, and done/not-done
state live in ordinary structured storage and deterministic logic. The LLM proposes; the app stores
the truth and fires reminders. This keeps the product reliable (no hallucinated deadlines) while
still getting the interpretation and reasoning that only an LLM provides.

### How I used an LLM as the development partner

As the brief required, I used an LLM throughout the *design* process, not just as a feature inside
the product: to pressure-test the problem framing against the three failure points, to brainstorm
and then narrow down the product name, to challenge weak features (an earlier "social leaderboard"
idea was cut as off-problem), and to draft and refine the microcopy shown in the mock-up. The LLM
acted as a fast, opinionated collaborator; the product decisions and the final cut were mine.

---

## 6. Prototype

The main-screen visual prototype is a single self-contained HTML file in
[`mockup/`](mockup/cadence-mockup.html), with a captured screenshot at
[`mockup/cadence-mockup.png`](mockup/cadence-mockup.png). It shows the two screens at the heart of
the core loop: the **brain-dump capture** screen and the **generated "Today" plan** with
prioritisation, an at-risk flag, and a context nudge.
