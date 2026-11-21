# ContextFlow — Agentic AI & Workflow Automation Platform

**A locally hosted AI-powered document intelligence and workflow automation application built with Python, Ollama and Streamlit.**

ContextFlow helps users organise information, retrieve relevant knowledge and turn unstructured documents into actionable tasks. It combines retrieval-augmented generation (RAG), semantic search and a tool-using AI agent to support multi-step workflows through natural language.

The application runs locally using open-source language models, without requiring paid AI APIs.

## Key Features

### AI Agent & Tool Calling
- **Goal-directed execution:** Accepts natural-language objectives and selects tools based on the task.
- **Dynamic tool selection:** Uses an LLM to choose between document search, task extraction, task retrieval and troubleshooting.
- **Multi-step workflows:** Executes a bounded reasoning and observation loop, using tool results to determine subsequent actions.
- **Structured tool execution:** Validates JSON tool requests and restricts execution to approved functions.
- **Human-in-the-loop approval:** Requires user confirmation before proposed tasks are saved.

### Document Intelligence & RAG
- Extracts and indexes text from uploaded documents.
- Retrieves relevant passages using TF-IDF and optional hybrid semantic search.
- Generates document-grounded answers with source references.
- Identifies relevant requirements, deadlines and actionable information.
- Supports local embeddings for meaning-based document retrieval.

### Workflow Automation & Productivity
- Extracts actionable tasks and deadlines from unstructured text.
- Maintains an SQLite-backed task workspace.
- Provides an IT troubleshooting assistant for common technical problems.
- Includes a reusable prompt library.
- Records agent execution history for inspection and troubleshooting.

### Evaluation & Reliability
- Automated tests covering agent behaviour, tool validation and workflow boundaries.
- Retrieval and task-extraction evaluation using a synthetic benchmark.
- Bounded agent execution to prevent uncontrolled tool loops.
- Read-only agent tools and explicit approval for database changes.
- Local processing to reduce dependence on external AI services.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| User Interface | Streamlit |
| Local AI | Ollama, Qwen 2.5 |
| AI Architecture | RAG, LLM Agents, Tool Calling, Prompt Engineering |
| Information Retrieval | TF-IDF, Semantic Embeddings, Hybrid Search |
| Database | SQLite |
| Data Processing | Scikit-learn, NumPy |
| Testing | Pytest |
| Model Integration | OpenAI-compatible local API |

---

## System Architecture

ContextFlow uses a modular architecture that separates the user interface, document processing, AI decision-making and workflow management.

```text
                  USER
                   |
                   v
             Streamlit UI
                app.py
                   |
                   v
             AI Agent
               agent.py
                   |
          Ollama / Qwen 2.5
                   |
            Tool Selection
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
    Search      Extract      Retrieve
   Documents     Tasks        Tasks
       |           |           |
       +-----------+-----------+
                   |
                   v
          Observe Tool Results
                   |
                   v
        Continue or Finish
                   |
                   v
           Human Approval
                   |
                   v
            SQLite Storage
```

The agent selects tools based on the objective and available observations rather than following a single predefined sequence.

Execution is limited to six tool steps, and only allowlisted functions can be called. The agent cannot execute arbitrary shell commands or autonomously perform external actions.

### Project Structure

```text
ContextFlow/
├── app.py
├── agent.py
├── core.py
├── workflows.py
├── evaluate.py
├── requirements.txt
├── run_windows.bat
├── README.md
├── .gitignore
├── sample_notes.txt
├── demo/
│   ├── meeting.txt
│   ├── requirements.txt
│   └── schedule.txt
└── tests/
    ├── test_agent.py
    ├── test_core.py
    └── test_workflows.py
```

**Module responsibilities**

- `app.py` — Streamlit interface, document management and task approval.
- `agent.py` — LLM-directed tool selection, execution loop, argument validation and audit logging.
- `core.py` — Document parsing, retrieval, database operations, Ollama integration and response validation.
- `workflows.py` — Deterministic task extraction and workflow evaluation.
- `evaluate.py` — Synthetic retrieval and extraction benchmark.
- `tests/` — Automated tests for core functionality, agent execution and workflow safeguards.

---

## Installation & Setup

### Prerequisites

- Python
- Ollama
- Windows (for the included launcher)

### 1. Install Ollama

Download Ollama from [ollama.com](https://ollama.com/download).

### 2. Download the local AI models

Open PowerShell and run:

```powershell
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

The models serve different purposes:

- **Qwen 2.5 7B:** Natural-language reasoning, tool selection and response generation.
- **Nomic Embed Text:** Semantic document retrieval.

### 3. Run ContextFlow

Download or clone the repository and open the project folder.

On Windows, double-click:

```text
run_windows.bat
```

The application will launch in your browser, typically at:

```text
http://localhost:8501
```

Alternatively, install the dependencies manually and run:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

### Optional: Smaller Language Model

For systems with limited memory:

```powershell
ollama pull qwen2.5:3b
```

Then configure the model in PowerShell before launching:

```powershell
$env:CHAT_MODEL="qwen2.5:3b"
.\run_windows.bat
```

---

## Example: Multi-Step AI Agent Workflow

**Objective:**

> Review the project documents, identify conflicting technical requirements, extract upcoming deadlines and propose actionable tasks with source references.

### Agent Execution

A demonstrated execution trace included:

```text
Step 1: search
Step 2: extract_tasks
Step 3: search
Step 4: extract_tasks
```

The agent retrieved relevant information, extracted tasks and generated a response referencing the source documents.

### Example Results

| Identified Task | Deadline |
|---|---|
| Resolve conflicting prototype current limits (300 mA vs 350 mA) | Not specified |
| Submit calibration report | 2026-11-30 |
| Review safety checklist | 2026-12-02 |
| Prepare design review slides | 2026-12-03 |

The agent identified conflicting values across separate documents and proposed tasks based on the retrieved information.

Task proposals remain subject to user approval before being stored.

*This example uses fictional demonstration documents.*

---

## Testing & Evaluation

Automated tests cover:

- Agent tool selection and execution.
- Rejection of invalid tool requests.
- Tool argument and citation validation.
- Agent execution limits.
- Task approval boundaries.
- Core document and workflow functionality.

Run the test suite from the project directory:

```powershell
python -m pytest -q
```

**Build-time test result:** 9 automated tests passed.

A small synthetic benchmark is included for retrieval and task extraction. Its results are intended for development validation rather than generalised accuracy claims.

Local Ollama operation has also been demonstrated through document analysis, task extraction and multi-step agent execution. Broader reliability testing across diverse documents and objectives remains ongoing.

---

## Safety & Design Considerations

ContextFlow uses several safeguards to support predictable AI-assisted workflows.

- **Local inference:** LLM requests are processed through a locally hosted Ollama endpoint.
- **Restricted tools:** The agent can only execute explicitly supported functions.
- **Execution limits:** Agent runs stop after a maximum of six tool steps.
- **Human approval:** Proposed tasks require confirmation before being saved.
- **Auditing:** Tool execution history is recorded for inspection.
- **Source references:** Retrieved document passages can be linked to generated answers.

### Current Limitations

- The agent does not execute shell commands, modify external systems or independently schedule future actions.
- IT troubleshooting provides general guidance rather than automated diagnosis or ticket resolution.
- The prompt library stores reusable prompts but does not automatically optimise them.
- Agent context is maintained within individual runs; persistent audit logs are not automatically used as long-term memory.
- PDF extraction requires machine-readable text.
- Source references and validation checks do not guarantee factual correctness.
- Local SQLite storage is not encrypted or authenticated; sensitive documents should not be uploaded.
- Audit logs may contain retrieved document content.
- The application is designed for local use rather than production-scale, multi-user deployment.

The agent uses validated JSON-based tool dispatch rather than native model function-calling APIs.

---

## Future Improvements

Potential extensions include:

- Document selection and filtering for targeted retrieval.
- Improved agent planning and reduction of redundant tool calls.
- Persistent conversational memory.
- Automated IT ticket classification and escalation.
- Integration with external workflow platforms.
- Expanded retrieval and agent evaluation datasets.
- Authentication, encrypted storage and stronger data isolation.
- Improved interface design and deployment options.

---

## Development Approach

ContextFlow was developed as a personal project exploring practical applications of generative AI, information retrieval and workflow automation.

AI-assisted development tools were used during implementation, alongside testing, debugging and iterative refinement.

The project focuses on integrating existing AI models into a useful software application rather than training a language model from scratch.

**Project focus:** Agentic AI · Generative AI · RAG · Workflow Automation · Python Software Engineering
