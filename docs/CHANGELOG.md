# Changelog

All notable changes to FIN Architect MCP are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-06-25

### Summary

FIN Architect MCP v1.0.0 is the first stable release of the project. It delivers 15 MCP tools across 6 modules, a validated Decision Engine as the sole analytical source of truth, and complete project documentation. Three architecture sprints eliminated approximately 1,500 lines of duplicated logic from `server.py` and established `decision_engine.py` as the central module for all scoring, detection, classification, and ranking functions.

---

### Added

#### Initial Architecture — 2026-06-24

- Created project skeleton: `main.py` (FastAPI health endpoint), `server.py` (FastMCP tool layer), `requirements.txt`, `Procfile`, `railway.toml`
- Established MCP server using `FastMCP` with SSE transport (`/sse` endpoint) and health route (`/`)
- Configured Railway deployment: `startCommand = "python server.py"`, health check at `/`, restart policy `on_failure`
- Added `.gitignore`

#### Guideline Core — 2026-06-24

- **`classify_guideline`** — Classifies a guideline by intent, risk level, and implementation priority (PR #1)
- **`detect_conflicts`** — Detects semantic conflicts across a guideline library using pairwise comparison (PR #2)
- **`score_guideline`** — Scores a guideline across 10 structured criteria (PR #3)
- **`simulate_fin`** — Simulates FIN's response behavior given a guideline as context; predicts escalation probability and resolution paths (PR #4)
- **`generate_guideline`** — Generates a structured guideline template from detected problem signals and behavior maps (PR #5)
- **`extract_guidelines`** — Initial implementation: extracts guideline candidates from raw conversation logs (PR #6)
- **`extract_guidelines` v2** — Rewrote with event-based detection using a conversation event catalog (PR #7)
- **`extract_guidelines` v3** — Added Jaccard-based semantic clustering; introduced cluster threshold and merge threshold; added pattern name resolution (PR #8)

#### Orchestrator — 2026-06-24 / 2026-06-25

- **`architect_review` v1** — Initial orchestrator tool: end-to-end pipeline accepting conversations and guidelines, returning a consolidated diagnosis (PR #9)
- **`architect_review` v2** — Added: main findings section, executive consulting summary, prioritized action plan, product maturity assessment, architect conclusion, automatic consolidation for guidelines scoring ≥90% (PR #10)
- **`architect_review` v3** — Introduced the ARCHITECT DECISION ENGINE internal pipeline; added cross-tool routing and structured report sections (PR #11)
- **`architect_review` v4** — Enterprise-grade executive report format; added FIN coverage matrix, maintainability index, confidence score, orphaned guideline detection, impact simulation, differentiated PM and Support team summaries (PR #13, PR #14)

#### Knowledge Core — 2026-06-24 / 2026-06-25

- **`audit_knowledge` v1** — Initial knowledge article audit tool; FIN Knowledge Core Phase 2 (PR #15)
- **`audit_knowledge` v2** — Upgraded to 9 AI-conversational auditor capabilities (PR #16)
- **`audit_knowledge` v3** — Introduced the Knowledge Decision Engine (KDE): 12-criterion weighted scoring framework (100-point scale), loop risk detection, anti-escalation detection, FIN blocker detection, hard caps (`KDE_HARD_CAP_BLOCKER=60`, `KDE_HARD_CAP_RESOLUTION=40`), automation readiness classification, deploy decision (PR #17)
- **`optimize_article`** — Generates a prioritized optimization plan for a knowledge article; uses ROI ranking (impact/effort ratio) to order recommendations (PR #18)
- **`knowledge_review`** — Bulk review tool: evaluates coverage, knowledge debt, and health across a full article set; detects duplicate articles via Jaccard similarity (PR #19)

#### Repository Core and Dashboard — 2026-06-25

- **`repository_review`** — Evaluates the entire knowledge repository as a system: global health score, duplicate detection, coverage gaps, deployment readiness (PR #21)
- **`recommend_improvements`** — Surfaces the highest-ROI improvements across the repository; parses upstream tool outputs and produces a ranked improvement backlog (PR #22)
- **`fin_dashboard`** — Unified executive health report: aggregates all module outputs, applies traffic-light indicators per module, returns deployment readiness decision (PR #23)

#### Project documentation — 2026-06-25

- `docs/PROJECT_CONTEXT.md` — Technical architecture context and sprint history (PR #20)
- `README.md` — Official project README: vision, architecture diagram, core modules, features, workflow, tool catalog, Decision Engine rationale, project metrics, roadmap, repository structure, philosophy
- `docs/Architecture.md` — Complete system architecture documentation: architectural goals, high-level diagram, module descriptions, design principles, data flow, internal components, extension guide, five architectural decisions (AD-1 through AD-5), future evolution
- `docs/DecisionEngine.md` — Complete Decision Engine reference: all 34 exported functions documented individually, all 45 constants by category, integration pattern per tool, internal scoring flow, best practices
- `docs/GettingStarted.md` — First-run guide: prerequisites, installation, server startup, client connection, repository structure, first tool example, typical workflow, troubleshooting, best practices
- `docs/Examples.md` — Official usage scenarios catalog: five complete examples with context, input, flow, expected output, and interpretation

---

### Changed

#### Sprint v1 — Decision Engine Introduction — 2026-06-25

- Introduced `decision_engine.py` as the central analytical module (PR #24)
- Migrated core analytical logic from `server.py` into `decision_engine.py`:
  - KDE scoring algorithm (`kde_score_article`, `kde_score_article_fast`, `kde_score_guideline_fast`)
  - Detection functions (`detect_loop_risk`, `detect_anti_escalation`, `detect_absolute_hits`, `detect_escalation`, `detect_escalation_repo`, `detect_fin_blockers`)
  - Similarity functions (`jaccard`, `word_set`)
  - Classification functions (`risk_level_from_health`, `compute_automation_readiness`, `compute_deploy_decision`)
  - Knowledge debt functions (`compute_knowledge_debt`, `debt_label_emoji`)
  - Coverage function (`compute_coverage`)
  - Executive status functions (`semaforo`, `global_status_from_health`, `deployment_readiness`)
  - ROI functions (`compute_roi`, `rank_improvements`)
  - Utility functions (`extract_int`, `extract_metrics_from_reports`)
  - All pattern constants (45 module-level constants)
- All tools in `server.py` now import `decision_engine as _de` and call `_de.*` functions

#### Sprint v2 — Core Consolidation — 2026-06-25

- **`audit_knowledge`** — Replaced 460-line inline KDE scoring loop with single `_de.kde_score_article()` call; removed local constant copies
- **`optimize_article`** — Replaced 8 locally defined pattern lists with `_de.LOOP_PATTERNS`, `_de.VAGUE_PHRASES`, `_de.STEP_VERBS`, and other `_de.*` constants; replaced inline ROI logic with `_de.compute_roi()` and `_de.rank_improvements()`
- **`audit_guideline`** — Replaced local `keywords_ambiguous` list with `_de.ABSOLUTE_TERMS`
- **`architect_review`** — Replaced local `text_jaccard()` and similarity helpers with `_de.jaccard()` and `_de.word_set()`
- Net result: approximately −445 lines removed from `server.py`

#### Sprint v3 — Guideline Core Consolidation — 2026-06-25

- Migrated all 7 Guideline tools to use `decision_engine.py` exclusively. Added Guideline module to `decision_engine.py` (lines 898–1264):
  - **`optimize_guideline`** — Replaced inline ambiguous term lists with `_de.GUIDELINE_AMBIGUOUS_TERMS`, `_de.GUIDELINE_RISKY_PATTERNS`, `_de.kde_score_guideline_fast()`
  - **`classify_guideline`** — Replaced local intent and emotion detection with `_de.detect_intention()`, `_de.detect_emotion()`, `_de.guideline_risk_level()`, `_de.guideline_priority_from_risk()`, `_de.guideline_impact_priority()`
  - **`detect_conflicts`** — Replaced local Jaccard implementation with `_de.jaccard()` + `_de.word_set()`; replaced local contradiction list with `_de.GUIDELINE_CONTRADICTION_PAIRS` and `_de.GUIDELINE_CONDITION_PAIRS`; replaced inline severity logic with `_de.conflict_severity_level()`
  - **`score_guideline`** — Replaced inline scoring with `_de.kde_score_guideline_fast()`; replaced local word lists with `_de.GUIDELINE_AMBIGUOUS_TERMS`, `_de.GUIDELINE_RISKY_PATTERNS`, `_de.GUIDELINE_ACTION_VERBS`, `_de.GUIDELINE_SPECIFIC_SIGNALS`
  - **`simulate_fin`** — Replaced local event catalog and detection with `_de.GUIDELINE_EVENT_CATALOG`, `_de.detect_guideline_events()`, `_de.detect_intention()`, `_de.detect_emotion()`
  - **`generate_guideline`** — Replaced local problem signal maps with `_de.GUIDELINE_PROBLEM_SIGNALS`, `_de.GUIDELINE_FAILURE_MAP`, `_de.GUIDELINE_BEHAVIOR_MAP`, `_de.GUIDELINE_TEMPLATES`; replaced inline impact logic with `_de.guideline_impact_priority()`
  - **`extract_guidelines`** — Replaced local `jaccard()` function, local `EVENT_CATALOG`, local `PATTERN_NAMES`, local `CLUSTER_THRESHOLD`, local `MERGE_THRESHOLD`, and local template dict with all `_de.*` equivalents: `_de.jaccard()`, `_de.word_set()`, `_de.GUIDELINE_EVENT_CATALOG`, `_de.detect_guideline_events()`, `_de.GUIDELINE_CLUSTER_THRESHOLD`, `_de.GUIDELINE_MERGE_THRESHOLD`, `_de.GUIDELINE_PATTERN_NAMES`, `_de.cluster_pattern_name()`, `_de.guideline_template_for()`, `_de.guideline_impact_priority()`
- Net result: approximately −580 lines removed from `server.py`

---

### Fixed

- **`_debt_raw` NameError** — Variable eliminated during refactor but one reference remained in `repository_review` and `fin_dashboard`; replaced with inline `compute_knowledge_debt()` call
- **`KeyError: 'problems'`** — `kde_score_article()` did not include a `"problems"` key in its return dict; added `"problems": res_factors` alias for backward compatibility with `knowledge_review` callers
- **`'dict' object has no attribute 'lower'`** — `architect_review` passed dict objects where string inputs were expected in a similarity check; fixed by enforcing string type before calling `_de.word_set()`
- **Duplicate Guideline module block in `decision_engine.py`** — During Sprint v3, two concurrent agents both appended the Guideline module block to `decision_engine.py`, producing an exact duplicate at lines 1265–1592. Python was silently using the last definition of each function. Removed by truncating the file at line 1264. Validated with AST parse, symbol uniqueness check, and import smoke tests. Net: −328 lines removed from `decision_engine.py`.

---

### Architecture milestones

| Milestone | Description | Lines removed |
|-----------|-------------|---------------|
| Sprint v1 — Decision Engine | Established `decision_engine.py`; migrated Knowledge module | — |
| Sprint v2 — Core Consolidation | Migrated `audit_knowledge`, `optimize_article`, `audit_guideline`, `architect_review` | ~445 |
| Sprint v3 — Guideline Core Consolidation | Migrated all 7 Guideline tools; added Guideline module to DE | ~580 |
| Decision Engine Cleanup | Removed internal duplicate Guideline block from `decision_engine.py` | 328 |
| **Total** | | **~1,353** |

---

### State at release

| Metric | Value |
|--------|-------|
| MCP tools | 15 |
| Decision Engine functions | 34 |
| Decision Engine constants | 45 |
| `decision_engine.py` lines | 1,264 |
| `server.py` lines | 6,634 |
| Duplicate function implementations | 0 |
| Architecture sprints | 3 |
| PRs merged | 24+ |
| Release status | Stable |

---

[1.0.0]: https://github.com/arrietaloggro/fin-architect-mcp/releases/tag/v1.0.0
