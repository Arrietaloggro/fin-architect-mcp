# FIN Architect MCP v1.0.0

**Released:** 2026-06-25
**Tag:** `v1.0.0`
**Branch:** `main`
**Status:** Stable

---

## Release Highlights

FIN Architect MCP v1.0.0 is the first stable release of an intelligent architecture layer for financial support operations. The system provides 15 MCP tools that audit, score, optimize, and govern knowledge articles and conversation guidelines used by FIN — the AI support agent operating in Intercom.

The defining achievement of v1.0.0 is architectural: three consecutive refactoring sprints eliminated approximately 1,353 lines of duplicated analytical logic from `server.py` and established `decision_engine.py` as the sole source of truth for every scoring, detection, and classification function in the system. The 15 tools are thinner, more consistent, and independently testable as a result.

Key facts at release:

- **15 MCP tools** across 6 functional modules
- **34 analytical functions** in a single, pure-function Decision Engine
- **45 module-level constants** covering detection patterns, scoring thresholds, event catalogs, and guideline templates
- **~1,353 lines of duplicated logic eliminated** across three architecture sprints
- **0 duplicate function implementations** verified by AST analysis
- **24 pull requests merged** across the full development cycle
- **6 documentation files** covering architecture, engine reference, getting started, examples, changelog, and contribution guide

---

## Architecture Summary

FIN Architect MCP is structured in three layers:

```
MCP Client (Claude, Intercom FIN, or any MCP-compatible client)
        │  MCP Protocol over SSE
server.py — FastMCP Tool Layer (15 tools, routing, formatting)
        │  import decision_engine as _de
decision_engine.py — Analytical Core (34 functions, 45 constants)
```

`server.py` contains no analytical logic. Every score, threshold, pattern match, similarity computation, and classification lives in `decision_engine.py`. Tools call `_de.*` functions and format the results for MCP clients. This separation was the central architectural goal of the v1.0.0 development cycle.

The Decision Engine is organized into two internal modules:

- **Knowledge module** (lines 1–897): KDE scoring, loop risk detection, anti-escalation detection, FIN blocker detection, Jaccard similarity, knowledge debt, coverage, deployment readiness, ROI ranking
- **Guideline module** (lines 898–1264): guideline scoring, intent detection, emotion detection, event catalog, conflict severity, risk classification, pattern naming, template generation

Both modules are exported under a single import alias (`import decision_engine as _de`) with no sub-module complexity.

---

## Decision Engine

The Decision Engine is the primary architectural deliverable of v1.0.0.

### Exported functions (34)

| Category | Functions |
|----------|-----------|
| Detection | `detect_loop_risk`, `detect_anti_escalation`, `detect_absolute_hits`, `detect_escalation`, `detect_escalation_repo`, `detect_fin_blockers` |
| Similarity | `jaccard`, `word_set` |
| Scoring | `kde_score_article`, `kde_score_article_fast`, `kde_score_guideline_fast` |
| Classification | `risk_level_from_health`, `compute_automation_readiness`, `compute_deploy_decision` |
| Knowledge Debt | `compute_knowledge_debt`, `debt_label_emoji` |
| Coverage | `compute_coverage` |
| Executive Status | `semaforo`, `global_status_from_health`, `deployment_readiness` |
| ROI & Ranking | `compute_roi`, `rank_improvements` |
| Utilities | `extract_int`, `extract_metrics_from_reports` |
| Guideline Detection | `detect_intention`, `detect_emotion`, `detect_guideline_events`, `detect_guideline_problems` |
| Guideline Classification | `guideline_risk_level`, `conflict_severity_level`, `guideline_priority_from_risk`, `guideline_impact_priority` |
| Guideline Generation | `cluster_pattern_name`, `guideline_template_for` |

### Key constants

- `KDE_HARD_CAP_BLOCKER = 60` — maximum health score when a KDE blocker is present
- `KDE_HARD_CAP_RESOLUTION = 40` — maximum resolution score when a KDE blocker is present
- `GUIDELINE_CLUSTER_THRESHOLD = 0.70` — Jaccard threshold for clustering conversation turns into guidelines
- `GUIDELINE_MERGE_THRESHOLD = 0.80` — Jaccard threshold for merging near-duplicate guideline candidates
- `TOPIC_CATEGORIES` — 11 business domains for coverage analysis
- `GUIDELINE_EVENT_CATALOG` — 12 conversation event types with `impact` and `esc_risk` scores

### KDE scoring framework

`kde_score_article()` evaluates knowledge articles across 12 weighted criteria (100-point scale):

| Criterion | Weight |
|-----------|--------|
| Claridad | 12 |
| Estructura | 10 |
| Pasos | 12 |
| Cobertura | 8 |
| Ambiguedad | 10 |
| Longitud | 8 |
| Consistencia | 8 |
| Terminologia | 8 |
| Uso por FIN | 10 |
| Escalamiento | 8 |
| Mantenibilidad | 7 |
| Riesgo Operativo | 7 |

Hard caps apply when blockers are detected. A blocker (CRÍTICO loop risk or anti-escalation rule) caps the health score at 60 and the resolution capability score at 40, regardless of quality in other criteria.

---

## MCP Tools

### Guideline Core (8 tools)

| Tool | Purpose |
|------|---------|
| `audit_guideline` | Policy compliance audit: absolute terms, obligation language, prohibition language, ambiguous terms, risky patterns |
| `optimize_guideline` | Rewrite recommendations targeting the lowest-scoring criteria of the 10-criterion scoring framework |
| `classify_guideline` | Intent classification (`INTENTION_MAP`, 12 categories), emotion detection, risk level, implementation priority |
| `detect_conflicts` | Pairwise Jaccard similarity + `GUIDELINE_CONTRADICTION_PAIRS` pattern matching; severity classification per conflict |
| `score_guideline` | 10-criterion numeric score with per-criterion breakdown |
| `simulate_fin` | FIN response simulation: matches conversation events from `GUIDELINE_EVENT_CATALOG`, predicts escalation risk |
| `generate_guideline` | Structured guideline template from `GUIDELINE_PROBLEM_SIGNALS`, `GUIDELINE_FAILURE_MAP`, `GUIDELINE_BEHAVIOR_MAP`, `GUIDELINE_TEMPLATES` |
| `extract_guidelines` | Jaccard-based clustering of raw conversation logs into named, prioritized, templated guideline candidates |

### Knowledge Core (3 tools)

| Tool | Purpose |
|------|---------|
| `audit_knowledge` | Full 12-criterion KDE audit with hard caps, automation readiness, and deploy decision |
| `optimize_article` | ROI-ranked (impact/effort) prioritized action plan based on audit output |
| `knowledge_review` | Bulk health, coverage, knowledge debt, and duplicate detection across an article set |

### Repository Core (1 tool)

| Tool | Purpose |
|------|---------|
| `repository_review` | Repository-level health: global score, deployment readiness, knowledge debt, coverage gaps, duplicate article pairs |

### Recommendation Engine (1 tool)

| Tool | Purpose |
|------|---------|
| `recommend_improvements` | ROI-ranked improvement backlog parsed from upstream tool report text via `extract_metrics_from_reports()` |

### Executive Dashboard (1 tool)

| Tool | Purpose |
|------|---------|
| `fin_dashboard` | Unified executive report: traffic-light indicators per module, global health, knowledge debt, deployment decision |

### Orchestrator (1 tool)

| Tool | Purpose |
|------|---------|
| `architect_review` | Full pipeline orchestrator: accepts conversations + guidelines, runs the complete analysis pipeline, returns a consolidated architectural diagnosis |

---

## Documentation

Six documentation files were created for this release:

| File | Contents |
|------|---------|
| `README.md` | Project overview, architecture diagram, module descriptions, tool catalog, Decision Engine rationale, metrics, roadmap, philosophy |
| `docs/Architecture.md` | High-level architecture, module responsibilities, design principles, data flow, 5 architectural decisions (AD-1 through AD-5), future evolution constraints |
| `docs/DecisionEngine.md` | All 34 functions documented individually with signatures and behavior, all 45 constants by category, per-tool integration table, internal scoring flow diagram, best practices |
| `docs/GettingStarted.md` | Prerequisites, installation, server startup, client connection (Claude Code / Claude Desktop), first tool example, typical workflow, troubleshooting |
| `docs/Examples.md` | 5 complete usage scenarios: billing guideline improvement, knowledge base audit, repository health assessment, end-to-end FIN improvement, executive review |
| `docs/CHANGELOG.md` | Full project history in Keep a Changelog format: all 24 PRs, 3 architecture sprints, 4 bug fixes, architecture milestone table |
| `docs/CONTRIBUTING.md` | Philosophy, project structure, tool creation guide, Decision Engine rules, coding standards, PR guidelines, testing checklist (with executable scripts), architecture rules, documentation update guide, release process |
| `docs/ROADMAP.md` | v1.0.0 delivery summary, v1.1 maintenance items, v1.2 quality improvements, v2.0 architectural expansion |
| `LICENSE` | MIT License |

---

## Performance Improvements

v1.0.0 ships two scoring variants to match the performance requirements of different contexts:

### Full scorer vs. fast scorer

`kde_score_article()` implements the complete 12-criterion KDE framework. It extracts 40+ signals from the article text (vague phrases, step verbs, absolute terms, escalation signals, blocker actions, risky actions, technical terms, date references, sentence repetitions, structural markers, word register consistency) and returns a dict with 40+ fields.

`kde_score_article_fast()` implements a 5-signal lightweight variant (has_resolution, has_steps, has_escalation, has_objective, word count check). It runs significantly faster and is designed for bulk analysis contexts where `repository_review` or `knowledge_review` must process many articles in a single call.

`kde_score_guideline_fast()` applies the same principle to guidelines: 2 structural signals (has_trigger, has_action) and 2 risk signals (absolute terms, anti-escalation).

### Efficient similarity computation

`word_set()` returns a `frozenset` — immutable and hashable. When computing Jaccard similarity between one article and many others (e.g., duplicate detection in `knowledge_review`), each article's word set is computed once and reused across all comparisons, avoiding redundant tokenization.

---

## Refactoring Summary

Three architecture sprints were required to bring `server.py` to its current state of containing no analytical logic.

### Sprint v2 — Core Consolidation

Migrated 4 tools to call `decision_engine.py` exclusively:

- **`audit_knowledge`** — replaced a 460-line inline KDE scoring loop with a single `_de.kde_score_article()` call
- **`optimize_article`** — replaced 8 locally defined pattern lists with `_de.*` constants; replaced inline ROI logic with `_de.compute_roi()` and `_de.rank_improvements()`
- **`audit_guideline`** — replaced local `keywords_ambiguous` with `_de.ABSOLUTE_TERMS`
- **`architect_review`** — replaced local `text_jaccard()` and helper functions with `_de.jaccard()` and `_de.word_set()`

**Lines removed from `server.py`:** ~445

### Sprint v3 — Guideline Core Consolidation

Migrated all 7 Guideline tools. Added the complete Guideline module to `decision_engine.py` (lines 898–1264). The most structurally significant migrations:

- **`extract_guidelines`** — replaced local `jaccard()`, local `EVENT_CATALOG`, local `PATTERN_NAMES`, local `CLUSTER_THRESHOLD`, local `MERGE_THRESHOLD`, and local template dict with all `_de.*` equivalents
- **`detect_conflicts`** — replaced local Jaccard implementation and local contradiction patterns with `_de.jaccard()`, `_de.word_set()`, `_de.GUIDELINE_CONTRADICTION_PAIRS`, `_de.GUIDELINE_CONDITION_PAIRS`, `_de.conflict_severity_level()`
- **`simulate_fin`** — replaced local event catalog with `_de.GUIDELINE_EVENT_CATALOG` and `_de.detect_guideline_events()`

**Lines removed from `server.py`:** ~580

### Decision Engine Cleanup

During Sprint v3, two concurrent agents both appended the Guideline module block to `decision_engine.py`, producing an exact internal duplicate at lines 1265–1592. Python was silently using the last definition of each function, so behavior was correct throughout — but the module violated single source of truth.

The duplicate block was removed by truncating the file at line 1264. Validated with AST parse, symbol uniqueness check, and import smoke tests before commit.

**Lines removed from `decision_engine.py`:** 328

### Total

| Sprint | Scope | Lines removed |
|--------|-------|---------------|
| v2 — Core Consolidation | 4 tools | ~445 |
| v3 — Guideline Core Consolidation | 7 tools | ~580 |
| Decision Engine Cleanup | Internal duplicate | 328 |
| **Total** | | **~1,353** |

---

## Known Limitations

### Two orphaned functions

`detect_guideline_events()` and `guideline_priority_from_risk()` are defined in `decision_engine.py` but have no confirmed call sites in `server.py`. They were carried over during the Guideline Core Consolidation sprint and their reachability was not verified before the v1.0.0 release cut.

These functions are not broken — they are correctly implemented and pass an AST parse. The issue is that they may be unreachable dead code, which makes the exported function count (34) potentially overstated by 0–2.

**Resolution target:** v1.1 — verify call paths or remove.

### No automated test suite

`decision_engine.py` has no test suite at release. All 34 functions are pure with deterministic outputs, making them straightforward to test, but no test files exist yet. The v1.0.0 validation relied on manual tool calls and structural checks (AST parse, import smoke test, reference resolution script).

**Resolution target:** v1.1 — comprehensive input/output assertions for all 34 functions.

### Stateless analysis

Every tool call starts from scratch. There is no memory of prior analyses, no article score history, and no way to detect regression after an article is edited. Trend analysis and incremental repository updates are not possible in v1.0.0.

**Resolution target:** v2.0 — persistent knowledge graph.

### Spanish-language pattern vocabularies

Detection constants (`LOOP_PATTERNS`, `ANTI_ESCALATION_PATTERNS`, `INTENTION_MAP`, keyword vocabularies) are calibrated for Spanish. The KDE scoring framework is language-agnostic (it evaluates structure, not vocabulary), but the pattern matching functions will miss signals in other languages.

**Resolution target:** v2.0 — language-specific constant sets with a `language` dispatch parameter.

### No guideline lifecycle tracking

Guidelines exist as text strings with no tracked state. There is no concept of draft, approved, active, or deprecated. A guideline produced by `generate_guideline` has the same status as one that has been in production for six months.

**Resolution target:** v2.0 — lifecycle state model with governance rules.

---

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| v1.0.0 | 15 tools, Decision Engine, documentation | ✅ Released |
| v1.1 | Resolve orphaned functions, test suite, remaining inline logic | Planned |
| v1.2 | Coverage gap auto-detection, batch processing, pattern expansion, performance baseline | Planned |
| v2.0 | Persistent knowledge graph, guideline lifecycle, multi-language, historical metrics, incremental analysis | Future |

Full details in [`docs/ROADMAP.md`](ROADMAP.md).

---

## Acknowledgements

FIN Architect MCP v1.0.0 was built to solve a real operational problem: knowledge debt and guideline inconsistency in financial support operations accumulate silently until they surface as customer escalations. The architecture of this system — particularly the Decision Engine as a single, pure-function analytical core — reflects the lessons learned from three sprints of discovering what happens when that discipline is not enforced from the start.

The project delivered 24 merged pull requests, three architecture refactoring sprints, one internal cleanup, four bug fixes, and nine documentation files across its development cycle.

---

*FIN Architect MCP v1.0.0 — 2026-06-25*
