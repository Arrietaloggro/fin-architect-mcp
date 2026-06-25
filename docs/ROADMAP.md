# FIN Architect MCP Roadmap

This roadmap is grounded in the real state of the project. Every item listed as completed was delivered. Every item listed as planned was identified during development as a real gap or improvement opportunity. Nothing here is aspirational without basis.

---

## v1.0.0 — Stable Release ✅

**Released:** 2026-06-25
**Status:** Complete

### Delivered

#### Guideline Core (8 tools)
- `classify_guideline` — intent, risk level, implementation priority classification
- `detect_conflicts` — pairwise conflict detection across a guideline library using Jaccard similarity
- `score_guideline` — 10-criterion guideline scoring framework
- `simulate_fin` — FIN response simulation and escalation probability prediction
- `generate_guideline` — structured guideline template generation from detected problem signals
- `extract_guidelines` — Jaccard-based clustering of conversation logs into guideline candidates
- `audit_guideline` — policy compliance and ambiguity audit
- `optimize_guideline` — rewrite recommendations targeting lowest-scoring criteria

#### Knowledge Core (3 tools)
- `audit_knowledge` — full KDE audit across 12 weighted criteria (100-point scale) with hard caps, loop risk detection, anti-escalation detection, FIN blocker detection, automation readiness, and deploy decision
- `optimize_article` — ROI-ranked optimization plan per article
- `knowledge_review` — bulk coverage, debt, and duplicate analysis across article sets

#### Repository Core (1 tool)
- `repository_review` — full repository health: global score, deployment readiness, coverage gaps, duplicate detection, knowledge debt

#### Recommendation Engine (1 tool)
- `recommend_improvements` — ROI-ranked improvement backlog parsed from upstream tool outputs

#### Executive Dashboard (1 tool)
- `fin_dashboard` — unified executive health report with traffic-light indicators and deployment decision

#### Orchestrator (1 tool)
- `architect_review` — end-to-end pipeline from raw conversations to consolidated architectural diagnosis

#### Decision Engine
- `decision_engine.py` established as the sole source of truth for all analytical logic
- 34 exported functions across two internal modules (Knowledge lines 1–897, Guideline lines 898–1264)
- 45 module-level constants
- Three architecture sprints eliminated ~1,353 lines of duplicated logic from `server.py`
- Zero duplicate function implementations at release

#### Documentation
- `README.md` — official project README
- `docs/Architecture.md` — complete system architecture
- `docs/DecisionEngine.md` — complete Decision Engine reference
- `docs/GettingStarted.md` — first-run guide
- `docs/Examples.md` — five complete usage scenarios
- `docs/CHANGELOG.md` — full project history in Keep a Changelog format
- `docs/CONTRIBUTING.md` — contribution guide with architecture rules and testing checklist
- `LICENSE` — MIT License

---

## v1.1 — Maintenance Release

**Status:** Planned
**Scope:** Hardening the existing architecture. No new tools. No behavior changes.

### Resolve 2 orphaned functions

`detect_guideline_events()` and `guideline_priority_from_risk()` are defined in `decision_engine.py` but have no confirmed call sites in `server.py`. This was flagged during v1.0 validation and deferred.

Resolution path: verify whether each function is reachable from any tool. If it is called indirectly through a data structure (e.g., via a dict dispatch), document the call path. If it is genuinely unreachable, remove it. Leaving unexported dead code in the analytical core creates misleading documentation — the function count would be reported as 34 when the effective count is 32.

**Impact:** no behavior change. Reduces the exported surface by 0–2 functions. Updates `docs/DecisionEngine.md` function count.

### Test suite for `decision_engine.py`

All 34 exported functions are pure — same inputs always produce the same outputs, no side effects, no I/O. This makes the analytical core trivially testable without mocking. A test suite does not exist yet.

Scope: input/output assertions for each function in `decision_engine.py`. Minimum coverage targets:

- `kde_score_article()` — at least 5 article profiles: minimal, healthy, CRÍTICO loop, anti-escalation blocker, FIN blockers present
- `kde_score_article_fast()` — at least 3 profiles: healthy, blocked, no-content
- `detect_loop_risk()` — both pattern sets (`use_repo_patterns=True` and `False`), all four risk levels
- `jaccard()` — identical sets, disjoint sets, partial overlap, empty set
- `compute_knowledge_debt()` — zero debt, MEDIO, CRÍTICO
- `deployment_readiness()` — all three outcomes (READY, READY WITH RECOMMENDATIONS, NOT READY)
- All Guideline module functions with representative inputs

A passing test suite means: every tool that calls `_de.*` has implicit regression coverage. If a threshold change in `decision_engine.py` breaks expected output, the test catches it before the change reaches production.

### Centralize remaining inline logic

During v1.0, three sprints migrated the most significant duplicate logic. Post-release review may surface smaller inline computations in `server.py` that belong in `decision_engine.py`. Any such logic found during v1.1 work should be migrated following the contribution rules in `docs/CONTRIBUTING.md`.

### Documentation corrections

Correct any inaccuracies in existing documentation discovered after release. Specifically:

- Verify function count (34) and constant count (45) after resolving orphaned functions.
- Update `docs/CHANGELOG.md` with the v1.1 release entry.
- Update the version badge in `README.md`.

---

## v1.2 — Quality Improvements

**Status:** Planned
**Scope:** Capability improvements within the existing architecture. Additive only — no existing tool signatures change.

### Coverage gap auto-detection

`repository_review` currently reports missing `TOPIC_CATEGORIES` when called. A proactive mode would surface coverage gaps on demand without requiring a full repository analysis — useful when a single new article is added and the operator wants to know which category it covers.

Implementation: a lightweight tool or an optional parameter on `knowledge_review` that accepts a single article text and returns which `TOPIC_CATEGORIES` it covers and which remain unrepresented across the known article set.

This is additive: no existing tool changes. All gap logic reuses `_de.compute_coverage()`.

### Batch processing interface

`knowledge_review` and `repository_review` already process article sets. For large repositories (50+ articles), the current interface requires the client to assemble all article texts into a single call. A batch mode with explicit progress signaling would allow incremental processing without requiring the client to hold the full set in memory.

Implementation path: optional parameters on existing tools, not new tools. The analytical logic remains unchanged — `_de.kde_score_article_fast()` already handles individual items. Batch mode adds chunking and progress metadata to the return format.

### Pattern vocabulary expansion

The detection constants in `decision_engine.py` (`LOOP_PATTERNS`, `VAGUE_PHRASES`, `GUIDELINE_RISKY_PATTERNS`, etc.) were defined based on the initial operational domain. As the system is used in production, false negatives and false positives will surface patterns that should be added or removed.

v1.2 formalizes this as a maintenance activity: reviewing detection accuracy against real conversation logs and updating the relevant constants in `decision_engine.py`. No function signatures change. All tools that use the updated constants receive the improvement automatically.

### Performance baseline

No performance benchmarks exist for the current system. v1.2 establishes baseline timing for:

- `kde_score_article()` on articles of varying length (100, 500, 1000 words)
- `kde_score_article_fast()` on sets of 10, 50, 100 articles
- `extract_guidelines()` on conversation sets of 10, 50, 100 turns
- `jaccard()` on sets of varying size

These baselines inform future optimization decisions and detect regressions.

---

## v2.0 — Architectural Expansion

**Status:** Future
**Scope:** Changes that require new infrastructure or extend the data model. The Decision Engine constraint — `decision_engine.py` remains the sole source of truth for analytical logic — holds in v2.0. New infrastructure sits above the existing layers, not inside them.

### Persistent knowledge graph

The current system is stateless: every call starts from scratch with no memory of prior analyses. A persistent knowledge graph would allow:

- Tracking article health over time (score history per article ID)
- Detecting regression after edits (health decreased since last audit)
- Surfacing trends (which categories are improving, which are degrading)
- Alerting when a previously healthy article drops below a threshold

**Architectural constraint:** `decision_engine.py` must remain stateless. The persistence layer sits between `server.py` and an external store — a separate module that reads from and writes to storage, then passes data to `_de.*` functions for analysis. The analytical functions do not change.

**Storage decision required:** the choice of storage backend (SQLite for local use, PostgreSQL for production, a graph database for relationship queries) is a deployment decision that must be made before implementation begins. This decision is deferred to the v2.0 planning phase.

### Guideline lifecycle management

Guidelines currently exist as text strings with no tracked state. A lifecycle model would add:

- States: `draft → under_review → approved → active → deprecated`
- Transition rules: a guideline cannot move from `draft` to `active` without passing `audit_guideline` and `detect_conflicts`
- History: when was each state transition made, by whom

**Implementation path:** optional `state` and `history` fields on guideline inputs. Tools that receive guidelines with state metadata respect the transition rules. Tools that receive guidelines without state metadata behave as they do today. This is backward-compatible if handled via optional parameters.

The analytical functions (`guideline_risk_level`, `conflict_severity_level`, etc.) do not change. The lifecycle layer adds governance around when tools may be called, not what they compute.

### Multi-language support

The current detection constants (`LOOP_PATTERNS`, `ANTI_ESCALATION_PATTERNS`, `INTENTION_MAP`, keyword vocabularies) are calibrated for Spanish. The KDE scoring framework is language-agnostic by design — it operates on structural signals that exist in any language — but the pattern vocabularies are language-specific.

Supporting English or Portuguese would require:

- Language-specific constant sets in `decision_engine.py` (e.g., `LOOP_PATTERNS_EN`, `INTENTION_MAP_EN`)
- A `language` parameter on functions that currently use language-specific patterns
- Dispatch logic inside those functions: `patterns = LOOP_PATTERNS_EN if language == 'en' else LOOP_PATTERNS`

**Architectural constraint:** the import interface (`import decision_engine as _de`) does not change. Tools call `_de.detect_loop_risk(text, language='en')`. The internal dispatch is transparent to the caller.

### Historical metrics and trend analysis

Building on the persistent knowledge graph, historical metrics would surface patterns across time:

- Which articles have been consistently low-scoring for 30+ days
- Which categories have the highest rate of new blockers being introduced
- Whether knowledge debt is increasing or decreasing over time
- Which guidelines have the highest conflict detection frequency

This is a reporting layer, not an analytical layer. The `_de.*` functions produce the scores. The historical metrics layer stores them, aggregates them, and surfaces the trends. `fin_dashboard` could be extended to include a trend section when historical data is available.

### Incremental repository analysis

In the current model, `repository_review` analyzes all articles in a single call. For repositories that change incrementally (one or two articles updated per day), re-analyzing the full set is wasteful.

Incremental analysis would track which articles have changed since the last full analysis and re-score only those articles, updating the repository-level metrics based on the delta. This requires the persistent knowledge graph (articles need IDs and score histories) and is therefore a v2.0 item contingent on that infrastructure being in place.

---

## Architectural invariants across all versions

These constraints apply to v1.1, v1.2, v2.0, and any version beyond:

1. `decision_engine.py` is the sole source of truth for analytical functions.
2. All functions in `decision_engine.py` remain pure — no side effects, no I/O.
3. All thresholds are named constants — no inline magic numbers.
4. The import interface `import decision_engine as _de` is stable.
5. No existing tool's observable output changes without an explicit version increment.
6. Internal duplication in `decision_engine.py` must not re-emerge.

---

*FIN Architect MCP — Roadmap based on real project state as of v1.0.0.*
