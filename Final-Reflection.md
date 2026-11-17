# Final Reflection

Looking back across PUSL 3205, the thing that stuck with me most is how the labs built on each other. They were not six unrelated exercises. They were a single progression from the simplest text classifier to systems that reason over documents and act through tools, and each step existed because the previous one had a clear limitation.

## What connected

Lab 01 was deliberately old-fashioned: Bag of Words and linear classifiers. It worked, reaching about 82 percent on sentiment, but it was blind to word order, so "not good" and "good" looked almost the same to it. That exact weakness is what Lab 03 fixed. Building a transformer from scratch, writing the self-attention, the causal mask, and the positional embeddings myself, I could see how a model finally uses context and sequence rather than a bag of isolated words. Doing it by hand, rather than importing a model, is what made the later labs make sense.

From there, Labs 04, 05, and 06 were really three answers to the same question: I have a capable base model, how do I make it useful for a specific job? Fine-tuning (Lab 04) changes the model's weights with LoRA and QLoRA, which is efficient but needs training data and a GPU. RAG (Lab 05) leaves the model alone and instead retrieves the right documents at answer time, which is cheaper to update and grounds the answer in a source. Agents (Lab 06) let the model act, choosing and calling tools, including the RAG retriever from Lab 05 as one of those tools. Seeing the Lab 05 vector store reappear as a tool inside the Lab 06 agent was the moment the whole module clicked into one system.

Lab 02 sat slightly apart, because it was about judgment rather than code: using an LLM as a design partner and deciding where a model belongs in a product and where deterministic logic should stay in charge. That lesson turned out to be the same one I kept meeting in the technical labs, for example keeping the timetable and reminders out of the LLM in Lab 02, and keeping credentials and the source of truth out of the agent in Lab 06.

## What was hardest

The hardest parts were rarely the core idea; they were the engineering reality around it. In Lab 03 the challenge was keeping the model tiny enough to train on CPU in a minute while still learning real structure. In Lab 04 it was honest limitation: my machine has no CUDA GPU and the environment even deadlocked loading the model, so the right thing to do was guard the GPU-only cells and not fabricate a loss curve. In Lab 05 the interesting difficulty was that my evaluation metric saturated, Recall@5 was 1.0 for both systems, which taught me that a metric that cannot separate two systems is not telling me anything, and that MRR and latency were the real story. In Lab 06 the friction was platform details (macOS Accessibility permissions, OAuth) rather than the agent loop itself.

## What I would build next

I would combine the last three labs into one coherent assistant: a RAG-grounded agent, fine-tuned on the domain's own style and tone, with memory and a small set of real tools, evaluated properly on a larger and noisier corpus with harder metrics such as Recall@1 and faithfulness checks. I would also take the reliability lessons more seriously from the start: measure before claiming an improvement, keep the model out of the source of truth, and never commit a secret.

Overall the module changed how I think about LLMs. I no longer see them as a single magic box, but as one component that you can train, ground, or equip with tools depending on the problem, and the skill is choosing the right one and knowing its trade-offs.
