# FIN Architect MCP — Architecture

**Version:** 1.0.0
**Status:** Architecture Certified
**Last updated:** 2026-06-25

---

## Table of Contents

1. [Architectural Goals](#1-architectural-goals)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Decision Engine](#3-decision-engine)
4. [Tool Ecosystem](#4-tool-ecosystem)
5. [Design Principles](#5-design-principles)
6. [Data Flow](#6-data-flow)
7. [Internal Components](#7-internal-components)
8. [Extension Guide](#8-extension-guide)
9. [Architectural Decisions](#9-architectural-decisions)
10. [Future Evolution](#10-future-evolution)

---

## 1. Architectural Goals

### Why the project exists

Financial support operations accumulate two kinds of silent debt: **knowledge debt** and **guideline debt**.

Knowledge articles become outdated as products change. Resolution steps drift from reality. Anti-escalation language creeps in. Ambiguous phrasing obscures what the agent should actually do. None of this is visible until a customer escalates — at which point the article has already failed.

Conversation guidelines face a different version of the same problem. Guidelines written at different times by different people contradict each other. A guideline that instructs the agent to offer a refund may conflict with another that prohibits refunds in the same scenario. A guideline written for one product may be applied incorrectly to another. Conflicts accumulate silently.

FIN Architect MCP exists to surface this debt before it reaches the customer. It provides a structured analytical layer — integrated directly into AI agent workflows via the Model Context Protocol — that continuously scores, audits, detects conflicts, and generates prioritized recommendations.

### Main design objectives

1. **Single analytical authority.** All scoring, detection, and classification logic must reside in one place. No tool may implement its own version of a function that already exists elsewhere.

2. **Zero behavioral divergence.** Two tools operating on the same input must produce consistent results because they call the same underlying functions, not because they happen to have been written similarly.

3. **Architectural refactorability.** The system must be restructurable — migrating logic from server.py into decision_engine.py, removing duplicates, reorganizing modules — without changing any tool's observable output.

4. **Auditability.** Every analytical decision must trace back to a named, testable function. Nothing should happen inside a tool that cannot be independently tested.

5. **Operational integration.** The system must integrate into existing AI agent workflows without requiring new infrastructure. MCP provides the protocol layer; the tools are the interface.

### Engineering principles

- **Pure functions first.** `decision_engine.py` has no side effects. All functions take inputs and return outputs. No global state is mutated.
- **Explicit thresholds.** Every threshold is a named constant. No magic numbers inside function bodies.
- **Separation of concerns.** `server.py` is responsible for routing and formatting. `decision_engine.py` is responsible for analysis. The two layers never overlap.
- **Conservative scoring.** When a hard blocker is present, the system enforces score caps regardless of other positive signals. High-risk conditions cannot be masked by high-quality prose.

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      MCP Client (AI Agent)                       │
│              Claude, Intercom FIN, or any MCP client             │
└────────────────────────────┬─────────────────────────────────────┘
                             │  MCP Protocol
┌────────────────────────────▼─────────────────────────────────────┐
│                        server.py                                  │
│                    FastMCP Tool Layer                             │
│                                                                   │
│   audit_guideline   optimize_guideline   classify_guideline       │
│   detect_conflicts  score_guideline      simulate_fin             │
│   generate_guideline  extract_guidelines                          │
│   audit_knowledge   optimize_article     knowledge_review         │
│   repository_review  recommend_improvements  fin_dashboard        │
│   architect_review                                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │  import decision_engine as _de
┌────────────────────────────▼─────────────────────────────────────┐
│                    decision_engine.py                             │
│                   The Analytical Core                             │
│                                                                   │
│   ┌────────────────────────┐  ┌──────────────────────────────┐   │
│   │   Knowledge Module     │  │     Guideline Module         │   │
│   │                        │  │                              │   │
│   │  kde_score_article()   │  │  kde_score_guideline_fast()  │   │
│   │  detect_loop_risk()    │  │  detect_intention()          │   │
│   │  detect_anti_esc()     │  │  detect_emotion()            │   │
│   │  detect_fin_blockers() │  │  detect_guideline_events()   │   │
│   │  compute_knowledge_   │  │  detect_guideline_problems() │   │
│   │    debt()              │  │  guideline_risk_level()      │   │
│   │  compute_roi()         │  │  conflict_severity_level()   │   │
│   │  rank_improvements()   │  │  cluster_pattern_name()      │   │
│   │  jaccard()             │  │  guideline_template_for()    │   │
│   │  semaforo()            │  │  GUIDELINE_EVENT_CATALOG     │   │
│   │  LOOP_PATTERNS         │  │  GUIDELINE_CLUSTER_THRESHOLD │   │
│   │  KDE_HARD_CAP_BLOCKER  │  │  GUIDELINE_MERGE_THRESHOLD   │   │
│   └────────────────────────┘  └──────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Layer responsibilities

| Layer | File | Responsibility |
|-------|------|----------------|
| MCP Protocol | FastMCP (framework) | Exposes tools to MCP clients; handles serialization |
| Tool Layer | `server.py` | Routes requests, formats responses, calls `_de.*` |
| Analytical Core | `decision_engine.py` | All scoring, detection, classification, ranking |
| Health Endpoint | `main.py` | FastAPI `/` endpoint returning service status |

---

## 3. Decision Engine

### What it centralizes

`decision_engine.py` is the single location for every analytical function in the system. It is organized into two internal modules — the Knowledge module and the Guideline module — but exported as one unified namespace.

**Knowledge module** (lines 1–897):

| Category | Functions / Constants |
|----------|-----------------------|
| Scoring | `kde_score_article()`, `kde_score_article_fast()`, `global_status_from_health()`, `deployment_readiness()`, `semaforo()` |
| Detection | `detect_loop_risk()`, `detect_anti_escalation()`, `detect_absolute_hits()`, `detect_escalation()`, `detect_fin_blockers()` |
| Similarity | `jaccard()`, `word_set()` |
| Debt & ROI | `compute_knowledge_debt()`, `debt_label_emoji()`, `compute_coverage()`, `compute_roi()`, `rank_improvements()` |
| Utilities | `extract_int()`, `extract_metrics_from_reports()` |
| Constants | `LOOP_PATTERNS`, `ANTI_ESCALATION_PATTERNS`, `ABSOLUTE_TERMS`, `ESCALATION_SIGNALS`, `STEP_VERBS`, `VAGUE_PHRASES`, `COVERAGE_SIGNALS`, `TECHNICAL_TERMS`, `FIN_POSITIVE_SIGNALS`, `FIN_BLOCKER_ACTIONS`, `RISKY_ACTIONS`, `TOPIC_CATEGORIES`, `KDE_HARD_CAP_BLOCKER=60`, `KDE_HARD_CAP_RESOLUTION=40` |

**Guideline module** (lines 898–1264):

| Category | Functions / Constants |
|----------|-----------------------|
| Scoring | `kde_score_guideline_fast()` |
| Detection | `detect_intention()`, `detect_emotion()`, `detect_guideline_events()`, `detect_guideline_problems()` |
| Classification | `guideline_risk_level()`, `conflict_severity_level()`, `guideline_priority_from_risk()`, `guideline_impact_priority()` |
| Generation | `cluster_pattern_name()`, `guideline_template_for()` |
| Constants | `GUIDELINE_EVENT_CATALOG`, `GUIDELINE_CLUSTER_THRESHOLD=0.70`, `GUIDELINE_MERGE_THRESHOLD=0.80`, `GUIDELINE_PATTERN_NAMES`, `GUIDELINE_TEMPLATES`, `INTENTION_MAP`, `FRUSTRATION_KEYWORDS`, `URGENCY_KEYWORDS`, `GUIDELINE_ESCALATION_WORDS`, `GUIDELINE_PROHIBITION_WORDS`, `GUIDELINE_OBLIGATION_WORDS`, `GUIDELINE_AMBIGUOUS_TERMS`, `GUIDELINE_RISKY_PATTERNS`, `GUIDELINE_CONTRADICTION_PAIRS`, `GUIDELINE_CONDITION_PAIRS`, `GUIDELINE_PROBLEM_SIGNALS`, `GUIDELINE_FAILURE_MAP`, `GUIDELINE_BEHAVIOR_MAP` |

**Total exported surface:** 34 functions, 45 constants, 1,264 lines.

### Problems it resolved

Before the Decision Engine was established as the sole source of truth, three specific problems existed:

**Problem 1 — Duplicate Jaccard implementations.**
`extract_guidelines`, `audit_knowledge`, and `architect_review` each contained their own local `jaccard()` or `text_jaccard()` function. The implementations were similar but not identical. A similarity check in one tool could return a different result than the same check in another tool on the same input. Resolution: single `jaccard()` in `decision_engine.py`, called by all three tools.

**Problem 2 — Inline constant duplication.**
`optimize_article` maintained its own local copies of pattern lists (loop signals, anti-escalation patterns, absolute terms) that were also defined in `audit_knowledge`. When patterns were updated in one place, the other was not updated. Resolution: all pattern constants live exclusively in `decision_engine.py`.

**Problem 3 — Scoring logic copied per tool.**
`audit_knowledge` contained a 460-line inline KDE scoring loop that was a diverged copy of what became `kde_score_article()`. The loop had drifted in subtle ways that were not visible without a side-by-side diff. Resolution: `kde_score_article()` in `decision_engine.py` is called by all tools that require article scoring.

### How tools use the module

All tools in `server.py` import the Decision Engine as a single alias:

```python
import decision_engine as _de
```

Tools access functions and constants via the `_de` namespace:

```python
# Scoring
result = _de.kde_score_article(text, title, category)

# Detection
loop_risk = _de.detect_loop_risk(text)
blockers  = _de.detect_fin_blockers(text)

# Similarity
score = _de.jaccard(_de.word_set(text_a), _de.word_set(text_b))

# Constants
if term in _de.ABSOLUTE_TERMS:
    ...

# Thresholds
if similarity >= _de.GUIDELINE_CLUSTER_THRESHOLD:
    ...
```

No tool defines its own analytical function. If a tool needs a computation, it calls `_de`.

---

## 4. Tool Ecosystem

### Tool inventory

| Tool | Module | Input | Core DE calls | Output |
|------|--------|-------|---------------|--------|
| `audit_guideline` | Guideline Core | guideline text | `ABSOLUTE_TERMS`, `detect_guideline_problems()`, `guideline_risk_level()` | Compliance report + score |
| `optimize_guideline` | Guideline Core | guideline text + score | `kde_score_guideline_fast()`, `GUIDELINE_AMBIGUOUS_TERMS`, `GUIDELINE_RISKY_PATTERNS` | Rewrite recommendations |
| `classify_guideline` | Guideline Core | guideline text | `detect_intention()`, `detect_emotion()`, `guideline_risk_level()`, `guideline_impact_priority()` | Category, risk, priority |
| `detect_conflicts` | Guideline Core | list of guidelines | `jaccard()`, `word_set()`, `conflict_severity_level()`, `GUIDELINE_CONTRADICTION_PAIRS` | Conflict map |
| `score_guideline` | Guideline Core | guideline text | `kde_score_guideline_fast()` | 10-criterion score breakdown |
| `simulate_fin` | Guideline Core | guideline text | `detect_intention()`, `detect_guideline_events()`, `GUIDELINE_EVENT_CATALOG` | FIN response simulation |
| `generate_guideline` | Guideline Core | event type + context | `cluster_pattern_name()`, `guideline_template_for()`, `GUIDELINE_TEMPLATES` | Structured guideline template |
| `extract_guidelines` | Guideline Core | conversation logs | `jaccard()`, `word_set()`, `GUIDELINE_CLUSTER_THRESHOLD`, `GUIDELINE_MERGE_THRESHOLD`, `GUIDELINE_PATTERN_NAMES` | Clustered guideline set |
| `audit_knowledge` | Knowledge Core | article text | `kde_score_article()`, `detect_loop_risk()`, `detect_anti_escalation()`, `detect_fin_blockers()` | KDE report + health score |
| `optimize_article` | Knowledge Core | article + audit | `rank_improvements()`, `compute_roi()`, `LOOP_PATTERNS`, `VAGUE_PHRASES` | Prioritized action plan |
| `knowledge_review` | Knowledge Core | list of articles | `kde_score_article_fast()`, `compute_knowledge_debt()`, `compute_coverage()`, `jaccard()` | Coverage + debt analysis |
| `repository_review` | Repository Core | full repository | `deployment_readiness()`, `global_status_from_health()`, `jaccard()`, `compute_knowledge_debt()` | Repository health report |
| `recommend_improvements` | Recommendation Engine | repository data | `rank_improvements()`, `compute_roi()`, `debt_label_emoji()` | ROI-ranked backlog |
| `fin_dashboard` | Executive Dashboard | all module outputs | `semaforo()`, `global_status_from_health()`, `deployment_readiness()` | Unified executive report |
| `architect_review` | Orchestrator | articles + guidelines | calls other tools | Full diagnostic pipeline |

### Tool interactions

Tools are designed to be composable. The output of one tool can serve as the input to another:

```
extract_guidelines  →  output feeds into  →  classify_guideline
classify_guideline  →  output feeds into  →  detect_conflicts
audit_knowledge     →  output feeds into  →  optimize_article
knowledge_review    →  output feeds into  →  recommend_improvements
[all tools]         →  output feeds into  →  fin_dashboard
```

`architect_review` is the only tool that calls other tools directly. It is the system's orchestration layer.

### Execution order

For a complete analysis pipeline, tools execute in this order:

```
1. extract_guidelines      (raw conversation → raw guidelines)
2. classify_guideline      (raw guidelines → categorized + prioritized)
3. detect_conflicts        (categorized guidelines → conflict map)
4. audit_guideline         (per guideline → compliance status)
5. optimize_guideline      (per guideline + audit → rewrite plan)
6. score_guideline         (per guideline → numeric score)
7. simulate_fin            (per guideline → FIN response prediction)
8. generate_guideline      (validated guideline → deployable template)
9. audit_knowledge         (per article → KDE health + blockers)
10. optimize_article       (per article + audit → action plan)
11. knowledge_review       (all articles → coverage + debt)
12. repository_review      (full repository → deployment readiness)
13. recommend_improvements (repository data → ranked backlog)
14. fin_dashboard          (all outputs → executive report)
```

Steps 1–8 (Guideline pipeline) and steps 9–11 (Knowledge pipeline) can run in parallel. Steps 12–14 depend on both pipelines completing.

---

## 5. Design Principles

### Single Source of Truth

Every scoring formula, every threshold value, every pattern list exists in exactly one place: `decision_engine.py`. This is not a convention — it is enforced by the architecture. `server.py` imports `decision_engine` and calls its functions. It does not redefine them.

Consequence: changing the Jaccard threshold for guideline clustering requires editing one constant (`GUIDELINE_CLUSTER_THRESHOLD`) in one file. The change propagates automatically to all tools that use it.

### Low Coupling

`server.py` depends on `decision_engine.py`. `decision_engine.py` depends on nothing inside this project. No tool depends on another tool directly (except `architect_review`, which is explicitly the orchestrator).

This means any tool can be tested in isolation by calling it with its expected inputs. Any tool can be modified without triggering cascading changes in other tools, as long as the `_de.*` interface contract is respected.

### High Cohesion

Each module contains everything it needs and nothing it does not need.

- `decision_engine.py` contains all analytical logic and no routing logic.
- `server.py` contains all tool definitions and no analytical logic.
- `main.py` contains the health endpoint and nothing else.

### Modularity

The Decision Engine is internally organized into two modules — Knowledge and Guideline — but they are exported as a single namespace. Adding a new analytical domain (e.g., a Macro module) means appending functions and constants to `decision_engine.py` without changing its import contract.

Tools in `server.py` are independent of each other. Adding a new tool requires:
1. Decorating a new function with `@mcp.tool()`
2. Calling the appropriate `_de.*` functions
3. Formatting and returning the result

No other file needs to be modified.

### Extensibility

The architecture is designed to grow without breaking. New tools can be added without touching existing tools. New analytical functions can be added to `decision_engine.py` without modifying existing functions. New constants can be added without changing existing constants.

The constraint is additive, not destructive: extensions add to the surface without altering it.

### Reuse

Before the Decision Engine, each tool was self-contained — which meant each tool duplicated the logic it needed. Reuse is now the default because every tool draws from the same module. The Jaccard function written once is used by `extract_guidelines`, `detect_conflicts`, `knowledge_review`, and `repository_review` without any of them being aware of the others.

---

## 6. Data Flow

### Complete pipeline

```
Intercom Conversations
        │
        │  Raw conversation text, turn-by-turn
        ▼
┌───────────────────┐
│ extract_guidelines│  Clusters semantically similar conversation turns
│                   │  into candidate guidelines using Jaccard similarity
│  DE: jaccard()    │  (GUIDELINE_CLUSTER_THRESHOLD=0.70 for clustering,
│      word_set()   │   GUIDELINE_MERGE_THRESHOLD=0.80 for deduplication)
│      CLUSTER_THR  │
└────────┬──────────┘
         │  Set of candidate guidelines (text, cluster metadata)
         ▼
┌───────────────────┐
│classify_guideline │  Assigns each guideline a category, intent,
│                   │  emotion signal, risk level, and priority score
│  DE: detect_      │
│    intention()    │
│    detect_        │
│    emotion()      │
│    guideline_     │
│    risk_level()   │
└────────┬──────────┘
         │  Classified guidelines
         ▼
┌───────────────────┐
│ detect_conflicts  │  Compares all guidelines pairwise using Jaccard
│                   │  similarity. Flags contradicting pairs using
│  DE: jaccard()    │  GUIDELINE_CONTRADICTION_PAIRS patterns.
│      word_set()   │  Assigns severity level per conflict.
│      conflict_    │
│      severity()   │
└────────┬──────────┘
         │  Conflict map + severity scores
         ▼
┌───────────────────┐
│  audit_guideline  │  Evaluates each guideline against policy:
│                   │  obligation language, prohibition language,
│  DE: ABSOLUTE_    │  ambiguous terms, absolute words, risky patterns.
│    TERMS          │  Returns compliance status + violation list.
│    detect_        │
│    guideline_     │
│    problems()     │
└────────┬──────────┘
         │  Audit report per guideline
         ▼
┌───────────────────┐
│optimize_guideline │  Uses audit output to generate specific rewrite
│                   │  recommendations. Targets the lowest-scoring
│  DE: kde_score_   │  criteria from the 10-criterion scoring framework.
│    guideline_     │
│    fast()         │
└────────┬──────────┘
         │  Rewrite recommendations
         ▼
┌───────────────────┐
│  score_guideline  │  Scores the guideline across 10 criteria.
│                   │  Returns numeric score + per-criterion breakdown.
│  DE: kde_score_   │
│    guideline_     │
│    fast()         │
└────────┬──────────┘
         │  Score + breakdown
         ▼
┌───────────────────┐
│   simulate_fin    │  Simulates how FIN would respond if given this
│                   │  guideline as context. Predicts escalation
│  DE: detect_      │  probability, resolution path, and failure modes.
│    intention()    │
│    detect_        │
│    guideline_     │
│    events()       │
│    GUIDELINE_     │
│    EVENT_CATALOG  │
└────────┬──────────┘
         │  Simulation result
         ▼
┌───────────────────┐
│generate_guideline │  Produces a final structured guideline template
│                   │  ready for deployment. Uses event catalog to
│  DE: cluster_     │  select the appropriate template format.
│    pattern_name() │
│    guideline_     │
│    template_for() │
└────────┬──────────┘
         │  Deployable guideline template
         ▼
Knowledge Article Pipeline
         │
         ▼
┌───────────────────┐
│  audit_knowledge  │  Scores article across 12 KDE criteria (100 pts).
│                   │  Detects loop risk, anti-escalation patterns,
│  DE: kde_score_   │  FIN blockers, absolute terms, vague phrases.
│    article()      │  Applies hard caps when blockers present.
│    detect_loop_   │
│    risk()         │
│    detect_fin_    │
│    blockers()     │
└────────┬──────────┘
         │  KDE health score + blocker list + criterion breakdown
         ▼
┌───────────────────┐
│ optimize_article  │  Generates a prioritized action plan using
│                   │  ROI ranking. Each recommended fix is ranked
│  DE: rank_        │  by impact/effort ratio.
│    improvements() │
│    compute_roi()  │
└────────┬──────────┘
         │  Prioritized action plan
         ▼
┌───────────────────┐
│ knowledge_review  │  Analyzes coverage, debt distribution, and
│                   │  duplicate articles across the full set.
│  DE: kde_score_   │  Jaccard threshold >= 0.55 for article duplicates.
│    article_fast() │  Sentence-level repetition threshold >= 0.80.
│    compute_       │
│    knowledge_     │
│    debt()         │
│    jaccard()      │
└────────┬──────────┘
         │  Coverage report + debt summary
         ▼
┌───────────────────┐
│repository_review  │  Evaluates the entire repository as a system.
│                   │  Computes deployment readiness based on
│  DE: deployment_  │  health distribution across all categories.
│    readiness()    │
│    global_status_ │
│    from_health()  │
└────────┬──────────┘
         │  Repository health + deployment readiness
         ▼
┌───────────────────────┐
│recommend_improvements │  Surfaces the highest-ROI improvements
│                       │  across the repository. Ranked by
│  DE: rank_            │  impact/effort ratio.
│    improvements()     │
│    debt_label_emoji() │
└────────┬──────────────┘
         │  Ranked improvement backlog
         ▼
┌───────────────────┐
│   fin_dashboard   │  Aggregates all upstream outputs into one
│                   │  unified executive report. Traffic-light
│  DE: semaforo()   │  indicators per module. Global health score.
│    global_status_ │  Deployment readiness indicator. Open blockers.
│    from_health()  │
│    deployment_    │
│    readiness()    │
└───────────────────┘
         │  Unified executive report
         ▼
      Stakeholders
```

---

## 7. Internal Components

### Guideline Core (8 tools)

The Guideline Core manages the full lifecycle of a conversation guideline from raw extraction to deployable template.

**Extraction:** `extract_guidelines` takes raw conversation logs and uses Jaccard-based clustering to group semantically similar turns into candidate guidelines. Two thresholds govern this process: `GUIDELINE_CLUSTER_THRESHOLD` (0.70) determines when two turns belong to the same cluster; `GUIDELINE_MERGE_THRESHOLD` (0.80) determines when two candidate guidelines are close enough to merge. The result is a deduplicated set of candidate guidelines with cluster metadata.

**Analysis:** `classify_guideline` assigns intent (using `INTENTION_MAP` patterns), emotion signal (using keyword vocabularies: `FRUSTRATION_KEYWORDS`, `URGENCY_KEYWORDS`, `NEUTRAL_KEYWORDS`), risk level, and priority. `detect_conflicts` identifies contradicting guideline pairs by combining Jaccard overlap with `GUIDELINE_CONTRADICTION_PAIRS` pattern matching and `GUIDELINE_CONDITION_PAIRS` logic.

**Audit and scoring:** `audit_guideline` evaluates compliance using `GUIDELINE_PROBLEM_SIGNALS`, `GUIDELINE_PROHIBITION_WORDS`, `GUIDELINE_OBLIGATION_WORDS`, and `ABSOLUTE_TERMS`. `score_guideline` applies the 10-criterion scoring framework via `kde_score_guideline_fast()`.

**Optimization and generation:** `optimize_guideline` produces rewrite recommendations targeting the lowest-scoring criteria. `simulate_fin` predicts FIN's response given the guideline as context, using `GUIDELINE_EVENT_CATALOG` to match scenario types. `generate_guideline` produces the final deployable template using `guideline_template_for()` and `GUIDELINE_TEMPLATES`.

### Knowledge Core (3 tools)

The Knowledge Core manages the health of knowledge articles used by FIN to resolve support cases.

**Audit:** `audit_knowledge` applies the KDE (Knowledge Decision Engine) framework — 12 weighted criteria summing to 100 points:

| Criterion | Weight | What it measures |
|-----------|--------|-----------------|
| Claridad | 12 | Clarity of language and resolution steps |
| Estructura | 10 | Document structure and navigability |
| Pasos | 12 | Completeness and correctness of step sequences |
| Cobertura | 8 | Scenario coverage relative to topic |
| Ambiguedad | 10 | Absence of ambiguous or vague phrasing |
| Longitud | 8 | Appropriate length for the complexity |
| Consistencia | 8 | Internal consistency of instructions |
| Terminologia | 8 | Use of correct domain terminology |
| Uso por FIN | 10 | Suitability for direct use by FIN |
| Escalamiento | 8 | Correct escalation path definition |
| Mantenibilidad | 7 | Ease of future maintenance |
| Riesgo Operativo | 7 | Absence of instructions that carry operational risk |

Hard caps apply when blockers are present: `KDE_HARD_CAP_BLOCKER=60` (maximum health score when a blocker is detected), `KDE_HARD_CAP_RESOLUTION=40` (maximum resolution score when a blocker is detected).

**Optimization:** `optimize_article` receives the audit output and generates a prioritized list of improvements. Each improvement is ranked by ROI: `compute_roi()` computes an impact/effort ratio for each recommendation. `rank_improvements()` sorts the list.

**Review:** `knowledge_review` processes the full article set. It uses `kde_score_article_fast()` (a lightweight variant of the full KDE scorer) to evaluate all articles, then computes `compute_knowledge_debt()` per article and aggregates debt by category. Duplicate detection runs via `jaccard()` with a threshold of 0.55 for article-level similarity and 0.80 for sentence-level repetitions.

### Repository Core (1 tool)

`repository_review` operates at the repository level — above individual articles and above individual categories. It answers the question: *Is this repository ready for production?*

It computes the distribution of health scores across all articles and categories, applies `global_status_from_health()` to derive a global status, runs `deployment_readiness()` to produce a readiness indicator (READY / NOT READY / BLOCKED), and surfaces open blockers that would prevent deployment.

### Decision Engine

See [Section 3](#3-decision-engine) for full detail.

Key architectural property: the Decision Engine is stateless. Every call to any function produces the same output for the same input. There are no counters, no caches, no session state. This makes the module trivially testable and safe to call from any context.

---

## 8. Extension Guide

### Adding a new tool

To add a new MCP tool that reuses the Decision Engine:

**Step 1 — Define the tool in `server.py`.**

```python
@mcp.tool()
def my_new_tool(input_text: str) -> dict:
    """Tool description for MCP clients."""
    # Call Decision Engine functions
    score = _de.kde_score_article(input_text, title="", category="general")
    risk  = _de.detect_loop_risk(input_text)

    return {
        "score": score["health"],
        "loop_risk": risk,
    }
```

**Step 2 — Use existing DE functions. Do not reimplement them.**

If the analysis you need already exists in `decision_engine.py`, call it. Do not write a local version. If the analysis does not exist, proceed to Step 3.

**Step 3 — If you need a new analytical function, add it to `decision_engine.py`.**

Add the function to the appropriate module section (Knowledge, lines 1–897; Guideline, lines 898–1264). Follow the existing conventions:

- Pure function signature: inputs in, output out, no side effects.
- Named constants for all thresholds — no inline numbers.
- If the function introduces new pattern lists, define them as module-level constants before the function.

**Step 4 — Do not modify any existing tool.**

A new tool must not change the behavior of existing tools. If your new function requires a change to an existing constant or function, evaluate whether that change breaks existing behavior before proceeding.

### Adding a new analytical function to the Decision Engine

1. Identify which module section the function belongs to (Knowledge or Guideline).
2. Define any new constants at the module level, above the function.
3. Write the function as a pure function with typed parameters.
4. Verify no existing function covers the same behavior (avoid internal duplication — this was the root cause of the cleanup sprint).
5. Update the exported surface count in project documentation.

### What not to do

- Do not define a function inside `server.py` that performs analysis — put it in `decision_engine.py`.
- Do not copy a constant from `decision_engine.py` into `server.py` — import it via `_de`.
- Do not implement `jaccard()` locally in a new tool — use `_de.jaccard()` and `_de.word_set()`.
- Do not hardcode a threshold value inline — define it as a named constant in `decision_engine.py`.

---

## 9. Architectural Decisions

### AD-1: Decision Engine as sole analytical authority

**Context:** Early tools each contained their own scoring logic. As more tools were added, the same logic (Jaccard similarity, KDE scoring, loop risk detection) was reimplemented multiple times with subtle differences.

**Decision:** All analytical logic is moved to `decision_engine.py` and imported by all tools. Server.py is reduced to routing and formatting.

**Consequences:** Three architecture sprints (v1, v2, v3) were required to migrate existing tools. Approximately 1,500 lines of duplicate logic were eliminated. The module now has 34 exported functions and 45 constants as the single source of truth.

**Trade-off accepted:** `decision_engine.py` is a larger file than individual tool modules would be. Cohesion within the module is the organizing principle, not file size.

---

### AD-2: Two internal modules within one file

**Context:** Knowledge article logic and Guideline logic are distinct enough to warrant separation, but share some utilities (particularly `jaccard()` and `word_set()`).

**Decision:** The Decision Engine is organized into two internal sections within one file: Knowledge module (lines 1–897) and Guideline module (lines 898–1264). Shared utilities exist in the Knowledge section and are reused by the Guideline section.

**Consequences:** The import interface is uniform — `import decision_engine as _de` — with no sub-module complexity. Shared utilities are not duplicated.

**Trade-off accepted:** A single file of 1,264 lines requires discipline to navigate. The internal structure (comments, section headers) mitigates this.

---

### AD-3: Hard caps for blocker conditions

**Context:** A high-quality article that instructs agents to block escalation paths incorrectly could receive a high overall score despite being operationally dangerous.

**Decision:** When a FIN blocker is detected, the health score is capped at `KDE_HARD_CAP_BLOCKER=60` and the resolution score is capped at `KDE_HARD_CAP_RESOLUTION=40`, regardless of other criterion scores.

**Consequences:** An article cannot receive a passing score if it contains a detected blocker. Scores are not just lower — they hit a ceiling that signals the article requires mandatory review.

**Trade-off accepted:** False positive blockers would unfairly cap otherwise-healthy articles. Pattern quality in `FIN_BLOCKER_ACTIONS` must be maintained carefully.

---

### AD-4: Jaccard similarity as the core semantic measure

**Context:** The system needs to detect duplicate articles, cluster similar conversation turns, and identify conflicting guidelines. NLP embedding models were considered but rejected.

**Decision:** Jaccard similarity over word sets is used for all similarity computations. Three different thresholds apply in different contexts: 0.55 (article-level duplication), 0.70 (guideline clustering), 0.80 (sentence repetition and guideline merging), 0.90 (guideline consolidation).

**Consequences:** The system has no external model dependencies for similarity. All computations are deterministic and fast. The functions `jaccard()` and `word_set()` are implemented once in `decision_engine.py`.

**Trade-off accepted:** Jaccard over word sets does not capture semantic similarity — two sentences with the same meaning but different vocabulary score low. For the operational domain (financial support guidelines written in consistent vocabulary), this trade-off is acceptable.

---

### AD-5: `architect_review` as the only inter-tool caller

**Context:** An orchestration layer is needed to run the full pipeline with a single call. But allowing arbitrary inter-tool calls would create coupling between tools.

**Decision:** Only `architect_review` may call other tools. All other tools are leaf nodes that call `_de.*` functions but not other tools.

**Consequences:** The dependency graph is a tree, not a graph. Any tool except `architect_review` can be tested in isolation without mocking other tools.

**Trade-off accepted:** Complex pipelines that do not need the full `architect_review` scope require the client to call tools individually. There is no partial orchestration mode.

---

## 10. Future Evolution

### v1.1 — Hardening the existing architecture

The v1.1 priorities do not change the architecture. They harden what exists:

**Test suite for decision_engine.py.** All 34 exported functions are pure functions with deterministic outputs. A comprehensive test suite can be written without any mocking. Target: full coverage of the analytical core.

**Resolve 2 orphaned functions.** `detect_guideline_events()` and `guideline_priority_from_risk()` are defined in `decision_engine.py` but their call sites in `server.py` were not confirmed during v1.0 validation. Resolution: either verify the call sites or remove the functions. Leaving unreachable exports in the module creates misleading documentation.

**Batch processing mode.** `knowledge_review` and `repository_review` process article sets. Adding an explicit batch interface (with progress signaling) allows processing of larger repositories without client-side orchestration.

**Coverage gap auto-detection.** The system currently reports coverage gaps when asked. A proactive mode — surfacing which `TOPIC_CATEGORIES` are underrepresented without requiring a full `repository_review` call — would be a high-value addition.

### v2.0 — Architectural expansion

v2.0 would require architectural changes, not just additions:

**Persistent knowledge graph.** The current system is stateless: every call starts from scratch. A persistent graph would allow the system to track article health over time, detect regression after edits, and surface trends. This requires a storage layer — a decision that must be made carefully to avoid coupling the analytical core to a specific database.

The Decision Engine should remain stateless. The persistence layer should sit above it, between `server.py` and an external store, without modifying `decision_engine.py`.

**Guideline lifecycle management.** Articles currently have no lifecycle state (draft, review, approved, deprecated). Adding lifecycle tracking would require extending the data model passed to tools — an additive change that would not break existing tool signatures if handled via optional fields.

**Multi-language support.** The current system's pattern constants (`LOOP_PATTERNS`, `ANTI_ESCALATION_PATTERNS`, etc.) are calibrated for Spanish. Supporting additional languages would require language-specific constant sets. The Decision Engine would need to accept a `language` parameter and dispatch to the appropriate constant set. This is a significant change to the internal structure of `decision_engine.py` but would not change the import interface.

**Integration with ticketing systems.** Connecting `recommend_improvements` output to ticketing systems (Jira, Linear) requires an outbound integration layer. This should be implemented as a separate module that consumes tool outputs — not by modifying tools themselves.

### Constraints for future evolution

Any change to the architecture must respect these constraints:

1. `decision_engine.py` must remain the single source of truth for all analytical logic.
2. No tool's observable output may change without an explicit version increment.
3. The import interface `import decision_engine as _de` must remain stable.
4. New tools follow the same pattern: `@mcp.tool()` decorator, `_de.*` calls, formatted return.
5. Internal duplication in `decision_engine.py` must not re-emerge. Any new function must be verified as unique before being added.

---

*FIN Architect MCP v1.0.0 — Architecture document.*
