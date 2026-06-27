# Examples

This document provides five complete usage scenarios for FIN Architect MCP. Each example includes the business context, the exact tools involved, the execution flow, the expected output, and how to interpret the results.

All tools shown here are real tools defined in `server.py`. All analytical decisions described are produced by `decision_engine.py`. No behavior is invented.

---

## Example 1 — Improving Billing Guidelines

### Objective

The billing module (`Facturación`) has a high escalation rate. Support agents report that FIN's responses in billing conversations are inconsistent — sometimes it escalates immediately, sometimes it tries to resolve without a clear path, and sometimes it repeats the same answer. The objective is to diagnose the guideline architecture for the billing module and produce a prioritized improvement plan.

### Context

- Product: `Facturación`
- Problem: Inconsistent FIN behavior in billing conversations
- Symptom: High escalation rate, user frustration signals in conversation logs
- Starting point: Raw conversation exports from Intercom for billing-related cases

### Tools used

1. `architect_review` — full pipeline diagnosis
2. `recommend_improvements` — ROI-ranked improvement backlog

### Input

**For `architect_review`:**
```
product: "Facturación"

conversations: [
  "El cliente indica que la factura no se generó después de completar la venta. 
   Ya revisó el artículo de ayuda y siguió los pasos pero el error persiste. 
   FIN le dio la misma respuesta dos veces.",

  "Usuario reporta que el CUFE no aparece en el PDF de la factura. 
   Dice que es urgente porque necesita presentar la factura ante la DIAN hoy mismo. 
   FIN le indicó que esperara sin dar un paso concreto.",

  "Cliente señala que se le cobró dos veces en el mismo mes. 
   Quiere un reembolso. FIN dijo que no podía hacer nada y cerró la conversación.",

  "El sistema no permite generar la factura electrónica. 
   El error es 'resolución vencida'. FIN no tiene información sobre este error.",

  "Factura generada con datos incorrectos del cliente. 
   FIN escaló sin agotar las opciones de corrección disponibles en el sistema."
]

current_guidelines: [
  "Cuando el usuario reporte un error de facturación, FIN debe indicar que el área 
   de soporte técnico revisará el caso.",
  
  "FIN no debe ofrecer reembolsos directamente. Derivar siempre al área financiera.",
  
  "Si el CUFE no aparece, indicar al usuario que espere 24 horas."
]

objective: "Identify guideline gaps and conflicts causing high escalation rate in billing"
```

### Flow

```
Step 1 — architect_review
         Receives conversations + current_guidelines.
         Internally runs:
           - extract_guidelines: clusters conversations into guideline candidates
           - classify_guideline: assigns intent, risk, priority to each candidate
           - detect_conflicts: compares candidates against current_guidelines
           - audit_guideline: compliance check per guideline
           - score_guideline: 10-criterion score per guideline
           - simulate_fin: predicts FIN behavior for each guideline
           - kde_score_article_fast: quick health check on referenced articles
         Returns: consolidated architectural report

Step 2 — recommend_improvements
         Receives the architect_review output as repository_review_text.
         Calls extract_metrics_from_reports() to parse:
           - blocked guidelines count
           - conflict count
           - knowledge debt level
           - missing coverage categories
         Calls rank_improvements() + compute_roi() to produce ranked backlog.
         Returns: prioritized list of improvements with ROI scores
```

### Expected output

**From `architect_review`:**

- **Detected patterns:** Loop instruccional (FIN repite sin avanzar), Urgencia no atendida, Escalamiento sin criterios, Fallo técnico sin guía
- **Conflicts detected:** The guideline "derivar siempre al área financiera" conflicts with the implicit need to resolve reimbursement cases autonomously when the cause is a system error. Severity: ALTA.
- **Blocked guidelines:** The guideline "espere 24 horas" receives a blocker flag — it instructs FIN to defer without diagnostic steps, producing a loop risk when the problem persists.
- **Health score:** Low (expected in the 40–55 range given the input signals)
- **Deployment readiness:** NOT READY or READY WITH RECOMMENDATIONS

**From `recommend_improvements`:**

| Priority | Improvement | Impact | Effort | ROI |
|----------|------------|--------|--------|-----|
| 1 | Create diagnostic guideline for "resolución vencida" error (DIAN category) | High | Low | High |
| 2 | Rewrite 24-hour deferral guideline with conditional escalation criteria | High | Low | High |
| 3 | Define autonomous resolution path for double-charge cases before escalating | Medium | Medium | Medium |
| 4 | Add CUFE-specific troubleshooting steps to the billing knowledge article | Medium | Medium | Medium |

### Interpretation

The high escalation rate is caused by three structural problems surfaced by the analysis:

1. **Missing diagnostic guidelines** for known error types (`resolución vencida`, CUFE absence). FIN has no protocol for these scenarios and defaults to deferral or escalation.
2. **A blocking guideline** that instructs FIN to tell users to wait 24 hours — this produces loop risk when users return with the same problem.
3. **A conflict** between the "never offer reimbursements" guideline and cases where the system error is the cause — FIN escalates these unnecessarily because it has no resolution path for system-caused charges.

The highest-ROI fix is creating a guideline for `resolución vencida` because it is a DIAN-category issue (high compliance risk), affects a specific and documentable error, and requires low effort (a single guideline template).

---

## Example 2 — Auditing a Knowledge Base

### Objective

The support team suspects that several knowledge articles used by FIN are underperforming — producing unresolved cases that come back as repeat contacts. The objective is to audit the current article set, identify which articles have blockers or low scores, and produce specific optimization plans.

### Context

- Product: General (multiple categories)
- Problem: High repeat contact rate, suspected article quality issues
- Starting point: Three knowledge articles for different support scenarios

### Tools used

1. `audit_knowledge` — full 12-criterion KDE audit per article
2. `optimize_article` — prioritized optimization plan per article
3. `knowledge_review` — bulk coverage and debt analysis across all articles

### Input

**Three articles to audit:**

```
Article A: "Cómo configurar el módulo de facturación"
  Content: An article with general instructions, no numbered steps, 
  uses "normalmente" and "según corresponda" multiple times, 
  no escalation path defined.

Article B: "Error al generar CUFE"  
  Content: Starts with "Nunca contactes a soporte directamente. 
  Vuelve a intentar el procedimiento hasta que funcione." 
  Has numbered steps but they reference backend admin panel access.

Article C: "Cancelación de cuenta"
  Content: Clear numbered steps, defines escalation condition 
  ("si el problema persiste después del paso 4, escalar con el ID del caso"), 
  no absolute terms, appropriate length.
```

### Flow

```
Step 1 — audit_knowledge (Article A)
         Calls kde_score_article(text).
         Computes 12 criteria, detects signals.
         Returns: health score, criterion breakdown, blocker list, deploy decision.

Step 2 — optimize_article (Article A + audit output)
         Receives Article A text + audit_knowledge output.
         Calls rank_improvements() + compute_roi() on identified weak criteria.
         Returns: prioritized action plan with specific rewrites.

Step 3 — audit_knowledge (Article B)
         Detects: anti_escalation = True ("nunca contactes a soporte"),
                  loop_risk = CRÍTICO ("vuelve a intentar el procedimiento"),
                  fin_blocker_hits = ["accede al panel de administración"].
         Applies KDE_HARD_CAP_BLOCKER: health capped at 60.
         Applies KDE_HARD_CAP_RESOLUTION: resolution capped at 40.
         Returns: BLOQUEADO deploy decision.

Step 4 — optimize_article (Article B + audit output)
         Returns: action plan focused on the three blockers first, 
         then secondary criteria.

Step 5 — audit_knowledge (Article C)
         Detects: no blockers, has escalation, no absolute terms.
         Returns: high health score, LISTO deploy decision.

Step 6 — knowledge_review (all three articles)
         Calls kde_score_article_fast() on each article.
         Calls compute_knowledge_debt() with aggregate counts.
         Calls jaccard() + word_set() across all pairs for duplicate detection.
         Calls compute_coverage() on combined text.
         Returns: bulk health summary, debt score, coverage map, duplicate detection.
```

### Expected output

**From `audit_knowledge` — Article A:**
- Health score: 48–58 (no escalation path, vague phrases, no numbered steps)
- Weak criteria: Estructura (no steps), Escalamiento (no path defined), Ambiguedad (vague phrases)
- Deploy decision: NO LISTO or LISTO CON RECOMENDACIONES
- Automation readiness: Media

**From `audit_knowledge` — Article B:**
- Health score: capped at 60 (KDE_HARD_CAP_BLOCKER active)
- Resolution score: capped at 40 (KDE_HARD_CAP_RESOLUTION active)
- Blockers: anti-escalation rule, CRÍTICO loop risk, FIN blocker actions
- Deploy decision: BLOQUEADO
- Automation readiness: No apto

**From `audit_knowledge` — Article C:**
- Health score: 78–90 (numbered steps, escalation defined, no absolute terms)
- No blockers
- Deploy decision: LISTO or LISTO CON RECOMENDACIONES
- Automation readiness: Alta or Excelente

**From `optimize_article` — Article B (highest priority):**

| Priority | Action | Target criterion |
|----------|--------|-----------------|
| 1 | Remove "nunca contactes a soporte" and replace with conditional escalation | Escalamiento |
| 2 | Remove "vuelve a intentar el procedimiento" — add conditional exit path | Loop risk / Pasos |
| 3 | Remove admin panel access instruction — replace with user-executable steps | Uso por FIN |
| 4 | Add numbered steps with action verbs | Estructura / Pasos |

**From `knowledge_review` — all three articles:**
- Global health: approximately 62 (weighted by article scores)
- Knowledge debt: MEDIO (one blocked article, no duplicates detected, partial coverage)
- Coverage gaps: categories not represented in the three articles identified from TOPIC_CATEGORIES
- Duplicate detection: no significant overlap (Jaccard < 0.55 between all pairs)
- Deployment readiness: NOT READY (Article B is blocked)

### Interpretation

Article B is the critical blocker. Until its three structural problems are resolved (anti-escalation rule, CRÍTICO loop risk, FIN blocker actions), the repository cannot be declared deployment-ready regardless of Article A and C quality.

Article A is the second priority. Its low escalation score and vague language will produce repeat contacts — users who cannot resolve their issue return because FIN has no exit path to offer them.

Article C demonstrates what a deployment-ready article looks like. The optimization effort should use it as a reference for structure and escalation definition.

---

## Example 3 — Repository Health Assessment

### Objective

Before a product launch, the operations team needs to know whether the knowledge repository is ready for FIN to operate autonomously. The objective is a single executive view of repository health and a ranked list of pre-launch fixes.

### Context

- Product: Full repository across all support categories
- Problem: Unknown — this is a proactive assessment, not a reactive diagnosis
- Starting point: Full article set + existing guidelines, no specific symptom to investigate

### Tools used

1. `repository_review` — full repository health analysis
2. `recommend_improvements` — ROI-ranked pre-launch backlog
3. `fin_dashboard` — unified executive report

### Input

**For `repository_review`:**
```
articles: [list of all knowledge article texts for the product]
guidelines: [list of all current guideline texts for the product]
product: "Inventario"
```

### Flow

```
Step 1 — repository_review
         Calls kde_score_article_fast() on every article.
         Calls kde_score_guideline_fast() on every guideline.
         Calls compute_knowledge_debt() with:
           - total_art_blocked (articles with CRÍTICO loop or anti-escalation)
           - total_g_conflicts (detected pairwise guideline conflicts)
           - total_art_dups (article pairs with Jaccard >= 0.55)
           - missing_cats_count (TOPIC_CATEGORIES not covered)
           - total_g_blocked (guidelines with anti-escalation or health < 50)
           - total_art_critical (articles with health < 35)
         Calls global_status_from_health() for the repository status.
         Calls deployment_readiness() for the executive decision.
         Returns: repository health report

Step 2 — recommend_improvements
         Parses the repository_review output via extract_metrics_from_reports().
         Builds improvement items from detected gaps.
         Calls compute_roi() per improvement.
         Calls rank_improvements() to produce the sorted backlog.
         Returns: ranked improvement list

Step 3 — fin_dashboard
         Receives repository_review + recommend_improvements outputs.
         Calls extract_metrics_from_reports() to read structured metrics.
         Calls semaforo() for each module score.
         Calls global_status_from_health() for the top-line indicator.
         Calls deployment_readiness() for the final decision.
         Returns: executive dashboard
```

### Expected output

**From `repository_review`:**
```
REPOSITORY HEALTH — Inventario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Global Health:           72/100
Knowledge Debt:          MEDIO
Deployment Readiness:    READY WITH RECOMMENDATIONS

Articles:
  Total:                 12
  Blocked:               1
  High risk:             3
  Acceptable:            5
  Healthy:               3

Guidelines:
  Total:                 8
  Blocked:               0
  Conflicts detected:    2

Coverage:
  Covered categories:    facturación, soporte técnico, configuración, inventario
  Missing categories:    reembolso, onboarding

Duplicate articles detected: 1 pair (Jaccard 0.62)
```

**From `recommend_improvements`:**

| Priority | Area | Improvement | ROI |
|----------|------|------------|-----|
| 1 | Article | Fix blocked article — remove loop instruction and add escalation path | High |
| 2 | Coverage | Create article for "reembolso" category (missing, affects debt score) | High |
| 3 | Guideline | Resolve conflict between two detected conflicting guidelines | Medium |
| 4 | Article | Merge or differentiate the duplicate article pair | Medium |
| 5 | Coverage | Create onboarding article (missing category) | Medium |
| 6 | Article | Improve 3 high-risk articles: add numbered steps and escalation criteria | Low–Medium |

**From `fin_dashboard`:**
```
FIN ARCHITECT EXECUTIVE DASHBOARD — Inventario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Global Health:           🟡 72/100 — ACEPTABLE
Knowledge Debt:          🟡 MEDIO
Knowledge Coverage:      🟠 64% (2 categories missing)
Guideline Health:        🟡 Conflicts detected (2)
Deployment Readiness:    🟡 READY WITH RECOMMENDATIONS

Open blockers:
  ⚠️  1 article blocked (loop instruction + missing escalation)
  ⚠️  2 guideline conflicts requiring resolution

Pre-launch priority: Resolve 2 items (1 blocked article, 1 coverage gap)
Estimated impact: +12 points global health after fixes
```

### Interpretation

The repository is not blocked — no structural condition prevents deployment. The `READY WITH RECOMMENDATIONS` status means FIN can operate, but with predictable gaps: the missing `reembolso` and `onboarding` categories will produce escalations in those scenarios because FIN has no resolution path for them.

The single blocked article is the highest-priority pre-launch fix. Its loop instruction means FIN will send users in circles for its specific topic until the article is corrected.

The two guideline conflicts are lower urgency but should be resolved before volume increases — conflicting guidelines produce inconsistent FIN behavior across agents and sessions.

---

## Example 4 — End-to-End FIN Improvement

### Objective

A complete improvement cycle: starting from raw Intercom conversations, extract and validate new guidelines, cross-check against the knowledge base, assess the full repository, and produce an executive report. This is the full pipeline run as a deliberate improvement sprint.

### Context

- Product: `Caja` (point-of-sale cash operations)
- Problem: Support team identifies recurring issues in shift-close conversations — FIN is not handling them well
- Starting point: 30 days of Intercom conversation exports for the Caja product

### Tools used

1. `extract_guidelines`
2. `generate_guideline`
3. `audit_guideline`
4. `architect_review`
5. `knowledge_review`
6. `repository_review`
7. `recommend_improvements`
8. `fin_dashboard`

### Input

**For `extract_guidelines`:**
```
conversations: [
  "Usuario reporta que el cierre de caja no coincide con las ventas del día.",
  "FIN no pudo explicar cómo corregir la diferencia de efectivo en el cierre.",
  "El sistema no permite abrir caja por segunda vez en el mismo día.",
  "Cliente intenta hacer cierre parcial y el sistema muestra error.",
  "Cajero sin acceso para hacer el cuadre porque otro usuario tiene sesión activa.",
  ... (full 30-day export)
]
product: "Caja"
```

### Flow

```
Step 1 — extract_guidelines
         Groups conversation turns into clusters using jaccard() + word_set().
         Applies GUIDELINE_CLUSTER_THRESHOLD (0.70) to form clusters.
         Applies GUIDELINE_MERGE_THRESHOLD (0.80) to merge near-duplicate clusters.
         For each cluster, calls detect_guideline_events() to identify conversation
         events (loop, urgency, frustration, problem-persists, etc.).
         Calls cluster_pattern_name() to name each pattern.
         Calls guideline_impact_priority() to score and prioritize.
         Returns: set of guideline candidates with names, priorities, impact scores,
                  and template suggestions.

         Typical output for Caja conversations:
           - Cluster 1: "Cierre de caja con diferencia" (pattern: Documentación insuficiente)
           - Cluster 2: "Error en apertura de caja" (pattern: Fallo técnico sin guía)
           - Cluster 3: "Sesión activa bloqueando cuadre" (pattern: Bloqueo sin resolución)

Step 2 — generate_guideline (for each high-priority cluster)
         Calls detect_guideline_problems() on the cluster conversation text.
         Uses GUIDELINE_FAILURE_MAP to describe what went wrong.
         Uses GUIDELINE_BEHAVIOR_MAP to prescribe FIN behavior.
         Calls guideline_template_for() to select the base template.
         Returns: structured guideline text ready for review.

Step 3 — audit_guideline (for each generated guideline)
         Checks: ABSOLUTE_TERMS, GUIDELINE_PROHIBITION_WORDS,
                 GUIDELINE_OBLIGATION_WORDS, detect_guideline_problems().
         Calls guideline_risk_level() for the risk classification.
         Returns: compliance status, issues list, suggestions per guideline.

Step 4 — architect_review
         Receives validated guidelines + original conversations.
         Runs the full pipeline internally:
           - Re-scores all guidelines via kde_score_guideline_fast()
           - Detects conflicts via jaccard() + GUIDELINE_CONTRADICTION_PAIRS
           - Simulates FIN behavior per guideline via simulate_fin logic
           - Audits referenced knowledge articles via kde_score_article_fast()
         Returns: consolidated architectural diagnosis for the Caja product.

Step 5 — knowledge_review
         Receives all Caja knowledge articles.
         Calls kde_score_article_fast() per article.
         Calls compute_knowledge_debt() with aggregate counts.
         Calls compute_coverage() to check Caja-relevant categories.
         Returns: article health summary, debt level, coverage gaps.

Step 6 — repository_review
         Receives full article + guideline sets for Caja.
         Calls global_status_from_health() for the product status.
         Calls deployment_readiness() for the executive decision.
         Returns: repository health report with deployment readiness.

Step 7 — recommend_improvements
         Parses architect_review + knowledge_review + repository_review outputs.
         Calls rank_improvements() + compute_roi() across all identified gaps.
         Returns: unified ranked improvement backlog.

Step 8 — fin_dashboard
         Aggregates all upstream outputs.
         Calls semaforo() per module.
         Calls global_status_from_health() and deployment_readiness().
         Returns: executive dashboard.
```

### Expected output

**From `extract_guidelines`:**
- 3 guideline candidates extracted from 30 days of conversations
- Top cluster: "Cierre de caja con diferencia" — impact score 85, priority INMEDIATA
- All three clusters receive template suggestions from `GUIDELINE_TEMPLATES`

**From `generate_guideline` — Cluster 1 example:**
```
[Generated guideline]
Trigger: When the user reports that the shift-close total does not match
the day's sales figures.

FIN behavior:
1. Acknowledge the discrepancy and ask for the difference amount and 
   payment method breakdown.
2. Guide the user through the reconciliation check in the system.
3. If the discrepancy is above [threshold], escalate to the cash operations
   area with: difference amount, affected payment methods, and shift date.

Escalation condition: difference > threshold OR system does not allow correction.
```

**From `architect_review`:**
- No conflicts detected among the three new guidelines (they cover distinct scenarios)
- Knowledge article health for Caja: 55–65 range (partial coverage, some articles missing steps)
- Deployment readiness: READY WITH RECOMMENDATIONS

**From `knowledge_review`:**
- 4 articles reviewed: 1 healthy, 2 acceptable, 1 no-data (missing article for session-conflict scenario)
- Coverage gap: no article covers the "sesión activa bloqueando cuadre" scenario
- Knowledge debt: BAJO (no blocked articles, low duplicate risk)

**From `fin_dashboard`:**
```
FIN ARCHITECT EXECUTIVE DASHBOARD — Caja
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Global Health:           🟡 68/100 — ACEPTABLE
Knowledge Debt:          🟢 BAJO
Guideline Coverage:      🟢 3 new guidelines validated (0 conflicts)
Article Coverage:        🟠 1 scenario without documentation
Deployment Readiness:    🟡 READY WITH RECOMMENDATIONS

Next actions:
  1. Create article for "sesión activa bloqueando cuadre" scenario
  2. Improve 2 acceptable articles (add numbered steps + escalation)
  3. Deploy 3 new guidelines to FIN production configuration
```

### Interpretation

The end-to-end pipeline converted 30 days of raw conversations into three validated, conflict-free guidelines and a specific knowledge gap report in a single sprint. The pipeline identified the one missing article (session conflict) that no one had flagged as a gap — it only became visible when the conversation cluster analysis showed it as a recurring unresolved pattern.

The `READY WITH RECOMMENDATIONS` status means the three new guidelines are safe to deploy immediately. The missing article should be created before the next high-volume period — without it, FIN will continue to escalate session-conflict cases without attempting resolution.

---

## Example 5 — Executive Review

### Objective

The product director needs a single, clear view of the support architecture health before a quarterly review. No deep analysis is needed — only the executive decision: is FIN ready, what are the open risks, and what would it take to reach full readiness?

### Context

- Audience: Product Director, Support Operations Lead
- Input: Previous analysis outputs already exist (repository_review ran last week, knowledge_review ran yesterday)
- Goal: One-call executive summary

### Tools used

1. `repository_review` — refreshed repository snapshot (if needed)
2. `fin_dashboard` — unified executive report and deployment decision

### Input

**For `fin_dashboard`:**
```
repository_review_text: [output from repository_review run last week]
knowledge_review_text:  [output from knowledge_review run yesterday]
architect_review_text:  ""  (not available for this session)
```

### Flow

```
Step 1 — repository_review (optional refresh)
         If the existing report is more than a week old, re-run to get
         a current snapshot. Otherwise skip this step and pass the
         existing output to fin_dashboard.

         If run: Calls kde_score_article_fast() + kde_score_guideline_fast()
         on the full repository. Computes global_status_from_health() and
         deployment_readiness(). Returns fresh health report.

Step 2 — fin_dashboard
         Receives repository_review_text + knowledge_review_text as inputs.
         Calls extract_metrics_from_reports() to parse:
           - global_health from repository_review output
           - knowledge_debt from repository_review output
           - prod_blocked, prod_high_risk from repository_review output
           - total_a_blocked, total_g_blocked from both reports
           - coverage_pct and missing_cats_count
         Calls semaforo() for each metric (thresholds: 70 warning, 85 ok).
         Calls global_status_from_health() for the top-line status.
         Calls deployment_readiness() for the final executive decision.
         Returns: executive dashboard.
```

### Expected output

**From `fin_dashboard`:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIN ARCHITECT — EXECUTIVE DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GLOBAL STATUS:           🟡 ACEPTABLE
DEPLOYMENT READINESS:    🟡 READY WITH RECOMMENDATIONS

─────────────────────────────────────────────────────────────
MODULE HEALTH
─────────────────────────────────────────────────────────────
Knowledge Articles:      🟡 73/100
Guidelines:              🟢 85/100
Coverage:                🟠 64% (2 categories missing)
Knowledge Debt:          🟡 MEDIO (score: 32)

─────────────────────────────────────────────────────────────
RISK INDICATORS
─────────────────────────────────────────────────────────────
Blocked articles:        ⚠️  1
Blocked guidelines:          0
Guideline conflicts:     ⚠️  2
Duplicate articles:      ⚠️  1 pair

─────────────────────────────────────────────────────────────
PATH TO FULL READINESS
─────────────────────────────────────────────────────────────
To reach READY status:
  1. Fix 1 blocked article (loop instruction + missing escalation path)
  2. Resolve 2 guideline conflicts
  3. Create articles for 2 missing categories (reembolso, onboarding)

Estimated effort: Medium (3–5 articles, 2 guideline rewrites)
Estimated health impact: +15 points → 88/100 (SALUDABLE)
─────────────────────────────────────────────────────────────
```

### Interpretation

**What the dashboard communicates to an executive audience:**

- FIN is operational. The `READY WITH RECOMMENDATIONS` status means it can handle the majority of support cases autonomously. This is not a blocked or failing system.

- Two categories of risk exist: a single blocked article (which causes loops in one specific scenario) and two guideline conflicts (which produce inconsistent FIN behavior across similar cases). Neither is catastrophic, but both will generate avoidable escalations until resolved.

- Full readiness (SALUDABLE, READY) requires a defined, bounded effort: 3–5 articles and 2 guideline rewrites. This is a sprint of work, not a system redesign. The health score projection (+15 points) gives the director a concrete before/after picture.

- Missing categories (`reembolso`, `onboarding`) are the largest coverage gap. FIN has no resolution path for reimbursement requests or new-user onboarding issues — both high-volume scenarios. This is the case for prioritizing those articles above lower-value improvements.

**When to use this workflow:**

- Before quarterly reviews: refresh `repository_review`, run `fin_dashboard`, present the output.
- After a product launch: run `repository_review` + `fin_dashboard` to establish a health baseline.
- After a support spike: run `repository_review` + `fin_dashboard` to confirm no regression in knowledge quality caused the spike.

`fin_dashboard` is designed for exactly this use case: a single call that aggregates all upstream analysis into one decision-grade report, without requiring the executive audience to interpret raw scores from individual tools.

---

*FIN Architect MCP v1.0.0 — Examples catalog.*
