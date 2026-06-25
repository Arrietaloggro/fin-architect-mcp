# Decision Engine

`decision_engine.py` is the architectural core of FIN Architect MCP. It is the single location for every analytical function in the system — scoring, detection, classification, similarity, knowledge debt, deployment readiness, ROI ranking, and guideline automation. No tool in `server.py` reimplements logic that exists here. No threshold is defined outside this file.

**File:** `decision_engine.py`
**Lines:** 1,264
**Exported functions:** 34
**Exported constants:** 45
**External dependencies:** `re` (standard library only)

---

## Why the Decision Engine Exists

### The original problem

FIN Architect MCP grew incrementally. Each new tool was written to be self-contained: it included the constants it needed, implemented the similarity functions it required, and embedded the scoring logic it was built around. This approach worked in isolation but created a structural problem at the system level.

By the time the project reached v1.0, the same logic existed in multiple places:

- **Jaccard similarity** was implemented independently in `extract_guidelines`, `audit_knowledge`, and `architect_review`. The three implementations were similar but not identical. A similarity check in one tool could return a different result than the same check in another tool on the same input.

- **Loop risk detection** existed as inline pattern matching in `audit_knowledge` with a different pattern set than what was used in `optimize_article`. The two tools could disagree on whether an article had a loop risk.

- **KDE scoring** — the 12-criterion scoring algorithm for knowledge articles — was copied from `audit_knowledge` into `optimize_article` during development, then evolved separately. By the time the discrepancy was found, the two versions had diverged in subtle ways.

- **Constant lists** (loop patterns, anti-escalation patterns, absolute terms, vague phrases) were defined inline within tool functions. When a pattern was added or corrected in one tool, the other tools were not updated.

The total volume of duplicated code across the server was approximately 1,500 lines. The duplication was not visible in any single file — it was a structural property of the system.

### The specific inconsistencies

Three categories of inconsistency were documented:

1. **Result inconsistency:** Two tools calling "their own" Jaccard function on the same text pair could return different similarity scores because the tokenization or the formula differed in minor ways. This meant duplicate detection in `knowledge_review` and `extract_guidelines` operated on different scales.

2. **Threshold drift:** Thresholds for what constituted a "high loop risk" or a "significant duplicate" were defined inline in each tool. As the project evolved, some tools were updated with improved thresholds while others retained the original values. There was no mechanism to keep them synchronized.

3. **Pattern drift:** `LOOP_PATTERNS` and `ANTI_ESCALATION_PATTERNS` existed in multiple forms across the codebase. A pattern added to fix a false negative in `audit_knowledge` was not propagated to `optimize_article`.

### The refactor objectives

Three architecture sprints addressed the problem:

- **v1 (Knowledge Module):** Established `decision_engine.py` and migrated the KDE scoring core.
- **v2 (Core Consolidation):** Migrated `audit_knowledge`, `optimize_article`, `audit_guideline`, and `architect_review` to call `_de.*` exclusively.
- **v3 (Guideline Core Consolidation):** Migrated all 7 Guideline tools. Added the complete Guideline module (lines 898–1264) to `decision_engine.py`.

After v3, `server.py` contains no analytical logic. All 15 tools call `_de.*` functions and constants. There are zero duplicate function implementations across the codebase.

---

## Design Philosophy

### Single Source of Truth

Every formula, every threshold, every pattern list exists in `decision_engine.py` and nowhere else. When `extract_guidelines` and `detect_conflicts` both need Jaccard similarity, they both call `_de.jaccard()`. When `audit_knowledge` and `knowledge_review` both need loop risk detection, they both call `_de.detect_loop_risk()`. There is no "their own version" of anything.

Consequence: changing the Jaccard threshold for guideline clustering requires editing one constant (`GUIDELINE_CLUSTER_THRESHOLD = 0.70`) in one file. All tools that use that threshold receive the change automatically.

### Low Coupling

`decision_engine.py` imports only `re` from the standard library. It has no dependency on `server.py`, `main.py`, or any other project file. Any tool in `server.py` can be tested by calling `_de.*` functions directly with synthetic inputs — no mocking required.

### High Cohesion

The module contains everything needed for analytical decisions and nothing else. There is no routing logic, no response formatting, no HTTP handling. The boundary is strict: if a function produces a number, label, list, or boolean from text input, it belongs here. If a function formats output for an MCP client, it belongs in `server.py`.

### Pure Functions

All 34 exported functions are pure: given the same inputs, they always return the same outputs. No function reads from disk, writes to disk, makes network calls, or modifies global state. The only module-level state is the constant definitions. This property makes the module trivially testable and safe to call from any context, including concurrent tool executions.

### Extensibility

Adding new analytical functions to the module does not require changing existing functions. The internal structure (Knowledge module lines 1–897, Guideline module lines 898–1264) is organized by domain. New functions are appended to the relevant section. New constants are defined at the module level above the functions that use them.

### Consistency

Because all tools share the same functions and constants, the system is internally consistent by construction. A "MEDIO" loop risk in `audit_knowledge` means exactly the same thing as a "MEDIO" loop risk in `knowledge_review` — both are produced by the same `detect_loop_risk()` call with the same pattern set.

---

## Internal Architecture

```
decision_engine.py
│
├── Module Constants
│   ├── KDE hard caps (KDE_HARD_CAP_BLOCKER, KDE_HARD_CAP_RESOLUTION)
│   ├── Topic categories (TOPIC_CATEGORIES)
│   └── Pattern lists (Knowledge module)
│
├── Detection Functions
│   ├── detect_loop_risk()          — BAJO / MEDIO / ALTO / CRÍTICO
│   ├── detect_anti_escalation()    — boolean
│   ├── detect_absolute_hits()      — list of matched terms
│   ├── detect_escalation()         — boolean
│   ├── detect_escalation_repo()    — boolean (lightweight variant)
│   └── detect_fin_blockers()       — list of matched blocker actions
│
├── Similarity Functions
│   ├── jaccard()                   — float 0.0–1.0
│   └── word_set()                  — frozenset
│
├── Scoring Functions (Knowledge)
│   ├── kde_score_article()         — full 12-criterion KDE (audit mode)
│   ├── kde_score_article_fast()    — lightweight KDE (review/repository mode)
│   └── kde_score_guideline_fast()  — lightweight guideline scorer
│
├── Classification Functions
│   ├── risk_level_from_health()    — BAJO / MEDIO / ALTO
│   ├── compute_automation_readiness() — readiness label + justification
│   └── compute_deploy_decision()   — LISTO / BLOQUEADO / NO LISTO / CON RECOMENDACIONES
│
├── Knowledge Debt Functions
│   ├── compute_knowledge_debt()    — 0–100 debt score
│   └── debt_label_emoji()          — BAJO / MEDIO / ALTO / CRÍTICO + emoji
│
├── Coverage Functions
│   └── compute_coverage()          — (covered_categories, missing_categories)
│
├── Executive Status Functions
│   ├── semaforo()                  — traffic light (emoji, label)
│   ├── global_status_from_health() — SALUDABLE / ACEPTABLE / EN REVISIÓN / BLOQUEADO
│   └── deployment_readiness()      — READY / READY WITH RECOMMENDATIONS / NOT READY
│
├── ROI & Ranking Functions
│   ├── compute_roi()               — impact / effort ratio
│   └── rank_improvements()         — sorted list with priority field
│
├── Utility Functions
│   ├── extract_int()               — regex integer extraction from text
│   └── extract_metrics_from_reports() — structured metrics from tool output text
│
└── Guideline Module (lines 898–1264)
    │
    ├── Guideline Constants
    │   ├── INTENTION_MAP, emotion keyword lists
    │   ├── GUIDELINE_ESCALATION_WORDS, GUIDELINE_RESOLVE_WORDS
    │   ├── GUIDELINE_PROHIBITION_WORDS, GUIDELINE_OBLIGATION_WORDS
    │   ├── GUIDELINE_AMBIGUOUS_TERMS, GUIDELINE_VAGUE_PHRASES
    │   ├── GUIDELINE_ACTION_VERBS, GUIDELINE_SPECIFIC_SIGNALS
    │   ├── GUIDELINE_RISKY_PATTERNS, GUIDELINE_EMPATHY_SIGNALS
    │   ├── GUIDELINE_CONTRADICTION_PAIRS, GUIDELINE_CONDITION_PAIRS
    │   ├── GUIDELINE_EVENT_CATALOG (12 event types with impact/esc_risk)
    │   ├── GUIDELINE_CLUSTER_THRESHOLD = 0.70
    │   ├── GUIDELINE_MERGE_THRESHOLD = 0.80
    │   ├── GUIDELINE_PATTERN_NAMES (frozenset → name mapping)
    │   ├── GUIDELINE_TEMPLATES (event_id → template text)
    │   ├── GUIDELINE_PROBLEM_SIGNALS, GUIDELINE_FAILURE_MAP
    │   └── GUIDELINE_BEHAVIOR_MAP
    │
    └── Guideline Functions
        ├── detect_intention()          — category string
        ├── detect_emotion()            — Frustrado / Molesto / Urgente / Neutral
        ├── detect_guideline_events()   — list of event ids
        ├── detect_guideline_problems() — list of problem type keys
        ├── guideline_risk_level()      — ALTO / MEDIO / BAJO
        ├── conflict_severity_level()   — ALTA / MEDIA / BAJA
        ├── guideline_priority_from_risk() — CRÍTICA / ALTA / MEDIA / BAJA
        ├── guideline_impact_priority() — (impact_label, implementation_priority)
        ├── cluster_pattern_name()      — pattern name string
        └── guideline_template_for()    — template text string
```

---

## Exported Functions

### Detection (6 functions)

These functions answer a yes/no or categorical question about a text. They are atomic: each detects one type of signal. Multiple tools combine them to build a complete picture.

**`detect_loop_risk(text_lower, use_repo_patterns=False) → (level, count, hits)`**
Scans text for instructional loop patterns — phrases that send the user back to the beginning without resolution. Returns a tuple: the risk level (`BAJO` / `MEDIO` / `ALTO` / `CRÍTICO`), the count of matched patterns, and the list of matched strings. The `use_repo_patterns` flag switches between two pattern sets: `LOOP_PATTERNS` (phrase-level, used by audit tools) and `LOOP_PATTERNS_REPO` (keyword-level, used by repository/bulk review tools). Also detects circular step references via regex (`vuelve al paso`, `regresa al paso`, `repite desde el paso`). Risk levels: 0 hits → BAJO, 1 → MEDIO, 2–3 → ALTO, 4+ → CRÍTICO.

**`detect_anti_escalation(text_lower, use_repo_patterns=False) → bool`**
Returns `True` if the text contains a rule that prohibits escalation. This is a critical blocker: an article that instructs agents never to escalate traps users in unresolvable loops. Two pattern sets: `ANTI_ESCALATION_PATTERNS` (strict regex, for individual article audit) and `ANTI_ESCALATION_PATTERNS_REPO` (broader regex, for bulk analysis).

**`detect_absolute_hits(text_lower, repo_mode=False) → list`**
Returns a list of absolute language terms found in the text. Absolute terms (`siempre`, `nunca`, `todos`, `ninguno`, `cualquier caso`) create policy rigidity that prevents appropriate judgment in edge cases. Two vocabulary sets: `ABSOLUTE_TERMS` (5 terms, for article audit) and `ABSOLUTE_TERMS_REPO` (6 terms including `jamás`, `absolutamente prohibido`, for repository review).

**`detect_escalation(text_lower) → bool`**
Returns `True` if the text contains any escalation signal from `ESCALATION_SIGNALS`. A knowledge article without an escalation path leaves FIN unable to handle cases beyond the article's scope. Used by `audit_knowledge` in the full KDE scoring pipeline.

**`detect_escalation_repo(text_lower) → bool`**
Lightweight variant of escalation detection using a smaller keyword set. Used by `kde_score_article_fast()` and `kde_score_guideline_fast()` in bulk analysis contexts where speed matters over precision.

**`detect_fin_blockers(text_lower) → list`**
Returns a list of FIN blocker actions found in the text. FIN blockers are actions that FIN cannot execute: accessing admin panels, running scripts, modifying databases, requiring superuser access. An article that instructs these actions as resolution steps cannot be used autonomously by FIN and receives a hard cap on its health and resolution scores.

---

### Similarity (2 functions)

**`jaccard(words_a: set, words_b: set) → float`**
Computes Jaccard similarity: `|A ∩ B| / |A ∪ B|`. Returns 0.0 if either set is empty. Returns a float between 0.0 and 1.0. Used in four different contexts with different thresholds:
- Article duplicate detection: threshold ≥ 0.55
- Sentence-level repetition: threshold ≥ 0.80 (computed inline in `kde_score_article()`)
- Guideline clustering: threshold ≥ `GUIDELINE_CLUSTER_THRESHOLD` (0.70)
- Guideline merging: threshold ≥ `GUIDELINE_MERGE_THRESHOLD` (0.80)

**`word_set(text: str) → frozenset`**
Tokenizes text into a frozenset of lowercase words using regex `\b\w+\b`. Returns a frozenset (immutable) compatible with `jaccard()`. Using a frozenset enables caching and set operations. Called before `jaccard()` in all similarity computations.

---

### Scoring (3 functions)

**`kde_score_article(text: str) → dict`**
The primary KDE (Knowledge Decision Engine) scorer. Evaluates a knowledge article across 12 weighted criteria and returns a comprehensive dict with 40+ fields including all raw signals, individual criterion scores, the aggregate health score, classification, risk level, resolution capability, automation readiness, and deploy decision.

The 12 criteria and their weights:

| Criterion | Weight | What it measures |
|-----------|--------|-----------------|
| Claridad | 12 | Language clarity; penalizes vague phrases |
| Estructura | 10 | Numbered steps, sections, bullet points |
| Pasos | 12 | Action verbs, step count, step completeness |
| Cobertura | 8 | Coverage signal count (cause, symptom, solution, etc.) |
| Ambiguedad | 10 | Absolute terms, internal contradictions |
| Longitud | 8 | Word count appropriateness (30–400 optimal) |
| Consistencia | 8 | Sentence repetitions, mixed register (tú/usted) |
| Terminologia | 8 | Technical term definitions, foreign word ratio |
| Uso por FIN | 10 | FIN guidance signals, absence of FIN blockers |
| Escalamiento | 8 | Escalation path definition, absence of anti-escalation |
| Mantenibilidad | 7 | Dated references, article length |
| Riesgo Operativo | 7 | Risky actions (delete, format, reset to factory) |

After computing the 12-criterion raw total, the function applies penalty adjustments to produce `kde_health`, then enforces hard caps if blockers are present. It also computes `kde_resolution` (weighted combination of 6 resolution-relevant criteria), `automation_readiness`, and `deploy_decision`.

Used by: `audit_knowledge`, `optimize_article`, `knowledge_review`.

**`kde_score_article_fast(text: str) → dict`**
Lightweight variant for bulk analysis. Instead of 12 weighted criteria, it uses 5 binary signals (has_resolution, has_steps, has_escalation, has_objective, word count check) and 3 detection calls. Returns a smaller dict: `health`, `risk`, `blocked`, `loop_risk`, `anti_escalation`, `resolution_rate`, `words`, `has_escalation`, `has_resolution`. Runs significantly faster than the full scorer, suitable for processing repositories of hundreds of articles.

Used by: `repository_review`, `knowledge_review` (for bulk passes).

**`kde_score_guideline_fast(text: str) → dict`**
Lightweight scorer for conversation guidelines. Evaluates two structural signals (`has_trigger` — conditional entry point, `has_action` — prescribed response) and two risk signals (absolute terms, anti-escalation). Returns `health`, `blocked`, `anti_escalation`, `words`, `has_escalation`. Guidelines without a trigger condition or a prescribed action receive significant deductions.

Used by: `repository_review`, `architect_review`.

---

### Classification (3 functions)

**`risk_level_from_health(kde_health: int, has_blocker: bool = False) → str`**
Maps a KDE health score to a risk level. Returns `ALTO` if health < 50 or if a blocker is present, `MEDIO` if health < 78, `BAJO` otherwise. Single function ensures all tools use identical risk classification thresholds.

**`compute_automation_readiness(kde_health, has_kde_blocker, kde_blocker_flags, loop_risk_level, loop_count, absolute_hits, has_escalation) → (label, emoji, justification)`**
Determines whether FIN can use an article autonomously. Returns a 3-tuple: readiness label (`Excelente` / `Alta` / `Media` / `Baja` / `No apto`), an emoji indicator, and a human-readable justification string. Rules: blockers → max `Baja`; ALTO loop risk → max `Media`; absolute terms without escalation → `Baja`; health ≥ 78, BAJO loop risk, has escalation, no absolutes → `Excelente`.

**`compute_deploy_decision(kde_health, has_kde_blocker, kde_blocker_flags, classification) → (label, emoji, reason)`**
Returns the deployment decision for an article. Four outcomes: `BLOQUEADO` (active blockers present), `NO LISTO` (health < 50), `LISTO CON RECOMENDACIONES` (health 50–77), `LISTO` (health ≥ 78). Returns a 3-tuple with label, emoji, and a specific reason string.

---

### Knowledge Debt (2 functions)

**`compute_knowledge_debt(total_art_blocked, total_g_conflicts, total_art_dups, missing_cats_count, total_g_blocked, total_art_critical) → (debt_score, debt_raw)`**
Computes the Knowledge Debt score for a repository. Applies weighted penalty formula: blocked articles (×15), guideline conflicts (×10), duplicate articles (×8), missing topic categories (×12), blocked guidelines (×8), critical-but-not-blocked articles (×5). Normalizes to 0–100 scale. Returns both the normalized score and the raw weighted sum.

**`debt_label_emoji(knowledge_debt: int) → (label, emoji)`**
Maps a debt score to a label and emoji. Returns `CRÍTICO 🔴` (≥70), `ALTO 🟠` (≥45), `MEDIO 🟡` (≥20), `BAJO 🟢` (<20).

---

### Coverage (1 function)

**`compute_coverage(all_text: str) → (covered_categories, missing_categories)`**
Evaluates which topic categories from `TOPIC_CATEGORIES` are represented in a combined text. Returns two lists: covered categories and missing categories. `TOPIC_CATEGORIES` defines 11 domains: facturación, soporte técnico, cancelación, configuración, escalamiento, reembolso, onboarding, seguridad, reportes, integraciones, general. Each domain has an associated keyword list.

---

### Executive Status (3 functions)

**`semaforo(value: int, thresholds: tuple = (70, 85)) → (emoji, label)`**
Traffic light function for executive dashboards. Returns `🟢 Excelente` if value ≥ upper threshold, `🟡 Atención` if value ≥ lower threshold, `🔴 Crítico` otherwise. Thresholds are configurable per call, defaulting to (70, 85).

**`global_status_from_health(global_health, prod_blocked_count, prod_high_risk) → (status_label, emoji)`**
Derives the global repository status. Returns `BLOQUEADO 🔴` if any products are blocked or global health < 50, `EN REVISIÓN 🟠` if health < 70 or any high-risk products exist, `ACEPTABLE 🟡` if health < 85, `SALUDABLE 🟢` otherwise.

**`deployment_readiness(prod_blocked_count, total_a_blocked, total_g_blocked, global_health, knowledge_debt, prod_high_risk) → (label, emoji)`**
Returns the executive deployment decision for the entire repository. `NOT READY 🔴` if any blocked items exist, `READY WITH RECOMMENDATIONS 🟡` if high-risk products exist or debt ≥ 45, `READY 🟢` if health ≥ 85 and debt < 20, otherwise `READY WITH RECOMMENDATIONS`.

---

### ROI & Ranking (2 functions)

**`compute_roi(impact: int, effort: int) → float`**
Computes the ROI ratio: `impact / effort`, rounded to 2 decimal places. Higher ratios indicate improvements that deliver more benefit relative to the effort required.

**`rank_improvements(improvements: list) → list`**
Sorts a list of improvement dicts by ROI descending, then by impact descending as a tiebreaker. Assigns a `priority` field (1-indexed) to each item in the sorted list. The input list is mutated in-place (priority field added) and returned in sorted order.

---

### Utilities (2 functions)

**`extract_int(pattern: str, text: str, default: int = 0) → int`**
Extracts the first integer captured by a regex pattern from text. Case-insensitive. Returns `default` if no match. Used by `extract_metrics_from_reports()` for structured extraction from tool output text.

**`extract_metrics_from_reports(repository_review_text, knowledge_review_text, architect_review_text) → dict`**
Centralizes all regex-based metric extraction from tool output text. Extracts: global health, knowledge debt, blocked products, high-risk products, blocked articles, blocked guidelines, guideline conflicts, duplicate articles, coverage percentage, total article and guideline counts, and missing category names. Falls back gracefully when individual report texts are absent. Returns a structured dict with 13 fields plus presence flags for each report type. Used by `recommend_improvements` and `fin_dashboard`.

---

### Guideline Detection (4 functions)

**`detect_intention(text_lower: str) → str`**
Identifies the primary business domain of a guideline or conversation. Scans `INTENTION_MAP` — 12 domain categories each with a keyword list (Facturación, Inventario, Caja, POS, Restobar, DIAN, Nómina, Reportes, Configuración, Error técnico, Acceso, Seguridad). Returns the first matching category name, or `"General"` if none match. Used by `classify_guideline` and `simulate_fin`.

**`detect_emotion(text_lower: str) → str`**
Identifies the emotional state of a user in a conversation text. Returns `"Frustrado"` if frustration keywords are present, `"Molesto"` if annoyance keywords are present, `"Urgente"` if urgency keywords are present, `"Neutral"` otherwise. Priority order: Frustrado > Molesto > Urgente > Neutral. Used by `classify_guideline` and `simulate_fin`.

**`detect_guideline_events(text_lower: str) → list`**
Scans text for conversation events from `GUIDELINE_EVENT_CATALOG`. Returns a list of matching event IDs. Each event in the catalog has an `id`, `label`, `signals` list, `impact` score, and `esc_risk` score. The 12 events cover: user already consulted documentation, FIN repeating solutions, problem persisting, user urgency, user frustration, FIN giving generic responses, FIN escalating, problem resolved, FIN requesting information, user multiple attempts, user completely blocked, and unnecessary escalation risk. Used by `extract_guidelines`.

**`detect_guideline_problems(text_lower: str) → list`**
Scans text for problem types from `GUIDELINE_PROBLEM_SIGNALS`. Returns a list of problem type keys. The 6 problem types are: escalamiento sin criterios, falta de resolución documentada, solución documentada insuficiente, respuesta genérica de FIN, fallo técnico sin guía, urgencia no atendida. Each maps to a `GUIDELINE_FAILURE_MAP` entry (what went wrong) and a `GUIDELINE_BEHAVIOR_MAP` entry (how FIN should behave instead). Used by `generate_guideline`.

---

### Guideline Classification (4 functions)

**`guideline_risk_level(risk_score: int) → str`**
Maps a numeric risk score to `ALTO` (≥7), `MEDIO` (≥4), or `BAJO` (<4). Used by `optimize_guideline` and `classify_guideline`.

**`conflict_severity_level(severity: int) → str`**
Maps a conflict severity integer to `ALTA` (≥10), `MEDIA` (≥4), or `BAJA` (<4). Used by `detect_conflicts` to classify how serious a guideline conflict is.

**`guideline_priority_from_risk(nivel_riesgo: str, categoria: str) → str`**
Derives implementation priority from risk level and business category. Returns `CRÍTICA` (ALTO risk), `ALTA` (MEDIO risk, or high-risk categories: DIAN, Seguridad, Facturación, Nómina), `MEDIA` otherwise. Used by `classify_guideline`.

**`guideline_impact_priority(total_impact_score: int) → (impact_label, implementation_priority)`**
Given a total impact score (sum of event impact scores for a guideline cluster), returns an impact label (`Alto` ≥80, `Medio` ≥50, `Bajo` <50) and an implementation priority (`INMEDIATA` ≥80, `ALTA` ≥50, `MEDIA` ≥30, `BAJA` <30). Used by `generate_guideline` and `extract_guidelines`.

---

### Guideline Generation (2 functions)

**`cluster_pattern_name(event_set: frozenset) → str`**
Looks up the canonical name for a set of conversation events. Checks `GUIDELINE_PATTERN_NAMES` for an exact match, then for a subset match. If no match is found, constructs a name from the first two event labels. `GUIDELINE_PATTERN_NAMES` contains 15 predefined pattern names covering the most common multi-event combinations (e.g., `frozenset(["fin_repeats_solution", "problem_persists"])` → `"Loop instruccional — FIN repite sin avanzar"`). Used by `extract_guidelines`.

**`guideline_template_for(event_set: frozenset) → str`**
Selects the most appropriate guideline template from `GUIDELINE_TEMPLATES` for a set of conversation events. Priority order: user_blocked > user_urgency > user_frustration > fin_repeats_solution > user_tried_docs > unnecessary_escalation_risk. Returns the `"default"` template if no priority event is in the set. Used by `extract_guidelines` and `generate_guideline`.

---

## Shared Constants

### Knowledge Module Constants

**Hard caps**
- `KDE_HARD_CAP_BLOCKER = 60` — Maximum health score an article can receive when a KDE blocker is present. An article with a critical loop or an anti-escalation rule cannot score higher than 60 regardless of quality in other criteria.
- `KDE_HARD_CAP_RESOLUTION = 40` — Maximum resolution capability score when a blocker is present. Prevents a well-written but fundamentally unsafe article from appearing capable of autonomous resolution.

**`TOPIC_CATEGORIES`**
11 business domains, each with a keyword list. Used by `compute_coverage()` to determine which areas of the product catalog have knowledge article coverage. Missing categories become debt items in the repository health calculation.

**Detection pattern lists**
- `LOOP_PATTERNS` (10 phrases) — Instructional loop indicators for article-level audit (`audit_knowledge`, `optimize_article`).
- `LOOP_PATTERNS_REPO` (9 keywords) — Simplified loop indicators for bulk review (`repository_review`, `knowledge_review`).
- `ANTI_ESCALATION_PATTERNS` (2 regex) — Strict anti-escalation detection for individual article audit.
- `ANTI_ESCALATION_PATTERNS_REPO` (7 regex) — Broader anti-escalation detection for repository review.
- `ABSOLUTE_TERMS` (5 terms) — Absolute language for article scoring.
- `ABSOLUTE_TERMS_REPO` (6 terms) — Absolute language for repository review.
- `ESCALATION_SIGNALS` (10 phrases) — Positive escalation path indicators.
- `STEP_VERBS` (29 verbs) — Action verbs that indicate procedural steps.
- `VAGUE_PHRASES` (14 phrases) — Ambiguous language that penalizes clarity.
- `COVERAGE_SIGNALS` (14 terms) — Signals of complete scenario coverage.
- `TECHNICAL_TERMS` (14 terms) — Domain-specific technical vocabulary.
- `FIN_POSITIVE_SIGNALS` (11 phrases) — Indicators that an article is structured for FIN use.
- `FIN_BLOCKER_ACTIONS` (10 phrases) — Actions FIN cannot execute.
- `RISKY_ACTIONS` (10 phrases) — Destructive operations that increase operational risk.

### Guideline Module Constants

**Clustering thresholds**
- `GUIDELINE_CLUSTER_THRESHOLD = 0.70` — Minimum Jaccard similarity for two conversation turns to belong to the same guideline cluster.
- `GUIDELINE_MERGE_THRESHOLD = 0.80` — Minimum Jaccard similarity for two candidate guidelines to be merged into one.

**Detection vocabularies**
- `GUIDELINE_ABSOLUTE_WORDS` — Absolute language in guideline context.
- `GUIDELINE_ESCALATION_WORDS` / `GUIDELINE_RESOLVE_WORDS` — Escalation and resolution indicators.
- `GUIDELINE_PROHIBITION_WORDS` / `GUIDELINE_OBLIGATION_WORDS` — Policy constraint language.
- `GUIDELINE_AMBIGUOUS_TERMS` / `GUIDELINE_VAGUE_PHRASES` — Low-precision language.
- `GUIDELINE_ACTION_VERBS` — Required action vocabulary for guideline clarity.
- `GUIDELINE_SPECIFIC_SIGNALS` — Domain-specific triggers.
- `GUIDELINE_RISKY_PATTERNS` — Guideline content that poses security or compliance risk.
- `GUIDELINE_EMPATHY_SIGNALS` — Empathetic language indicators.
- `GUIDELINE_CONTRADICTION_PAIRS` — Known contradiction patterns between guideline clauses.
- `GUIDELINE_CONDITION_PAIRS` — Context condition pairs (e.g., primera vez / reincidente).

**Emotion vocabularies**
- `INTENTION_MAP` — 12 domain categories with keyword lists.
- `FRUSTRATION_KEYWORDS` / `ANNOYANCE_KEYWORDS` / `URGENCY_KEYWORDS` / `NEUTRAL_KEYWORDS` — Emotional state detection vocabularies.

**Guideline generation structures**
- `GUIDELINE_EVENT_CATALOG` — 12 conversation event types. Each entry: `id`, `label`, `signals` list, `impact` score (0–55), `esc_risk` score (0–65).
- `GUIDELINE_PATTERN_NAMES` — Mapping from event `frozenset` combinations to canonical pattern names. 15 named patterns.
- `GUIDELINE_TEMPLATES` — Mapping from event type to guideline template text. 7 specific templates + 1 default.
- `GUIDELINE_PROBLEM_SIGNALS` — 6 problem categories, each with a signal keyword list.
- `GUIDELINE_FAILURE_MAP` — Problem type → description of what went wrong.
- `GUIDELINE_BEHAVIOR_MAP` — Problem type → prescribed FIN behavior to address the problem.

---

## Integration

### How each tool uses the Decision Engine

**`audit_knowledge`**
Calls `kde_score_article(text)` and receives the full 40-field dict. Formats and returns the KDE report. All scoring, blocker detection, classification, and deployment decision come from the single function call.

**`optimize_article`**
Uses `_de.LOOP_PATTERNS`, `_de.VAGUE_PHRASES`, and `_de.STEP_VERBS` as reference vocabularies to identify specific improvement targets. Calls `_de.rank_improvements()` and `_de.compute_roi()` to produce a prioritized action plan. Passes the `kde_score_article()` output from `audit_knowledge` as input context.

**`knowledge_review`**
Calls `kde_score_article_fast()` on each article for bulk health assessment. Calls `compute_knowledge_debt()` with aggregate counts. Calls `jaccard()` + `word_set()` to detect duplicate articles across the set. Calls `compute_coverage()` to identify missing topic categories.

**`repository_review`**
Calls `kde_score_article_fast()` and `kde_score_guideline_fast()` for all items. Calls `global_status_from_health()` for the repository-level status indicator. Calls `deployment_readiness()` for the executive decision. Calls `compute_knowledge_debt()` with the full repository-level aggregate counts.

**`recommend_improvements`**
Calls `extract_metrics_from_reports()` to parse metrics from upstream tool outputs. Calls `rank_improvements()` and `compute_roi()` to build the prioritized backlog. Calls `debt_label_emoji()` for debt classification labels.

**`fin_dashboard`**
Calls `extract_metrics_from_reports()` for structured metrics. Calls `semaforo()` for each module score. Calls `global_status_from_health()` for the global indicator. Calls `deployment_readiness()` for the executive readiness decision.

**`audit_guideline`**
Uses `_de.ABSOLUTE_TERMS` and calls `detect_guideline_problems()` for violation detection. Calls `guideline_risk_level()` for the risk classification.

**`classify_guideline`**
Calls `detect_intention()`, `detect_emotion()`, `guideline_risk_level()`, `guideline_priority_from_risk()`, and `guideline_impact_priority()` to produce a complete classification.

**`detect_conflicts`**
Calls `jaccard()` + `word_set()` for pairwise similarity. Uses `GUIDELINE_CONTRADICTION_PAIRS` and `GUIDELINE_CONDITION_PAIRS` for semantic conflict detection. Calls `conflict_severity_level()` to classify each identified conflict.

**`score_guideline`**
Calls `kde_score_guideline_fast()` for the 10-criterion score. Uses `GUIDELINE_AMBIGUOUS_TERMS`, `GUIDELINE_RISKY_PATTERNS`, and other constant lists to annotate the per-criterion breakdown.

**`simulate_fin`**
Calls `detect_intention()` and `detect_emotion()` for context. Calls `detect_guideline_events()` to identify which conversation events the guideline addresses. Uses `GUIDELINE_EVENT_CATALOG` to retrieve impact and escalation risk scores for matched events.

**`generate_guideline`**
Calls `detect_guideline_problems()` to identify what went wrong. Uses `GUIDELINE_FAILURE_MAP` and `GUIDELINE_BEHAVIOR_MAP` to construct the guideline content. Calls `guideline_impact_priority()` for the implementation priority.

**`extract_guidelines`**
Calls `jaccard()` + `word_set()` for clustering (threshold: `GUIDELINE_CLUSTER_THRESHOLD`) and merging (threshold: `GUIDELINE_MERGE_THRESHOLD`). Calls `detect_guideline_events()` on each cluster. Calls `cluster_pattern_name()` to name the pattern. Calls `guideline_template_for()` to produce the initial template. Calls `guideline_impact_priority()` for prioritization.

**`architect_review`**
Calls `jaccard()` + `word_set()` for cross-item similarity analysis. Uses `ABSOLUTE_TERMS` for cross-document absolute language detection. Calls `kde_score_article()` and `kde_score_guideline_fast()` for the items under review.

---

## Internal Flow

The path of a single article through the full Knowledge Decision Engine pipeline:

```
Input: article text (string)
        │
        ▼
  Tokenization
  ├── word_count = len(text.split())
  ├── sentences  = re.split(r'[.!?]+', text)
  └── text_lower = text.lower()
        │
        ▼
  Atomic Detection (parallel, all run on text_lower)
  ├── detect_loop_risk()       → (level, count, hits)
  ├── detect_anti_escalation() → bool
  ├── detect_absolute_hits()   → list
  ├── detect_escalation()      → bool
  ├── detect_fin_blockers()    → list
  ├── vague_hits  (VAGUE_PHRASES scan)
  ├── step_hits   (STEP_VERBS scan)
  ├── cov_hits    (COVERAGE_SIGNALS scan)
  └── risky_hits  (RISKY_ACTIONS scan)
        │
        ▼
  12-Criterion Scoring (sequential, each criterion uses detection results)
  ├── clarity          (12 pts) — penalizes vague_hits, short text
  ├── structure        (10 pts) — requires numbered steps, sections, bullets
  ├── steps_score      (12 pts) — requires step_hits, non-zero step count
  ├── coverage         ( 8 pts) — requires cov_hits count ≥ 2
  ├── ambiguity        (10 pts) — penalizes absolute_hits, contradictions
  ├── length_score     ( 8 pts) — optimal 60–400 words
  ├── consistency      ( 8 pts) — penalizes repetitions, mixed register
  ├── terminology      ( 8 pts) — penalizes undefined technical terms
  ├── fin_usability    (10 pts) — requires FIN_POSITIVE_SIGNALS, penalizes blockers
  ├── escalation_score ( 8 pts) — requires escalation, penalizes anti-escalation
  ├── maintainability  ( 7 pts) — penalizes dated references
  └── operational_risk ( 7 pts) — penalizes risky_hits
  → _raw_total = sum of 12 criteria (0–100)
        │
        ▼
  Penalty Adjustments (applied to _raw_total → kde_health)
  ├── absolute_hits    → up to -8
  ├── loop_risk ALTO   → -8
  ├── loop_risk CRÍTICO → -15
  └── ambiguous_steps  → up to -6
        │
        ▼
  Hard Cap Enforcement
  ├── if has_kde_blocker: kde_health = min(kde_health, KDE_HARD_CAP_BLOCKER)
  └── kde_health = max(0, min(100, kde_health))
        │
        ▼
  Classification
  ├── kde_health ≥ 90 → Excelente ✅
  ├── kde_health ≥ 78 → Muy Bueno 🟢
  ├── kde_health ≥ 65 → Bueno 🔵
  ├── kde_health ≥ 50 → Aceptable ⚠️
  ├── kde_health ≥ 35 → Deficiente 🔶
  └── kde_health < 35 → Crítico 🔴
        │
        ▼
  Resolution Capability (kde_resolution)
  ├── Weighted combination of 6 criteria: clarity(20%), steps(25%),
  │   coverage(15%), ambiguity(15%), fin_usability(15%), escalation(10%)
  ├── Loop risk penalties: MEDIO -5, ALTO -15, CRÍTICO -30
  ├── FIN blocker penalty: up to -20
  └── Hard cap: if has_kde_blocker → min(kde_resolution, KDE_HARD_CAP_RESOLUTION)
        │
        ▼
  Automation Readiness
  └── compute_automation_readiness() → (label, emoji, justification)
        │
        ▼
  Deploy Decision
  └── compute_deploy_decision() → (label, emoji, reason)
        │
        ▼
  Output: dict with 40+ fields
```

---

## Benefits

### Elimination of duplication

Before the Decision Engine was established as the sole source of truth, approximately 1,500 lines of logic existed in duplicate or triplicate across `server.py`. Three architecture sprints migrated this logic:

| Sprint | Tools migrated | Lines removed from server.py |
|--------|---------------|------------------------------|
| v2 — Core Consolidation | `audit_knowledge`, `optimize_article`, `audit_guideline`, `architect_review` | ~445 |
| v3 — Guideline Core Consolidation | All 7 Guideline tools | ~580 |
| Decision Engine Cleanup | Removed internal duplicate in `decision_engine.py` | ~328 |

The result: zero duplicate function implementations across the entire codebase. Verified by AST parse, symbol uniqueness check, and import smoke tests.

### Consistency

All tools that check for loop risk produce results on the same scale with the same thresholds because they all call `detect_loop_risk()`. All tools that check for duplicates use the same Jaccard implementation. All tools that classify health scores use the same threshold table. Inconsistency between tools is now architecturally prevented.

### Scalability

Adding a new tool does not require writing new analytical logic. The analytical functions exist and are ready to be called. A new tool for `flag_outdated_articles` would call `kde_score_article_fast()`, filter on `date_refs`, and call `rank_improvements()` — implementing only the business logic specific to that tool, nothing else.

### Testability

Because all 34 functions are pure — no side effects, no I/O, deterministic outputs — the entire analytical core can be tested with simple input/output assertions. A test suite for `decision_engine.py` tests the behavior of all 15 tools simultaneously, since all tools derive their analytical results from this module.

### Maintainability

When a pattern is incorrect — for example, `LOOP_PATTERNS` generates false positives — the fix is made in one place and propagates to all tools that use it. When a threshold needs to be tuned — for example, the Jaccard threshold for guideline clustering — one constant value is changed. No grep-and-replace across multiple files is needed.

---

## Best Practices

### What to do

**Always import as the `_de` alias.**
```python
import decision_engine as _de
```
This is the established convention across all 15 tools. Consistency in the import alias makes it immediately clear when a function call is delegating to the Decision Engine.

**Call `word_set()` before `jaccard()`.**
```python
words_a = _de.word_set(text_a)
words_b = _de.word_set(text_b)
similarity = _de.jaccard(words_a, words_b)
```
`word_set()` returns a `frozenset`, which is hashable and can be stored for reuse. If you are computing similarity between one article and many others, compute `word_set()` once for each text and reuse.

**Use the appropriate scorer for the context.**
- Single article, full detail: `kde_score_article(text)`
- Bulk review of many articles: `kde_score_article_fast(text)` — significantly faster, returns fewer fields
- Guideline evaluation: `kde_score_guideline_fast(text)`

**Check `has_kde_blocker` before using health scores.**
When a blocker is active, the health score and resolution score are capped. Code that computes averages or comparisons should account for the cap. The `has_kde_blocker` field in the `kde_score_article()` output signals this condition.

**Use `extract_metrics_from_reports()` for parsing tool outputs.**
`recommend_improvements` and `fin_dashboard` receive the text outputs of other tools and need to extract numeric metrics. Always use `_de.extract_metrics_from_reports()` for this purpose. Do not write new regex patterns inline in tools.

**Use named constants, never inline values.**
```python
# Correct
if similarity >= _de.GUIDELINE_CLUSTER_THRESHOLD:
    ...

# Wrong — creates a hidden threshold inconsistent with the DE
if similarity >= 0.70:
    ...
```

### What NOT to do

**Do not reimplement any function that exists in `decision_engine.py`.**
If you need Jaccard similarity in a new tool, call `_de.jaccard()`. Do not write a local `text_similarity()` or `compute_overlap()`. This is the root cause of the duplication problem that required three sprints to fix.

**Do not define pattern lists inside tool functions.**
All pattern vocabularies belong in `decision_engine.py`. If a new tool needs a new pattern list, add it to `decision_engine.py` as a module-level constant.

**Do not hardcode threshold values inside tools.**
Every threshold that governs a decision should be a named constant in `decision_engine.py`. Hardcoded values drift silently and cannot be tuned centrally.

**Do not add side effects to `decision_engine.py`.**
The module must remain stateless. Do not add file I/O, logging calls, database connections, network requests, or mutable global state. These belong in the tool layer or in a separate integration layer.

**Do not add duplicate functions internally.**
During v3 of the Guideline Core Consolidation, a duplicate block (lines 1265–1592) was accidentally appended to `decision_engine.py` when two concurrent agents both wrote the Guideline module. The duplicate was removed before v1.0 release. Before adding any new function, verify it does not already exist in the module.

**Do not use `kde_score_article()` for bulk analysis.**
The full 12-criterion scorer is expensive. For bulk operations (reviewing 50+ articles), use `kde_score_article_fast()`. Reserve the full scorer for single-article audit contexts.

---

## Future Evolution

### Extending the Knowledge module (lines 1–897)

New analytical functions for knowledge articles follow this pattern:

1. Define any new pattern lists or constants at the module level, above the function, following the existing constant block structure.
2. Write the function as a pure function — typed inputs, typed output, no side effects.
3. Place it in the appropriate section: Detection (after line 120), Scoring (after line 193), Classification (after line 618), Knowledge Debt (after line 710), Coverage (after line 748), or ROI (after line 807).
4. Verify no existing function covers the same behavior.

Example: a function to detect FAQ-appropriate content would be placed in the Detection section, use a new `FAQ_SIGNALS` constant, and be called from whichever tool needs it.

### Extending the Guideline module (lines 898–1264)

New guideline functions follow the same pattern. Constant additions go into the Guideline constants block (lines 898–1136). Function additions go into the Guideline functions block (lines 1139–1264). The `GUIDELINE_EVENT_CATALOG` can be extended with new event types — each event needs `id`, `label`, `signals`, `impact`, and `esc_risk`. New entries in `GUIDELINE_PATTERN_NAMES` and `GUIDELINE_TEMPLATES` cover new multi-event patterns.

### Adding a third module

If a future domain (e.g., Macro Management, SLA Compliance) requires its own set of constants and functions, it should be added as a new section in `decision_engine.py` — not as a separate file. The single-file design keeps the import interface simple (`import decision_engine as _de`) and ensures all domains share the same utility functions (`jaccard`, `word_set`, `semaforo`, etc.) without needing cross-module imports.

### What must not change

The following are architectural invariants that must be preserved across any future evolution:

1. `decision_engine.py` is the only place where analytical functions are defined.
2. All functions remain pure — no side effects, no I/O.
3. All threshold values are named constants — no inline magic numbers.
4. The import interface remains `import decision_engine as _de`.
5. Functions are not duplicated internally. Before adding a function, check it does not already exist.
6. The `KDE_HARD_CAP_BLOCKER` and `KDE_HARD_CAP_RESOLUTION` constants enforce safety floors. They must not be removed or bypassed.

---

*Decision Engine — FIN Architect MCP v1.0.0*
