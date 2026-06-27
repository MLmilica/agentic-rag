# Agentic RAG

An agentic Retrieval-Augmented Generation (RAG) application built with **LangChain** and **LangGraph**. The system routes user questions, retrieves relevant documents, grades their quality, optionally falls back to web search, and generates answers with self-correction loops.

Based on Lilian Weng's blog posts about agents, prompt engineering, and LLM attacks.

## Features

- **Adaptive routing** — sends questions to the vector store or Tavily web search
- **Document grading** — filters irrelevant retrieved documents before generation
- **Hallucination check** — verifies the answer is grounded in retrieved facts
- **Answer grading** — checks whether the generation actually addresses the question
- **Self-correction loop** — retries generation or expands context via web search when needed

## Architecture

```
                    ┌─────────────┐
                    │   question  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   router    │
                    └──┬───────┬──┘
           vectorstore │       │ websearch
                ┌─────▼──┐  ┌─▼──────────┐
                │retrieve│  │ web_search │
                └─────┬──┘  └─────┬──────┘
                      │           │
                ┌─────▼──┐        │
                │ grade  │        │
                │  docs  │        │
                └─────┬──┘        │
                      │           │
                ┌─────▼───────────▼──┐
                │     generate       │
                └─────────┬──────────┘
                          │
              ┌───────────▼────────────┐
              │ hallucination + answer │
              │        grader          │
              └───┬────────┬───────┬───┘
            retry │   END  │       │ websearch
                  └────────┘       └──────► generate
```

Running `graph/graph.py` generates a visual diagram at `graph.png`.

## Project structure

```
agentic-rag/
├── main.py                 # Entry point
├── ingestion.py            # Load web docs, build Chroma vector store
├── graph/
│   ├── graph.py            # LangGraph workflow definition
│   ├── state.py            # GraphState (question, documents, generation, web_search)
│   ├── consts.py           # Node name constants
│   ├── nodes/              # Graph nodes (retrieve, grade, generate, web_search)
│   └── chains/             # LLM chains (graders, router, generation)
│       └── tests/          # Chain unit tests
└── .chroma/                # Local vector store (gitignored)
```

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Tavily API key

## Setup

1. Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd agentic-rag
uv sync
```

2. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
USER_AGENT=agentic-rag/1.0
```

3. Build the vector store (runs automatically on first import, or explicitly):

```bash
uv run python ingestion.py
```

This loads blog posts from Lilian Weng's site, splits them into chunks, and persists embeddings to `.chroma/`.

## Usage

Run the agent with a question:

```bash
uv run python main.py
```

Or invoke the graph programmatically:

```python
from graph.graph import app

result = app.invoke({"question": "What is agent memory?"})
print(result)
```

Try routing to web search with an out-of-domain question:

```python
result = app.invoke({"question": "how to make a pizza?"})
```

## Tests

Run all chain tests:

```bash
uv run pytest graph/chains/tests/ -s -v
```

Run a single test:

```bash
uv run pytest graph/chains/tests/test_chains.py::test_router_to_vectorstore -s -v
```

## Graph state

The workflow shares a single state object across nodes:

| Key          | Description                                      |
|--------------|--------------------------------------------------|
| `question`   | User question                                    |
| `documents`  | Retrieved or web-searched documents              |
| `generation` | LLM-generated answer                             |
| `web_search` | Flag indicating whether web search is needed   |

Each node returns a partial update; LangGraph merges it into the existing state.

## Tech stack

- **LangGraph** — agent workflow orchestration
- **LangChain** — LLM chains, prompts, document loaders
- **Chroma** — local vector store
- **OpenAI** — chat model and embeddings
- **Tavily** — web search
- **pytest** — testing
