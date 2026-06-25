# FIN Ecosystem — Architectural Model

**Version:** 1.0 — aligned with FIN Architect MCP v1.0.0
**Status:** Source of truth for Phase 2 intelligence tooling
**Audience:** Architecture, Product, Engineering — not end users

---

## 1. Purpose

### What this document represents

This document is the complete architectural model of the FIN ecosystem. It is not user documentation. It is the formal reference that describes every layer FIN operates across — products, knowledge, guidelines, attributes, workflows, and escalation — and how those layers interact to produce a conversation outcome.

Every structure described here is grounded in data that exists in `decision_engine.py` and `server.py`. No layer, product, or rule has been invented. Where a component is partially modeled (present in constants but not yet a full tool), that is stated explicitly.

### Scope

This model covers:

- The product domains FIN operates across and their analytical signatures
- The knowledge base layer: how articles are organized, scored, and consumed
- The guideline layer: how behavioral rules are classified, scored, and applied
- The attribute layer: how contextual signals route FIN's decision logic
- The workflow layer: the operational sequence from conversation start to resolution
- The escalation layer: the rules that govern when FIN transfers control
- The complete execution flow from first message to case closure
- Cross-layer relationships and invariants that must hold as the system evolves

### What this model does not cover

- Real-time inference infrastructure (not present in v1.0.0)
- User identity or authentication systems
- Intercom-specific configuration beyond the MCP interface
- Billing, SLA, or contractual policy (business layer, not analytical layer)

---

## 2. Products

### Overview

FIN operates across multiple product domains. Each domain has a distinct vocabulary that the analytical layer uses to detect intent, route decisions, and apply domain-specific scoring rules. Products are modeled as **intention categories** in `INTENTION_MAP` (`decision_engine.py`, line 903) and as routing signals in `simulate_fin` (`server.py`, line 3797).

### Modeled product domains

#### Restobar

The restaurant and bar vertical. FIN detects Restobar-domain conversations through signals associated with table service, orders, and kitchen operations.

**Intent signals:** `mesa`, `comanda`, `pedido`, `cocina`, `restaurante`, `bar`

Restobar cases are handled through the standard Knowledge and Guideline layers with no special hard cap. Priority escalates to ALTA when combined with technical failures (e.g., POS terminal down during service hours) or when the user is detected as Frustrado.

#### Pymes (Small and Medium Enterprises)

The SME horizontal layer. Pymes is not modeled as a dedicated intention category in v1.0.0. It is the general business context within which Facturación, Caja, Inventario, Configuración, and Reportes operate. Pymes cases are routed through those functional categories.

**Resolution target:** v1.2 — dedicated `Pymes` segment attribute for cross-domain routing.

#### Alojamientos

The hospitality and lodging vertical. Alojamientos is not modeled as a dedicated intention category in v1.0.0. Cases that originate in this domain are currently classified under the closest functional category (Facturación, Configuración, Error técnico, or Reportes).

**Resolution target:** v1.2 — dedicated `Alojamientos` intention entry with domain-specific keyword vocabulary.

#### Nómina

The payroll module. Nómina is one of four high-priority categories in the analytical layer — alongside DIAN, Seguridad, and Facturación — that trigger elevated implementation priority regardless of risk score.

**Intent signals:** `nómina`, `empleado`, `salario`, `liquidación`, `prestaciones`

**Analytical significance:** `guideline_priority_from_risk()` returns `ALTA` for Nómina categories even at BAJO risk level. This reflects the operational impact of payroll errors.

#### Supporting domains (cross-product)

These domains appear across all product verticals:

| Domain | Intent signals | Notes |
|--------|---------------|-------|
| Facturación | factura, cobro, pago, cargo, recibo, monto | Priority domain; MEDIA base priority |
| Inventario | inventario, stock, producto, artículo, bodega | Standard domain |
| Caja | caja, cierre, apertura, efectivo, denominación | Standard domain; MEDIA base priority |
| POS | pos, terminal, punto de venta, datáfono, impresora | Hardware-adjacent; Error técnico overlap |
| DIAN | dian, cufe, resolución, factura electrónica, habilitación | Regulatory; highest implementation priority |
| Reportes | reporte, informe, estadística, consulta, historial | Read-only; lower escalation risk |
| Configuración | configurar, configuración, ajuste, parámetro, módulo | Setup/onboarding overlap |
| Error técnico | error, falla, no funciona, fallo, reiniciar, caído | Technical failure; ALTA base priority |
| Acceso | acceso, contraseña, usuario, clave, iniciar sesión, bloqueado | Security-adjacent; MEDIA base priority |
| Seguridad | seguridad, permiso, rol, administrador, auditoría | Highest implementation priority |

### Product-domain relationships

```
Restobar ──────────────────────┐
Alojamientos (not yet modeled) ├──► Facturación (shared)
Pymes (cross-cutting) ─────────┘    Caja (shared)
                                    Inventario (shared)
                                    POS (shared)
                                    DIAN (Nómina + Facturación)
                                    Reportes (all products)
                                    Configuración (all products)
                                    Error técnico (all products)
                                    Acceso / Seguridad (all products)
```

No product domain is analytically isolated. Every product uses the same Knowledge and Guideline scoring frameworks. Product identity enters the system as the `product` attribute on tool calls, not as a separate scoring dimension in v1.0.0.

---

## 3. Knowledge Layer

### What the knowledge base is

The knowledge base is the collection of articles that FIN uses to resolve user issues autonomously. Each article is a text document that FIN retrieves and interprets in the context of a conversation. The quality of these articles directly determines FIN's autonomous resolution rate.

### How articles are scored

Every knowledge article is evaluated by the Knowledge Decision Engine (KDE) across 12 weighted criteria (100-point scale):

| Criterion | Weight | What it measures |
|-----------|--------|-----------------|
| Claridad | 12 | Absence of vague phrases; use of direct language |
| Pasos | 12 | Presence and completeness of step-by-step resolution instructions |
| Ambigüedad | 10 | Absence of absolute terms without conditions |
| Estructura | 10 | Logical organization: objective → steps → escalation |
| Uso por FIN | 10 | Whether FIN can extract a direct action from the article |
| Escalamiento | 8 | Presence of a clear escalation criterion |
| Cobertura | 8 | Coverage of expected resolution paths |
| Longitud | 8 | Appropriate length (not too short, not too long) |
| Consistencia | 8 | Absence of contradictory instructions |
| Terminología | 8 | Use of consistent, domain-aligned terminology |
| Mantenibilidad | 7 | Article is updateable without structural rewrite |
| Riesgo Operativo | 7 | Absence of instructions that could cause harm if misapplied |

**Hard caps** apply when blockers are detected:
- A CRÍTICO loop risk or anti-escalation rule caps `kde_health` at 60.
- A KDE blocker caps `resolution_capability` at 40.

These caps cannot be overridden by quality in other criteria.

### Knowledge domain coverage

The analytical layer tracks 11 topic domains for coverage analysis (`TOPIC_CATEGORIES`):

`facturación` · `soporte técnico` · `cancelación` · `configuración` · `escalamiento` · `reembolso` · `onboarding` · `seguridad` · `reportes` · `integraciones` · `general`

A knowledge base is considered complete when articles cover all 11 categories. Missing categories surface as coverage gaps in `repository_review` and `knowledge_review`.

### Audiences

Knowledge articles are not segmented by audience in v1.0.0. The `product` parameter on `audit_knowledge` and `knowledge_review` provides context for the audit but does not apply product-specific scoring rules. All articles are evaluated against the same 12-criterion KDE framework.

**Resolution target:** v1.2 — product-aware scoring profiles for Restobar, Nómina, and DIAN articles.

### Relationship to products

| Domain | Primary product | KDE sensitivity |
|--------|----------------|-----------------|
| Facturación, DIAN | Pymes, Nómina | High — regulatory articles require maximum clarity |
| Inventario, Caja | Restobar, Pymes | Medium — operational; step completeness critical |
| Acceso, Seguridad | All products | High — security articles must have no absolute terms |
| Error técnico, POS | All products | High — technical articles must have complete diagnostic steps |
| Reportes, Configuración | All products | Medium — lower urgency; mantenibilidad weighted more |

---

## 4. Guideline Layer

### What guidelines are

Guidelines are behavioral rules that define how FIN must respond to specific conversation patterns. Unlike knowledge articles (which contain resolution content), guidelines define **conduct**: when to escalate, how to handle emotion, what language to use, what is prohibited.

In v1.0.0, guidelines exist as text strings. There is no tracked state (draft, approved, active, deprecated). A guideline is active the moment it is passed to a tool.

### Communication style guidelines

Guidelines that govern tone and language are detected through:

- **Empathy signals** (`GUIDELINE_EMPATHY_SIGNALS`): `disculpa`, `lamentamos`, `entendemos`, `comprendo`, `lo sentimos`
- **Absolute terms** (`GUIDELINE_AMBIGUOUS_TERMS`): `siempre`, `nunca`, `normalmente`, `generalmente` — penalized in scoring
- **Vague phrases** (`GUIDELINE_VAGUE_PHRASES`): `de alguna manera`, `como sea posible`, `a discreción` — penalized

A guideline that uses absolute terms without conditions receives a higher risk score. A guideline that includes empathy language receives positive signals in `score_guideline`.

### Context guidelines

Guidelines that define behavior based on situational context are classified as **Flujo Condicional** (containing `cuando`, `si`, `solo si`) or **Regla Absoluta** (containing `siempre`, `nunca`, `todos`).

Context-sensitive guidelines (conditional flow) score lower risk than absolute rules. The `GUIDELINE_CONDITION_PAIRS` capture the most common contextual distinctions:

```
("frustración", "molesto")
("primera vez", "reincidente")
("cliente nuevo", "cliente antiguo")
("horario laboral", "fuera de horario")
```

### Escalation guidelines

Escalation is the highest-criticality guideline category. It is also the most constrained by the analytical layer:

- Guidelines containing **escalation words** (`escalar`, `transferir`, `agente humano`, `agente`) without a conditional trigger receive elevated risk scores.
- Guidelines containing **prohibition words** (`no escalar`, `nunca escalar`, `no transferir`) are flagged as anti-escalation patterns — a hard blocker.
- Guidelines containing **obligation words** (`siempre escalar`, `debe escalar`) without conditions are flagged as absolute rules.

`detect_conflicts` checks every guideline pair for contradictions. The most critical conflict pair is `("escalar", "no escalar")` — two guidelines that simultaneously instruct FIN to escalate and not escalate produce a ALTA severity conflict.

### Other guideline types

| Category | Classification trigger | Risk sensitivity |
|----------|----------------------|-----------------|
| Acceso y Seguridad | contraseña, acceso, usuario, cuenta, sesión | High — security actions must be conditional |
| Soporte Técnico | error, fallo, no funciona, problema técnico | Medium — technical instructions must be step-complete |
| Onboarding | onboarding, bienvenida, registro, activación | Low — lower operational risk |
| Facturación | factura, cobro, pago, cargo, reembolso | High — financial instructions must have clear criteria |
| General | no other category matches | Base risk profile |

### How guidelines interact

Guidelines are not applied in isolation. `simulate_fin` matches all provided guidelines against the conversation's detected intention and emotion, then resolves conflicts between competing instructions. When two guidelines apply to the same conversation and contradict each other, the conflict is flagged and escalation risk increases.

---

## 5. Attribute Layer

### What attributes represent

Attributes are the contextual signals that modify how FIN's analytical tools process a conversation or document. In v1.0.0, attributes are not a separate data type — they are the parameters passed to every MCP tool call.

### How attributes are used

Every tool in the system accepts these attributes:

| Attribute | Type | Default | Role |
|-----------|------|---------|------|
| `product` | str | `"general"` | Routes the call to product-specific context; used by `simulate_fin` priority logic |
| `context` | str | `""` | Free-text operational context passed to the tool for interpretation |

`simulate_fin` uses `product` and `context` in conjunction with detected `intention` and `emotion` to determine conversation priority:

```
emotion == "Frustrado" OR blocker signals     → priority = CRÍTICA
emotion in ("Molesto", "Urgente") OR
  intention in ("DIAN", "Seguridad", "Error técnico") → priority = ALTA
intention in ("Facturación", "Caja", "Nómina", "Acceso") → priority = MEDIA
otherwise                                              → priority = BAJA
```

### What decisions attributes control

Attributes feed into three decision branches:

1. **Priority assignment** — determines how urgently FIN must resolve or escalate
2. **Guideline matching** — `simulate_fin` uses intention keywords from the active product domain to filter which guidelines apply to the current conversation
3. **Report context** — `architect_review`, `repository_review`, and `fin_dashboard` include the `product` attribute in their outputs to scope the diagnosis

### Future attribute expansion

In v2.0, attributes are the natural extension point for:
- User segment (new customer, returning customer, enterprise)
- Conversation channel (chat, email, phone)
- Time-of-day context (business hours, off-hours)
- Previous escalation history

These would extend the existing `product`/`context` pattern — new parameters on existing tools, not new tools.

---

## 6. Workflow Layer

### Overview

A FIN conversation follows a deterministic operational sequence. The analytical layer models this sequence through the tools it provides. No step in the workflow operates outside this sequence.

### Step 1 — Initiation

The conversation begins. FIN receives the user's first message. The `architect_review` orchestrator (or individual tools) is called with:
- `conversations` — list of conversation turns
- `product` — the product domain
- `guidelines` — the active guideline set
- `objective` — optional context

### Step 2 — Classification

`detect_intention()` scans the conversation text against `INTENTION_MAP` and returns the dominant category. `detect_emotion()` scans against `FRUSTRATION_KEYWORDS`, `ANNOYANCE_KEYWORDS`, `URGENCY_KEYWORDS`, and `NEUTRAL_KEYWORDS`.

These two signals — **intention** and **emotion** — are the primary routing inputs for every downstream decision.

### Step 3 — Routing

Priority is computed from the combination of intention and emotion (see Attribute Layer, section 5). This priority determines:
- Which guideline templates apply
- Whether immediate escalation is indicated
- How the conversation is classified in the executive report

`extract_guidelines` clusters conversation patterns through Jaccard similarity to detect which behavior patterns are recurring and require new guidelines.

### Step 4 — Attention

`simulate_fin` processes each active guideline against the conversation. It determines:
- Which guidelines apply (by intention keyword overlap)
- What action the guidelines instruct (`escalate`, `resolve`, `guide`, `request_info`)
- Whether the active guidelines conflict with each other
- The aggregate escalation risk score

If the guidelines instruct resolution, `audit_knowledge` verifies whether a qualifying knowledge article exists. If the article's KDE health is below threshold or a blocker is present, autonomous resolution is not possible.

### Step 5 — Escalation

If resolution is not possible (no qualifying article, blocked health score, high escalation risk, or explicit guideline instruction), FIN escalates. The escalation rules in the Escalation Layer (section 7) determine the path and the information required for handoff.

### Step 6 — Closure

The conversation closes when:
- FIN resolves autonomously (article used, steps followed, `problem_resolved` event detected)
- FIN escalates with complete handoff information
- The user disengages

`fin_dashboard` aggregates outcomes across all conversations into an executive health report. `recommend_improvements` produces the ranked action backlog for closing architectural gaps identified during the workflow.

---

## 7. Escalation Layer

### Rules

Escalation in FIN is governed by a set of explicit rules encoded in the analytical layer. These rules are not heuristics — they are deterministic conditions evaluated from the conversation text and the active guidelines.

**Rule 1 — Hard blocker:** If a loop risk of CRÍTICO is detected OR an anti-escalation pattern is present, the knowledge article is capped at health 60 and resolution capability 40. The article cannot be used for autonomous resolution.

**Rule 2 — Anti-escalation prohibition:** If a guideline contains an anti-escalation pattern (`nunca escalar`, `no transferir`, `no escales`, `nunca escalar`, `no ofrecer`), it is flagged as a compliance violation. Anti-escalation guidelines that block a legitimate escalation path are a ALTO risk finding.

**Rule 3 — Conflict escalation:** If two active guidelines contradict each other on escalation (`"escalar"` vs `"no escalar"`), `detect_conflicts` assigns ALTA severity. The conflict must be resolved before the guideline set is considered production-ready.

**Rule 4 — Mandatory escalation triggers:** The following events in `GUIDELINE_EVENT_CATALOG` carry the highest escalation risk and require immediate escalation evaluation:
- `user_blocked` (esc_risk: 55) — user completely blocked
- `user_tried_docs` (esc_risk: 60) — user already followed documentation
- `unnecessary_escalation_risk` (esc_risk: 65) — FIN cannot diagnose

### Priorities

Escalation priority mirrors conversation priority:

| Priority | Condition | Target |
|----------|-----------|--------|
| CRÍTICA | Frustrado + blocker OR system down | Immediate transfer |
| ALTA | Urgente/Molesto OR DIAN/Seguridad/Error técnico | Expedited transfer with ETA |
| MEDIA | Facturación/Caja/Nómina/Acceso | Standard transfer |
| BAJA | General/Configuración/Reportes | Transfer with full context |

### Transfer conditions

A valid escalation must include:
1. The exact error or symptom reported by the user
2. The steps FIN already performed and the result of each
3. The knowledge articles consulted (if any) and why they were insufficient
4. The emotion state and priority level
5. The product domain and any relevant context attributes

These requirements are enforced by `GUIDELINE_BEHAVIOR_MAP` for the `"escalamiento sin criterios"` failure type:

> "FIN debe agotar al menos 2 alternativas de resolución autónoma antes de escalar. Al escalar, debe incluir: error exacto, pasos realizados y resultado de cada uno."

### Conditions that block escalation

- A guideline explicitly prohibits escalation → compliance violation, must be resolved
- FIN has not yet requested diagnostic information → must request before escalating
- The conversation has not reached a documented failure point → autonomous resolution must be attempted first

---

## 8. Complete Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER SENDS MESSAGE                               │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CLASSIFICATION                                                         │
│  detect_intention() → INTENTION_MAP → category                         │
│  detect_emotion()   → FRUSTRATION / ANNOYANCE / URGENCY / NEUTRAL      │
│  priority           → CRÍTICA / ALTA / MEDIA / BAJA                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  GUIDELINE MATCHING                                                     │
│  simulate_fin: match guidelines to intention + emotion                 │
│  Flags: escalate / resolve / guide / request_info                      │
│  detect_conflicts: check pairwise contradiction                        │
│  Conflict? → flag, increase escalation risk                            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              flags: resolve         flags: escalate OR
              OR request_info        no qualifying article
                    │                       │
                    ▼                       ▼
┌───────────────────────────┐  ┌───────────────────────────────────────┐
│  KNOWLEDGE LOOKUP         │  │  ESCALATION PATH                      │
│  audit_knowledge          │  │                                       │
│  kde_score_article()      │  │  Priority: CRÍTICA → immediate        │
│  health ≥ threshold?      │  │  Priority: ALTA    → expedited + ETA  │
│  No blocker?              │  │  Priority: MEDIA   → standard         │
└───────────┬───────────────┘  │  Priority: BAJA    → with context     │
            │                  │                                       │
       ┌────┴────┐             │  Transfer payload:                    │
       │         │             │  · exact error                        │
      YES        NO            │  · steps attempted                    │
       │         │             │  · articles consulted                 │
       ▼         └────────────►│  · emotion + priority                 │
┌──────────────┐               │  · product + context                  │
│  AUTONOMOUS  │               └───────────────────────────────────────┘
│  RESOLUTION  │                                   │
│              │                                   ▼
│  FIN guides  │                    ┌──────────────────────────────────┐
│  user through│                    │  HUMAN AGENT RECEIVES CASE       │
│  article     │                    │  with complete context payload    │
└──────┬───────┘                    └──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  OUTCOME DETECTION                                                   │
│  detect_guideline_events() → problem_resolved / problem_persists     │
│  problem_resolved → case closed autonomously                         │
│  problem_persists → re-enter workflow at GUIDELINE MATCHING          │
│  fin_repeats_solution → flag loop risk, consider escalation          │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  REPORTING                                                           │
│  fin_dashboard       → executive health report                       │
│  repository_review   → global health, debt, coverage gaps           │
│  recommend_improvements → ranked improvement backlog                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 9. Cross-layer Relationships

The five layers do not operate in isolation. Every tool call traverses multiple layers simultaneously.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ATTRIBUTE LAYER                                 │
│          product · context → routing and priority signals           │
└───────┬─────────────────────────────────┬───────────────────────────┘
        │                                 │
        ▼                                 ▼
┌───────────────────┐           ┌─────────────────────┐
│  KNOWLEDGE LAYER  │           │  GUIDELINE LAYER     │
│  articles         │           │  behavioral rules    │
│  KDE scoring      │◄──────────│  classify_guideline  │
│  coverage gaps    │           │  detect_conflicts    │
│  knowledge debt   │           │  score_guideline     │
└────────┬──────────┘           └──────────┬───────────┘
         │                                 │
         └─────────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │   WORKFLOW LAYER    │
              │   simulate_fin      │
              │   architect_review  │
              │   extract_guidelines│
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  ESCALATION LAYER   │
              │  rules + conditions │
              │  transfer payload   │
              │  priority routing   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  REPORTING          │
              │  fin_dashboard      │
              │  recommend_         │
              │  improvements       │
              └─────────────────────┘
```

### Key cross-layer dependencies

| Dependency | Layers involved | Mechanism |
|------------|----------------|-----------|
| Intention drives guideline matching | Attribute → Guideline | `INTENTION_MAP` keyword overlap in `simulate_fin` |
| Emotion drives priority | Attribute → Workflow → Escalation | Emotion detection feeds priority assignment in `simulate_fin` |
| Knowledge health blocks resolution | Knowledge → Workflow | KDE hard cap prevents autonomous resolution path |
| Anti-escalation blocks escalation | Guideline → Escalation | `detect_anti_escalation()` sets hard cap on knowledge health |
| Conflict severity drives escalation risk | Guideline → Escalation | `conflict_severity_level()` feeds escalation risk score |
| Coverage gaps inform roadmap | Knowledge → Reporting | `compute_coverage()` identifies missing `TOPIC_CATEGORIES` |
| Conversation events drive guideline extraction | Workflow → Guideline | `GUIDELINE_EVENT_CATALOG` patterns cluster into new guideline candidates |

---

## 10. Architectural Invariants

These rules apply to FIN Architect MCP in all versions. Any tool, module, or layer added in Phase 2 must comply with all of them.

**Invariant 1 — Single analytical source of truth**
All scoring, detection, classification, and ranking logic lives in `decision_engine.py`. No new tool may implement analytical logic inline. Every new function goes into `decision_engine.py` first; the tool calls `_de.*` and formats the result.

**Invariant 2 — Pure functions**
All functions in `decision_engine.py` are pure: same inputs always produce the same outputs, no side effects, no I/O, no global state mutation. This must hold for all functions added in Phase 2.

**Invariant 3 — Named constants only**
No inline magic numbers or hardcoded strings in analytical logic. Every threshold, pattern, and catalog entry is a named module-level constant in `decision_engine.py`.

**Invariant 4 — Stable import interface**
The import alias `import decision_engine as _de` is stable. Tools call `_de.*`. No sub-module complexity, no dynamic imports.

**Invariant 5 — Hard caps are unconditional**
`KDE_HARD_CAP_BLOCKER = 60` and `KDE_HARD_CAP_RESOLUTION = 40` cannot be bypassed by quality in other criteria. No new scoring criterion may override a blocker. If a new blocker type is added, it must respect the same cap mechanism.

**Invariant 6 — Anti-escalation is a compliance violation**
Any guideline pattern that instructs FIN to never escalate under any condition is a blocker, not a warning. Detection of anti-escalation patterns in knowledge articles produces a health cap. Detection in guidelines produces a risk flag. This behavior must not be softened in any version.

**Invariant 7 — No behavior change without a version increment**
No existing tool's observable output may change without an explicit version increment in `docs/CHANGELOG.md`. Adding a new function to `decision_engine.py` is not a behavior change. Changing a threshold, pattern vocabulary, or scoring weight is.

**Invariant 8 — No duplicate analytical logic**
Zero duplicate function implementations in `decision_engine.py`. This was verified at v1.0.0 release via AST analysis. Any architecture sprint must run the duplicate detection script before merge.

**Invariant 9 — Escalation path is always available**
No tool, guideline, or configuration may result in a state where FIN has no valid escalation path. The escalation channel must remain open even when autonomous resolution fails. Guidelines that close this path are a compliance violation, not a design choice.

**Invariant 10 — Product context does not change scoring logic**
The `product` attribute provides context for reporting and routing. It does not alter KDE thresholds, risk classifications, or scoring weights. Scoring logic is product-agnostic in v1.0.0. Product-aware scoring profiles, if introduced in v1.2, must be implemented as separate constant sets — not as conditional branches inside existing scoring functions.

---

## 11. Future Evolution

This model is designed to be the foundation for Phase 2 intelligence tooling. Each planned tool maps directly to a layer defined in this document.

### `ecosystem_review`

**Layer:** Cross-layer (all five)
**Purpose:** A holistic health report for the entire FIN ecosystem in one call. Would combine the output of `repository_review` (Knowledge Layer), `detect_conflicts` across all guidelines (Guideline Layer), `fin_dashboard` (Workflow Layer), and escalation rule compliance (Escalation Layer) into a single executive diagnosis.

**Foundation already in place:** `fin_dashboard` and `architect_review` already perform partial cross-layer aggregation. `ecosystem_review` would extend this to include explicit compliance checks against the Architectural Invariants in section 10.

### `workflow_health`

**Layer:** Workflow Layer
**Purpose:** Measures the health of the conversation workflow by analyzing patterns across a set of conversations. Detects workflow failures: excessive loops (`fin_repeats_solution` event), unresolved urgency (`user_urgency` without `problem_resolved`), systematic escalation without autonomous resolution attempts.

**Foundation already in place:** `GUIDELINE_EVENT_CATALOG` (12 events with `impact` and `esc_risk` scores), `detect_guideline_events()`, `extract_guidelines` clustering logic. `workflow_health` would aggregate event frequency across a conversation set rather than analyzing individual conversations.

### `attribute_health`

**Layer:** Attribute Layer
**Purpose:** Audits the consistency and coverage of attributes across the active guideline and knowledge base sets. Detects: guidelines with no `product` scope (applies to everything), knowledge articles with no `context` anchor, missing attribute coverage for high-priority domains (DIAN, Nómina, Seguridad).

**Foundation already in place:** `product` and `context` parameters are present on all 15 tools. `classify_guideline` already resolves product-domain alignment through `INTENTION_MAP`. `attribute_health` would formalize this into a coverage report.

### `knowledge_graph`

**Layer:** Knowledge Layer (persistent)
**Purpose:** A persistent layer that tracks knowledge article health over time. Records KDE scores per article ID, detects score regression after edits, surfaces trend data (which categories are improving, which are degrading). Requires a storage backend (SQLite for local, PostgreSQL for production).

**Foundation already in place:** `kde_score_article()` and `kde_score_article_fast()` produce all required signals. The persistent layer would store their outputs, not reimplement them. The `decision_engine.py` functions remain stateless — persistence sits between `server.py` and an external store, per Architectural Decision AD-5.

### `ecosystem_dashboard`

**Layer:** Reporting (cross-layer)
**Purpose:** The Phase 2 successor to `fin_dashboard`. Extends the executive health report with: per-product health breakdown, trend lines from `knowledge_graph`, workflow failure rates from `workflow_health`, attribute coverage from `attribute_health`, and escalation compliance from the Escalation Layer.

**Foundation already in place:** `fin_dashboard` already produces traffic-light indicators per module and a global health score. `ecosystem_dashboard` adds the time dimension and the product-segmented view.

### Constraint on all Phase 2 tools

Every tool listed above must comply with all 10 Architectural Invariants in section 10. Specifically:
- Analytical logic goes into `decision_engine.py`, not into the new tool's implementation
- New functions must be pure
- New constants must be named and module-level
- No existing tool's observable output changes as a side effect of adding Phase 2 tools

The ecosystem model defined in this document is the input specification for Phase 2 design. Tools that operate outside the layer model defined here — inventing new layers or bypassing existing ones — are not valid extensions of FIN Architect.

---

*FIN Ecosystem Architectural Model — aligned with FIN Architect MCP v1.0.0 — 2026-06-25*
