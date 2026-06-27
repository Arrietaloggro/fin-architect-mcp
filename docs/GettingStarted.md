# Getting Started

This guide walks you through installing, running, and using FIN Architect MCP for the first time. By the end you will have a running MCP server and a connected client ready to analyze knowledge articles and conversation guidelines.

---

## Prerequisites

### Python

FIN Architect MCP requires **Python 3.10 or later**. Verify your version:

```bash
python --version
```

If the output is below `3.10`, install a compatible version from [python.org](https://www.python.org/downloads/) or via your system package manager.

### Git

You need Git to clone the repository:

```bash
git --version
```

### MCP-compatible client

The server communicates over the Model Context Protocol (MCP) using Server-Sent Events (SSE). You need a client that supports MCP over SSE transport. The two primary options:

- **Claude Desktop** — Anthropic's desktop application
- **Claude Code** — Anthropic's CLI tool (`claude` command)

Either client can connect to a locally running instance of this server.

### Dependencies

The server depends on four packages (defined in `requirements.txt`):

```
mcp[cli]>=1.3.0      # MCP server framework (FastMCP + SSE transport)
uvicorn>=0.29.0      # ASGI server
starlette>=0.36.0    # HTTP routing layer
httpx>=0.27.0        # HTTP client
```

These are installed in the [Installation](#installation) step below.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/arrietaloggro/fin-architect-mcp.git
cd fin-architect-mcp
```

### 2. Create a virtual environment

Creating a virtual environment isolates the project's dependencies from your system Python installation.

```bash
python -m venv .venv
```

Activate the environment:

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

After activation your prompt should show `(.venv)` as a prefix.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Verify the installation succeeded by checking that the `mcp` package is available:

```bash
python -c "import mcp; print('mcp OK')"
```

Expected output: `mcp OK`

---

## Running the Server

Start the MCP server with:

```bash
python server.py
```

The server starts on port `8000` by default. If the environment variable `PORT` is set, it uses that value instead:

```bash
PORT=9000 python server.py
```

### Expected output on successful start

```
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Verify the server is running

In a separate terminal, send a health check request:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{"status": "ok", "service": "fin-architect-mcp"}
```

### SSE endpoint

The MCP protocol is served at:

```
http://localhost:8000/sse
```

This is the URL your MCP client will connect to.

---

## Connecting a Client

### Claude Code (CLI)

Add the server to your Claude Code MCP configuration. Edit or create the MCP configuration file for your project (`.claude/mcp.json` or the global Claude Code settings):

```json
{
  "mcpServers": {
    "fin-architect-mcp": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Restart Claude Code or reload the MCP server list. The 15 tools provided by FIN Architect MCP will appear in your session.

### Claude Desktop

Open Claude Desktop settings and navigate to the MCP servers section. Add a new server entry:

- **Name:** `fin-architect-mcp`
- **URL:** `http://localhost:8000/sse`
- **Transport:** SSE

Save the configuration and reconnect. The tools will be listed as available in the conversation.

### What to expect after connecting

Once connected, your MCP client has access to the following 15 tools:

| Tool | Purpose |
|------|---------|
| `audit_guideline` | Audit a single conversation guideline |
| `optimize_guideline` | Generate rewrite recommendations |
| `classify_guideline` | Classify intent, risk, and priority |
| `detect_conflicts` | Find conflicts across a guideline set |
| `score_guideline` | Score against 10 criteria |
| `simulate_fin` | Simulate FIN's response to a guideline |
| `generate_guideline` | Generate a structured guideline template |
| `extract_guidelines` | Extract guidelines from conversation logs |
| `audit_knowledge` | Full KDE audit of a knowledge article |
| `optimize_article` | Prioritized optimization plan for an article |
| `knowledge_review` | Bulk coverage and debt analysis |
| `repository_review` | Full repository health and readiness |
| `recommend_improvements` | ROI-ranked improvement backlog |
| `fin_dashboard` | Unified executive health report |
| `architect_review` | Full end-to-end analysis pipeline |

---

## Repository Structure

```
fin-architect-mcp/
├── decision_engine.py     # Analytical core — all scoring, detection, and
│                          # classification logic. 34 functions, 45 constants.
│                          # Never called by clients directly.
│
├── server.py              # MCP server — 15 tools exposed via FastMCP.
│                          # All analytical calls delegate to decision_engine.py.
│
├── main.py                # FastAPI health endpoint (separate from MCP server).
│                          # Returns {"name": "Fin Architect MCP", "status": "running"}.
│
├── requirements.txt       # Python dependencies.
│
├── Procfile               # Process definition for deployment (web: python server.py).
│
├── railway.toml           # Railway deployment configuration.
│
└── docs/
    ├── GettingStarted.md  # This file.
    ├── Architecture.md    # Full system architecture documentation.
    ├── DecisionEngine.md  # Complete Decision Engine reference.
    └── PROJECT_CONTEXT.md # Architecture context and sprint history.
```

**Key relationship:** `server.py` imports `decision_engine.py` as `_de`. Every analytical function (scoring, detection, similarity, classification, ranking) lives in `decision_engine.py`. The tools in `server.py` call `_de.*` functions and format the results for MCP clients. If you are reading the code and want to understand how a score is computed, look in `decision_engine.py`, not in the tool definition.

---

## First Tool

`architect_review` is the orchestrator — the single tool that runs the full analysis pipeline and returns a complete architectural diagnosis. It is the right starting point when you want a full picture of a product's knowledge and guideline health.

### Tool signature

```
architect_review(
    product: str,           # Product name being analyzed
    conversations: list,    # List of conversation strings from Intercom
    current_guidelines: list = [],  # Existing guidelines for the product (optional)
    objective: str = ""             # Analysis focus or context (optional)
) -> str
```

### What happens when you call it

1. The tool receives the conversation list and any existing guidelines.
2. It extracts guideline candidates from the conversations using Jaccard-based clustering.
3. It audits each guideline candidate and scores it against the guideline scoring framework.
4. It detects conflicts across the guideline set.
5. It audits any knowledge articles referenced in the conversations.
6. It computes repository-level health metrics.
7. It returns a consolidated report: health scores, blocker list, conflict map, coverage gaps, and a deployment readiness decision.

### Example call (in a Claude session with the server connected)

```
Use architect_review with:
- product: "Facturación"
- conversations: [
    "El cliente indica que la factura no se generó. Ya revisó el artículo y siguió los pasos pero el error persiste.",
    "Usuario reporta que el CUFE no aparece en el PDF. FIN ofreció la misma solución dos veces sin resolver."
  ]
- objective: "Identify coverage gaps and guideline conflicts for the billing module"
```

The tool returns a structured report with:
- Global health score for the product
- List of detected guideline patterns with names and priorities
- Any detected conflicts between guidelines
- Knowledge article health assessment
- Deployment readiness decision (READY / READY WITH RECOMMENDATIONS / NOT READY / BLOCKED)
- Specific recommendations ranked by ROI

---

## Typical Workflow

A complete analysis of a product's conversational support architecture follows this sequence:

```
1. Intercom Conversations
   │  Collect raw conversation exports for the product.
   │  These are the input to the entire pipeline.
   ▼

2. extract_guidelines
   │  Feed conversations into extract_guidelines to cluster
   │  semantically similar turns into candidate guidelines.
   │  Output: a set of named guideline candidates with
   │  priority scores and template suggestions.
   ▼

3. Guideline analysis (for each candidate)
   │  classify_guideline  → intent, risk level, priority
   │  detect_conflicts    → conflicts with existing guidelines
   │  audit_guideline     → compliance and ambiguity issues
   │  optimize_guideline  → specific rewrite recommendations
   │  score_guideline     → 10-criterion numeric score
   │  simulate_fin        → predicted FIN behavior and escalation risk
   │  generate_guideline  → final deployable template
   ▼

4. Knowledge article analysis
   │  audit_knowledge     → full KDE score for each article (12 criteria)
   │  optimize_article    → prioritized action plan per article
   │  knowledge_review    → coverage, debt, and duplicates across all articles
   ▼

5. repository_review
   │  Evaluate the entire repository as a system.
   │  Output: global health score, deployment readiness,
   │  knowledge debt level, open blockers.
   ▼

6. recommend_improvements
   │  Surface the highest-ROI improvements from the repository review.
   │  Output: ranked backlog of specific improvements.
   ▼

7. fin_dashboard
      Aggregate all upstream outputs into a single executive report.
      Output: traffic-light health indicators, global score,
      debt classification, and deployment decision.
```

For a single-call version of steps 1–7, use `architect_review` with the full conversation set and any existing guidelines.

---

## Troubleshooting

### Server does not start

**Symptom:** Command exits immediately or shows an import error.

**Check 1 — Virtual environment is not activated.**
```bash
# Activate and retry
source .venv/bin/activate
python server.py
```

**Check 2 — Dependencies are not installed.**
```bash
pip install -r requirements.txt
```

**Check 3 — Port is already in use.**
```
ERROR:    [Errno 98] Address already in use
```
Either stop the process using port 8000, or start the server on a different port:
```bash
PORT=8001 python server.py
```

**Check 4 — Python version is below 3.10.**
```bash
python --version
```
If below 3.10, upgrade Python and recreate the virtual environment.

---

### Import error on startup

**Symptom:**
```
ModuleNotFoundError: No module named 'mcp'
```

The virtual environment is active but dependencies were not installed, or were installed in a different environment.

```bash
pip install -r requirements.txt
python -c "import mcp; import uvicorn; import starlette; print('All OK')"
```

---

### MCP client does not connect

**Symptom:** Claude Code or Claude Desktop shows the server as unavailable or the tools do not appear.

**Check 1 — Server is running.**
```bash
curl http://localhost:8000/
```
If this returns a connection error, the server is not running.

**Check 2 — SSE URL is correct.**
The SSE endpoint is `http://localhost:8000/sse`, not `http://localhost:8000/`. Verify the URL in your client configuration.

**Check 3 — Port mismatch.**
If you started the server on a custom port (e.g., `PORT=8001`), update the client configuration URL to match:
```
http://localhost:8001/sse
```

**Check 4 — Firewall or network restriction.**
If running the server inside a container or on a remote machine, ensure the port is accessible from where the client is running.

---

### A tool returns an unexpected result or error

**Symptom:** A tool call returns an error message or an empty result.

**Check 1 — Input format.**
All list parameters (`conversations`, `current_guidelines`) must be lists of strings, not a single string. A common mistake is passing a newline-separated string instead of a list.

**Check 2 — Minimum input length.**
Most tools validate that the input text is not empty or trivially short. An article with fewer than 20 characters will be rejected by `audit_knowledge`.

**Check 3 — Server logs.**
The uvicorn output in the terminal where `python server.py` is running shows any Python exceptions that occur during tool execution. Check there for the full traceback.

---

## Best Practices

### Working with branches

All development should happen on a dedicated branch. Never push directly to `main` without review.

```bash
# Create a feature branch
git checkout -b feature/my-change

# After making changes, commit with a descriptive message
git add <specific-files>
git commit -m "describe what changed and why"

# Push to remote
git push -u origin feature/my-change
```

Keep `decision_engine.py` and `server.py` changes in separate commits when possible. Changes to the analytical core and changes to the tool interface are distinct concerns.

### Extending tools

If you need a new tool:

1. Add it to `server.py` using the `@mcp.tool()` decorator.
2. Implement the business logic by calling `_de.*` functions — do not implement analytical logic inline.
3. If the analysis you need does not exist in `decision_engine.py`, add it there first as a pure function.
4. Do not modify any existing tool's return structure or parameter names — this is a breaking change for clients.

If you need a new analytical function:

1. Add it to `decision_engine.py` in the appropriate section (Knowledge module lines 1–897, Guideline module lines 898–1264).
2. Define any new constants at the module level above the function.
3. Verify the function does not duplicate existing behavior before adding it.

### Maintaining the architecture

The central constraint of this project is that `decision_engine.py` is the sole source of truth for all analytical logic. This constraint must be actively maintained:

- **Do not define pattern lists inside tool functions.** If you find yourself writing `loop_patterns = [...]` inside a tool in `server.py`, that list belongs in `decision_engine.py`.
- **Do not inline thresholds.** If a tool checks `if similarity >= 0.70`, that `0.70` should be `_de.GUIDELINE_CLUSTER_THRESHOLD`.
- **Do not copy functions.** If two tools need Jaccard similarity, both call `_de.jaccard()`. There should never be two implementations of the same function in the codebase.
- **After any change to `decision_engine.py`, verify no duplication was introduced.** The root cause of the cleanup sprint (which removed 328 lines of accidentally duplicated code) was two concurrent writes to the same file that each appended the same block.

### Verifying a change did not break behavior

After modifying `decision_engine.py`, verify the server still starts and the import is clean:

```bash
python -c "import decision_engine; print('DE OK')"
python server.py &
sleep 2
curl http://localhost:8000/
kill %1
```

If the import succeeds and the health endpoint responds, the module is structurally sound. For deeper verification, call representative tools through a connected MCP client with known inputs and check that outputs match expected values.

---

*FIN Architect MCP v1.0.0 — Getting Started guide.*
