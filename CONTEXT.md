# Personal Mirror

> **An AI-assisted instrument for personal introspection.**

## 1. Context

Personal Mirror is an experimental Proof of Concept (POC) for exploring whether AI can help a person observe, explore, and understand their own thoughts over time.

The core idea is **not** to build:

* a virtual psychologist;
* a mental-health diagnostic system;
* another generic note-taking application;
* a traditional "second brain";
* a chatbot with a long conversation history.

Instead, the goal is to build something closer to a **personal mirror**.

The user continuously produces thoughts, ideas, reflections, decisions, observations, and experiences. These can be written directly, imported from other sources, or eventually transcribed from audio.

The system should progressively construct a structured representation of those thoughts and make it possible to explore that representation.

For example:

> "What ideas keep appearing in my thoughts?"

> "What tensions or conflicts appear repeatedly?"

> "How has my thinking about work changed over the last six months?"

> "What concepts seem to be connected even though I never explicitly connected them?"

> "What beliefs or claims have changed over time?"

> "Show me the evidence behind this observation."

The system should **reflect what can be observed in the user's material**, rather than claim to know who the user "really is."

---

# 2. Core Concept

The central concept is:

> **A personal mirror assisted by AI: a system that builds a navigable, temporal, evidence-backed representation of a person's expressed thoughts and allows the person to explore that representation.**

The important distinction is between a normal AI conversation and Personal Mirror.

### Traditional AI conversation

```text
User thought
     |
     v
    LLM
     |
     v
Response
```

### Personal Mirror

```text
                     User material
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           Notes         Audio       Imported data
             |             |             |
             +-------------+-------------+
                           |
                           v
                  Knowledge extraction
                           |
             +-------------+-------------+
             |                           |
             v                           v
       Cognitive graph             Embeddings
             |                           |
             +-------------+-------------+
                           |
                           v
                    Personal model
                           |
                           v
                    Retrieval / LLM
                           |
                           v
                       Reflection
```

The graph is not intended to represent "the user's mind" as an objective truth.

It represents:

> **what can be observed and inferred from the user's expressed material.**

---

# 3. Why a Graph?

Embeddings and vector search are useful, but they represent semantic similarity rather than explicit relationships.

For example, embeddings can help answer:

> "Which notes are semantically similar to this thought?"

A graph can represent:

```text
AUTONOMY
    |
    | related to
    v
WORK
    |
    | creates concern about
    v
STABILITY
```

The project should therefore experiment with both representations.

## Vector representation

```text
Document
   |
   v
Embedding
   |
   v
Vector store
```

Useful for:

* semantic similarity;
* finding related notes;
* retrieving relevant context;
* fuzzy search.

## Graph representation

```text
Document
   |
   +---- mentions ----> Concept
   |
   +---- contains ----> Claim
                         |
                         +---- relates to ----> Concept
                         |
                         +---- contradicts ----> Claim
```

Useful for:

* explicit relationships;
* traversing concepts;
* identifying communities;
* temporal relationships;
* contradictions;
* evidence;
* reasoning over structured relationships.

The POC should **not assume that one representation replaces the other**.

---

# 4. Important Conceptual Principle

There is probably no single "correct graph."

Different questions may require different information.

For example:

| Question                           | Potential representation      |
| ---------------------------------- | ----------------------------- |
| What topics do I think about?      | Topics / concepts             |
| What things are important to me?   | Concepts + claims             |
| What contradictions appear?        | Claims + relationships + time |
| How did an idea change?            | Claims + temporal information |
| What thoughts are similar?         | Embeddings                    |
| What concepts are connected?       | Knowledge graph               |
| What ideas keep recurring?         | Graph + frequency + time      |
| What caused something?             | Causal relationships          |
| What emotional associations exist? | Sentiment/emotion metadata    |

The system should therefore be designed to **experiment with different extraction strategies**.

Do not over-engineer the ontology before observing real data.

---

# 5. Initial Data Model

The initial model should remain intentionally small.

## Document

Represents the original user material.

```text
Document
- id
- content
- created_at
- source
```

Possible future sources:

* Markdown
* plain text
* audio transcription
* ChatGPT exports
* WhatsApp
* Telegram
* other imported material

The original document must always be preserved.

---

## Concept

An abstract concept identified in the material.

Examples:

```text
autonomy
stability
creativity
money
learning
work
freedom
```

```text
Concept
- id
- name
```

---

## Entity

A concrete identifiable thing.

Examples:

```text
Company X
La Falda
Project Y
Person Z
```

```text
Entity
- id
- name
- type
```

---

## Claim

An explicit statement expressed by the user.

Example:

> "I want more autonomy in my work."

```text
Claim
- id
- text
- type
- timestamp
```

Possible claim types:

* belief
* desire
* concern
* observation
* decision
* preference
* hypothesis

Do not assume these types are definitive psychological categories. They are simply descriptions of expressed statements.

---

# 6. Initial Relationships

Start with a very small set.

```text
MENTIONS
CONTAINS
ABOUT
RELATES_TO
SUPPORTS
CONTRADICTS
EXPRESSES
```

Example:

```text
Document
    |
    +-- MENTIONS --> Concept(work)
    |
    +-- CONTAINS --> Claim("I want more autonomy")
                             |
                             +-- ABOUT --> Concept(autonomy)
```

Relationships may later be expanded based on actual experiments.

Potential future relationships:

```text
CAUSES
ASSOCIATED_WITH
EVOLVED_INTO
DEPENDS_ON
CONFLICTS_WITH
SIMILAR_TO
PRECEDES
```

Do not implement these unless the POC demonstrates a need for them.

---

# 7. Evidence and Provenance

This is a core design requirement.

The system must be able to answer:

> "Why does the system think this?"

For example:

```text
Concept: autonomy

Evidence:
- Document 183
- Document 213
- Document 271
```

The graph should therefore maintain links back to the original material.

The system must distinguish between:

### Observed

> "The concept 'autonomy' appears in 17 documents."

### Extracted

> "The system identified autonomy as a concept."

### Inferred

> "Autonomy appears to be associated with work."

These are different levels of certainty.

The LLM must never silently turn an inference into a fact.

---

# 8. LLM Extraction

The first important AI component is a structured extraction pipeline.

Input:

```text
Document
```

Output:

```json
{
  "concepts": [],
  "entities": [],
  "claims": [],
  "relationships": []
}
```

Example input:

> "I'm thinking about leaving my job. I like how much I'm learning, but I feel like I'm losing freedom. At the same time I'm worried about losing financial stability."

Potential output:

```json
{
  "concepts": [
    "work",
    "learning",
    "freedom",
    "financial stability"
  ],
  "claims": [
    {
      "text": "I am considering leaving my job",
      "type": "desire"
    },
    {
      "text": "I am learning a lot from my job",
      "type": "observation"
    },
    {
      "text": "I feel like I am losing freedom",
      "type": "concern"
    },
    {
      "text": "I am worried about losing financial stability",
      "type": "concern"
    }
  ],
  "relationships": []
}
```

The exact extraction schema should remain open to experimentation.

---

# 9. Sentiment and Emotion

Sentiment/emotion should **not automatically define the graph**.

They may instead be properties attached to documents, claims, or relationships.

Example:

```text
Claim
  |
  +-- sentiment: negative
  +-- confidence: 0.82
```

This is preferable to creating an entire emotional graph before knowing whether it is useful.

Possible future attributes:

```text
sentiment
emotion
intensity
confidence
```

These should only be introduced after experimentation.

---

# 10. Embeddings

Documents and/or claims should also have embeddings.

Conceptually:

```text
Document
    |
    v
Embedding model
    |
    v
[0.12, -0.43, ...]
```

Embeddings should be used for semantic retrieval.

Example:

> "Show me thoughts similar to this one."

This is separate from graph traversal.

The POC should eventually compare:

```text
Vector retrieval
```

against:

```text
Graph retrieval
```

and potentially:

```text
Hybrid retrieval
```

---

# 11. Retrieval

A future query could look like:

> "What recurring tensions appear in my thoughts about work?"

The system may retrieve information through:

```text
                 Query
                   |
          +--------+--------+
          |                 |
          v                 v
   Vector retrieval    Graph retrieval
          |                 |
          +--------+--------+
                   |
                   v
                Context
                   |
                   v
                  LLM
                   |
                   v
              Reflection
```

The response should preferably contain evidence.

Example:

```text
I found a recurring tension between autonomy and stability.

This appears in:
- note 183
- note 213
- note 271

The relationship became more frequent during the last three months.
```

The system should avoid presenting speculative psychological interpretations as facts.

---

# 12. Initial Technology Stack

The initial POC should use:

```text
Python
FastAPI
Pydantic
Neo4j
neo4j-graphrag
OpenAI API
Docker Compose
pytest
```

Optional:

```text
Ollama
```

Ollama can later be used to experiment with local models.

The initial implementation should prefer an API-based LLM to minimize infrastructure complexity.

---

# 13. LlamaIndex

LlamaIndex should **not be required for the first implementation**.

It is worth evaluating later as an abstraction layer.

Possible future comparison:

```text
Neo4j + neo4j-graphrag
```

versus:

```text
LlamaIndex + Neo4j
```

The purpose is educational and architectural:

* How much abstraction does LlamaIndex provide?
* What does it hide?
* What does it simplify?
* What control is lost?
* How does graph retrieval differ?

Do not introduce LlamaIndex merely because it is popular.

---

# 14. Local Infrastructure

For the POC, everything except the LLM can run locally.

Recommended setup:

```text
Docker Compose
    |
    +-- Neo4j
    |
    +-- Backend
```

The developer machine may also run:

```text
Ollama
    |
    +-- local LLM
    |
    +-- local embedding model
```

A GPU is not required for Neo4j or the backend.

The development machine has an NVIDIA RTX 2060 with approximately 6 GB VRAM.

This is sufficient for experimentation with small quantized local models, but the first POC should use an API-based LLM.

---

# 15. Input Strategy

Do not start with a mobile application.

The first input format should be simple:

```text
data/
    notes/
        001.md
        002.md
        003.md
```

This allows fast experimentation.

Later inputs may include:

```text
Markdown
TXT
Audio
ChatGPT exports
WhatsApp
Telegram
```

Audio should eventually follow:

```text
Audio
  |
  v
Speech-to-text
  |
  v
Document
  |
  v
Knowledge extraction
```

---

# 16. Mobile Application

The mobile app is a future layer, not part of the initial POC.

Eventually it could provide:

```text
Write
Record audio
Ask
Explore
```

Architecture:

```text
Mobile app
    |
   HTTPS
    |
FastAPI
    |
Personal Mirror backend
```

The mobile device should not be responsible for running the main LLM.

A PWA is acceptable for the first mobile experiment.

---

# 17. Suggested Repository Structure

Start with a clean but intentionally simple architecture:

```text
personal-mirror/
│
├── src/
│   ├── ingestion/
│   ├── extraction/
│   ├── graph/
│   ├── embeddings/
│   └── query/
│
├── data/
│   └── notes/
│
├── tests/
│
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

Avoid premature abstraction.

The architecture should be easy to change while the conceptual model is still being discovered.

---

# 18. Development Phases

## Phase 1 — Foundation

Build:

* Python project
* dependency management
* Docker Compose
* Neo4j
* configuration
* logging
* basic tests

No LLM yet.

---

## Phase 2 — Ingestion

Implement:

```text
Markdown/TXT
    |
    v
Document
```

Requirements:

* preserve original content;
* assign stable IDs;
* preserve timestamps where available;
* preserve source metadata.

---

## Phase 3 — Knowledge Extraction

Implement:

```text
Document
    |
    v
LLM
    |
    v
Concepts
Entities
Claims
Relationships
```

Use structured output.

This is expected to be the most experimental part of the system.

---

## Phase 4 — Graph Persistence

Implement:

```text
Extracted knowledge
        |
        v
     Neo4j
```

Add basic Cypher queries.

The developer should be able to inspect the resulting graph manually.

---

## Phase 5 — Embeddings

Implement:

```text
Documents / Claims
        |
        v
Embeddings
        |
        v
Vector retrieval
```

The system should support a basic semantic search.

---

## Phase 6 — Reflection

Implement:

```python
answer(question: str)
```

Combine:

* graph retrieval;
* vector retrieval;
* original document evidence;
* LLM generation.

The response should clearly distinguish:

* evidence;
* extracted relationships;
* inference.

---

## Phase 7 — Experiments

Create a set of questions such as:

```text
What topics appear repeatedly?

What concerns appear repeatedly?

What tensions appear in my thoughts?

What ideas have changed over time?

What claims seem contradictory?

What projects or ideas keep coming back?

What concepts appear to be connected?

What has disappeared from my thoughts?

What did I seem to care about more six months ago?

Why does the system think this concept is important?
```

Use the results to improve the data model.

---

# 19. Evaluation Philosophy

This is an exploratory POC, not a production system.

The most important question is not:

> "Does the graph look technically correct?"

The important questions are:

> **Does it reflect something meaningful about the user's own material?**

> **Does it reveal connections the user did not explicitly notice?**

> **Does it help the user ask better questions?**

> **Does it provide useful evidence?**

> **Does it avoid inventing patterns?**

A successful result may be a surprising insight.

A successful result may also be discovering that a particular representation is useless.

Both outcomes are valuable.

---

# 20. Important Non-Goals

Do not build these in the initial POC:

* mental-health diagnosis;
* therapy workflows;
* psychological profiling;
* personality scoring;
* medical advice;
* autonomous psychological conclusions;
* recommendation engine;
* social network;
* complex mobile UI;
* authentication;
* multi-user architecture;
* cloud deployment;
* Kubernetes;
* microservices;
* production-grade scalability.

The goal is to understand the core mechanism.

---

# 21. Guiding Principle

The project should remain **user-controlled and evidence-based**.

The AI should not tell the user:

> "This is who you are."

It should say things closer to:

> "This idea appears frequently in your notes."

> "These two claims seem to conflict."

> "These concepts often appear together."

> "Your notes contain evidence of a change in this idea."

> "This is an interpretation based on these documents."

The user should be able to inspect, reject, or correct the system's interpretation.

---

# 22. First Technical Milestone

The first meaningful milestone is deliberately small:

Given approximately **20–50 real personal notes**, the system should:

1. ingest the notes;
2. extract concepts, entities, claims, and relationships;
3. store them in Neo4j;
4. preserve evidence links to the original notes;
5. generate embeddings;
6. support semantic search;
7. answer a small number of reflective questions using graph + vector retrieval;
8. expose the evidence used to generate each observation.

Only after this works should the project expand.

---

# 23. Future Directions

Potential future experiments:

### Temporal model

Track how concepts and claims evolve.

```text
Claim A
   |
   | evolved into
   v
Claim B
```

### Contradiction detection

Identify claims that may conflict.

### Community detection

Discover clusters of concepts.

### Emotional associations

Attach sentiment/emotion to claims or concepts.

### Automatic topic discovery

Identify recurring areas without predefined categories.

### Multi-source ingestion

Import information from multiple personal sources.

### Audio-first interaction

Make speaking to the mirror as easy as writing.

### Interactive graph exploration

Allow the user to visually explore their personal knowledge graph.

### Local-first privacy

Experiment with running the entire pipeline locally using Ollama and local embeddings.

---

# 24. First Agent Tasks

The implementation should be developed incrementally.

Recommended agent sequence:

```text
Agent 1
Foundation
    ↓
Agent 2
Ingestion
    ↓
Agent 3
Knowledge extraction
    ↓
Agent 4
Neo4j persistence
    ↓
Agent 5
Embeddings
    ↓
Agent 6
Query / reflection
    ↓
Agent 7
Experiments
    ↓
Agent 8
Mobile/API
```

Each agent should modify the existing project rather than independently redesigning the architecture.

Before introducing a new abstraction or dependency, prefer the simplest implementation that supports the current experiment.

---

# 25. Philosophy of the POC

This project is intentionally exploratory.

We do **not** know yet:

* what the ideal graph schema is;
* which concepts are useful;
* whether sentiment belongs in the graph;
* whether topics should be nodes;
* which relationships are meaningful;
* whether GraphRAG is actually the best approach;
* how much value vector retrieval adds;
* how much value graph retrieval adds;
* whether users benefit more from visualization or conversation.

The POC exists to answer those questions.

Therefore:

> **Do not optimize for architectural completeness. Optimize for learning.**

The most valuable output of the first version is not the code.

It is discovering **what kind of representation of personal thought actually produces useful reflection.**
