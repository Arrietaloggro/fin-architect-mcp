# FIN Architect MCP — Enterprise

> **Intelligent architecture layer for financial support operations** — audit, optimize, and govern knowledge articles and conversation guidelines through a unified Decision Engine.

[![Version](https://img.shields.io/badge/version-1.0_Beta-blue.svg)](https://github.com/arrietaloggro/fin-architect-mcp)
[![Status](https://img.shields.io/badge/status-Beta_Operacional-green.svg)]()
[![MCP](https://img.shields.io/badge/protocol-MCP-purple.svg)]()
[![License](https://img.shields.io/badge/license-MIT-gray.svg)]()

---

## Project Status

🟢 **Status:** Beta Operacional

| Campo            | Valor                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| Versión          | 1.0 Beta                                                                    |
| Estado           | Baseline congelada                                                          |
| Arquitectura     | Congelada                                                                   |
| Implementación   | Parcial                                                                     |
| Uso interno      | Aprobado                                                                    |
| Producción       | Asistida                                                                    |
| Modo actual      | Operación y mejora continua                                                 |
| Próximo objetivo | Validar impacto en producción sobre CSAT, resolución y eficiencia operativa |

FIN Architect Enterprise entra oficialmente en su fase de operación y mejora continua basada en evidencia. La baseline v1.0 Beta está congelada: la arquitectura de 12 módulos, las 9 herramientas MCP implementadas, y los modelos de scoring FIS y PCS son la referencia estable desde la cual se inicia la validación operacional. El foco a partir de esta versión es ejecutar el sistema sobre conversaciones reales, medir su impacto, y acumular evidencia para informar la evolución hacia v2.0.

---

## Descripción

FIN Architect Enterprise es una plataforma de inteligencia operacional para equipos de CX que supervisan agentes de IA. Proporciona herramientas para auditar, evaluar, simular y mejorar el comportamiento del agente Lia de Loggro, operado sobre Intercom.

## Arquitectura Enterprise

El sistema está compuesto por 12 módulos en 3 capas:

**Capa 1 — Ejecución (9 herramientas MCP activas):**
- `audit_guideline` — Audita si una pauta se aplicó correctamente
- `optimize_guideline` — Propone mejoras a pautas existentes
- `classify_guideline` — Clasifica pautas por tipo, complejidad y producto
- `detect_conflicts` — Detecta pautas contradictorias o redundantes
- `score_guideline` — Calcula el FIN Intelligence Score (FIS) por conversación
- `simulate_fin` — Simula el comportamiento óptimo de Lia
- `generate_guideline` — Genera nuevas pautas desde patrones detectados
- `extract_guidelines` — Extrae pautas implícitas de conversaciones históricas
- `architect_review` — Orquestador principal del pipeline completo

**Capa 2 — Orquestación:**
- `architect_review` integra todas las herramientas en un pipeline de revisión end-to-end

**Capa 3 — Inteligencia (diseñados, pendientes de implementación):**
- `fin_intelligence_review()` — Revisión inteligente con análisis temporal y clustering
- FIN Continuous Learning Engine — Ciclo OBSERVE→LEARN automatizado
- CSAT Improvement Engine — Predicción y mejora del Predicted CSAT Score (PCS)

## Documentación

| Documento | Descripción |
|-----------|-------------|
| `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` | **Documento de cierre oficial** — referencia canónica de v1.0 Beta |
| `FIN_ARCHITECT_ENTERPRISE.md` | Blueprint completo del producto (v1.1) |
| `FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md` | Arquitectura de `fin_intelligence_review()` |
| `FIN_CONTINUOUS_LEARNING_ENGINE.md` | Diseño del motor de aprendizaje continuo |
| `KNOWLEDGE_DIGITAL_TWIN.md` | Inventario completo de 1,036 artículos KB |
| `CHANGELOG.md` | Historial de versiones |

## Datos

| Archivo | Descripción |
|---------|-------------|
| `dataset_fin_25_conversaciones.json` | 25 conversaciones Restobar anotadas (36 campos) |
| `knowledge_inventory.json` | 1,036 artículos KB con metadatos completos |

## Uso

```bash
# Iniciar servidor MCP
python server.py

# El servidor expone las 9 herramientas MCP via SSE en el puerto configurado
# Conectar desde Claude con el MCP configurado en settings
```

## Roadmap Enterprise

| Versión | Objetivo | Criterio de entrada |
|---------|----------|---------------------|
| v1.0 Beta (actual) | Baseline congelada, inicio de operación | — |
| v1.1 | Calibración FIS + datasets Pymes y Nómina | Correlación FIS-humano ≥ 0.75 |
| v2.0 | Implementación CLE + CIE | 3/4 productos con dataset; 8 semanas de uso activo |
| Enterprise | Plataforma multi-producto completa | PCS validado; primer ciclo de mejora completado |

---

## Vision

FIN Architect MCP was built to solve a structural problem in financial support operations: knowledge and conversation guidelines accumulate debt silently. Articles become outdated, guidelines conflict, and no system surfaces the risk before it reaches the customer.

This project provides a **Model Context Protocol (MCP) server** that integrates directly into AI agent workflows. It scores, audits, detects conflicts, generates guidelines, and produces executive dashboards — all grounded in a single, validated Decision Engine that acts as the sole source of truth for every analytical function.

The goal is not automation for its own sake. It is architectural discipline: every decision made by the system traces back to a defined, testable function inside `decision_engine.py`.

---

## Technical Architecture

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
| Version | 1.0 Beta |
| MCP Tools | 15 (9 active, 6 in design) |
| Decision Engine functions | 34 |
| Decision Engine constants | 45 |
| Decision Engine lines | 1,264 |
| Server lines | 6,634 |
| Duplicate lines eliminated | ~1,500 |
| Architecture sprints | 3 |
| Release status | Beta Operacional |
| Final Acceptance Test score | 64/100 |

### Architecture Sprints

| Sprint | Scope | Result |
|--------|-------|--------|
| v1 — Knowledge Module | KDE scoring, article audit tools | Decision Engine created |
| v2 — Core Consolidation | `audit_knowledge`, `optimize_article`, `audit_guideline`, `architect_review` | -445 lines from server.py |
| v3 — Guideline Core Consolidation | All 7 Guideline tools | -580 lines from server.py |

---

## Roadmap

### v1.0 Beta — Current (Baseline Congelada)
- [x] 15 MCP tools across 6 modules
- [x] Decision Engine as single source of truth
- [x] KDE scoring (12 criteria) for knowledge articles
- [x] Guideline scoring (10 criteria) for conversation guidelines
- [x] Conflict detection, loop risk, anti-escalation detection
- [x] ROI-ranked recommendation engine
- [x] Executive dashboard
- [x] Full architectural audit and cleanup
- [x] FIN Architect Enterprise v1.0 Beta documentation

### v1.1 — Next
- [ ] Structured test suite for all 34 Decision Engine functions
- [ ] Batch processing mode for large article repositories
- [ ] Coverage gap auto-detection with category suggestions
- [ ] Calibración FIS + datasets Pymes y Nómina (correlación FIS-humano ≥ 0.75)

### v2.0 — Future
- [ ] Persistent knowledge graph across sessions
- [ ] Automated guideline lifecycle management (draft → review → approved → deprecated)
- [ ] Multi-language support beyond Spanish/English
- [ ] FIN Continuous Learning Engine (CLE) — ciclo OBSERVE→LEARN
- [ ] CSAT Improvement Engine (CIE) — predicción y mejora del PCS

---

## Repository Structure

```
fin-architect-mcp/
├── decision_engine.py                    # Analytical core — 34 functions, 45 constants
├── server.py                             # MCP server — 15 tools
├── main.py                               # FastAPI health endpoint
├── requirements.txt                      # Dependencies
├── CHANGELOG.md                          # Version history
├── FIN_ARCHITECT_ENTERPRISE.md           # Product blueprint v1.1
├── FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md # Official v1.0 Beta closure document
├── FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md
├── FIN_CONTINUOUS_LEARNING_ENGINE.md
├── KNOWLEDGE_DIGITAL_TWIN.md            # 1,036 KB articles inventory
├── dataset_fin_25_conversaciones.json   # 25 annotated conversations
├── knowledge_inventory.json             # Full KB inventory with metadata
├── loggro-incidents-portal/             # Portal Interno de Incidencias (standalone)
│   ├── ARCHITECTURE.md
│   ├── backend/                         # Node.js + Express + SQLite
│   └── frontend/                        # React + Vite + Tailwind CSS
└── docs/
    └── PROJECT_CONTEXT.md               # Architecture context and sprint history
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

*FIN Architect MCP — v1.0 Beta Operacional. Baseline congelada. Decision Engine validado. Listo para operación.*
