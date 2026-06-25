"""
decision_engine.py — Motor de Decisión Centralizado de FIN Architect MCP

Centraliza toda la lógica de cálculo compartida entre las herramientas:
  - audit_knowledge, optimize_article, knowledge_review
  - repository_review, recommend_improvements, fin_dashboard
  - audit_guideline, architect_review

Reglas de diseño:
  - Ninguna herramienta reimplementa lógica definida aquí.
  - Todas las métricas derivadas (health, risk, debt, semáforo, etc.)
    se calculan desde este módulo.
  - Las funciones son puras: sin side-effects, sin I/O.
"""

import re as _re

# ════════════════════════════════════════════════════════════════════════════ #
# CONSTANTES                                                                   #
# ════════════════════════════════════════════════════════════════════════════ #

KDE_HARD_CAP_BLOCKER   = 60   # health máximo cuando hay bloqueador
KDE_HARD_CAP_RESOLUTION = 40  # resolution máximo cuando hay bloqueador

TOPIC_CATEGORIES = {
    "facturación":     ["factura", "facturación", "cobro", "pago", "cargo", "recibo"],
    "soporte técnico": ["error", "falla", "problema", "no funciona", "reiniciar", "técnico"],
    "cancelación":     ["cancelar", "cancelación", "baja", "terminar", "finalizar contrato"],
    "configuración":   ["configurar", "configuración", "ajuste", "parámetro", "instalar"],
    "escalamiento":    ["escalar", "escala", "supervisor", "agente humano", "área responsable"],
    "reembolso":       ["reembolso", "devolución", "devolver", "reintegro"],
    "onboarding":      ["registro", "activar", "alta", "nuevo usuario", "cómo empezar"],
    "seguridad":       ["contraseña", "clave", "acceso", "bloqueo", "seguridad", "autenticación"],
    "reportes":        ["reporte", "informe", "estadística", "consulta", "historial"],
    "integraciones":   ["integración", "api", "conector", "sistema externo", "sincronizar"],
    "general":         ["información", "consulta general", "pregunta", "detalle", "dato"],
}

LOOP_PATTERNS = [
    "vuelve a intentar", "consulta nuevamente este artículo",
    "reinicia nuevamente", "repite los pasos", "inténtalo otra vez",
    "vuelve a reiniciar", "vuelve a intentar el procedimiento",
    "repite el procedimiento", "intenta de nuevo", "vuelve a empezar",
]

LOOP_PATTERNS_REPO = [
    "loop", "bucle", "ciclo infinito", "repite", "vuelve a preguntar",
    "pregunta lo mismo", "mismo resultado", "sin salida", "sin solución",
]

ANTI_ESCALATION_PATTERNS = [
    r"nunca\s+(escal|contact|transf)\w*",
    r"no\s+(escal|contact|transf)\w*\s+este",
]

ANTI_ESCALATION_PATTERNS_REPO = [
    r"nunca escal[ae]", r"no escal[ae]", r"no (se |)transfier[ae]",
    r"prohibid[oa] escal[ae]", r"sin excepci[oó]n[^.]*no escal[ae]",
    r"bajo ning[uú]n concepto[^.]*escal[ae]", r"en ning[uú]n caso[^.]*escal[ae]",
]

ABSOLUTE_TERMS = ["siempre", "nunca", "todos", "ninguno", "cualquier caso"]

ABSOLUTE_TERMS_REPO = [
    "nunca", "jamás", "absolutamente prohibido", "en ningún caso",
    "bajo ningún concepto", "sin excepción",
]

ESCALATION_SIGNALS = [
    "escalar", "escala", "contacta a soporte", "contactar soporte",
    "comunícate con", "transfiere", "agente", "asesor", "caso de soporte",
    "ticket", "si el problema persiste", "si no se resuelve",
]

STEP_VERBS = [
    "hacer clic", "selecciona", "ingresa", "abre", "cierra", "navega",
    "accede", "verifica", "confirma", "guarda", "descarga", "instala",
    "actualiza", "reinicia", "copia", "pega", "escribe", "busca",
    "haz clic", "pulsa", "presiona", "dirígete", "ve a", "entra",
    "click", "ir a", "login", "inicia sesión",
]

VAGUE_PHRASES = [
    "de alguna manera", "como sea posible", "en la medida",
    "según corresponda", "a discreción", "podría", "quizás",
    "tal vez", "depende", "en algunos casos", "eventualmente",
    "normalmente", "generalmente", "usualmente",
]

COVERAGE_SIGNALS = [
    "causa", "síntoma", "solución", "resultado", "verificar", "error",
    "problema", "cuándo", "prerequisito", "requisito", "nota", "importante",
    "advertencia", "aviso", "ejemplo",
]

TECHNICAL_TERMS = [
    "api", "webhook", "endpoint", "token", "oauth", "json", "xml",
    "cufe", "dian", "rut", "nit", "uuid", "erp", "crm", "ide",
]

FIN_POSITIVE_SIGNALS = [
    "el usuario debe", "el cliente debe", "verifique", "confirme",
    "paso", "primero", "luego", "después", "finalmente", "a continuación",
    "si el error persiste", "si el problema continúa", "si no funciona",
]

FIN_BLOCKER_ACTIONS = [
    "accede al panel de administración", "desde el backend", "en la consola de",
    "modifica la base de datos", "ejecuta el script", "reinicia el servidor",
    "contacta al equipo de desarrollo", "solicita al administrador del sistema",
    "acceso de superusuario", "requiere acceso root",
]

RISKY_ACTIONS = [
    "eliminar", "borrar", "formatear", "reinstalar", "resetear a fábrica",
    "eliminar todos los datos", "vaciar la base", "truncar",
    "desinstalar", "modificar permisos del sistema",
]


# ════════════════════════════════════════════════════════════════════════════ #
# DETECCIÓN — funciones de señal atómicas                                     #
# ════════════════════════════════════════════════════════════════════════════ #

def detect_loop_risk(text_lower: str, use_repo_patterns: bool = False) -> tuple:
    """
    Devuelve (level: str, count: int, hits: list).
    level: BAJO / MEDIO / ALTO / CRÍTICO
    use_repo_patterns: usa keywords simples (repo/knowledge_review)
                       vs patrones de frase (audit_knowledge/optimize_article)
    """
    patterns = LOOP_PATTERNS_REPO if use_repo_patterns else LOOP_PATTERNS
    hits = [p for p in patterns if p in text_lower]
    count = len(hits)
    if not use_repo_patterns:
        if _re.search(r'(vuelve al paso|regresa al paso|repite desde el paso|vuelve a la sección)', text_lower):
            count += 1
            hits = list(hits) + ["referencia circular entre pasos"]
    if count == 0:
        level = "BAJO"
    elif count == 1:
        level = "MEDIO"
    elif count <= 3:
        level = "ALTO"
    else:
        level = "CRÍTICO"
    return level, count, hits


def detect_anti_escalation(text_lower: str, use_repo_patterns: bool = False) -> bool:
    """True si el texto contiene una regla que prohíbe el escalamiento."""
    patterns = ANTI_ESCALATION_PATTERNS_REPO if use_repo_patterns else ANTI_ESCALATION_PATTERNS
    return any(_re.search(p, text_lower) for p in patterns)


def detect_absolute_hits(text_lower: str, repo_mode: bool = False) -> list:
    """Lista de términos absolutos encontrados."""
    terms = ABSOLUTE_TERMS_REPO if repo_mode else ABSOLUTE_TERMS
    return [t for t in terms if t in text_lower]


def detect_escalation(text_lower: str) -> bool:
    """True si el texto menciona alguna señal de escalamiento."""
    return any(e in text_lower for e in ESCALATION_SIGNALS)


def detect_escalation_repo(text_lower: str) -> bool:
    """Versión simplificada de detección de escalamiento (para repository_review)."""
    esc_kw = ["escala", "escalar", "transfiere", "transferir", "derivar",
              "agente humano", "supervisor", "área responsable"]
    return any(k in text_lower for k in esc_kw)


def detect_fin_blockers(text_lower: str) -> list:
    """Acciones que FIN no puede ejecutar."""
    return [b for b in FIN_BLOCKER_ACTIONS if b in text_lower]


def jaccard(words_a: set, words_b: set) -> float:
    """Similaridad de Jaccard entre dos conjuntos de palabras."""
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def word_set(text: str) -> set:
    """Conjunto de palabras en minúsculas de un texto."""
    return frozenset(_re.findall(r'\b\w+\b', text.lower()))


# ════════════════════════════════════════════════════════════════════════════ #
# KDE — Knowledge Decision Engine (nivel artículo, audit_knowledge)           #
# ════════════════════════════════════════════════════════════════════════════ #

def kde_score_article(text: str) -> dict:
    """
    Calcula el KDE completo de un artículo individual.
    Usado por audit_knowledge, optimize_article y knowledge_review.
    Devuelve un dict con todos los campos necesarios.
    """
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)
    sentences = [s.strip() for s in _re.split(r'[.!?]+', text) if s.strip()]
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Título
    title_m = _re.match(r'^#+\s*(.+?)$', text.strip(), _re.MULTILINE)
    title = title_m.group(1).strip() if title_m else (lines[0] if lines else "Sin título")

    # Señales estructurales
    has_numbered_steps = bool(_re.search(r'(?:^|\n)\s*\d+[\.\)]\s+\S', text))
    has_bullets = bool(_re.search(r'(?:^|\n)\s*[-•*]\s+\S', text))
    has_sections = bool(_re.search(
        r'(?:^|\n)\s*#{1,3}\s+\S|(?:^|\n)[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{3,}:', text
    ))

    # Detecciones
    vague_hits      = [p for p in VAGUE_PHRASES if p in text_lower]
    step_hits       = [v for v in STEP_VERBS if v in text_lower]
    absolute_hits   = detect_absolute_hits(text_lower)
    has_escalation  = detect_escalation(text_lower)
    anti_escalation = detect_anti_escalation(text_lower)
    loop_risk_level, loop_count, loop_hits = detect_loop_risk(text_lower)
    fin_blocker_hits = detect_fin_blockers(text_lower)

    cov_hits = [s for s in COVERAGE_SIGNALS if s in text_lower]
    undefined_terms = [t for t in TECHNICAL_TERMS if t in text_lower]
    has_definitions = any(w in text_lower for w in ["significa", "es decir", "se refiere", "corresponde a", "definido como"])
    english_terms = [w for w in words if _re.match(r'^[a-zA-Z]{4,}$', w) and w.lower() not in [
        "cufe", "dian", "login", "error", "click", "api", "token", "json", "xml", "nit",
    ]]
    foreign_ratio = len(english_terms) / max(word_count, 1)

    step_count = len(_re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+\S', text))
    ambiguous_steps = []
    if has_numbered_steps:
        for st in _re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+(.+)', text):
            if len(st.split()) < 3:
                ambiguous_steps.append(st.strip())

    sentence_words = [frozenset(s.lower().split()) for s in sentences if len(s.split()) >= 5]
    repetitions = 0
    seen_sents = []
    for sw in sentence_words:
        for prev in seen_sents:
            if sw and prev and len(sw & prev) / max(len(sw), len(prev)) >= 0.80:
                repetitions += 1
                break
        seen_sents.append(sw)

    uses_tu    = bool(_re.search(r'\b(haz|selecciona|entra|ve a|escribe|abre)\b', text_lower))
    uses_usted = bool(_re.search(r'\b(haga|seleccione|entre|vaya|escriba|abra)\b', text_lower))

    risky_hits = [r for r in RISKY_ACTIONS if r in text_lower]
    has_warning = any(w in text_lower for w in ["advertencia", "precaución", "importante", "nota", "atención"])

    date_patterns = [
        _re.compile(r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}\b', _re.I),
        _re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
        _re.compile(r'\bversión\s+\d+[\.\d]*\b', _re.I),
        _re.compile(r'\bv\d+[\.\d]+\b'),
    ]
    date_refs = []
    for dp in date_patterns:
        date_refs.extend(dp.findall(text))

    esc_cond = any(c in text_lower for c in [
        "si el problema persiste", "si no se resuelve", "si el error continúa",
        "si ninguno de los pasos",
    ])

    # ── Criterios (12) ────────────────────────────────────────────────────────

    clarity = 12
    if vague_hits:     clarity -= min(len(vague_hits) * 2, 8)
    if word_count < 20: clarity -= 5
    clarity = max(clarity, 0)

    structure = 10
    if not has_numbered_steps: structure -= 4
    if not has_sections:       structure -= 3
    if not has_bullets and not has_numbered_steps: structure -= 3
    structure = max(structure, 0)

    steps_score = 12
    if not step_hits:                              steps_score -= 7
    if step_count == 0 and word_count > 60:        steps_score -= 3
    if ambiguous_steps: steps_score -= min(len(ambiguous_steps) * 2, 4)
    steps_score = max(steps_score, 0)

    coverage = 8
    if len(cov_hits) < 2:   coverage -= 5
    elif len(cov_hits) < 4: coverage -= 2
    coverage = max(coverage, 0)

    ambiguity = 10
    if absolute_hits: ambiguity -= min(len(absolute_hits) * 3, 8)
    # internal contradictions
    contradictions = [
        ("activar", "desactivar"), ("habilitar", "deshabilitar"),
        ("guardar", "no guardar"), ("cerrar", "no cerrar"),
        ("contactar soporte", "no contactar soporte"),
    ]
    for ca, cb in contradictions:
        if ca in text_lower and cb in text_lower:
            ambiguity -= 2
    ambiguity = max(ambiguity, 0)

    length_score = 8
    if word_count < 30:    length_score -= 6
    elif word_count < 60:  length_score -= 3
    elif word_count > 800: length_score -= 4
    elif word_count > 400: length_score -= 2
    length_score = max(length_score, 0)

    consistency = 8
    if repetitions > 0: consistency -= min(repetitions * 3, 6)
    if uses_tu and uses_usted: consistency -= 3
    consistency = max(consistency, 0)

    terminology = 8
    if undefined_terms and not has_definitions:
        terminology -= min(len(undefined_terms) * 2, 6)
    if foreign_ratio > 0.15: terminology -= 2
    terminology = max(terminology, 0)

    fin_usability = 10
    if not any(p in text_lower for p in FIN_POSITIVE_SIGNALS): fin_usability -= 5
    if fin_blocker_hits: fin_usability -= min(len(fin_blocker_hits) * 3, 6)
    fin_usability = max(fin_usability, 0)

    escalation_score = 8
    if anti_escalation:
        escalation_score -= 7
    elif has_escalation:
        if not esc_cond: escalation_score -= 4
    else:
        escalation_score -= 5
    escalation_score = max(escalation_score, 0)

    maintainability = 7
    if date_refs:      maintainability -= 3
    if word_count > 400: maintainability -= 2
    maintainability = max(maintainability, 0)

    operational_risk_score = 7
    if risky_hits: operational_risk_score -= min(len(risky_hits) * 2, 5)
    operational_risk_score = max(operational_risk_score, 0)

    _raw_total = max(0, min(100,
        clarity + structure + steps_score + coverage + ambiguity
        + length_score + consistency + terminology + fin_usability
        + escalation_score + maintainability + operational_risk_score
    ))

    # ── KDE bloqueadores ──────────────────────────────────────────────────────

    kde_blocker_flags = []
    if loop_risk_level == "CRÍTICO":
        kde_blocker_flags.append("loop instruccional CRÍTICO")
    if anti_escalation:
        kde_blocker_flags.append("regla que prohíbe el escalamiento")
    has_kde_blocker = bool(kde_blocker_flags)

    # ── KDE Health ────────────────────────────────────────────────────────────

    kde_health = _raw_total
    if absolute_hits:
        kde_health = max(0, kde_health - min(len(absolute_hits) * 2, 8))
    if loop_risk_level == "ALTO":
        kde_health = max(0, kde_health - 8)
    elif loop_risk_level == "CRÍTICO":
        kde_health = max(0, kde_health - 15)
    if ambiguous_steps:
        kde_health = max(0, kde_health - min(len(ambiguous_steps) * 2, 6))
    if has_kde_blocker:
        kde_health = min(kde_health, KDE_HARD_CAP_BLOCKER)
    kde_health = max(0, min(100, kde_health))

    # ── KDE Clasificación ─────────────────────────────────────────────────────

    if kde_health >= 90:
        classification, class_emoji = "Excelente", "✅"
    elif kde_health >= 78:
        classification, class_emoji = "Muy Bueno", "🟢"
    elif kde_health >= 65:
        classification, class_emoji = "Bueno", "🔵"
    elif kde_health >= 50:
        classification, class_emoji = "Aceptable", "⚠️"
    elif kde_health >= 35:
        classification, class_emoji = "Deficiente", "🔶"
    else:
        classification, class_emoji = "Crítico", "🔴"

    # ── KDE Risk ─────────────────────────────────────────────────────────────

    kde_risk = risk_level_from_health(kde_health, has_kde_blocker)

    # ── KDE Resolution Capability ─────────────────────────────────────────────

    _rc_clarity    = clarity          / 12.0
    _rc_steps      = steps_score      / 12.0
    _rc_coverage   = coverage         / 8.0
    _rc_ambiguity  = ambiguity        / 10.0
    _rc_fin        = fin_usability    / 10.0
    _rc_escalation = escalation_score / 8.0
    kde_resolution = round(
        (_rc_clarity * 0.20 + _rc_steps * 0.25 + _rc_coverage * 0.15
         + _rc_ambiguity * 0.15 + _rc_fin * 0.15 + _rc_escalation * 0.10) * 100
    )
    if loop_risk_level == "CRÍTICO":
        kde_resolution = max(0, kde_resolution - 30)
    elif loop_risk_level == "ALTO":
        kde_resolution = max(0, kde_resolution - 15)
    elif loop_risk_level == "MEDIO":
        kde_resolution = max(0, kde_resolution - 5)
    if fin_blocker_hits:
        kde_resolution = max(0, kde_resolution - min(len(fin_blocker_hits) * 10, 20))
    if ambiguous_steps:
        kde_resolution = max(0, kde_resolution - min(len(ambiguous_steps) * 3, 10))
    if has_kde_blocker:
        kde_resolution = min(kde_resolution, KDE_HARD_CAP_RESOLUTION)
    kde_resolution = min(100, kde_resolution)

    # ── KDE Automation Readiness ──────────────────────────────────────────────

    automation_readiness, automation_emoji, automation_justif = compute_automation_readiness(
        kde_health, has_kde_blocker, kde_blocker_flags, loop_risk_level,
        loop_count, absolute_hits, has_escalation
    )

    # ── KDE Deploy Decision ───────────────────────────────────────────────────

    deploy_decision, deploy_emoji, deploy_motivo = compute_deploy_decision(
        kde_health, has_kde_blocker, kde_blocker_flags, classification
    )

    # ── Factores de resolución ────────────────────────────────────────────────

    res_factors = []
    if _rc_clarity < 0.6:    res_factors.append("claridad insuficiente")
    if _rc_steps < 0.6:      res_factors.append("pasos incompletos o sin verbos de acción")
    if _rc_coverage < 0.6:   res_factors.append("cobertura temática parcial")
    if _rc_ambiguity < 0.6:  res_factors.append("ambigüedad alta o términos absolutos")
    if _rc_fin < 0.6:        res_factors.append("señales de guía para FIN insuficientes")
    if _rc_escalation < 0.6: res_factors.append("criterio de escalamiento ausente o bloqueado")
    if loop_risk_level in ("ALTO", "CRÍTICO"): res_factors.append(f"riesgo de loop {loop_risk_level.lower()}")
    if fin_blocker_hits:     res_factors.append("acciones no ejecutables por FIN presentes")
    if anti_escalation:      res_factors.append("regla que prohíbe el escalamiento")

    return {
        # Identidad
        "title":               title,
        "word_count":          word_count,
        # Señales brutas
        "vague_hits":          vague_hits,
        "step_hits":           step_hits,
        "absolute_hits":       absolute_hits,
        "has_escalation":      has_escalation,
        "anti_escalation":     anti_escalation,
        "loop_risk_level":     loop_risk_level,
        "loop_count":          loop_count,
        "loop_hits":           loop_hits,
        "fin_blocker_hits":    fin_blocker_hits,
        "ambiguous_steps":     ambiguous_steps,
        "risky_hits":          risky_hits,
        "date_refs":           date_refs,
        "has_numbered_steps":  has_numbered_steps,
        "has_sections":        has_sections,
        "has_bullets":         has_bullets,
        "has_definitions":     has_definitions,
        "undefined_terms":     undefined_terms,
        "has_warning":         has_warning,
        "repetitions":         repetitions,
        "cov_hits":            cov_hits,
        # Criterios
        "clarity":             clarity,
        "structure":           structure,
        "steps_score":         steps_score,
        "coverage":            coverage,
        "ambiguity":           ambiguity,
        "length_score":        length_score,
        "consistency":         consistency,
        "terminology":         terminology,
        "fin_usability":       fin_usability,
        "escalation_score":    escalation_score,
        "maintainability":     maintainability,
        "operational_risk_score": operational_risk_score,
        "_raw_total":          _raw_total,
        # KDE outputs
        "kde_blocker_flags":   kde_blocker_flags,
        "has_kde_blocker":     has_kde_blocker,
        "kde_health":          kde_health,
        "classification":      classification,
        "class_emoji":         class_emoji,
        "kde_risk":            kde_risk,
        "kde_resolution":      kde_resolution,
        "res_factors":         res_factors,
        "automation_readiness": automation_readiness,
        "automation_emoji":    automation_emoji,
        "automation_justif":   automation_justif,
        "deploy_decision":     deploy_decision,
        "deploy_emoji":        deploy_emoji,
        "deploy_motivo":       deploy_motivo,
        # Aliases (compatibilidad backward)
        "total":               kde_health,
        "anti_escalation_rule": anti_escalation,
        "kde_blockers":        kde_blocker_flags,
        "deploy":              deploy_decision,
        "words_set":           word_set(text),
        "text_lower":          text.lower(),
        # Proporciones para resolución
        "_rc_clarity":         _rc_clarity,
        "_rc_steps":           _rc_steps,
        "_rc_coverage":        _rc_coverage,
        "_rc_ambiguity":       _rc_ambiguity,
        "_rc_fin":             _rc_fin,
        "_rc_escalation":      _rc_escalation,
    }


# ════════════════════════════════════════════════════════════════════════════ #
# KDE — Análisis rápido de artículo (repository_review / knowledge_review)    #
# ════════════════════════════════════════════════════════════════════════════ #

def kde_score_article_fast(text: str) -> dict:
    """
    Versión ligera del KDE para análisis masivo en repository_review.
    Usa keywords simples en lugar del análisis de 12 criterios completo.
    """
    t = text.lower()
    words = word_set(text)

    loop_risk, _, _ = detect_loop_risk(t, use_repo_patterns=True)
    anti_escalation = detect_anti_escalation(t, use_repo_patterns=True)
    absolute_hits   = detect_absolute_hits(t, repo_mode=True)
    has_resolution  = any(k in t for k in [
        "resuelve", "solución", "resolver", "resultado", "cierra", "finaliza",
        "concluye", "éxito", "completado", "solucionado", "resuelto",
    ])
    has_steps = any(k in t for k in ["paso", "step", "primero", "segundo", "1.", "2.", "a)", "b)"])
    has_escalation  = detect_escalation_repo(t)
    has_objective   = any(k in t for k in [
        "objetivo", "propósito", "finalidad", "para qué", "cuando aplica",
        "cuándo aplica", "este artículo",
    ])
    wc = len(text.split())

    _rt = 100
    if not has_resolution:       _rt -= 15
    if not has_steps:            _rt -= 10
    if not has_escalation:       _rt -= 8
    if not has_objective:        _rt -= 8
    if wc < 30:                  _rt -= 12
    elif wc > 600:               _rt -= 6
    if absolute_hits:            _rt = max(0, _rt - min(len(absolute_hits) * 2, 8))
    if loop_risk == "ALTO":      _rt = max(0, _rt - 8)
    elif loop_risk == "CRÍTICO": _rt = max(0, _rt - 15)

    has_blocker = loop_risk == "CRÍTICO" or anti_escalation
    kde_health  = min(_rt, KDE_HARD_CAP_BLOCKER) if has_blocker else _rt
    kde_health  = max(0, min(100, kde_health))
    risk        = risk_level_from_health(kde_health, has_blocker)

    _esc_ok  = has_escalation and not anti_escalation
    res_rate = 90 if (has_resolution and _esc_ok) else (70 if has_resolution else 40)
    if has_blocker:
        res_rate = min(res_rate, KDE_HARD_CAP_RESOLUTION)

    return {
        "health":          kde_health,
        "risk":            risk,
        "blocked":         has_blocker,
        "loop_risk":       loop_risk,
        "anti_escalation": anti_escalation,
        "resolution_rate": res_rate,
        "words":           words,
        "has_escalation":  has_escalation,
        "has_resolution":  has_resolution,
    }


# ════════════════════════════════════════════════════════════════════════════ #
# KDE — Análisis rápido de guideline                                          #
# ════════════════════════════════════════════════════════════════════════════ #

def kde_score_guideline_fast(text: str) -> dict:
    """
    Análisis rápido de una guideline para repository_review / architect_review.
    """
    t = text.lower()
    words = word_set(text)

    anti_escalation = detect_anti_escalation(t, use_repo_patterns=True)
    has_escalation  = detect_escalation_repo(t)
    absolute_hits   = detect_absolute_hits(t, repo_mode=True)
    has_trigger     = any(k in t for k in ["cuando", "si el", "si la", "en caso de", "al detectar"])
    has_action      = any(k in t for k in ["responde", "indica", "informa", "ejecuta", "deriva"])

    _rt = 100
    if not has_trigger: _rt -= 12
    if not has_action:  _rt -= 12
    if absolute_hits:   _rt = max(0, _rt - min(len(absolute_hits) * 2, 8))
    if anti_escalation: _rt = min(_rt, KDE_HARD_CAP_BLOCKER)

    blocked = anti_escalation or _rt < 50

    return {
        "health":          _rt,
        "blocked":         blocked,
        "anti_escalation": anti_escalation,
        "words":           words,
        "has_escalation":  has_escalation,
    }


# ════════════════════════════════════════════════════════════════════════════ #
# MÉTRICAS DERIVADAS                                                           #
# ════════════════════════════════════════════════════════════════════════════ #

def risk_level_from_health(kde_health: int, has_blocker: bool = False) -> str:
    """Nivel de riesgo: BAJO / MEDIO / ALTO — derivado exclusivamente del health."""
    if has_blocker or kde_health < 50:
        return "ALTO"
    if kde_health < 78:
        return "MEDIO"
    return "BAJO"


def compute_automation_readiness(
    kde_health: int,
    has_kde_blocker: bool,
    kde_blocker_flags: list,
    loop_risk_level: str,
    loop_count: int,
    absolute_hits: list,
    has_escalation: bool,
) -> tuple:
    """
    Devuelve (readiness_label, emoji, justificación).
    Reglas: bloqueador → máx Baja. Loop ALTO → máx Media. Absolutos sin esc → Baja.
    """
    if has_kde_blocker:
        readiness = "Baja" if kde_health >= 40 else "No apto"
        emoji     = "🔶"   if kde_health >= 40 else "🔴"
        justif    = f"Bloqueadores activos: {', '.join(kde_blocker_flags)}. FIN no puede usar este artículo de forma autónoma hasta resolverlos."
    elif loop_risk_level == "ALTO":
        readiness = "Media" if kde_health >= 55 else "Baja"
        emoji     = "🔵"    if kde_health >= 55 else "🔶"
        justif    = f"Loop risk ALTO ({loop_count} patrón(es) detectado(s)). FIN requiere supervisión activa para evitar ciclos repetitivos."
    elif absolute_hits and not has_escalation:
        readiness = "Baja"
        emoji     = "🔶"
        justif    = f"Términos absolutos ({', '.join(absolute_hits)}) combinados con ausencia de criterio de escalamiento limitan el uso autónomo de FIN."
    elif kde_health >= 78 and loop_risk_level == "BAJO" and has_escalation and not absolute_hits:
        readiness = "Excelente"
        emoji     = "✅"
        justif    = "El artículo cumple todos los criterios para uso autónomo por FIN: health score alto, sin loop risk y escalamiento definido."
    elif kde_health >= 65 and loop_risk_level in ("BAJO", "MEDIO"):
        readiness = "Alta"
        emoji     = "🟢"
        justif    = "El artículo es apto para automatización con ajustes menores. Aplicar recomendaciones antes de activarlo en producción."
    elif kde_health >= 50:
        readiness = "Media"
        emoji     = "🔵"
        justif    = "FIN puede usar este artículo con supervisión activa. Se recomienda revisión humana de los casos no resueltos en el primer intento."
    elif kde_health >= 35:
        readiness = "Baja"
        emoji     = "🔶"
        justif    = "El artículo presenta riesgos significativos para uso autónomo. Requiere corrección de problemas detectados."
    else:
        readiness = "No apto"
        emoji     = "🔴"
        justif    = "El artículo no debe usarse como fuente de resolución autónoma. Requiere reescritura completa."
    return readiness, emoji, justif


def compute_deploy_decision(
    kde_health: int,
    has_kde_blocker: bool,
    kde_blocker_flags: list,
    classification: str,
) -> tuple:
    """
    Devuelve (decision_label, emoji, motivo).
    Reglas: bloqueador → BLOQUEADO. health<50 → NO LISTO. health<78 → CON RECOMENDACIONES.
    """
    if has_kde_blocker:
        decision = "BLOQUEADO"
        emoji    = "🚫"
        motivo   = ("Bloqueadores críticos que impiden cualquier despliegue: "
                    + " y ".join(kde_blocker_flags)
                    + ". Corrige estos problemas antes de considerar el uso por FIN.")
    elif kde_health < 50:
        decision = "NO LISTO"
        emoji    = "🔴"
        motivo   = (f"Health score insuficiente ({kde_health}/100). El artículo no cumple el mínimo de calidad para resolución autónoma. Aplica las recomendaciones y re-audita.")
    elif kde_health < 78:
        decision = "LISTO CON RECOMENDACIONES"
        emoji    = "⚠️"
        motivo   = (f"El artículo puede desplegarse con precaución (score {kde_health}/100). Aplica las optimizaciones y monitorea las primeras interacciones de FIN.")
    else:
        decision = "LISTO"
        emoji    = "✅"
        motivo   = (f"El artículo cumple los estándares para despliegue autónomo (score {kde_health}/100 — {classification}). FIN puede utilizarlo sin supervisión activa.")
    return decision, emoji, motivo


# ════════════════════════════════════════════════════════════════════════════ #
# KNOWLEDGE DEBT                                                               #
# ════════════════════════════════════════════════════════════════════════════ #

def compute_knowledge_debt(
    total_art_blocked: int,
    total_g_conflicts: int,
    total_art_dups: int,
    missing_cats_count: int,
    total_g_blocked: int,
    total_art_critical: int,
) -> int:
    """
    Calcula Knowledge Debt score 0-100.
    Fórmula: raw / 200 * 100, capped a 100.
    """
    _debt_raw = (
        total_art_blocked   * 15
        + total_g_conflicts * 10
        + total_art_dups    * 8
        + missing_cats_count * 12
        + total_g_blocked   * 8
        + max(0, total_art_critical - total_art_blocked) * 5
    )
    return min(100, round(_debt_raw / 200 * 100)), _debt_raw


def debt_label_emoji(knowledge_debt: int) -> tuple:
    """Devuelve (label, emoji) para un score de Knowledge Debt."""
    if knowledge_debt >= 70:
        return "CRÍTICO", "🔴"
    if knowledge_debt >= 45:
        return "ALTO", "🟠"
    if knowledge_debt >= 20:
        return "MEDIO", "🟡"
    return "BAJO", "🟢"


# ════════════════════════════════════════════════════════════════════════════ #
# COBERTURA                                                                    #
# ════════════════════════════════════════════════════════════════════════════ #

def compute_coverage(all_text: str) -> tuple:
    """
    Devuelve (covered_cats, missing_cats) basado en TOPIC_CATEGORIES.
    all_text debe estar en minúsculas.
    """
    covered = [cat for cat, kws in TOPIC_CATEGORIES.items() if any(k in all_text for k in kws)]
    missing = [cat for cat in TOPIC_CATEGORIES if cat not in covered]
    return covered, missing


# ════════════════════════════════════════════════════════════════════════════ #
# SEMÁFORO EJECUTIVO                                                           #
# ════════════════════════════════════════════════════════════════════════════ #

def semaforo(value: int, thresholds: tuple = (70, 85)) -> tuple:
    """
    Devuelve (emoji, label) según umbrales.
    thresholds = (warning_threshold, ok_threshold)
    """
    if value >= thresholds[1]:
        return "🟢", "Excelente"
    if value >= thresholds[0]:
        return "🟡", "Atención"
    return "🔴", "Crítico"


def global_status_from_health(global_health: int, prod_blocked_count: int, prod_high_risk: int) -> tuple:
    """Devuelve (status_label, emoji) para el estado global del repositorio."""
    if prod_blocked_count > 0 or global_health < 50:
        return "BLOQUEADO", "🔴"
    if global_health < 70 or prod_high_risk > 0:
        return "EN REVISIÓN", "🟠"
    if global_health < 85:
        return "ACEPTABLE", "🟡"
    return "SALUDABLE", "🟢"


def deployment_readiness(
    prod_blocked_count: int,
    total_a_blocked: int,
    total_g_blocked: int,
    global_health: int,
    knowledge_debt: int,
    prod_high_risk: int,
) -> tuple:
    """Devuelve (readiness_label, emoji) para la decisión ejecutiva de despliegue."""
    if prod_blocked_count > 0 or total_a_blocked + total_g_blocked > 0:
        return "NOT READY", "🔴"
    if prod_high_risk > 0 or knowledge_debt >= 45:
        return "READY WITH RECOMMENDATIONS", "🟡"
    if global_health >= 85 and knowledge_debt < 20:
        return "READY", "🟢"
    return "READY WITH RECOMMENDATIONS", "🟡"


# ════════════════════════════════════════════════════════════════════════════ #
# ROI Y PRIORIZACIÓN                                                           #
# ════════════════════════════════════════════════════════════════════════════ #

def compute_roi(impact: int, effort: int) -> float:
    """ROI = impact / effort, redondeado a 2 decimales."""
    return round(impact / effort, 2)


def rank_improvements(improvements: list) -> list:
    """Ordena por ROI desc, luego impact desc. Asigna prioridad numérica."""
    ranked = sorted(improvements, key=lambda x: (-x["roi"], -x["impact"]))
    for i, imp in enumerate(ranked, 1):
        imp["priority"] = i
    return ranked


# ════════════════════════════════════════════════════════════════════════════ #
# EXTRACCIÓN DE MÉTRICAS DESDE TEXTO                                          #
# (para recommend_improvements y fin_dashboard)                               #
# ════════════════════════════════════════════════════════════════════════════ #

def extract_int(pattern: str, text: str, default: int = 0) -> int:
    """Extrae el primer entero que coincide con el patrón regex en el texto."""
    m = _re.search(pattern, text, _re.IGNORECASE)
    return int(m.group(1)) if m else default


def extract_metrics_from_reports(
    repository_review_text: str = "",
    knowledge_review_text: str = "",
    architect_review_text: str = "",
) -> dict:
    """
    Extrae métricas de los textos de salida de las herramientas de análisis.
    Centraliza todos los patrones de extracción usados en recommend_improvements
    y fin_dashboard.
    """
    rrl = repository_review_text.lower()
    krl = knowledge_review_text.lower()
    arl = architect_review_text.lower()

    global_health   = extract_int(r"salud global\s*[:\|]+\s*(\d+)", rrl, 75)
    knowledge_debt  = extract_int(r"knowledge debt\s*[:\|]+\s*(\d+)", rrl, 30)
    prod_blocked    = extract_int(r"productos bloqueados\s*[:\|]+\s*(\d+)", rrl, 0)
    prod_high_risk  = extract_int(r"productos en riesgo alto\s*[:\|]+\s*(\d+)", rrl, 0)
    total_a_blocked = extract_int(r"artículos\s+bloqueados\s*[:\|]+\s*(\d+)", rrl, 0)
    total_g_blocked = extract_int(r"guidelines\s+bloqueadas\s*[:\|]+\s*(\d+)", rrl, 0)
    total_g_conflicts = extract_int(r"conflictos\s+guidelines\s*[:\|]+\s*(\d+)", rrl, 0)
    total_a_dups    = extract_int(r"artículos duplicados\s*[:\|]+\s*(\d+)", rrl, 0)
    coverage_pct    = extract_int(r"cobertura\s+(?:global|temática)\s*[:\|]+\s*(\d+)%", rrl, 70)
    total_articles  = extract_int(r"artículos totales\s*[:\|]+\s*(\d+)", rrl, 0)
    total_guidelines = extract_int(r"guidelines totales\s*[:\|]+\s*(\d+)", rrl, 0)

    m_mc = _re.search(r"faltantes\s*:\s*([^\n]+)", rrl)
    missing_cats_str = m_mc.group(1).strip() if m_mc else ""
    missing_cats_count = len([
        c for c in missing_cats_str.split(",")
        if c.strip() and "ninguna" not in c.strip()
    ])

    # Enriquece desde knowledge_review si no hay repository_review
    if not repository_review_text:
        total_a_blocked = extract_int(r"bloqueados?\s*[:\|]+\s*(\d+)", krl, total_a_blocked)
        knowledge_debt  = max(knowledge_debt, extract_int(r"artículos.*?crítico", krl, 0) * 15)

    # Enriquece desde architect_review
    ar_blocked_g = extract_int(r"guidelines.*?bloqueadas?\s*[:\|]+\s*(\d+)", arl, total_g_blocked)
    total_g_blocked = max(total_g_blocked, ar_blocked_g)

    return {
        "global_health":      global_health,
        "knowledge_debt":     knowledge_debt,
        "prod_blocked":       prod_blocked,
        "prod_high_risk":     prod_high_risk,
        "total_a_blocked":    total_a_blocked,
        "total_g_blocked":    total_g_blocked,
        "total_g_conflicts":  total_g_conflicts,
        "total_a_dups":       total_a_dups,
        "coverage_pct":       coverage_pct,
        "missing_cats_str":   missing_cats_str,
        "missing_cats_count": missing_cats_count,
        "total_articles":     total_articles,
        "total_guidelines":   total_guidelines,
        "has_rr":             bool(repository_review_text.strip()),
        "has_kr":             bool(knowledge_review_text.strip()),
        "has_ar":             bool(architect_review_text.strip()),
    }
