# Activity Outcomes

**Scenario:** Group 5, the Busy Student.

## The product

The outcome of the activity is **Cadence**, a mobile time companion for students who juggle lectures, assignments, group projects, and deadlines. Its core loop is Brain-dump, Plan, Adapt:

- **Brain-dump.** You type or speak everything on your mind in one box, deadlines, fixed classes, and vague intentions all mixed together.
- **Plan.** The LLM parses that into structured tasks and schedules them into the real free gaps around your fixed timetable, producing a time-blocked "Today" plan.
- **Adapt.** As the day moves, you finish things, fall behind, or something new lands, and Cadence rebuilds the rest of the week in one tap and explains, in a sentence, what it changed and why.

The full concept, including the target user and persona, is in [`../product-concept.md`](../product-concept.md), and the visual prototype is in [`../screenshots/`](../screenshots/).

## Key features delivered in the concept

1. Natural-language capture, one box that extracts tasks, due dates, and effort from a free-text brain-dump.
2. Smart auto-schedule, places tasks into real free slots around the fixed timetable.
3. Deadline-aware prioritisation, ranks by due date, grade weight, and remaining effort, with an at-risk flag.
4. Assignment breakdown, decomposes a large deliverable into ordered subtasks back-planned from the due date.
5. One-tap re-plan, reshuffles the week when you fall behind and explains the change.
6. Daily brief and context nudges, a morning summary plus timely, specific prompts.

## How an LLM powers the product

The LLM is the reasoning engine behind the loop: parsing unstructured input into structured tasks, reasoning over timetable constraints to build a schedule, decomposing big deliverables, and writing the plain-language explanations and nudges. The timetable, the done state, and reminder timing stay in deterministic storage, so the product stays reliable while still getting the interpretation only an LLM can provide.
