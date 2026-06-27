# Contributing to FIN Architect MCP

Thank you for contributing to FIN Architect MCP. This guide covers the conventions, rules, and processes required to contribute correctly to this project. Read it in full before submitting a pull request.

---

## 1. Philosophy

Every contribution to FIN Architect MCP must be consistent with the following principles. These are not stylistic preferences — they are architectural constraints enforced across all 15 tools and the Decision Engine.

### Single Source of Truth

Every analytical function, threshold value, and pattern list exists in `decision_engine.py` and nowhere else. If you need Jaccard similarity in a new tool, you call `_de.jaccard()`. You do not write your own. If a constant does not exist in `decision_engine.py`, you add it there before using it anywhere else.

### Decision Engine First

Before writing any analytical logic in a tool, check whether `decision_engine.py` already provides it. Read `docs/DecisionEngine.md` before writing a new tool. The Decision Engine has 34 functions covering detection, scoring, classification, similarity, debt computation, coverage, ROI ranking, and status derivation. Most new tools will need nothing beyond what already exists.

### No Duplicated Logic

The root cause of three architecture sprints was logic that existed in multiple places. `audit_knowledge` had its own KDE scoring loop. `extract_guidelines` had its own Jaccard function. `optimize_article` had its own loop pattern list. All three were diverging silently. This must not happen again. If you find yourself writing a function that does something `decision_engine.py` already does, stop and call the existing function instead.

### Pure Functions

All functions in `decision_engine.py` are pure: same inputs, same outputs, no side effects, no I/O, no global mutation. New functions added to `decision_engine.py` must follow the same rule. Tools in `server.py` are allowed to have async I/O — that is the tool layer's responsibility. The analytical core must remain stateless.

### Low Coupling

Tools do not call other tools, with one exception: `architect_review` is the designated orchestrator and is the only tool permitted to invoke other tools internally. All other tools are leaf nodes that call `_de.*` functions and format results. A new tool that needs output from another tool should accept that output as an input parameter, not call the other tool directly.

### High Cohesion

`server.py` contains routing and formatting logic only. `decision_engine.py` contains analytical logic only. Do not put scoring, detection, or classification logic inside a tool function. Do not put HTTP routing or MCP formatting logic inside `decision_engine.py`.

### Evidence-Driven Decisions

Every score, classification, and recommendation must trace back to a specific function call in `decision_engine.py` with specific inputs. Do not hardcode labels or decisions inside tool functions. If a tool produces a "BLOQUEADO" classification, it must be because `_de.compute_deploy_decision()` returned that value for a specific input, not because the tool string-matched "blocker" and injected a label.

---

## 2. Project Structure

```
fin-architect-mcp/
├── decision_engine.py     # Analytical core. All changes here require full review.
├── server.py              # MCP tool layer. One @mcp.tool() function per tool.
├── main.py                # FastAPI health endpoint only. Do not add business logic.
├── requirements.txt       # Python dependencies. Additions require justification.
├── Procfile               # Deployment entry point: web: python server.py
├── railway.toml           # Railway platform configuration.
└── docs/
    ├── Architecture.md
    ├── DecisionEngine.md
    ├── Examples.md
    ├── GettingStarted.md
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md    # This file.
    └── PROJECT_CONTEXT.md
```

### `decision_engine.py`

This is the highest-impact file in the project. A bug here affects all 15 tools simultaneously. A change here that introduces a regression will not be caught by a single tool's test — it will manifest as incorrect output across every tool that calls the modified function.

Rules:
- All changes require an AST validity check before commit.
- No function may be duplicated internally. Before adding a function, verify it does not already exist.
- All thresholds must be named constants at the module level, not inline values.
- All functions must be pure (no side effects, no I/O).
- The Knowledge module occupies lines 1–897. The Guideline module occupies lines 898–1264. Additions go at the end of the relevant section, not inserted into the middle.

### `server.py`

This file defines all 15 MCP tools using the `@mcp.tool()` decorator from FastMCP. Every tool function is `async`. The file also contains the SSE transport setup (`SseServerTransport`), the Starlette application with routes (`/`, `/sse`, `/messages/`), and the uvicorn entrypoint.

Rules:
- No analytical logic. All scoring, detection, and classification happens in `_de.*`.
- One `@mcp.tool()` function per tool. No helper functions for analytics inline.
- All tool functions return `str` — the formatted MCP response.
- The import `import decision_engine as _de` must remain at the top of the file.

### `main.py`

FastAPI health endpoint returning `{"name": "Fin Architect MCP", "status": "running", "version": "0.1"}`. Do not add tools, routes, or business logic here.

### `requirements.txt`

Four dependencies: `mcp[cli]>=1.3.0`, `uvicorn>=0.29.0`, `starlette>=0.36.0`, `httpx>=0.27.0`. New dependencies must be justified in the PR description. Prefer the standard library when possible.

### `docs/`

All documentation files. Markdown only. English only. Based on real project behavior — no invented features, no aspirational descriptions of functionality that does not exist.

---

## 3. Creating a New MCP Tool

### Step 1 — Define the tool's scope

Before writing code, answer these questions:

- What inputs does the tool receive?
- What outputs does it return?
- Which `_de.*` functions provide the analytical logic it needs?
- Does any required function exist in `decision_engine.py`? If not, add it there first.

### Step 2 — Add new analytical functions to `decision_engine.py` (if needed)

If the tool requires logic that does not exist in `decision_engine.py`:

1. Identify the correct section: Knowledge module (lines 1–897) or Guideline module (lines 898–1264).
2. Define any new constants at the module level above the function.
3. Write the function as a pure function with typed parameters.
4. Verify it does not duplicate an existing function.

### Step 3 — Register the tool in `server.py`

Add the tool function using the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def my_new_tool(
    input_text: str,
    product: str = "general"
) -> str:
    """
    One-line description of what the tool does and what it returns.
    """
    # Delegate all analytics to the Decision Engine
    result = _de.kde_score_article(input_text)
    risk   = _de.detect_loop_risk(input_text.lower())

    # Format and return
    return f"""
## MY NEW TOOL REPORT

Health: {result['kde_health']}/100
Loop risk: {risk[0]}
""".strip()
```

Rules:
- Function must be `async`.
- Return type is `str`.
- All analytical calls use `_de.*`.
- No analytical logic inside the function body.
- Docstring is a single concise sentence describing what the tool does.

### Step 4 — Do not modify existing tool signatures

Adding a new tool must not change the parameter names, parameter types, or return structure of any existing tool. Existing clients may depend on the current interface. If a signature change is genuinely required, document it as a breaking change and justify it in the PR.

### Step 5 — Test the tool manually

Before opening a PR:

```bash
# Verify server starts
python server.py &
sleep 2
curl http://localhost:8000/
kill %1

# Verify the Decision Engine imports correctly
python -c "import decision_engine; print('DE OK')"

# Verify no AST errors
python -c "import ast, pathlib; ast.parse(pathlib.Path('decision_engine.py').read_text()); print('AST OK')"
python -c "import ast, pathlib; ast.parse(pathlib.Path('server.py').read_text()); print('AST OK')"
```

---

## 4. Decision Engine Rules

### What can be added

- New pure functions that compute a score, detect a signal, classify a value, or rank a list.
- New module-level constants: pattern lists, keyword vocabularies, threshold values, mapping dicts, template strings.
- New module-level sections for future analytical domains, following the Knowledge module / Guideline module pattern.

### What must NOT be added

- Any function that performs I/O (file reads, network calls, database queries).
- Any function that mutates global state.
- Any function that duplicates the logic of an existing function.
- Any inline threshold value — every threshold must be a named constant.
- Any routing, formatting, or MCP protocol logic.
- Any function that is only called from one place and could be inlined without loss of clarity — the Decision Engine is not a utility module for minor formatting; it is the analytical core.

### When to create a new function

Create a new function when:
- Two or more tools would need the same analytical computation.
- The computation is non-trivial (not a one-liner that any reader would understand immediately).
- The computation has a threshold or constant that might need to be tuned independently.

Do not create a new function when:
- Only one tool ever needs it and the computation is a simple filter or format.
- An existing function already covers the same logic with a parameter variation.

### When to reuse an existing function

Always verify existing functions before writing new ones. The full list of 34 exported functions is documented in `docs/DecisionEngine.md`. Specific cases:

- Any similarity computation between text snippets → `_de.jaccard()` + `_de.word_set()`
- Any loop risk check → `_de.detect_loop_risk()`
- Any escalation path check → `_de.detect_escalation()` or `_de.detect_escalation_repo()`
- Any article health score → `_de.kde_score_article()` (full) or `_de.kde_score_article_fast()` (bulk)
- Any guideline health score → `_de.kde_score_guideline_fast()`
- Any deployment decision → `_de.compute_deploy_decision()`
- Any ROI ranking → `_de.compute_roi()` + `_de.rank_improvements()`
- Any traffic light indicator → `_de.semaforo()`
- Any intent detection → `_de.detect_intention()`
- Any emotion detection → `_de.detect_emotion()`

### How to add new shared constants

1. Choose a descriptive name in UPPER_SNAKE_CASE.
2. Place it at the module level in the appropriate section — before the first function that uses it.
3. Add a comment on the line above the constant explaining which tools use it.
4. Do not define the same constant under a different name elsewhere.

Example:

```python
# Loop patterns for bulk repository analysis — used by kde_score_article_fast, repository_review
LOOP_PATTERNS_REPO = [
    "loop", "bucle", "ciclo infinito", "repite", "vuelve a preguntar",
    ...
]
```

---

## 5. Coding Standards

### Python style

- Follow PEP 8 for formatting.
- Maximum line length: 100 characters (not enforced by a linter, but preferred).
- Use 4 spaces for indentation. No tabs.
- The project uses only standard library imports in `decision_engine.py` (`re` only). Do not add third-party imports to `decision_engine.py`.

### Naming conventions

| Context | Convention | Example |
|---------|-----------|---------|
| Tool functions | `snake_case` | `audit_knowledge` |
| DE functions | `snake_case` | `kde_score_article` |
| Constants | `UPPER_SNAKE_CASE` | `KDE_HARD_CAP_BLOCKER` |
| Local variables | `snake_case` | `text_lower`, `word_count` |
| Private helpers (DE) | leading `_` prefix | `_raw_total`, `_rc_clarity` |
| DE import alias | always `_de` | `import decision_engine as _de` |

### Async tools

All tool functions in `server.py` must be declared `async`:

```python
@mcp.tool()
async def my_tool(input_text: str) -> str:
    ...
```

Functions in `decision_engine.py` are synchronous. Do not make them async — they have no I/O and do not need it.

### Docstrings

Tool functions: one sentence describing what the tool does and what it returns. Keep it concise — MCP clients display this to users.

```python
@mcp.tool()
async def audit_guideline(guideline: str, product: str = "general", context: str = "") -> str:
    """
    Audita una guideline de FIN para detectar ambigüedades, conflictos o mejoras recomendadas.
    """
```

Decision Engine functions: describe what the function computes, what it returns, and any important parameter variants. Use the existing docstrings in `decision_engine.py` as reference.

```python
def detect_loop_risk(text_lower: str, use_repo_patterns: bool = False) -> tuple:
    """
    Devuelve (level: str, count: int, hits: list).
    level: BAJO / MEDIO / ALTO / CRÍTICO
    use_repo_patterns: usa keywords simples (repo/knowledge_review)
                       vs patrones de frase (audit_knowledge/optimize_article)
    """
```

### Report formatting

Tool reports use a consistent visual format across the project. Follow existing tools as reference:

- Section headers use `##` or `━` dividers.
- Metrics use `label: value` format.
- Lists use `-` bullets or numbered items.
- Emojis appear on status indicators (🟢 🟡 🔴 ⚠️ ✅ 🚫), not on every line.
- Reports end with a deployment or action decision block.

### ASCII diagrams

Architecture diagrams in documentation use box-drawing characters (`┌ ─ ┐ │ └ ┘ ▼ ►`). Keep diagrams within 70 characters wide to render correctly in standard terminal widths.

### Type hints

Use type hints where they exist in the current codebase style. Tool parameters and return types are annotated. Decision Engine function parameters and return types are annotated where the type is unambiguous. Do not add complex generic types (`Dict[str, List[Tuple[...]]]`) — prefer simple annotations or none.

---

## 6. Pull Request Guidelines

### Branch naming

```
feature/<short-description>     # New tool or feature
refactor/<short-description>    # Internal restructuring, no behavior change
fix/<short-description>         # Bug fix
docs/<short-description>        # Documentation only
chore/<short-description>       # Config, dependencies, tooling
```

Examples from this project's history:
- `feature/fin-dashboard`
- `feature/audit-knowledge-kde`
- `refactor/decision-engine`
- `feat/architect-review-v4`

### Commit messages

Use the format: `<type>: <short description>`

Types: `feat`, `fix`, `refactor`, `docs`, `chore`

Rules:
- Present tense, imperative mood: "add tool" not "added tool"
- First line under 72 characters
- If the change is non-obvious, add a blank line and a body paragraph explaining the why

Examples from this project's history:
```
feat: add fin_dashboard MCP tool
refactor: centralize audit_knowledge, optimize_article, architect_review into decision_engine
fix: remove duplicate Guideline module block from decision_engine.py
docs: add official README for FIN Architect MCP v1.0.0
```

### Pull Request description

Every PR must include:

1. **What changed** — a clear statement of what was added, modified, or removed.
2. **Why** — the motivation. Link to an issue if one exists.
3. **How it uses the Decision Engine** — which `_de.*` functions the new or modified code calls.
4. **Verification steps** — the commands you ran to confirm the change works (server startup, AST check, manual tool test).
5. **Behavior impact** — does this change any existing tool's observable output? If yes, explain why and document it as a breaking change.

### Review criteria

A PR will be reviewed against these criteria:

- Does it follow the Single Source of Truth rule? No analytical logic duplicated from `decision_engine.py`.
- Is `decision_engine.py` still internally consistent? No duplicate functions introduced.
- Do all existing tools still compile and return expected output?
- Is the PR scoped appropriately? Logic changes and documentation changes should be in separate PRs when possible.
- Are all new constants in `decision_engine.py`, not inline in `server.py`?

### Merge

PRs are merged after passing the testing checklist (Section 7) and receiving approval. Squash merging is acceptable for small changes. Merge commits are acceptable for feature branches with multiple logical commits.

---

## 7. Testing Checklist

Run these checks before marking a PR ready for review. All items must pass.

### Structural validity

```bash
# Python syntax — decision_engine.py
python -c "import ast, pathlib; ast.parse(pathlib.Path('decision_engine.py').read_text()); print('AST OK: decision_engine.py')"

# Python syntax — server.py
python -c "import ast, pathlib; ast.parse(pathlib.Path('server.py').read_text()); print('AST OK: server.py')"

# Clean import — decision_engine
python -c "import decision_engine; print('Import OK: decision_engine')"

# Clean import — server (full module load)
python -c "import server; print('Import OK: server')"
```

### Server startup

```bash
python server.py &
sleep 2
curl -s http://localhost:8000/ | python -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='ok', d; print('Health OK')"
kill %1
```

### No broken DE references

```bash
# All _de.* calls in server.py must resolve to exported names in decision_engine
python - <<'EOF'
import re, ast, pathlib

de_src = pathlib.Path("decision_engine.py").read_text()
de_tree = ast.parse(de_src)
de_names = {
    node.name
    for node in ast.walk(de_tree)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign))
    and (not isinstance(node, ast.Assign) or (
        isinstance(node, ast.Assign) and node.targets
        and isinstance(node.targets[0], ast.Name)
    ))
}

server_src = pathlib.Path("server.py").read_text()
refs = set(re.findall(r'_de\.(\w+)', server_src))
missing = refs - de_names
if missing:
    print(f"BROKEN REFERENCES: {missing}")
else:
    print(f"All {len(refs)} _de.* references resolve OK")
EOF
```

### No internal duplication in decision_engine.py

```bash
python - <<'EOF'
import ast, pathlib, collections

tree = ast.parse(pathlib.Path("decision_engine.py").read_text())
names = [
    node.name
    for node in ast.walk(tree)
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
]
dupes = [name for name, count in collections.Counter(names).items() if count > 1]
if dupes:
    print(f"DUPLICATE FUNCTIONS: {dupes}")
else:
    print(f"No duplicate functions ({len(names)} total)")
EOF
```

### Manual tool verification

After server startup, call at minimum:

- One Guideline tool (e.g., `audit_guideline` with a short guideline text)
- One Knowledge tool (e.g., `audit_knowledge` with a short article text)
- `fin_dashboard` with empty string inputs (should return a report with defaults, not crash)

### Checklist summary

Before requesting review, confirm:

- [ ] `decision_engine.py` passes AST parse
- [ ] `server.py` passes AST parse
- [ ] Both modules import without error
- [ ] Server starts and health endpoint returns `{"status": "ok"}`
- [ ] All `_de.*` references resolve to exported names
- [ ] No duplicate function names in `decision_engine.py`
- [ ] At least one tool called manually and returned expected output
- [ ] No analytical logic added inside tool functions
- [ ] All new constants defined in `decision_engine.py`, not in `server.py`
- [ ] `docs/CHANGELOG.md` updated if the change is user-visible

---

## 8. Architecture Rules

The following rules are inviolable. They exist because the project has already paid the cost of violating them — three architecture sprints were required to undo the damage.

### Rules that must never be broken

**Rule 1 — No analytical logic in `server.py`.**
If a function computes a score, detects a pattern, classifies a value, or ranks a list, it belongs in `decision_engine.py`. Tool functions in `server.py` call `_de.*` and format results. Nothing else.

**Rule 2 — No constants defined in `server.py`.**
Pattern lists, threshold values, keyword vocabularies — all of these belong in `decision_engine.py`. A constant that appears anywhere other than `decision_engine.py` is a maintenance liability: it will drift from the canonical version and produce inconsistent behavior.

**Rule 3 — No duplicate implementations.**
One `jaccard()`. One `detect_loop_risk()`. One `kde_score_article()`. If a function is needed, call the existing one. The existence of two implementations of the same function is an architectural defect, not a stylistic issue.

**Rule 4 — No tool calls another tool directly (except `architect_review`).**
`architect_review` is the designated orchestrator. All other tools are leaf nodes. A leaf tool that needs data from another tool should accept that data as an input parameter. This keeps the dependency graph a tree.

**Rule 5 — Hard caps are not optional.**
`KDE_HARD_CAP_BLOCKER = 60` and `KDE_HARD_CAP_RESOLUTION = 40` enforce safety floors for blocked articles. No tool may bypass or ignore these caps. A blocked article must not receive a score above the cap regardless of quality in other criteria.

**Rule 6 — Tool return signatures are stable.**
Once a tool's parameters and return format are established, changing them is a breaking change. Existing clients may depend on the current interface. Breaking changes require explicit documentation and justification.

**Rule 7 — `decision_engine.py` must not contain duplicates.**
The duplicate Guideline module block (lines 1265–1592, removed before v1.0) was introduced by two concurrent writes to the same file. Before merging any change to `decision_engine.py`, run the duplicate function check from Section 7.

### When to raise a concern

If a proposed change would require violating any of the above rules, raise it in the PR discussion before implementation. The correct response is always to find an approach that respects the architecture, not to carve out an exception.

---

## 9. Documentation

Documentation must stay synchronized with code. When a change affects user-visible behavior, update the relevant documents.

### When to update each document

**`README.md`**
Update when: a new tool is added, a module is created, project metrics change (tool count, DE function count, line counts), the roadmap changes.
Do not update for: internal refactors with no behavior change.

**`docs/Architecture.md`**
Update when: a new module is introduced, a new architectural decision is made, the layer structure changes, the data flow changes.
Do not update for: new tools within existing modules (those go in `README.md`).

**`docs/DecisionEngine.md`**
Update when: a new function is added to `decision_engine.py`, an existing function's behavior changes, a new constant is added.
Update the relevant section: function documentation (Section "Exported Functions"), constant documentation (Section "Shared Constants"), or integration table (Section "Integration").

**`docs/Examples.md`**
Update when: a new tool is added that enables a new workflow, an existing tool's output format changes significantly.
Do not update for: internal refactors.

**`docs/GettingStarted.md`**
Update when: the server startup command changes, a new dependency is added, the repository structure changes.
Do not update for: new tools (those go in the tool catalog table in `README.md`).

**`docs/CHANGELOG.md`**
Update for every PR that changes user-visible behavior. Use the Keep a Changelog format. Place entries under the correct version and subsection (Added / Changed / Fixed).

**`docs/CONTRIBUTING.md`**
Update when: a new development process is established, a new architectural rule is added, the testing checklist changes.

---

## 10. Release Process

### Feature branch

All work happens on a dedicated branch. Never commit directly to `main`.

```bash
git checkout -b feature/my-feature
# ... make changes ...
git add <specific files>
git commit -m "feat: describe the change"
git push -u origin feature/my-feature
```

### Pull Request

Open a PR from the feature branch to `main`. The PR description must follow the template in Section 6. The author runs the full testing checklist from Section 7 before requesting review.

### Validation

Before merge, verify:

1. All items in the testing checklist pass.
2. No architectural rules from Section 8 are violated.
3. `docs/CHANGELOG.md` is updated with the change.
4. No existing tool's observable output changed unexpectedly.

### Merge

Merge the PR after validation passes. For refactoring PRs that touch `decision_engine.py`, prefer a squash merge to keep the main branch history readable. For feature PRs with multiple logical commits (e.g., adding a tool + updating documentation), a merge commit is appropriate.

### Post-merge verification

After merging to `main`, verify the server starts cleanly from the merged state:

```bash
git checkout main
git pull origin main
python -c "import decision_engine, server; print('Import OK')"
python server.py &
sleep 2
curl -s http://localhost:8000/
kill %1
```

### Deployment

The project deploys via Railway using the configuration in `railway.toml`. The start command is `python server.py`. The health check path is `/`. Deployment is triggered automatically on push to the configured branch.

Verify deployment by checking the health endpoint on the deployed URL:

```bash
curl https://<deployed-url>/
# Expected: {"status": "ok", "service": "fin-architect-mcp"}
```

### Documentation update

After a release, update:

- `docs/CHANGELOG.md` — add the release date to the version header
- `README.md` — update the version badge and project metrics table if values changed

### Release tag

Tag the release in git:

```bash
git tag -a v1.0.0 -m "FIN Architect MCP v1.0.0 — stable release"
git push origin v1.0.0
```

---

*FIN Architect MCP — Contributing Guide*
