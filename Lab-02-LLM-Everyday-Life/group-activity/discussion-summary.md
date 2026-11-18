# Discussion Summary

This file summarises how our group worked through the Lab 2 activity, from framing the problem to settling on Cadence, and how we used an LLM as our development partner along the way.

## Framing the problem

We started with our scenario, Group 5, the Busy Student, and agreed early that the real problem was not laziness. Students miss deadlines because they lose visibility of what is due, how long it takes, and when they actually have time to do it. To keep ourselves focused, we named three failure points and kept coming back to them:

1. Capture friction, where logging a task takes more effort than it is worth, so tasks never get written down.
2. No sense of time cost, where a flat list shows what but not when or how long.
3. Plans that break and never recover, where one missed afternoon makes the whole plan wrong.

Every feature we kept had to answer at least one of these.

## Using an LLM as our development partner

We used an LLM throughout the design process, not just as a feature inside the product.

- **Brainstorming directions.** We asked it to generate a wide range of product ideas for the Busy Student, then clustered them into themes (reminders, capture, scheduling, and motivation).
- **Pressure-testing the idea.** We made the model argue against our favourite direction. That is how we realised a plain reminder app would not solve the visibility problem, and that the value was in planning and rescheduling.
- **Naming.** We generated and narrowed a shortlist of names and chose Cadence, because it captures the idea of a sustainable rhythm rather than a rigid schedule.
- **Refining features and copy.** We used it to tighten the feature list and to draft the short microcopy shown in the mock-ups, such as the morning brief and the at-risk message.

We treated the model as a fast, opinionated collaborator. The decisions were ours.

## Decisions and alternatives we dropped

- **Chose the Capture, Plan, Adapt loop** as the core, because it maps directly onto the three failure points.
- **Dropped a social study leaderboard.** It was fun, but it solved a motivation problem, not the time-management problem in the brief.
- **Dropped a pure voice assistant.** Voice stayed as an input option, but we decided the plan itself had to be visual so the student can see the day at a glance.
- **Kept the LLM out of the source of truth.** We agreed the model should propose the plan while the timetable, reminders, and done state stay in deterministic logic, so the product never hallucinates a deadline. This was our most important design decision.

## How we split the work

SAP Prabhashana led the activity and carried the product concept and naming, the LLM integration design, the prototype and mock-ups, and the pitch deck. DD Rubasinghe contributed to feature definition and user-flow input and to the slide content. PGT Sewmini led the problem research, kept the discussion notes, and reviewed the visuals. The full split is in [`group-members.md`](group-members.md).

## Challenges

The main challenge was scope. Our first feature list was far too long, and the discipline that saved us was asking of every feature whether it solved one of the three failure points. The second challenge was making the prototype show the reasoning the LLM does, which we handled by putting concrete artefacts on the screens: parsed task chips, an at-risk flag, and an explained morning brief, rather than generic placeholder UI.
