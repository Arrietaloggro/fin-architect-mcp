# ecosystem_review — Architectural Design

**Status:** Design only — no code written
**Aligned with:** FIN Architect MCP v1.0.0 / FIN_ECOSYSTEM.md v1.0
**Date:** 2026-06-25

---

## 1. Objective

`ecosystem_review` is a cross-layer health tool. Its goal is to answer a single executive question:

> **Is the FIN ecosystem — across all products, all guidelines, all knowledge articles, and all escalation rules — architecturally sound and ready to operate?**

The existing tools answer this question per-layer or per-product:
- `repository_review` evaluates the Knowledge and Guideline layers per product
- `detect_conflicts` evaluates the Guideline layer for a single product
- `fin_dashboard` produces an executive report from `repository_review` output

`ecosystem_review` is designed to go one level above all of them. It evaluates:
1. The cross-product guideline layer for ecosystem-wide conflicts (guidelines from different products contradicting each other)
2. The escalation compliance layer (does the full guideline set contain any anti-escalation violations)
3. The knowledge coverage layer against the 11 `TOPIC_CATEGORIES` across all products combined
4. The invariant compliance layer (do the active guidelines violate any of the 10 Architectural Invariants defined in `FIN_ECOSYSTEM.md`)
5. A unified ecosystem score that is not a simple average of product scores, but a weighted composite that penalizes cross-product gaps that `repository_review` cannot see

This tool does not replace `repository_review` or `fin_dashboard`. It sits above them in the reporting hierarchy.

---

## 2. Problems it will solve

### Problem 1 — Cross-product guideline conflicts are invisible

`detect_conflicts` operates on a single product's guideline set. If Product A has a guideline that says "Escala siempre en casos de facturación" and Product B has a guideline that says "No escalar sin autorización del supervisor", neither tool detects the contradiction — because each only sees its own product.

In a multi-product ecosystem, agents and knowledge articles are often shared across products (a Facturación article applies to Restobar, Pymes, and Alojamientos). A contradiction between products is an operational risk that manifests when the same article or conversation is evaluated under two conflicting guideline sets.

**What `ecosystem_review` resolves:** Cross-product Jaccard + contradiction pattern analysis across all guidelines from all products simultaneously.

### Problem 2 — Escalation compliance is not evaluated globally

The escalation compliance rules (Architectural Invariants 6 and 9 in `FIN_ECOSYSTEM.md`) require that no configuration leaves FIN without a valid escalation path. Currently, no single tool verifies escalation compliance across the full ecosystem — only per-product, per-article, or per-guideline.

A single anti-escalation guideline in one product that also governs shared articles can propagate a compliance violation system-wide without detection.

**What `ecosystem_review` resolves:** Escalation compliance audit across all guidelines and articles from all products in a single call.

### Problem 3 — The ecosystem score is not defined

`fin_dashboard` produces a global health score as an average of product health scores. This is a valid starting point, but it does not account for:
- Cross-product conflicts (two products with BAJO risk individually but a ALTA conflict between them)
- Invariant violations (a violation that makes the ecosystem non-compliant regardless of health scores)
- Knowledge coverage at the ecosystem level vs. per-product coverage

**What `ecosystem_review` resolves:** A composite Ecosystem Health Score (EHS) that incorporates cross-layer and cross-product signals that no existing tool captures.

### Problem 4 — No tool verifies Architectural Invariant compliance

The 10 invariants in `FIN_ECOSYSTEM.md` and the 7 architecture rules in `docs/CONTRIBUTING.md` are documented but not enforced by any tool. A guideline set that violates Invariant 6 (anti-escalation is always a violation) or Invariant 9 (escalation path must always be open) is not currently flagged at the ecosystem level.

**What `ecosystem_review` resolves:** Explicit invariant compliance check for the guidelines and knowledge articles passed to the tool.

---

## 3. Inputs

```
ecosystem_review(
    products: list,        # required — same schema as repository_review
    conversations: list,   # optional — list of str; adds Workflow layer analysis
    context: str           # optional — free-text operational context
) -> str
```

### `products` — required

Same schema as `repository_review` and `fin_dashboard`:

```json
[
  {
    "nombre": "Restobar",
    "guidelines": ["guideline text 1", "guideline text 2"],
    "knowledge_articles": ["article text 1", "article text 2"]
  },
  {
    "nombre": "Nómina",
    "guidelines": ["..."],
    "knowledge_articles": ["..."]
  }
]
```

Minimum: 1 product. Designed for 2–10 products. No hard upper limit, but performance degrades on cross-product pairwise comparisons at scale (see Risk 1 in section 11).

### `conversations` — optional

A list of conversation text strings. When provided, enables the Workflow layer analysis:
- Detects dominant intentions across all conversations via `detect_intention()`
- Detects emotion distribution via `detect_emotion()`
- Identifies which product domains the conversations map to
- Detects conversation events via `detect_guideline_events()`
- Identifies conversations with no matching guideline (uncovered workflow gaps)

When omitted, the Workflow layer section of the report is replaced with "Conversaciones no proporcionadas — análisis de workflow omitido."

### `context` — optional

Passed through to `repository_review` and used in the report header. Does not affect analytical logic.

---

## 4. Modules the tool will reuse

### `server.py` tools called directly

| Tool called | Why |
|-------------|-----|
| `repository_review(products, context)` | Per-product health scores, knowledge debt, coverage, duplicate detection. Avoids re-implementing all per-product logic. |
| `detect_conflicts(guidelines, product, context)` | Called once per product for intra-product conflict detection. Cross-product conflicts are computed separately in `ecosystem_review`. |
| `recommend_improvements(repository_review, ...)` | Produces the ranked improvement backlog. Called with the output of `repository_review`. |

### `decision_engine.py` functions called directly

See section 5 for the complete list with signatures.

### Pattern: call existing tools, then extend

`fin_dashboard` demonstrated this pattern: it calls `repository_review` and `recommend_improvements` as sub-calls, then extends the output with traffic-light indicators and deployment decision. It does not re-implement any analytical logic.

`ecosystem_review` follows the same pattern:
- Call `repository_review` → get per-product scores
- Call `detect_conflicts` per product → get intra-product conflicts
- Call `recommend_improvements` → get ranked backlog
- Then add cross-product analysis using `_de.*` directly
- Compose the final report

This structure ensures zero duplication with existing tools.

---

## 5. Decision Engine functions used

All functions listed here already exist in `decision_engine.py`. No new functions are required for Phase 1 of implementation.

### Cross-product guideline analysis

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `jaccard` | `(words_a: set, words_b: set) -> float` | Cross-product pairwise guideline similarity. When `jaccard >= 0.30` and a contradiction pair matches, a cross-product conflict is flagged. |
| `word_set` | `(text: str) -> set` | Tokenizes each guideline text once; the frozenset is reused across all pairwise comparisons. |
| `kde_score_guideline_fast` | `(text: str) -> dict` | Fast guideline scoring for all guidelines across all products. Returns `blocked`, `health`, `has_escalation`, `anti_escalation`, `words`. |

### Escalation compliance audit

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `detect_anti_escalation` | `(text_lower: str, use_repo_patterns: bool = False) -> bool` | Called with `use_repo_patterns=True` on all guidelines and articles. Any match is an Invariant 6 violation. |
| `detect_escalation_repo` | `(text_lower: str) -> bool` | Checks whether the full ecosystem has at least one article with a valid escalation criterion. |
| `detect_loop_risk` | `(text_lower: str, use_repo_patterns: bool = False) -> tuple` | Called with `use_repo_patterns=True` on all articles. Returns `(level, count, hits)`. CRÍTICO → hard blocker. |
| `detect_fin_blockers` | `(text_lower: str) -> list` | FIN blocker detection on all articles. |

### Coverage and debt

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `compute_coverage` | `(all_text: str) -> tuple` | Called on the combined text of all articles from all products. Returns `(covered_cats, missing_cats)`. |
| `compute_knowledge_debt` | `(blocked_articles, g_conflicts, dup_articles, missing_cats, blocked_guidelines, high_risk_articles) -> tuple` | Computes ecosystem-level knowledge debt from the aggregated cross-product counts. |
| `debt_label_emoji` | `(knowledge_debt: int) -> tuple` | Maps debt score to label and emoji. |

### Status and deployment

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `global_status_from_health` | `(global_health, prod_blocked_count, prod_high_risk) -> tuple` | Ecosystem global status label. |
| `deployment_readiness` | `(prod_blocked_count, total_a_blocked, total_g_blocked, global_health, knowledge_debt, prod_high_risk) -> tuple` | Ecosystem deployment decision. |
| `semaforo` | `(value: int, thresholds: tuple) -> tuple` | Traffic-light indicator per section score. Thresholds: `(70, 85)` for health scores; `(20, 40)` for debt (inverted). |

### Workflow layer (when conversations provided)

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `detect_intention` | `(text_lower: str) -> str` | Dominant intention per conversation. Distribution across all conversations shows which product domains are most active. |
| `detect_emotion` | `(text_lower: str) -> str` | Emotion distribution. High Frustrado/Urgente ratio is a workflow health signal. |
| `detect_guideline_events` | `(text_lower: str) -> list` | Event detection across conversations. Aggregated event frequency identifies recurring workflow failures. |

### Utilities

| Function | Signature | Usage in ecosystem_review |
|----------|-----------|--------------------------|
| `extract_metrics_from_reports` | `(repository_review_text, knowledge_review_text, architect_review_text) -> dict` | Extracts structured metrics from the `repository_review` text output. Avoids re-parsing. |
| `risk_level_from_health` | `(kde_health: int, has_blocker: bool) -> str` | Per-product risk level for the ecosystem ranking table. |

### Constants used (no new constants needed for Phase 1)

| Constant | Usage |
|----------|-------|
| `GUIDELINE_CONTRADICTION_PAIRS` | Cross-product conflict detection |
| `GUIDELINE_CONDITION_PAIRS` | Cross-product condition conflict detection |
| `TOPIC_CATEGORIES` | Ecosystem-level coverage gap identification |
| `GUIDELINE_ABSOLUTE_WORDS` | Invariant compliance check (absolute terms audit) |
| `ANTI_ESCALATION_PATTERNS_REPO` | Invariant 6 compliance check |

---

## 6. What information is obtained from each layer

### Knowledge Layer

Obtained via `repository_review` sub-call + direct `_de.*` calls:

- Per-product article count, blocked count, ALTO risk count, average health, duplicate pairs
- Ecosystem-level coverage: `compute_coverage()` on the union of all article texts
- Ecosystem knowledge debt: `compute_knowledge_debt()` from aggregated cross-product counts
- Loop risk distribution: `detect_loop_risk()` on each article (already done inside `repository_review`; extracted via `extract_metrics_from_reports()`)
- Articles with anti-escalation patterns (Invariant 6 signal)
- Articles with FIN blockers

**Key output:** knowledge health score per product, ecosystem coverage percentage, ecosystem debt score, blocker count.

### Guideline Layer

Obtained via `detect_conflicts` sub-calls (per product) + direct cross-product analysis:

**Intra-product (from `detect_conflicts`):**
- Conflict count and severity per product
- Guidelines with anti-escalation rules
- Guidelines with absolute terms without conditions

**Cross-product (computed in `ecosystem_review` directly):**
- All guidelines from all products are collected into a single pool
- `word_set()` is computed once per guideline
- `jaccard()` is run on every cross-product pair (not intra-product — those are already covered)
- Pairs with `jaccard >= 0.30` AND a matching entry in `GUIDELINE_CONTRADICTION_PAIRS` → cross-product conflict
- Severity is assigned by the same rules as `detect_conflicts` using `conflict_severity_level()`

**Key output:** intra-product conflict counts (from sub-calls), cross-product conflict count and severity (computed here), anti-escalation violation count across all products.

### Attribute Layer

The `product` attribute on each product dict is the primary routing signal. The Attribute Layer analysis in `ecosystem_review` covers:

- Number of distinct product domains present
- Product domains with no guidelines (attribute scope is undefined)
- Product domains with no knowledge articles (attribute is orphaned)
- Products with ALTO risk that share articles or guidelines with BAJO risk products (attribute contamination: one product's weak guidelines affect another's evaluation)

In v1.0.0, `product` and `context` do not alter scoring weights. The Attribute Layer analysis is therefore structural — it checks completeness and isolation, not scoring.

**Key output:** attribute coverage map (which products are defined, which are incomplete), orphaned attribute detection.

### Workflow Layer

Only computed when `conversations` list is provided.

- Intention distribution: `detect_intention()` on each conversation → frequency per INTENTION_MAP category
- Emotion distribution: `detect_emotion()` on each conversation → Frustrado/Molesto/Urgente/Neutral counts
- Event distribution: `detect_guideline_events()` → which `GUIDELINE_EVENT_CATALOG` events appear most frequently
- Uncovered workflow gaps: conversations whose dominant intention maps to a product domain that has no guidelines and no knowledge articles
- High-escalation-risk conversations: conversations with events `user_tried_docs` (esc_risk: 60), `unnecessary_escalation_risk` (esc_risk: 65), or `user_blocked` (esc_risk: 55)

**Key output:** workflow health indicators, top 3 recurring events, uncovered domain count, escalation risk distribution.

### Escalation Layer

Computed entirely from `_de.*` functions on the full guideline and article set:

**Compliance checks (mapped to Architectural Invariants):**

| Check | Invariant | Signal |
|-------|-----------|--------|
| Any guideline with `detect_anti_escalation(..., use_repo_patterns=True)` | Invariant 6 | Anti-escalation violation — hard flag |
| Any article with `detect_anti_escalation(..., use_repo_patterns=True)` | Invariant 6 | Same — hard flag |
| Full article corpus has zero `detect_escalation_repo()` matches | Invariant 9 | Escalation path closed — critical finding |
| Cross-product conflict on escalation instruction | Invariant 6 | Cross-product compliance violation |

**Escalation health score:** Derived from the count and severity of violations. Formula:

```
escalation_health = 100
  − (anti_escalation_violations × 20)   # each violation −20, capped at −60
  − (path_closed_violation × 30)        # if escalation path is closed −30
  − (cross_product_esc_conflicts × 10)  # each cross-product conflict −10, capped at −30
  = floor at 0
```

**Key output:** escalation health score (0–100), violation list with severity, compliance status (COMPLIANT / VIOLATION DETECTED / CRITICAL VIOLATION).

---

## 7. Metrics calculated

### Per-product metrics (from `repository_review` sub-call)

| Metric | Source |
|--------|--------|
| `prod_health` | Weighted avg: guidelines 40% + articles 60%; capped at 60 if blocked |
| `prod_risk` | BAJO / MEDIO / ALTO derived from `prod_health` and blocker presence |
| `g_avg_health` | Average `kde_score_guideline_fast().health` across product guidelines |
| `a_avg_health` | Average `kde_score_article_fast().health` across product articles |
| `g_blocked` | Count of guidelines with `blocked=True` |
| `a_blocked` | Count of articles with `deploy=BLOQUEADO` |
| `g_conflicts` | Intra-product conflicts from `detect_conflicts` |
| `a_dups` | Duplicate article pairs with Jaccard ≥ 0.55 |
| `coverage_pct` | % of `TOPIC_CATEGORIES` covered by product articles |
| `missing_cats` | List of uncovered categories |

### Ecosystem-level metrics (computed in `ecosystem_review`)

| Metric | Formula / Source | Range |
|--------|-----------------|-------|
| `ecosystem_coverage_pct` | `compute_coverage(all_articles_combined)` | 0–100% |
| `ecosystem_knowledge_debt` | `compute_knowledge_debt(aggregated inputs)` | 0–100 |
| `cross_product_conflicts` | Cross-product jaccard + contradiction pair matches | ≥ 0 |
| `anti_escalation_violations` | Sum of `detect_anti_escalation()` matches across all guidelines + articles | ≥ 0 |
| `escalation_path_open` | `any(detect_escalation_repo(a) for a in all_articles)` | bool |
| `escalation_health` | Formula in section 6 (Escalation Layer) | 0–100 |
| `global_health` | `global_status_from_health()` input; avg of `prod_health` values, capped at 60 if any product blocked | 0–100 |
| `ecosystem_health_score` (EHS) | Composite score — see section 9 | 0–100 |
| `deployment_readiness` | `deployment_readiness()` from `_de` | NOT READY / READY WITH RECOMMENDATIONS / READY |

### Workflow metrics (when `conversations` provided)

| Metric | Source |
|--------|--------|
| `dominant_intentions` | Frequency distribution from `detect_intention()` |
| `emotion_distribution` | Count per emotion from `detect_emotion()` |
| `top_events` | Top 3 event IDs by frequency from `detect_guideline_events()` |
| `uncovered_domains` | Product domains with active conversations but no guidelines |
| `high_esc_risk_conversations` | Count with esc_risk events > 55 |
| `workflow_health` | Derived: 100 − (uncovered_domains × 15) − (high_esc_risk_pct × 0.5) |

---

## 8. Report structure

The report is a formatted string divided into 8 sections, consistent with the report style of `repository_review` and `fin_dashboard`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ECOSYSTEM REVIEW — FIN ARCHITECT
  [context if provided]
  [N] productos · [N] guidelines · [N] artículos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECCIÓN 1 — ECOSYSTEM HEALTH SCORE
  EHS: [score]/100 [semaforo emoji]
  Estado global: [SALUDABLE / ACEPTABLE / EN REVISIÓN / BLOQUEADO]
  Decisión de despliegue: [READY / READY WITH RECOMMENDATIONS / NOT READY]

SECCIÓN 2 — PRODUCT RANKING
  [Ranked table: producto | salud | riesgo | guidelines | artículos | estado]

SECCIÓN 3 — KNOWLEDGE LAYER
  Cobertura ecosistema: [N]%
  Knowledge Debt: [score] [label] [emoji]
  Artículos bloqueados (total): [N]
  Categorías sin cobertura: [list]

SECCIÓN 4 — GUIDELINE LAYER
  Conflictos intra-producto: [N] (total across all products)
  Conflictos cross-producto: [N] [severity breakdown]
  Guidelines bloqueadas: [N]
  [Cross-product conflict detail list]

SECCIÓN 5 — ESCALATION COMPLIANCE
  Estado: [COMPLIANT / VIOLATION DETECTED / CRITICAL VIOLATION] [emoji]
  Escalation Health: [score]/100
  Violaciones de anti-escalamiento: [N]
  Ruta de escalamiento abierta: [SÍ / NO]
  [Violation detail list if any]

SECCIÓN 6 — ATTRIBUTE LAYER
  Productos con cobertura completa: [N]/[total]
  Productos sin guidelines: [list]
  Productos sin artículos: [list]
  Dominios con mayor actividad: [from conversations if provided]

SECCIÓN 7 — WORKFLOW LAYER
  [If conversations provided:]
  Conversaciones analizadas: [N]
  Intención dominante: [category] ([N]%)
  Distribución emocional: Frustrado [N]% · Molesto [N]% · Urgente [N]% · Neutral [N]%
  Eventos más frecuentes: [top 3 event labels]
  Dominios sin cobertura de guideline: [N]
  [If not provided:]
  "Conversaciones no proporcionadas — análisis de workflow omitido."

SECCIÓN 8 — PLAN DE ACCIÓN
  CRÍTICO (resolver antes de operar):
    [list of blocker-level findings]
  SPRINT (resolver en próximo ciclo):
    [list of high-priority improvements]
  MEJORAS (siguiente versión):
    [list of medium-priority improvements]
  [From recommend_improvements sub-call output]
```

---

## 9. Ecosystem Health Score (EHS)

The EHS is a composite score on a 0–100 scale. It is **not** a simple average of product health scores. It is a weighted sum that penalizes cross-layer failures that product-level averages cannot capture.

### Formula

```
EHS = round(
    knowledge_component    × 0.30
  + guideline_component    × 0.25
  + escalation_component   × 0.25
  + coverage_component     × 0.10
  + workflow_component     × 0.10   # replaces with 0 when no conversations provided;
                                    # redistribution: knowledge 0.35, guideline 0.30, escalation 0.30, coverage 0.05
)
```

### Component definitions

**`knowledge_component`** (0–100):
```
= global_health (from repository_review)
```
Uses the same global health computed by `repository_review`: weighted average of product healths, capped at 60 if any product is blocked.

**`guideline_component`** (0–100):
```
= 100
  − (total_intra_product_conflicts × 5)   # each −5, capped at −30
  − (cross_product_conflicts × 10)        # each −10, capped at −30
  − (total_g_blocked × 8)                 # each −8, capped at −20
  floor at 0
```

**`escalation_component`** (0–100):
```
= escalation_health  (from section 6, Escalation Layer)
```

**`coverage_component`** (0–100):
```
= ecosystem_coverage_pct  (from compute_coverage on all articles combined)
```

**`workflow_component`** (0–100, only when conversations provided):
```
= workflow_health  (from section 7, Workflow metrics)
```

### Hard penalties (applied after weighted sum)

These are not deductions — they cap the EHS regardless of other scores:

| Condition | EHS cap |
|-----------|---------|
| Any invariant violation (anti-escalation in any guideline/article) | max EHS = 60 |
| Escalation path closed (no article with valid escalation criterion) | max EHS = 40 |
| Any product with `prod_blocked = True` | max EHS = 70 (consistent with KDE_HARD_CAP_BLOCKER) |

Hard penalties stack. A tool with 3 blocked products AND an anti-escalation violation AND a closed escalation path has `EHS = min(60, 40, 70) = 40`.

### EHS interpretation

| EHS | Label | Emoji | Deployment |
|-----|-------|-------|------------|
| ≥ 85 | SALUDABLE | 🟢 | READY |
| 70–84 | ACEPTABLE | 🟡 | READY WITH RECOMMENDATIONS |
| 50–69 | EN REVISIÓN | 🟠 | READY WITH RECOMMENDATIONS |
| < 50 | BLOQUEADO | 🔴 | NOT READY |

---

## 10. Code reuse strategy

The central reuse principle is: **call existing tools as sub-functions, then extend with cross-layer logic using `_de.*` directly.**

### Reuse map

| Existing capability | Reused how |
|---------------------|-----------|
| Per-product knowledge + guideline scoring | `await repository_review(products, context)` sub-call |
| Improvement backlog | `await recommend_improvements(rr_output, ...)` sub-call |
| Intra-product conflict detection | `await detect_conflicts(product_guidelines, product_name, context)` per product |
| Global health → status label | `_de.global_status_from_health()` |
| Deployment decision | `_de.deployment_readiness()` |
| Knowledge debt score | `_de.compute_knowledge_debt()` on aggregated metrics |
| Coverage analysis | `_de.compute_coverage()` on combined article text |
| Traffic-light formatting | `_de.semaforo()` per section score |
| Guideline fast scoring | `_de.kde_score_guideline_fast()` for cross-product pool |
| Similarity computation | `_de.jaccard()` + `_de.word_set()` |
| Conflict pair matching | `_de.GUIDELINE_CONTRADICTION_PAIRS` |
| Anti-escalation detection | `_de.detect_anti_escalation(..., use_repo_patterns=True)` |
| Escalation path check | `_de.detect_escalation_repo()` |
| Metrics extraction | `_de.extract_metrics_from_reports(rr_output)` |
| Intention classification | `_de.detect_intention()` |
| Emotion detection | `_de.detect_emotion()` |
| Event detection | `_de.detect_guideline_events()` |

### What `ecosystem_review` will NOT reimplement

- Any KDE scoring logic (already in `_de.kde_score_article` and `_de.kde_score_article_fast`)
- Any per-product health computation (already in `repository_review`)
- Any intra-product conflict logic (already in `detect_conflicts`)
- Any improvement ranking logic (already in `recommend_improvements`)
- Any report formatting patterns already established by `fin_dashboard`

The only net-new logic in `ecosystem_review` is:
1. The cross-product pairwise guideline comparison (not done by any existing tool)
2. The ecosystem-wide escalation compliance audit
3. The EHS composite score formula
4. The Workflow layer aggregation across multiple conversations

All four pieces operate exclusively on `_de.*` functions and constants that already exist. No new function in `decision_engine.py` is required for Phase 1.

---

## 11. Implementation risks

### Risk 1 — O(n²) cross-product pairwise comparison

**Description:** Cross-product conflict detection requires comparing every guideline from Product A against every guideline from Product B, for every product pair. For N total cross-product guidelines, this is O(N²) comparisons.

**Impact level:** MEDIO  
**Threshold:** At 10 products × 20 guidelines each = 200 guidelines → ~20,000 cross-product pairs. At typical guideline lengths, this is fast (milliseconds per `jaccard()` call with precomputed `word_set()`). At 50 products × 50 guidelines = 2,500 guidelines → ~3,125,000 pairs. This is a realistic risk at ecosystem scale.

**Mitigation:** `word_set()` returns a `frozenset` — compute once per guideline, reuse across all comparisons (already the pattern in `repository_review`). For Phase 1, this is acceptable. For Phase 2, a bloom filter or inverted index on `GUIDELINE_CONTRADICTION_PAIRS` keywords can reduce the comparison space before running `jaccard()`.

### Risk 2 — `repository_review` output parsing dependency

**Description:** `extract_metrics_from_reports()` extracts metrics from the text output of `repository_review` using regex patterns. If the `repository_review` output format changes, `extract_metrics_from_reports()` will silently return incorrect values (it returns defaults on regex miss, not errors).

**Impact level:** MEDIO  
**Mitigation:** `ecosystem_review` calls `repository_review` as a sub-call within the same process. If the output format changes, both tools are updated in the same commit. The dependency is explicitly documented in this design document so it is not forgotten. A smoke test (see Phase 3 testing) verifies the regex patterns return non-default values when given known input.

### Risk 3 — Workflow layer is optional but must degrade gracefully

**Description:** When `conversations` is not provided, the EHS formula changes (weights are redistributed). The weight redistribution must produce a mathematically consistent result — the EHS with no conversations must be comparable to an EHS with conversations (otherwise the score is not a stable metric).

**Impact level:** BAJO  
**Mitigation:** The redistribution is defined in the formula (section 9) before implementation begins. The weight changes are symmetric: knowledge goes from 0.30 to 0.35, guideline from 0.25 to 0.30, escalation from 0.25 to 0.30, coverage from 0.10 to 0.05. Sum = 1.0 in both cases. The formula is validated against test inputs in Phase 3.

### Risk 4 — Cross-product conflict may produce noise at low similarity

**Description:** The threshold `jaccard >= 0.30` for cross-product comparison is lower than the intra-product threshold used in `detect_conflicts` (`>= 0.30` with escalation/anti-escalation signal required). At low similarity, two guidelines from different products may produce a false positive conflict if they happen to share domain vocabulary without actually contradicting each other.

**Impact level:** BAJO  
**Mitigation:** Cross-product conflict detection requires both `jaccard >= 0.30` AND a match against `GUIDELINE_CONTRADICTION_PAIRS`. A pure vocabulary overlap without a contradiction pair match does not produce a conflict. This is the same approach used in `repository_review` for intra-product detection. The threshold and the pair requirement together reduce false positive rate.

### Risk 5 — Escalation path check is article-level only

**Description:** `detect_escalation_repo()` checks whether an article text contains escalation signals. It cannot verify whether the escalation path is actually reachable by FIN in a given conversation — only that the text mentions escalation. An article that says "never escalate, but if you must escalate, contact support" would pass the check despite the anti-escalation rule.

**Impact level:** BAJO  
**Mitigation:** `ecosystem_review` runs both `detect_anti_escalation()` AND `detect_escalation_repo()` on every article. An article that passes `detect_escalation_repo()` but also matches `detect_anti_escalation()` is flagged as a contradiction — not as compliant. This is more conservative than either check alone.

---

## 12. Implementation plan

### Phase 1 — Core implementation (recommended first sprint)

**Scope:** Implement `ecosystem_review` with all required layers except Workflow.

**Steps:**

1. Add `async def ecosystem_review(products, context="") -> str` to `server.py` decorated with `@mcp.tool()`.
2. Sub-call `repository_review(products, context)` — assign output to `rr_output`.
3. Call `_de.extract_metrics_from_reports(rr_output)` — extract per-product aggregated metrics.
4. Sub-call `detect_conflicts(product["guidelines"], product["nombre"], context)` for each product — accumulate intra-product conflict counts.
5. Build cross-product guideline pool: collect all guidelines across all products with their product label. Compute `_de.word_set()` once per guideline.
6. Run cross-product pairwise `_de.jaccard()` + `GUIDELINE_CONTRADICTION_PAIRS` check. Collect cross-product conflicts with severity.
7. Run escalation compliance audit: `_de.detect_anti_escalation(..., use_repo_patterns=True)` on every guideline and article. `_de.detect_escalation_repo()` on every article. Compute `escalation_health`.
8. Compute `ecosystem_coverage_pct` via `_de.compute_coverage()` on combined article text.
9. Compute `ecosystem_knowledge_debt` via `_de.compute_knowledge_debt()` on aggregated inputs.
10. Compute EHS using the formula in section 9. Apply hard penalties.
11. Sub-call `recommend_improvements(rr_output, "", "", context)` — assign output to `ri_output`.
12. Compose report string in 8-section format. Workflow section outputs placeholder.

**Deliverable:** A functional `ecosystem_review` tool that passes all Phase 3 smoke tests without Workflow layer.

**Constraint check before commit:**
- `server.py` contains no new analytical logic — all computation delegates to `_de.*` or sub-calls
- `decision_engine.py` is not modified
- No existing tool is modified

---

### Phase 2 — Workflow layer

**Scope:** Add `conversations: list = []` parameter. Implement Workflow layer analysis when conversations are provided.

**Steps:**

1. Add `conversations: list = []` to the function signature.
2. When `conversations` is non-empty:
   - Call `_de.detect_intention(conv.lower())` for each conversation. Build frequency dict.
   - Call `_de.detect_emotion(conv.lower())` for each. Build emotion counts.
   - Call `_de.detect_guideline_events(conv.lower())` for each. Aggregate event frequency.
   - Compute uncovered domains: intentions that map to product domains with no guidelines.
   - Compute high-escalation-risk count from events with `esc_risk > 55`.
   - Compute `workflow_health` from the formula in section 7.
3. Update EHS formula to include `workflow_component × 0.10` when conversations provided.
4. Update report Sección 7 with Workflow layer output.

**Constraint check before commit:**
- Same as Phase 1. No `decision_engine.py` modifications.

---

### Phase 3 — Testing and validation

**Scope:** Verify the tool against real inputs. No new code in `server.py` or `decision_engine.py`.

**Minimum test cases:**

| Test case | Input | Expected |
|-----------|-------|----------|
| Single healthy product | 1 product, no blockers, full coverage | EHS ≥ 85 |
| Single blocked product | 1 product, 1 article with anti-escalation | EHS ≤ 60 (hard cap) |
| Two products with cross-product conflict | Product A escalates always, Product B prohibits escalation | cross_product_conflicts ≥ 1, EHS reduced |
| No escalation path | All articles lack escalation signals | EHS ≤ 40 (hard cap) |
| Conversations provided, uncovered domain | 3 conversations about Nómina, no Nómina guidelines | uncovered_domains ≥ 1 |
| Empty conversations list | `conversations=[]` | Workflow section shows placeholder, EHS formula uses redistributed weights |

**Smoke test commands** (consistent with `docs/CONTRIBUTING.md` testing checklist):

```bash
# AST parse — no syntax errors
python -c "import ast, pathlib; ast.parse(pathlib.Path('server.py').read_text()); print('OK')"

# Import smoke test — decision_engine loads cleanly
python -c "import decision_engine as _de; print('OK')"

# Symbol uniqueness — no duplicate functions in decision_engine
python -c "
import ast, pathlib, collections
tree = ast.parse(pathlib.Path('decision_engine.py').read_text())
names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
dups  = [n for n, c in collections.Counter(names).items() if c > 1]
print('DUPLICATES:', dups) if dups else print('OK — no duplicates')
"

# ecosystem_review registered as MCP tool
python -c "
import ast, pathlib
src = pathlib.Path('server.py').read_text()
tree = ast.parse(src)
tools = [n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
print('ecosystem_review registered:', 'ecosystem_review' in tools)
"
```

---

### Phase 4 — Documentation update

**Scope:** Update documentation to reflect the new tool. No code changes.

**Files to update:**

| File | What to add |
|------|-------------|
| `README.md` | Add `ecosystem_review` to the tool catalog table |
| `docs/Architecture.md` | Add `ecosystem_review` to the tool ecosystem table with Input/DE calls/Output |
| `docs/DecisionEngine.md` | Update the per-tool integration table — `ecosystem_review` row |
| `docs/CHANGELOG.md` | Add v1.1 entry: `ecosystem_review` added |
| `docs/ROADMAP.md` | Mark `ecosystem_review` as delivered in v1.1 |
| `docs/FIN_ECOSYSTEM.md` | Update Phase 2 tools section — `ecosystem_review` status: delivered |

---

*FIN Architect MCP — ecosystem_review Design Document — 2026-06-25*
