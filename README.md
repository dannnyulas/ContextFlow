# ContextFlow — Local AI Agent & Workflow Automation

Personal document workspace with a bounded, model-directed agent. Python, Streamlit, SQLite, TF-IDF, optional local embeddings and Ollama. No paid API required.

## Windows setup
Install Ollama, then run in PowerShell:
```powershell
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```
Extract this ZIP, open its folder and double-click run_windows.bat. Stop the older Streamlit instance first. To retain your previous documents and tasks, copy workspace.db from the old folder while both apps are stopped. For a smaller model use `ollama pull qwen2.5:3b` and set `$env:CHAT_MODEL='qwen2.5:3b'` before running ` .\run_windows.bat` in the same PowerShell.

## Demo
Load demo workspace. Open AI agent and enter: `Find the calibration requirements and dated actions, identify conflicting current limits, and propose tasks with source citations.` Inspect the tools and cited passages; approve tasks only after reviewing. Try an IT troubleshooting question. Prompt library stores reusable text to copy into the objective field. Search-only and local extraction still work without Ollama.

## Architecture
- app.py: interface and explicit task approval
- core.py: parsing, SQLite, lexical and optional hybrid retrieval, local model connection and response validation
- workflows.py: deterministic extraction baseline and workflow metrics
- agent.py: JSON tool dispatch, bounded observation loop, allowlisted read-only tools, argument validation, run audit
- evaluate.py: synthetic retrieval/extraction benchmark

The model chooses search, list_tasks, extract_tasks, troubleshoot or finish based on the objective and observations. The loop stops on a final response or six tool steps. IT tool provides a generic safety-oriented checklist, not automated diagnosis or ticket resolution. The model can supplement it with advice. No shell execution, external actions, autonomous scheduling or n8n integration. Proposed tasks are only written following user approval. Agent memory is within a run; logs persist, but are not automatically used as long-term memory. Audit records successful or step-limited runs; exceptions stop execution and are displayed. Prompt library is manual. Reports are text responses, not a dedicated report tool.

## Testing and limitations
Run `python -m pytest -q` from the project folder (or `.venv\Scripts\python.exe -m pytest -q`). Nine automated tests passed in the build environment, including scripted-model tool selection, invalid tools and citations, step limits and approval boundaries. Live Ollama and browser integration have not been verified here. The benchmark is a tiny synthetic fixture, not a general accuracy claim. Source ID checks do not guarantee factual accuracy. Local storage is not encrypted or authenticated; use non-sensitive documents. Audit logs include retrieved text. PDF extraction requires selectable text. The OpenAI Python library is used only as a client for the local Ollama-compatible endpoint. Agent decisions use JSON dispatch, not native function-calling API.

AI-assisted implementation: inspect, test and document your own contributions and measured results before presenting as portfolio work.
