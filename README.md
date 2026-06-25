# FIN Architect MCP

> **Intelligent architecture layer for financial support operations** — audit, optimize, and govern knowledge articles and conversation guidelines through a unified Decision Engine.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/arrietaloggro/fin-architect-mcp)
[![Status](https://img.shields.io/badge/status-stable-green.svg)]()
[![MCP](https://img.shields.io/badge/protocol-MCP-purple.svg)]()
[![License](https://img.shields.io/badge/license-MIT-gray.svg)]()

---

## Vision

FIN Architect MCP was built to solve a structural problem in financial support operations: knowledge and conversation guidelines accumulate debt silently. Articles become outdated, guidelines conflict, and no system surfaces the risk before it reaches the customer.

This project provides a **Model Context Protocol (MCP) server** that integrates directly into AI agent workflows. It scores, audits, detects conflicts, generates guidelines, and produces executive dashboards — all grounded in a single, validated Decision Engine that acts as the sole source of truth for every analytical function.

The goal is not automation for its own sake. It is architectural discipline: every decision made by the system traces back to a defined, testable function inside `decision_engine.py`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FIN Architect MCP                        │
│                         MCP Server (FastMCP)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │     Decision Engine     │
              │   decision_engine.py    │
              │  34 functions · 45 cst  │
              └──┬──────┬──────┬───┬───┘
                 │      │      │   │
    ┌────────────▼──┐ ┌─▼──────▼┐ │  ┌──────────────────┐
    │ Guideline Core│ │Knowledge│ │  │ Recommendation   │
    │  8 tools      │ │  Core   │ │  │     Engine       │
    │               │ │ 3 tools │ │  │     1 tool       │
    └───────────────┘ └─────────┘ │  └──────────────────┘
                                  │
              ┌───────────────────▼───┐
              │    Repository Core    │
              │       1 tool          │
              └───────────────────────┘
                                  │
              ┌───────────────────▼───┐
              │  Executive Dashboard  │
              │       1 tool          │
              └───────────────────────┘
                                  │
              ┌───────────────────▼───┐
              │      Orchestrator     │
              │    architect_review   │
              └───────────────────────┘
```

**Design principle:** `server.py` contains no analytical logic. Every score, every threshold, every pattern match lives in `decision_engine.py`. The server only formats and routes.

---

## Core Modules

### Decision Engine (`decision_engine.py`)
The analytical core of the system. A pure-function module with no side effects. Contains all scoring algorithms, detection patterns, Jaccard similarity computations, KDE scoring, guideline classification, loop risk detection, and ROI ranking. Never called by clients directly — only by tools inside `server.py`.

### Guideline Core
Eight tools that govern conversation guidelines: auditing for policy compliance, optimization for clarity and scope, conflict detection across the guideline library, scoring by 10 structured criteria, FIN conversation simulation, new guideline generation, and cluster-based extraction from raw conversation logs.

### Knowledge Core
Three tools for the knowledge article lifecycle: full KDE audit across 12 weighted criteria, structured optimization with prioritized action plans, and bulk review for coverage and debt analysis.

### Repository Core
One tool that evaluates the entire knowledge repository as a system: coverage gaps, duplicate detection (Jaccard >= 0.55), debt distribution, and deployment readiness across all article categories.

### Recommendation Engine
Surfaces the highest-impact improvements across the repository using ROI prioritization (impact/effort ratio), ranking articles and guidelines by their contribution to overall health.

### Executive Dashboard
Aggregates all module outputs into a single unified report: global health score, knowledge debt by category, FIN coverage, escalation risk, open blockers, and deployment readiness indicator.

### Orchestrator (`architect_review`)
The only tool that calls other tools. Accepts a set of articles and guidelines and routes them through the full analysis pipeline, returning a consolidated architectural diagnosis.

---

## Features

- **KDE Scoring** — 12-criterion weighted scoring for knowledge articles (100-point scale): Claridad, Estructura, Pasos, Cobertura, Ambiguedad, Longitud, Consistencia, Terminologia, Uso por FIN, Escalamiento, Mantenibilidad, Riesgo Operativo
- **Guideline Scoring** — 10-criterion scoring framework specifically calibrated for conversation guidelines
- **Loop Risk Detection** — classifies conversation loop risk as BAJO / MEDIO / ALTO / CRITICO using pattern matching
- **Anti-Escalation Detection** — identifies whether an article suppresses escalation paths incorrectly
- **Conflict Detection** — semantic overlap detection across the full guideline library using Jaccard similarity
- **Duplicate Detection** — identifies near-duplicate articles (threshold >= 0.55) and sentence-level repetitions (threshold >= 0.80)
- **Knowledge Debt** — computes and labels accumulated debt per article and per repository
- **Guideline Generation** — produces structured guideline templates from event catalog entries
- **FIN Simulation** — tests how FIN (the AI assistant) would respond given a guideline, predicting escalation probability and resolution paths
- **ROI Ranking** — prioritizes improvements by impact/effort ratio across the full article catalog
- **Hard Caps** — enforces scoring floors when blocker conditions are present (health max 60, resolution max 40)
- **Executive Dashboard** — single-call full-system health report with traffic light indicators

---

## Workflow

```
Intercom Conversations
        │
        ▼
  extract_guidelines  ──►  Raw guidelines from conversation clusters
        │
        ▼
  classify_guideline  ──►  Category, intent, risk level, priority
        │
        ▼
  detect_conflicts    ──►  Conflict map across the guideline library
        │
        ▼
  audit_guideline     ──►  Policy compliance, ambiguity, obligation score
        │
        ▼
  optimize_guideline  ──►  Specific rewrite recommendations
        │
        ▼
  score_guideline     ──►  Numeric score + criterion breakdown
        │
        ▼
  simulate_fin        ──►  FIN response simulation + escalation prediction
        │
        ▼
  generate_guideline  ──►  Final structured guideline ready for deployment
        │
        ▼
  audit_knowledge ────►  Article health score + blockers
        │
  optimize_article ───►  Prioritized optimization plan
        │
  knowledge_review ───►  Bulk coverage + debt analysis
        │
  repository_review ──►  Full repository health + deployment readiness
        │
  recommend_improvements ► Ranked improvement backlog
        │
        ▼
  fin_dashboard       ──►  Unified executive report
```

---

## Tool Catalog

| Tool | Module | Objective | Status |
|------|--------|-----------|--------|
| `audit_guideline` | Guideline Core | Full policy and compliance audit of a single guideline | Stable |
| `optimize_guideline` | Guideline Core | Generates specific rewrite recommendations for a guideline | Stable |
| `classify_guideline` | Guideline Core | Classifies intent, risk level, and priority of a guideline | Stable |
| `detect_conflicts` | Guideline Core | Detects semantic conflicts across the guideline library | Stable |
| `score_guideline` | Guideline Core | Scores a guideline across 10 structured criteria | Stable |
| `simulate_fin` | Guideline Core | Simulates FIN's response given a guideline | Stable |
| `generate_guideline` | Guideline Core | Generates a complete structured guideline template | Stable |
| `extract_guidelines` | Guideline Core | Extracts and clusters guidelines from conversation logs | Stable |
| `audit_knowledge` | Knowledge Core | KDE audit of a knowledge article across 12 criteria | Stable |
| `optimize_article` | Knowledge Core | Produces a prioritized optimization plan for an article | Stable |
| `knowledge_review` | Knowledge Core | Bulk review of coverage, debt, and health across articles | Stable |
| `repository_review` | Repository Core | Full repository health analysis and deployment readiness | Stable |
| `recommend_improvements` | Recommendation Engine | ROI-ranked improvement backlog for the repository | Stable |
| `fin_dashboard` | Executive Dashboard | Unified executive health report across all modules | Stable |
| `architect_review` | Orchestrator | End-to-end architectural diagnosis pipeline | Stable |

---

## Decision Engine

### Why it exists

Before the Decision Engine, analytical logic was duplicated across every tool. `audit_knowledge` had its own scoring loop. `optimize_article` maintained its own constant lists. `extract_guidelines` had its own `jaccard()` implementation. Every sprint that added a tool added another copy of the same logic — diverging silently, impossible to test as a unit.

### What it centralizes

`decision_engine.py` is the single location for:

- All scoring algorithms (KDE article scoring, guideline scoring, fast-path variants)
- All detection functions (loop risk, anti-escalation, escalation signals, FIN blockers, absolute terms)
- All similarity computations (Jaccard, word sets, sentence-level overlap)
- All classification logic (intent detection, emotion detection, risk levels, conflict severity)
- All ranking functions (ROI computation, debt computation, improvement ranking)
- All constant definitions (pattern lists, signal vocabularies, event catalogs, templates)
- All threshold values (GUIDELINE_CLUSTER_THRESHOLD, GUIDELINE_MERGE_THRESHOLD, KDE hard caps)

### Benefits

| Before | After |
|--------|-------|
| Logic duplicated across 15 tools | Single source of truth |
| Thresholds defined inline per tool | Named constants in one file |
| Jaccard implemented 3x independently | One `jaccard()` + `word_set()` |
| KDE scoring copied per tool | `kde_score_article()` called once |
| ~1,500 lines of duplicate code | 0 duplicates verified |
| No unit-testable analytical core | Pure functions, fully testable |

---

## Project Metrics

| Metric | Value |
|--------|-------|
| Version | 1.0.0 |
| MCP Tools | 15 |
| Decision Engine functions | 34 |
| Decision Engine constants | 45 |
| Decision Engine lines | 1,264 |
| Server lines | 6,634 |
| Duplicate lines eliminated | ~1,500 |
| Architecture sprints | 3 |
| Release status | READY |

### Architecture Sprints

| Sprint | Scope | Result |
|--------|-------|--------|
| v1 — Knowledge Module | KDE scoring, article audit tools | Decision Engine created |
| v2 — Core Consolidation | `audit_knowledge`, `optimize_article`, `audit_guideline`, `architect_review` | -445 lines from server.py |
| v3 — Guideline Core Consolidation | All 7 Guideline tools | -580 lines from server.py |

---

## Roadmap

### v1.0 — Current (Architecture Certified)
- [x] 15 MCP tools across 6 modules
- [x] Decision Engine as single source of truth
- [x] KDE scoring (12 criteria) for knowledge articles
- [x] Guideline scoring (10 criteria) for conversation guidelines
- [x] Conflict detection, loop risk, anti-escalation detection
- [x] ROI-ranked recommendation engine
- [x] Executive dashboard
- [x] Full architectural audit and cleanup

### v1.1 — Next
- [ ] Structured test suite for all 34 Decision Engine functions
- [ ] Batch processing mode for large article repositories
- [ ] Coverage gap auto-detection with category suggestions
- [ ] Resolve 2 orphaned functions (`detect_guideline_events`, `guideline_priority_from_risk`)

### v2.0 — Future
- [ ] Persistent knowledge graph across sessions
- [ ] Automated guideline lifecycle management (draft → review → approved → deprecated)
- [ ] Multi-language support beyond Spanish/English
- [ ] Integration with ticketing and escalation systems

---

## Repository Structure

```
fin-architect-mcp/
├── decision_engine.py     # Analytical core — 34 functions, 45 constants, 1,264 lines
├── server.py              # MCP server — 15 tools, 6,634 lines
├── main.py                # FastAPI health endpoint
├── requirements.txt       # Dependencies
├── docs/
│   └── PROJECT_CONTEXT.md # Architecture context and sprint history
└── README.md              # This file
```

### Dependencies

```
mcp[cli]>=1.3.0      # MCP server framework (FastMCP)
uvicorn>=0.29.0      # ASGI server
starlette>=0.36.0    # HTTP layer
httpx>=0.27.0        # HTTP client
```

---

## Philosophy

**One source of truth.** Every threshold, every pattern, every scoring formula lives in `decision_engine.py`. No tool holds its own copy of logic that another tool also holds.

**No silent divergence.** When two tools used Jaccard similarity with different implementations, they could produce different results on the same input without anyone noticing. The Decision Engine makes divergence impossible: there is only one `jaccard()`.

**Behavior over structure.** Three architecture sprints rewrote the internals without changing a single tool's public output. The API surface is stable. The analytical core is clean. Users of the tools saw nothing change because nothing observable changed.

**Debt is visible.** Knowledge debt, guideline conflicts, and coverage gaps are not surfaced only when someone asks. The dashboard makes them unavoidable. The health score turns red before the customer complaint arrives.

**Minimalism.** The system does one thing: govern the knowledge and guideline architecture of a financial support operation. It does not try to be a general-purpose knowledge management platform. Scope discipline is part of the design.

---

## License

MIT License — see `LICENSE` for details.

---

## Author

Built for the FIN support operations architecture team.

---

*FIN Architect MCP v1.0.0 — Architecture certified. Decision Engine validated. Ready for production.*
