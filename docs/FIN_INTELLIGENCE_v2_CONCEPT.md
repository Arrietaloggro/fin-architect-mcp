# FIN Intelligence v2 — Conceptual Architecture

**Version:** 1.0
**Date:** 2026-06-26
**Status:** Conceptual model only — no implementation proposed
**Scope:** Entity definitions, relationships, and information flow across the
           FIN ecosystem. Grounded exclusively in structures already present
           in `decision_engine.py`, `server.py`, and validated documentation.

---

## Purpose of this document

This document defines the conceptual architecture of the FIN ecosystem as it
exists today and as it must be understood before connecting Intercom to FIN
Architect. It is not a feature specification. It is not a roadmap. It is the
formal entity model that any future intelligence layer must respect.

Every entity defined here has a direct counterpart in the running system:
constants in `decision_engine.py`, parameters in `server.py` tool signatures,
or structures validated during the v1.0.0 development cycle. Nothing is invented.

---

## Entity Catalog

---

### Entity 1 — Product

**Purpose**

A Product is a named operational domain within the FIN ecosystem. It groups
together the guidelines, knowledge articles, and conversation context that apply
to a specific vertical or module. Products are the primary unit of organization
for every cross-product analysis tool.

**Attributes**

| Field | Type | Source |
|-------|------|--------|
| `nombre` | str | Input to `repository_review`, `fin_dashboard`, `ecosystem_review` |
| `guidelines` | list[str] | Active behavioral rules for this product |
| `knowledge_articles` | list[str] | Knowledge base articles available to FIN for this product |

**Modeled domains** (from `INTENTION_MAP`, `decision_engine.py` line 903):

| Product domain | Keyword signals |
|---------------|----------------|
| Facturación | factura, cobro, pago, cargo, recibo, monto |
| Inventario | inventario, stock, producto, artículo, bodega |
| Caja | caja, cierre, apertura, efectivo, denominación |
| POS | pos, terminal, punto de venta, datáfono, impresora |
| Restobar | mesa, comanda, pedido, cocina, restaurante, bar |
| DIAN | dian, cufe, resolución, factura electrónica, habilitación |
| Nómina | nómina, empleado, salario, liquidación, prestaciones |
| Reportes | reporte, informe, estadística, consulta, historial |
| Configuración | configurar, configuración, ajuste, parámetro, módulo |
| Error técnico | error, falla, no funciona, fallo, reiniciar, caído |
| Acceso | acceso, contraseña, usuario, clave, iniciar sesión, bloqueado |
| Seguridad | seguridad, permiso, rol, administrador, auditoría |

**Inputs received by:** `repository_review`, `fin_dashboard`, `ecosystem_review`,
`audit_knowledge`, `knowledge_review`, `audit_guideline`, `classify_guideline`,
`detect_conflicts`, `score_guideline`, `simulate_fin`, `generate_guideline`,
`extract_guidelines`, `architect_review`

**Outputs produced:** Product health score (0–100), risk level (BAJO/MEDIO/ALTO),
blocked flag, coverage report, guideline set, knowledge article set.

**Dependencies:** Guideline, Knowledge Article, Attribute (product name as routing signal)

**Relationships:**

```
Product ──has many──► Guidelines
Product ──has many──► Knowledge Articles
Product ──is identified by──► Intention (via INTENTION_MAP keyword matching)
Product ──is evaluated by──► repository_review, ecosystem_review, fin_dashboard
```

---

### Entity 2 — Knowledge Article

**Purpose**

A Knowledge Article is a text document that FIN consults to resolve a user issue
autonomously. Its quality determines whether FIN can act without human intervention.
The article is not just content — it is a deployable unit with a health score,
a risk level, an automation readiness classification, and a deployment decision.

**Attributes**

| Field | Source | Range |
|-------|--------|-------|
| `text` | Raw string input | — |
| `kde_health` | `kde_score_article()` | 0–100 |
| `risk_level` | `risk_level_from_health()` | BAJO / MEDIO / ALTO |
| `automation_readiness` | `compute_automation_readiness()` | No apto / Baja / Media / Alta / Excelente |
| `deploy_decision` | `compute_deploy_decision()` | BLOQUEADO / NO LISTO / LISTO CON RECOMENDACIONES / LISTO |
| `loop_risk_level` | `detect_loop_risk()` | BAJO / MEDIO / ALTO / CRÍTICO |
| `has_escalation` | `detect_escalation()` | bool |
| `anti_escalation_rule` | `detect_anti_escalation()` | bool — triggers hard cap if True |
| `kde_blocker_flags` | `kde_score_article()` | list of active blocker descriptions |
| `resolution_capability` | `kde_score_article()` | 0–100; capped at 40 if blocker present |

**Scoring framework** (12 weighted criteria, 100-point scale):

| Criterion | Weight |
|-----------|--------|
| Claridad | 12 |
| Pasos | 12 |
| Ambigüedad | 10 |
| Estructura | 10 |
| Uso por FIN | 10 |
| Escalamiento | 8 |
| Cobertura | 8 |
| Longitud | 8 |
| Consistencia | 8 |
| Terminología | 8 |
| Mantenibilidad | 7 |
| Riesgo Operativo | 7 |

**Hard caps** (unconditional):
- `KDE_HARD_CAP_BLOCKER = 60`: max `kde_health` when loop CRÍTICO or anti-escalation detected
- `KDE_HARD_CAP_RESOLUTION = 40`: max `resolution_capability` when blocker present

**Inputs received by:** `audit_knowledge`, `optimize_article`, `knowledge_review`,
`repository_review`, `ecosystem_review`

**Outputs produced:** 40+ fields including all scoring signals; subset used by
`optimize_article` for ROI-ranked recommendation plan.

**Dependencies:** Decision Engine (KDE functions), Product (context and routing)

**Relationships:**

```
Knowledge Article ──belongs to──► Product
Knowledge Article ──is scored by──► kde_score_article() / kde_score_article_fast()
Knowledge Article ──feeds──► Workflow (resolution path)
Knowledge Article ──contributes to──► Coverage (TOPIC_CATEGORIES matching)
Knowledge Article ──if blocker──► blocks Autonomous Resolution
```

---

### Entity 3 — Guideline

**Purpose**

A Guideline is a behavioral rule that defines how FIN must respond to a specific
conversation pattern. It governs conduct, not content: when to escalate, what
tone to use, what is prohibited, what is mandatory. Guidelines operate as a
constraint layer on top of Knowledge Articles.

**Attributes**

| Field | Source | Notes |
|-------|--------|-------|
| `text` | Raw string | The rule itself |
| `intention` | `detect_intention()` | Dominant domain from INTENTION_MAP |
| `emotion_scope` | `detect_emotion()` | Emotion state the rule addresses |
| `risk_level` | `guideline_risk_level()` | ALTO / MEDIO / BAJO |
| `health` | `kde_score_guideline_fast()` | 0–100 fast score |
| `has_escalation` | `kde_score_guideline_fast()` | bool |
| `anti_escalation` | `detect_anti_escalation()` | bool — compliance violation if True |
| `blocked` | `kde_score_guideline_fast()` | bool |
| `implementation_priority` | `guideline_priority_from_risk()` | CRÍTICA / ALTA / MEDIA / BAJA |
| `impact_priority` | `guideline_impact_priority()` | INMEDIATA / ALTA / MEDIA / BAJA |

**Classification categories** (from `classify_guideline` logic):

- **Escalamiento** — contains escalation or transfer words
- **Facturación** — billing-domain instructions
- **Acceso y Seguridad** — credential and access rules
- **Soporte Técnico** — technical failure response
- **Onboarding** — registration and activation flows
- **General** — no specific category match

**Subcategories:**

- **Gestión Emocional** — frustración, molesto, enojado triggers
- **Flujo Condicional** — `cuando`, `si`, `solo si` conditioning
- **Regla Absoluta** — `siempre`, `nunca`, `todos`, `ninguno`
- **Política Extensa** — length > 300 chars
- **Instrucción Simple** — default

**Conflict detection** (from `GUIDELINE_CONTRADICTION_PAIRS`):

| Pair | Risk |
|------|------|
| `("escalar", "no escalar")` | ALTA severity |
| `("siempre", "solo si")` | MEDIA severity |
| `("nunca", "en algunos casos")` | MEDIA severity |
| `("ofrece descuento", "no ofrece descuento")` | MEDIA severity |
| `("disculpa", "no disculpa")` | BAJA severity |

**Inputs received by:** `audit_guideline`, `optimize_guideline`, `classify_guideline`,
`detect_conflicts`, `score_guideline`, `simulate_fin`, `generate_guideline`,
`extract_guidelines`, `architect_review`, `ecosystem_review`

**Outputs produced:** Risk score, classification, conflict list, compliance status,
optimization recommendations, FIN behavior prediction.

**Dependencies:** Decision Engine (guideline functions), Product (context),
Intention (category detection), Emotion (scope detection)

**Relationships:**

```
Guideline ──belongs to──► Product
Guideline ──governs──► FIN behavior in Workflow
Guideline ──is matched against──► Intention + Emotion in simulate_fin
Guideline ──may conflict with──► other Guidelines (intra and cross-product)
Guideline ──if anti_escalation──► compliance violation (Invariant 6)
Guideline ──is extracted from──► Conversations via extract_guidelines
```

---

### Entity 4 — Conversation

**Purpose**

A Conversation is a sequence of text turns between a user and FIN. It is the
raw operational signal from which all other analytical entities derive meaning.
Conversations are the input to `extract_guidelines`, `architect_review`,
`simulate_fin`, and (when provided) the Workflow layer of `ecosystem_review`.

**Attributes**

| Field | Source | Notes |
|-------|--------|-------|
| `text` | Raw string | Full conversation text |
| `intention` | `detect_intention()` | Dominant category from INTENTION_MAP |
| `emotion` | `detect_emotion()` | Frustrado / Molesto / Urgente / Neutral |
| `events` | `detect_guideline_events()` | List of event IDs from GUIDELINE_EVENT_CATALOG |
| `problems` | `detect_guideline_problems()` | List of problem keys from GUIDELINE_PROBLEM_SIGNALS |
| `priority` | `simulate_fin` logic | CRÍTICA / ALTA / MEDIA / BAJA |

**Priority assignment rules** (from `simulate_fin`, `server.py` line 3793):

```
Frustrado + blocker signals         → CRÍTICA
Molesto/Urgente OR DIAN/Seguridad/Error técnico → ALTA
Facturación/Caja/Nómina/Acceso      → MEDIA
otherwise                           → BAJA
```

**Event catalog** — 12 events with `impact` and `esc_risk` scores
(from `GUIDELINE_EVENT_CATALOG`):

| Event ID | Label | esc_risk |
|----------|-------|---------|
| `unnecessary_escalation_risk` | FIN no puede diagnosticar | 65 |
| `user_tried_docs` | Usuario ya consultó documentación | 60 |
| `user_blocked` | Usuario bloqueado completamente | 55 |
| `user_multiple_attempts` | Usuario intentó múltiples veces | 50 |
| `problem_persists` | Problema persiste después de pasos | 50 |
| `user_frustration` | Frustración del usuario | 45 |
| `user_urgency` | Urgencia del usuario | 40 |
| `fin_repeats_solution` | FIN repite misma solución | 55 |
| `fin_generic_response` | FIN dio respuesta genérica | 35 |
| `fin_escalated` | FIN escaló el caso | 30 |
| `fin_requests_info` | FIN solicitó más información | 10 |
| `problem_resolved` | Problema resuelto | 0 |

**Inputs received by:** `extract_guidelines`, `architect_review`, `simulate_fin`

**Outputs produced:** Guideline candidates (via clustering), architectural
diagnosis, FIN behavior simulation, event and problem detection.

**Dependencies:** Intention, Emotion, Event, Guideline (for simulation)

**Relationships:**

```
Conversation ──contains──► Events (from GUIDELINE_EVENT_CATALOG)
Conversation ──expresses──► Intention (from INTENTION_MAP)
Conversation ──carries──► Emotion (Frustrado/Molesto/Urgente/Neutral)
Conversation ──clusters into──► Guideline Candidates (via extract_guidelines)
Conversation ──is simulated against──► Guidelines (via simulate_fin)
Conversation ──drives──► Escalation decisions
```

---

### Entity 5 — Intention

**Purpose**

An Intention is the dominant business domain of a conversation or guideline,
detected by matching text against `INTENTION_MAP` keyword lists. It is the
primary routing signal in the system: it determines which guidelines apply,
what priority level is assigned, and which product domain the conversation
belongs to.

**Attributes**

| Field | Value |
|-------|-------|
| `category` | One of 12 categories from INTENTION_MAP, or "General" |
| `keywords` | List of trigger words for this category |
| `priority_tier` | ALTA (DIAN, Seguridad, Error técnico) / MEDIA (Facturación, Caja, Nómina, Acceso) / BAJA (others) |

**Detection rule:** First matching category in `INTENTION_MAP` order wins.
If no category matches: `"General"` (renamed to `"Otro"` in `simulate_fin`).

**Priority impact** (from `guideline_priority_from_risk()`):
DIAN, Seguridad, Facturación, Nómina → implementation priority `ALTA` regardless
of risk score. This encodes the operational criticality of these domains.

**Inputs received by:** All tools that accept `conversation` or `guideline` text

**Outputs produced:** Category label used for routing, priority assignment,
guideline matching, and coverage analysis.

**Dependencies:** `INTENTION_MAP` constant, text input

**Relationships:**

```
Intention ──is detected from──► Conversation text / Guideline text
Intention ──determines──► Conversation priority
Intention ──filters──► applicable Guidelines in simulate_fin
Intention ──maps to──► Product domain
Intention ──drives──► implementation_priority in guideline scoring
```

---

### Entity 6 — Emotion

**Purpose**

Emotion is the detected affective state of the user in a conversation. It is a
secondary routing signal that, combined with Intention, determines conversation
priority and the type of guideline response required. Emotion detection is binary
per keyword set — the first matching set wins.

**States and detection vocabulary:**

| State | Detection keywords |
|-------|-------------------|
| Frustrado | furioso, harto, pésimo, terrible, inaceptable, no sirve, fraude, robo, incompetente, nunca funciona, siempre falla |
| Molesto | molesto, enojado, fastidiado, no entiendo, no sirve |
| Urgente | urgente, emergencia, ya mismo, hoy mismo, crítico, no puedo esperar |
| Neutral | (default — no keywords matched) |
| Confundido | no entiendo, no sé, confundido, cómo, qué significa (only in `simulate_fin`) |

**Priority impact:**

```
Frustrado + blocker context → CRÍTICA
Molesto / Urgente           → ALTA
Neutral / Confundido        → inherits from Intention
```

**Inputs received by:** `simulate_fin`, `classify_guideline`, `generate_guideline`,
`extract_guidelines`, `architect_review`

**Outputs produced:** Emotion label used in priority assignment, guideline
matching filter, and escalation risk calculation.

**Dependencies:** `FRUSTRATION_KEYWORDS`, `ANNOYANCE_KEYWORDS`, `URGENCY_KEYWORDS`,
`NEUTRAL_KEYWORDS` constants

**Relationships:**

```
Emotion ──is detected from──► Conversation text
Emotion ──combined with Intention──► determines Conversation priority
Emotion ──is used by──► simulate_fin for guideline matching
Emotion ──triggers──► Escalation when Frustrado + blocker signals
Emotion ──is referenced by──► GUIDELINE_CONDITION_PAIRS (frustración, molesto)
```

---

### Entity 7 — Escalation

**Purpose**

Escalation is the event in which FIN transfers control of a conversation to a
human agent. It is not a tool — it is an outcome. The system's entire analytical
architecture is designed to optimize this outcome: maximize justified escalations,
eliminate unnecessary escalations, and prevent blocked escalation paths.

**States:**

| State | Condition |
|-------|-----------|
| **Justified** | Guideline instructs escalation with conditions; article has escalation criterion; FIN has exhausted autonomous options |
| **Unnecessary** | FIN escalates without sufficient diagnostic information (`unnecessary_escalation_risk` event) |
| **Blocked** | A guideline or article contains an anti-escalation pattern (`ANTI_ESCALATION_PATTERNS`) |
| **Missing** | No article in the product has a valid escalation criterion (`detect_escalation_repo()` returns False for all articles) |

**Detection rules:**

- **Anti-escalation (article-level):** `detect_anti_escalation(text, use_repo_patterns=False)` — strict patterns
- **Anti-escalation (repo/ecosystem-level):** `detect_anti_escalation(text, use_repo_patterns=True)` — broader patterns
  - Patterns: `nunca escal[ae]`, `no escal[ae]`, `no se transfier[ae]`, `prohibido escal[ae]`,
    `sin excepción.*no escal[ae]`, `bajo ningún concepto.*escal[ae]`, `en ningún caso.*escal[ae]`

**Hard caps when anti-escalation detected:**
- `kde_health` capped at `KDE_HARD_CAP_BLOCKER = 60`
- `resolution_capability` capped at `KDE_HARD_CAP_RESOLUTION = 40`

**Escalation transfer requirements** (from `GUIDELINE_BEHAVIOR_MAP`,
`"escalamiento sin criterios"` entry):

> "FIN debe agotar al menos 2 alternativas de resolución autónoma antes de escalar.
> Al escalar, debe incluir: error exacto, pasos realizados y resultado de cada uno."

**Priority in escalation:**

| Priority | Condition |
|----------|-----------|
| CRÍTICA | user_blocked event OR Frustrado + system down signals |
| ALTA | DIAN / Seguridad / Error técnico intention OR Urgente/Molesto emotion |
| MEDIA | Facturación / Caja / Nómina / Acceso intention |
| BAJA | General / Reportes / Configuración |

**Architectural Invariant (Invariant 6 in FIN_ECOSYSTEM.md):**
Anti-escalation is always a compliance violation — never a design choice.

**Inputs received by:** Detected in `audit_knowledge`, `audit_guideline`,
`ecosystem_review`, `repository_review`, `simulate_fin`

**Outputs produced:** Compliance status, escalation health score, transfer payload.

**Dependencies:** `ANTI_ESCALATION_PATTERNS`, `ESCALATION_SIGNALS`,
`GUIDELINE_ESCALATION_WORDS`, `GUIDELINE_PROHIBITION_WORDS`,
`GUIDELINE_OBLIGATION_WORDS`, `GUIDELINE_EVENT_CATALOG`

**Relationships:**

```
Escalation ──is triggered by──► Events (user_blocked, unnecessary_escalation_risk, etc.)
Escalation ──is governed by──► Guidelines (escalation rules)
Escalation ──is blocked by──► anti_escalation patterns in Guidelines / Articles
Escalation ──requires──► open escalation path in Knowledge Articles
Escalation ──is evaluated by──► ecosystem_review, audit_knowledge, audit_guideline
Escalation ──determines──► EHS hard cap (anti-esc → max 60; path closed → max 40)
```

---

### Entity 8 — Workflow

**Purpose**

A Workflow is the operational sequence FIN executes from the moment a conversation
begins to its resolution or escalation. It is not a data structure — it is the
emergent behavior produced by the interaction of Conversations, Guidelines,
Knowledge Articles, Intentions, and Emotions flowing through the tool pipeline.

**Stages** (derived from `simulate_fin` and `architect_review` pipeline):

| Stage | Mechanism |
|-------|-----------|
| **Initiation** | Conversation received; `product` and `context` set |
| **Classification** | `detect_intention()` + `detect_emotion()` → priority |
| **Guideline matching** | `simulate_fin`: guidelines filtered by intention keyword overlap |
| **Decision** | flags: `escalate` / `resolve` / `guide` / `request_info` |
| **Resolution attempt** | Knowledge Article consulted; KDE health checked |
| **Outcome** | `problem_resolved` / `problem_persists` / `fin_repeats_solution` events detected |
| **Escalation** | If resolution fails or guideline instructs escalation |
| **Closure** | Conversation closed; outcome fed to reporting tools |

**Failure patterns** (from `GUIDELINE_PROBLEM_SIGNALS`):

| Failure | Signal |
|---------|--------|
| escalamiento sin criterios | me pasaron con, escalaron sin, nadie me ayudó |
| falta de resolución documentada | no encuentro, no hay artículo, no existe documentación |
| solución documentada insuficiente | ya seguí los pasos, hice lo que dice |
| respuesta genérica de FIN | me dijo lo mismo, misma respuesta, no me ayuda |
| fallo técnico sin guía | error al, no carga, se traba, no responde |
| urgencia no atendida | hoy mismo, urgente, necesito ahora |

**Inputs received by:** `extract_guidelines` (pattern detection from conversations),
`architect_review` (full pipeline), `simulate_fin` (single conversation simulation)

**Outputs produced:** Guideline candidates, escalation events, resolution flags,
architectural diagnosis.

**Dependencies:** Conversation, Guideline, Knowledge Article, Intention, Emotion,
Escalation

**Relationships:**

```
Workflow ──processes──► Conversations
Workflow ──applies──► Guidelines
Workflow ──consults──► Knowledge Articles
Workflow ──produces──► Events (from GUIDELINE_EVENT_CATALOG)
Workflow ──detects──► Failure patterns (GUIDELINE_PROBLEM_SIGNALS)
Workflow ──triggers──► Escalation
Workflow ──is analyzed by──► extract_guidelines, architect_review, simulate_fin
```

---

### Entity 9 — Attribute

**Purpose**

An Attribute is a contextual signal passed to a tool at call time that modifies
how the tool routes, reports, or scopes its analysis. In v1.0.0, there are two
attributes: `product` (routing) and `context` (free-text scope). Attributes do
not change scoring weights or analytical thresholds — they provide context for
interpretation and reporting.

**Defined attributes:**

| Attribute | Type | Default | Effect |
|-----------|------|---------|--------|
| `product` | str | `"general"` | Product domain routing; used in priority assignment in `simulate_fin`; included in all report headers |
| `context` | str | `""` | Free-text operational context; passed through to sub-reports; does not affect analytical logic |

**Attribute completeness** (evaluated by `ecosystem_review`):

- A product with no guidelines is an attribute with undefined behavioral scope
- A product with no knowledge articles is an attribute with no resolution capability
- A product defined in `INTENTION_MAP` but not present in the `products` list is
  an uncovered attribute (domain exists but is not analytically governed)

**Inputs received by:** Every tool in `server.py` (all accept `product` and `context`)

**Outputs produced:** Scoped reports, priority modifiers, coverage completeness indicators.

**Dependencies:** Product entity, Intention (product is matched to domain via INTENTION_MAP)

**Relationships:**

```
Attribute ──scopes──► every tool call
Attribute ──routes──► priority assignment in simulate_fin
Attribute ──identifies──► Product domain
Attribute ──is checked for completeness by──► ecosystem_review
Attribute ──does not modify──► scoring weights or thresholds (Invariant 10)
```

---

### Entity 10 — MCP Tool

**Purpose**

An MCP Tool is a callable analytical function exposed via the FastMCP protocol
over SSE. It is the interface layer between FIN clients (Claude, Intercom, any
MCP-compatible client) and the Decision Engine. Tools contain no analytical
logic — they route inputs to `_de.*` functions and format the results.

**The 16 tools** (15 original + 1 new):

| Tool | Layer | Primary entities consumed | Primary output |
|------|-------|--------------------------|----------------|
| `audit_guideline` | Guideline | Guideline, Attribute | Compliance audit, risk flags |
| `optimize_guideline` | Guideline | Guideline, Attribute | Rewrite recommendations |
| `classify_guideline` | Guideline | Guideline, Attribute | Category, risk, priority |
| `detect_conflicts` | Guideline | Guidelines[], Attribute | Conflict list, severity |
| `score_guideline` | Guideline | Guideline, Attribute | 10-criterion score |
| `simulate_fin` | Workflow | Conversation, Guidelines[], Attribute | Decision, escalation risk, applied rules |
| `generate_guideline` | Guideline | Conversation, Attribute | Guideline template |
| `extract_guidelines` | Workflow→Guideline | Conversations[], Attribute | Guideline candidates (clustered) |
| `audit_knowledge` | Knowledge | Article, Attribute | KDE score, deploy decision |
| `optimize_article` | Knowledge | Article, Attribute | ROI-ranked improvement plan |
| `knowledge_review` | Knowledge | Articles[], Attribute | Bulk health, coverage, debt |
| `repository_review` | Knowledge+Guideline | Products[] | Per-product + global scores |
| `recommend_improvements` | Reporting | Report texts | Ranked improvement backlog |
| `fin_dashboard` | Reporting | Products[] | Executive health report |
| `architect_review` | Orchestration | Product, Conversations[], Guidelines[] | Full pipeline diagnosis |
| `ecosystem_review` | Cross-layer | Products[] | Cross-product EHS, compliance |

**Protocol details** (from `server.py` infrastructure):
- Transport: SSE at `/sse` endpoint
- Health: `GET /` returns `{"status": "ok", "service": "fin-architect-mcp"}`
- Entry: `python server.py` → uvicorn on `PORT` env var (default 8000)

**Invariant:** Tools call `_de.*` and format results. No analytical logic in tools.

**Relationships:**

```
MCP Tool ──receives──► Product, Guideline, Article, Conversation (as inputs)
MCP Tool ──calls──► Decision Engine functions (_de.*)
MCP Tool ──may call──► other MCP Tools (sub-calls: fin_dashboard→repository_review)
MCP Tool ──produces──► structured text report consumed by FIN clients
MCP Tool ──is registered with──► FastMCP via @mcp.tool() decorator
```

---

## ASCII Information Flow Diagram

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     FIN INTELLIGENCE v2 — ENTITY FLOW                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │                         INTERCOM / FIN CLIENT                       │    ║
║  │              (MCP Client — Claude, Intercom, API consumer)          │    ║
║  └───────────────────────────┬─────────────────────────────────────────┘    ║
║                              │ MCP Protocol over SSE                        ║
║                              ▼                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │                    MCP TOOL LAYER  (server.py)                      │    ║
║  │                                                                     │    ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │    ║
║  │  │  Guideline   │  │  Knowledge   │  │  Orchestration│             │    ║
║  │  │  Core (8)    │  │  Core (3)    │  │  (2 tools)   │             │    ║
║  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │    ║
║  │         │                 │                  │                     │    ║
║  │  ┌──────┴────────────────┴──────────────────┴───────────────┐     │    ║
║  │  │         Reporting + Ecosystem (3 tools)                   │     │    ║
║  │  │  repository_review · fin_dashboard · ecosystem_review      │     │    ║
║  │  └───────────────────────────────────────────────────────────┘     │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                              │ _de.* calls                                  ║
║                              ▼                                               ║
║  ┌─────────────────────────────────────────────────────────────────────┐    ║
║  │               DECISION ENGINE  (decision_engine.py)                 │    ║
║  │         34 pure functions · 45 named constants · 1,264 lines        │    ║
║  └─────────────────────────────────────────────────────────────────────┘    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ENTITY INTERACTION FLOW
  ═══════════════════════

  CONVERSATION (raw text)
      │
      ├──► detect_intention() ──────────────────────► INTENTION
      │                                                   │
      ├──► detect_emotion()  ──────────────────────► EMOTION
      │                                                   │
      └──► detect_guideline_events() ──────────────► EVENT LIST
                                                          │
             INTENTION + EMOTION ──────────────────► PRIORITY
                    │                                (CRÍTICA/ALTA/MEDIA/BAJA)
                    │
                    ▼
             ┌─────────────────────────────────────────────────────────┐
             │                  GUIDELINE MATCHING                      │
             │  simulate_fin: intention keywords ∩ guideline text       │
             │                                                          │
             │  GUIDELINE ──classified by──► category / subcategory    │
             │  GUIDELINE ──scored by──► kde_score_guideline_fast()    │
             │  GUIDELINE ──checked for──► anti_escalation flag        │
             │  GUIDELINE PAIR ──checked for──► contradiction          │
             │  GUIDELINES[] ──clustered by──► jaccard() similarity    │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                  ┌─────────────────────┴──────────────────────┐
                  │                                             │
                  ▼                                             ▼
       flags: resolve / guide                      flags: escalate /
       request_info                                conflict / blocked
                  │                                             │
                  ▼                                             ▼
       ┌──────────────────────┐                   ┌────────────────────────┐
       │   KNOWLEDGE ARTICLE  │                   │     ESCALATION         │
       │                      │                   │                        │
       │  kde_score_article() │                   │  Priority: CRÍTICA /   │
       │  kde_health: 0–100   │                   │           ALTA /       │
       │  loop_risk detection │                   │           MEDIA /      │
       │  anti_esc detection  │                   │           BAJA         │
       │  deploy_decision     │                   │                        │
       │                      │                   │  Transfer payload:     │
       │  ┌────────────────┐  │                   │  · exact error         │
       │  │ health ≥ 78    │  │                   │  · steps attempted     │
       │  │ no blocker     ├──┼──► AUTONOMOUS     │  · articles consulted  │
       │  │ escalation OK  │  │    RESOLUTION     │  · emotion + priority  │
       │  └────────────────┘  │                   └────────────────────────┘
       │  ┌────────────────┐  │
       │  │ blocker active │  │
       │  │ health capped  ├──┼──► ESCALATION PATH (mandatory)
       │  │ at 60 / 40     │  │
       │  └────────────────┘  │
       └──────────────────────┘
                  │
                  ▼
       ┌──────────────────────────────────────────────────────────────┐
       │                     OUTCOME                                  │
       │                                                              │
       │  problem_resolved   ──► case closed autonomously            │
       │  problem_persists   ──► re-enter Workflow (loop risk)       │
       │  fin_repeats_solution──► flag loop, escalate                │
       └──────────────────────────────────────────────────────────────┘
                  │
                  ▼
       ┌──────────────────────────────────────────────────────────────┐
       │                     REPORTING LAYER                          │
       │                                                              │
       │  PRODUCT[] ──► repository_review ──► global_health          │
       │                                       knowledge_debt         │
       │                                       coverage_pct           │
       │                                       prod_risk_ranking      │
       │                │                                             │
       │                └──► recommend_improvements ──► ranked        │
       │                                                backlog        │
       │                │                                             │
       │                └──► fin_dashboard ──► executive report      │
       │                                        deploy_readiness       │
       │                │                                             │
       │                └──► ecosystem_review ──► EHS composite       │
       │                                          cross-product        │
       │                                          esc compliance       │
       └──────────────────────────────────────────────────────────────┘


  CROSS-ENTITY DEPENDENCY MAP
  ════════════════════════════

  PRODUCT
    ├── contains ────────────────────────────► GUIDELINES[]
    ├── contains ────────────────────────────► KNOWLEDGE ARTICLES[]
    └── is identified by ───────────────────► INTENTION (via INTENTION_MAP)

  CONVERSATION
    ├── expresses ──────────────────────────► INTENTION
    ├── carries ────────────────────────────► EMOTION
    ├── contains ──────────────────────────► EVENTS[]
    └── clusters into ─────────────────────► GUIDELINE CANDIDATES

  GUIDELINE
    ├── governs ────────────────────────────► FIN behavior in WORKFLOW
    ├── is matched by ──────────────────────► INTENTION + EMOTION
    ├── may block ──────────────────────────► ESCALATION (anti-escalation)
    └── may conflict with ──────────────────► other GUIDELINES

  KNOWLEDGE ARTICLE
    ├── enables ────────────────────────────► AUTONOMOUS RESOLUTION
    ├── may block ──────────────────────────► RESOLUTION (if blocker)
    └── contributes to ─────────────────────► COVERAGE (TOPIC_CATEGORIES)

  ESCALATION
    ├── is triggered by ────────────────────► EVENTS (esc_risk > threshold)
    ├── is governed by ────────────────────► GUIDELINES (escalation rules)
    ├── is blocked by ──────────────────────► ANTI_ESCALATION patterns
    └── requires ──────────────────────────► open path in KNOWLEDGE ARTICLES

  ATTRIBUTE
    ├── scopes ─────────────────────────────► every MCP TOOL call
    ├── routes ─────────────────────────────► PRIORITY in WORKFLOW
    └── identifies ─────────────────────────► PRODUCT domain

  MCP TOOL
    ├── receives ───────────────────────────► PRODUCT, GUIDELINE, ARTICLE,
    │                                         CONVERSATION (as inputs)
    ├── delegates to ───────────────────────► DECISION ENGINE (_de.*)
    ├── may call ──────────────────────────► other MCP TOOLS (sub-calls)
    └── returns ───────────────────────────► structured report to CLIENT


  COVERAGE TOPOLOGY
  ═════════════════

  11 TOPIC_CATEGORIES ──── required coverage ────► KNOWLEDGE ARTICLES
  │                                                        │
  │  facturación · soporte técnico · cancelación           │
  │  configuración · escalamiento · reembolso              │
  │  onboarding · seguridad · reportes                     │
  │  integraciones · general                               │
  │                                                        │
  └──► missing categories ──────────────────────► KNOWLEDGE DEBT

  12 INTENTION_MAP entries ──── routing ──────────► CONVERSATIONS
  │                                                        │
  │  Facturación · Inventario · Caja · POS                │
  │  Restobar · DIAN · Nómina · Reportes                  │
  │  Configuración · Error técnico · Acceso · Seguridad   │
  │                                                        │
  └──► unmatched conversations ─────────────────► "General" / uncovered domain

  12 GUIDELINE_EVENT_CATALOG entries ── signals ──► CONVERSATIONS
  │                                                        │
  │  impact: 0–55 · esc_risk: 0–65                        │
  │                                                        │
  └──► high-esc_risk events ──────────────────────► ESCALATION pressure
```

---

## Entity Relationship Summary Table

| Entity | Produces | Consumed by | Key constants |
|--------|----------|-------------|---------------|
| Product | health score, risk level | repository_review, fin_dashboard, ecosystem_review | — |
| Knowledge Article | KDE score, deploy decision, coverage contribution | audit_knowledge, knowledge_review, repository_review | KDE_HARD_CAP_BLOCKER, KDE_HARD_CAP_RESOLUTION |
| Guideline | risk score, compliance status, conflict flags | audit_guideline, detect_conflicts, simulate_fin | GUIDELINE_CONTRADICTION_PAIRS, GUIDELINE_CONDITION_PAIRS |
| Conversation | events, intention, emotion, guideline candidates | extract_guidelines, architect_review, simulate_fin | GUIDELINE_EVENT_CATALOG, GUIDELINE_PROBLEM_SIGNALS |
| Intention | category label, priority tier | simulate_fin, classify_guideline, extract_guidelines | INTENTION_MAP |
| Emotion | emotion state | simulate_fin, generate_guideline, classify_guideline | FRUSTRATION_KEYWORDS, ANNOYANCE_KEYWORDS, URGENCY_KEYWORDS |
| Escalation | compliance status, transfer payload | ecosystem_review, audit_knowledge, audit_guideline | ANTI_ESCALATION_PATTERNS, ESCALATION_SIGNALS |
| Workflow | events, failure patterns, guideline extracts | architect_review, extract_guidelines | GUIDELINE_PROBLEM_SIGNALS, GUIDELINE_FAILURE_MAP |
| Attribute | routing signal, scope context | all tools | — |
| MCP Tool | structured text report | FIN clients (Claude, Intercom) | — |

---

## Architectural invariants this model depends on

All entity definitions in this document presuppose the following invariants
remain intact. Any future integration layer (including Intercom ↔ FIN Architect)
must preserve them:

1. `decision_engine.py` is the sole source of truth for all analytical logic.
2. All functions in `decision_engine.py` are pure — no side effects, no I/O.
3. All thresholds are named constants — `KDE_HARD_CAP_BLOCKER`, `KDE_HARD_CAP_RESOLUTION`,
   `GUIDELINE_CLUSTER_THRESHOLD`, `GUIDELINE_MERGE_THRESHOLD`.
4. The import interface `import decision_engine as _de` is stable.
5. Anti-escalation in any guideline or article is always a compliance violation.
6. The escalation path must always remain open across the full ecosystem.
7. Scoring weights and thresholds do not vary by product — Attribute context
   does not alter analytical logic.

---

*FIN Intelligence v2 — Conceptual Architecture — 2026-06-26*
*Grounded in FIN Architect MCP v1.0.0 / decision_engine.py 1,264 lines / server.py 16 tools*
