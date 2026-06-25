from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn
import os

import decision_engine as _de

# Inicializar servidor MCP
mcp = FastMCP("fin-architect-mcp")


@mcp.tool()
async def audit_guideline(
    guideline: str,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Audita una guideline de FIN para detectar ambigüedades,
    conflictos o mejoras recomendadas.
    """

    issues = []
    suggestions = []

    if len(guideline.strip()) < 20:
        issues.append(
            "La guideline es demasiado corta para ser accionable."
        )

    for word in _de.ABSOLUTE_TERMS:
        if word in guideline.lower():
            issues.append(
                f"Término absoluto detectado: '{word}'. Considera añadir condiciones."
            )

    if "escalar" in guideline.lower() and "cuando" not in guideline.lower():
        issues.append(
            "Se menciona escalación sin condición 'cuando'. FIN puede escalar incorrectamente."
        )

    if len(guideline) > 500:
        suggestions.append(
            "Guideline extensa. Considera dividirla en reglas más atómicas."
        )

    if product != "general":
        suggestions.append(
            "Verifica que esta guideline no colisione con reglas globales de otros productos."
        )

    result_parts = [
        f"**Auditoría de Guideline — Producto: {product.upper()}**\n"
    ]

    result_parts.append(
        f"**Guideline analizada:**\n> {guideline}\n"
    )

    if context:
        result_parts.append(
            f"**Contexto:** {context}\n"
        )

    if issues:
        result_parts.append("**⚠️ Problemas detectados:**")
        for issue in issues:
            result_parts.append(f"- {issue}")
    else:
        result_parts.append(
            "**✅ Sin problemas críticos detectados.**"
        )

    if suggestions:
        result_parts.append("\n**💡 Sugerencias:**")
        for suggestion in suggestions:
            result_parts.append(f"- {suggestion}")

    result_parts.append(
        "\n**Recomendación:** Valida esta guideline contra conversaciones reales en Intercom antes de publicar."
    )

    return "\n".join(result_parts)


@mcp.tool()
async def optimize_guideline(
    guideline: str
) -> str:

    text = guideline.lower()

    findings = []
    risk_score = 0

    # Detectar términos absolutos
    absolute_words = _de.GUIDELINE_ABSOLUTE_WORDS

    for word in absolute_words:
        if word in text:
            findings.append(
                f"Término absoluto detectado: '{word}'."
            )
            risk_score += 2

    # Detectar ambigüedad
    ambiguous_words = [
        "error",
        "problema",
        "consulta",
        "caso",
        "solicitud"
    ]

    for word in ambiguous_words:
        if word in text:
            findings.append(
                f"Término ambiguo detectado: '{word}'. Requiere mayor precisión."
            )
            risk_score += 1

    # Detectar escalamiento
    escalation_words = _de.GUIDELINE_ESCALATION_WORDS

    escalation_detected = False

    for word in escalation_words:
        if word in text:
            escalation_detected = True

    if escalation_detected:

        findings.append(
            "La pauta contiene instrucciones de escalamiento."
        )

        risk_score += 2

        if (
            "cuando" not in text
            and "si " not in text
            and "solo si" not in text
        ):
            findings.append(
                "No se identificaron criterios claros para escalar."
            )

            risk_score += 3

    # Detectar frustración
    if (
        "frustración" in text
        or "frustrado" in text
        or "molesto" in text
        or "enojado" in text
    ):

        findings.append(
            "La pauta involucra emociones del cliente. Se recomienda intentar resolver antes de escalar."
        )

        risk_score += 1

    # Calcular riesgo
    risk = _de.guideline_risk_level(risk_score)

    # Generar versión optimizada
    optimized = guideline

    replacements = {
        "Siempre": "Escala únicamente cuando se cumplan los criterios definidos",
        "siempre": "únicamente cuando se cumplan los criterios definidos",
        "Nunca": "Excepto en los casos definidos",
        "nunca": "excepto en los casos definidos",
        "cualquier": "las situaciones que cumplan los criterios definidos"
    }

    for old, new in replacements.items():
        optimized = optimized.replace(old, new)

    recommendation = """
Escala únicamente cuando exista bloqueo operativo, no haya solución documentada, el cliente haya seguido los pasos sugeridos sin éxito o solicite explícitamente atención humana. Prioriza la resolución autónoma antes de transferir el caso.
"""

    return f"""
GUIDELINE ORIGINAL

{guideline}

PROBLEMAS DETECTADOS

{chr(10).join('- ' + f for f in findings) if findings else '- No se detectaron problemas relevantes'}

NIVEL DE RIESGO

{risk}

VERSIÓN OPTIMIZADA

{optimized}

RECOMENDACIÓN FIN

{recommendation}

JUSTIFICACIÓN

- Reduce ambigüedad.
- Evita escalamientos innecesarios.
- Define criterios más objetivos.
- Favorece la resolución autónoma.
"""


@mcp.tool()
async def classify_guideline(
    guideline: str,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Clasifica una guideline de FIN asignando categoría principal,
    subcategoría, nivel de riesgo, prioridad y justificación.
    """

    text = guideline.lower()

    # Determinar categoría principal
    if any(w in text for w in ["escalar", "transferir", "agente humano", "agente"]):
        categoria = "Escalamiento"
    elif any(w in text for w in ["factura", "cobro", "pago", "cargo", "reembolso"]):
        categoria = "Facturación"
    elif any(w in text for w in ["contraseña", "acceso", "usuario", "cuenta", "sesión"]):
        categoria = "Acceso y Seguridad"
    elif any(w in text for w in ["error", "fallo", "no funciona", "problema técnico"]):
        categoria = "Soporte Técnico"
    elif any(w in text for w in ["onboarding", "bienvenida", "registro", "activación"]):
        categoria = "Onboarding"
    else:
        categoria = "General"

    # Determinar subcategoría
    if "frustración" in text or "frustrado" in text or "molesto" in text or "enojado" in text:
        subcategoria = "Gestión Emocional"
    elif "cuando" in text or "si " in text or "solo si" in text:
        subcategoria = "Flujo Condicional"
    elif any(w in text for w in ["siempre", "nunca", "todos", "ninguno"]):
        subcategoria = "Regla Absoluta"
    elif len(guideline) > 300:
        subcategoria = "Política Extensa"
    else:
        subcategoria = "Instrucción Simple"

    # Calcular nivel de riesgo
    risk_score = 0

    absolute_words = _de.GUIDELINE_ABSOLUTE_WORDS
    for word in absolute_words:
        if word in text:
            risk_score += 2

    if "escalar" in text or "transferir" in text:
        risk_score += 2
        if "cuando" not in text and "si " not in text:
            risk_score += 3

    if "frustración" in text or "molesto" in text or "enojado" in text:
        risk_score += 1

    if len(guideline.strip()) < 20:
        risk_score += 2

    nivel_riesgo = _de.guideline_risk_level(risk_score)

    # Determinar prioridad
    if nivel_riesgo == "ALTO" or categoria == "Escalamiento":
        prioridad = "URGENTE"
    elif nivel_riesgo == "MEDIO" or categoria in ["Facturación", "Acceso y Seguridad"]:
        prioridad = "ALTA"
    elif nivel_riesgo == "BAJO" and subcategoria == "Instrucción Simple":
        prioridad = "NORMAL"
    else:
        prioridad = "MEDIA"

    # Construir justificación
    justificacion_items = []

    if nivel_riesgo == "ALTO":
        justificacion_items.append(
            "Riesgo alto por presencia de términos absolutos o escalamiento sin criterios definidos."
        )
    elif nivel_riesgo == "MEDIO":
        justificacion_items.append(
            "Riesgo medio por ambigüedad o condiciones de escalamiento parcialmente definidas."
        )
    else:
        justificacion_items.append(
            "Riesgo bajo. La guideline es clara y no contiene instrucciones de alto impacto."
        )

    if subcategoria == "Regla Absoluta":
        justificacion_items.append(
            "Contiene términos absolutos que pueden generar comportamientos no deseados en FIN."
        )

    if subcategoria == "Gestión Emocional":
        justificacion_items.append(
            "Involucra emociones del cliente, lo que requiere manejo cuidadoso antes de escalar."
        )

    if prioridad == "URGENTE":
        justificacion_items.append(
            "Prioridad urgente: debe revisarse antes de desplegar en producción."
        )

    if product != "general":
        justificacion_items.append(
            f"Clasificada en contexto del producto '{product}'. Verificar colisiones con reglas globales."
        )

    result_parts = [
        f"**Clasificación de Guideline — Producto: {product.upper()}**\n"
    ]

    result_parts.append(
        f"**Guideline analizada:**\n> {guideline}\n"
    )

    if context:
        result_parts.append(
            f"**Contexto:** {context}\n"
        )

    result_parts.append(f"**Categoría principal:** {categoria}")
    result_parts.append(f"**Subcategoría:** {subcategoria}")
    result_parts.append(f"**Nivel de riesgo:** {nivel_riesgo}")
    result_parts.append(f"**Prioridad:** {prioridad}")

    result_parts.append("\n**Justificación:**")
    for item in justificacion_items:
        result_parts.append(f"- {item}")

    result_parts.append(
        "\n**Recomendación:** Usa audit_guideline y optimize_guideline para profundizar en los hallazgos detectados."
    )

    return "\n".join(result_parts)


@mcp.tool()
async def detect_conflicts(
    guidelines: list,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Analiza un conjunto de guidelines de FIN y detecta conflictos entre ellas:
    escalamiento contradictorio, acciones prohibidas vs obligadas, condiciones
    incompatibles, prioridades distintas para el mismo escenario, respuestas
    contradictorias, duplicados y conflictos global vs producto.
    """

    conflicts = []
    severity_score = 0

    texts = [g.lower() for g in guidelines]

    escalation_words = _de.GUIDELINE_ESCALATION_WORDS
    resolve_words = _de.GUIDELINE_RESOLVE_WORDS
    prohibition_words = _de.GUIDELINE_PROHIBITION_WORDS
    obligation_words = _de.GUIDELINE_OBLIGATION_WORDS
    priority_words = _de.GUIDELINE_PRIORITY_WORDS

    escalation_indices = [
        i for i, t in enumerate(texts)
        if any(w in t for w in escalation_words)
    ]

    resolve_indices = [
        i for i, t in enumerate(texts)
        if any(w in t for w in resolve_words)
    ]

    # Conflicto 1: escalar siempre vs resolver primero
    absolute_escalation = [
        i for i in escalation_indices
        if any(w in texts[i] for w in ["siempre", "siempre escalar", "debe escalar"])
        and "cuando" not in texts[i]
        and "si " not in texts[i]
    ]

    conditional_resolve = [
        i for i in resolve_indices
        if "antes" in texts[i] or "primero" in texts[i] or "intentar" in texts[i]
    ]

    for i in absolute_escalation:
        for j in conditional_resolve:
            conflicts.append(
                f"Guideline {i + 1} ordena escalar sin condiciones, "
                f"pero guideline {j + 1} indica intentar resolver antes de escalar."
            )
            severity_score += 4

    # Conflicto 2: acción prohibida vs obligada
    prohibition_indices = [
        i for i, t in enumerate(texts)
        if any(w in t for w in prohibition_words)
    ]

    obligation_indices = [
        i for i, t in enumerate(texts)
        if any(w in t for w in obligation_words)
    ]

    for i in prohibition_indices:
        for j in obligation_indices:
            if i != j:
                conflicts.append(
                    f"Guideline {i + 1} prohíbe una acción que guideline {j + 1} obliga a realizar."
                )
                severity_score += 5

    # Conflicto 3: condiciones incompatibles
    condition_pairs = _de.GUIDELINE_CONDITION_PAIRS

    for word_a, word_b in condition_pairs:
        indices_a = [i for i, t in enumerate(texts) if word_a in t]
        indices_b = [i for i, t in enumerate(texts) if word_b in t]
        for i in indices_a:
            for j in indices_b:
                if i != j:
                    conflicts.append(
                        f"Guideline {i + 1} aplica a '{word_a}' y guideline {j + 1} "
                        f"aplica a '{word_b}': condiciones potencialmente incompatibles o solapadas."
                    )
                    severity_score += 2

    # Conflicto 4: diferentes prioridades para el mismo escenario
    shared_scenarios = _de.GUIDELINE_SHARED_SCENARIOS

    for scenario in shared_scenarios:
        indices_with_scenario = [i for i, t in enumerate(texts) if scenario in t]
        if len(indices_with_scenario) >= 2:
            priorities_found = set()
            for i in indices_with_scenario:
                for pw in priority_words:
                    if pw in texts[i]:
                        priorities_found.add(pw)
            if len(priorities_found) >= 2:
                involved = ", ".join(
                    str(i + 1) for i in indices_with_scenario
                )
                conflicts.append(
                    f"Guidelines {involved} abordan el escenario '{scenario}' "
                    f"con prioridades distintas: {', '.join(priorities_found)}."
                )
                severity_score += 3

    # Conflicto 5: respuestas contradictorias para el mismo caso
    contradiction_pairs = _de.GUIDELINE_CONTRADICTION_PAIRS

    for affirm, deny in contradiction_pairs:
        indices_affirm = [i for i, t in enumerate(texts) if affirm in t]
        indices_deny = [i for i, t in enumerate(texts) if deny in t]
        for i in indices_affirm:
            for j in indices_deny:
                if i != j:
                    conflicts.append(
                        f"Guideline {i + 1} indica '{affirm}', "
                        f"pero guideline {j + 1} indica '{deny}': respuestas contradictorias."
                    )
                    severity_score += 4

    # Conflicto 6: duplicados o casi idénticos
    for i in range(len(guidelines)):
        for j in range(i + 1, len(guidelines)):
            overlap = _de.jaccard(_de.word_set(texts[i]), _de.word_set(texts[j]))
            if overlap >= 0.8:
                conflicts.append(
                    f"Guidelines {i + 1} y {j + 1} son casi idénticas "
                    f"({int(overlap * 100)}% de palabras en común). Posible duplicado."
                )
                severity_score += 2

    # Conflicto 7: regla global vs regla específica del producto
    if product != "general":
        global_indices = [
            i for i, t in enumerate(texts)
            if "todos los productos" in t
            or "en general" in t
            or "por defecto" in t
        ]
        specific_indices = [
            i for i, t in enumerate(texts)
            if product.lower() in t
        ]
        for i in global_indices:
            for j in specific_indices:
                if i != j:
                    conflicts.append(
                        f"Guideline {i + 1} define una regla global que puede colisionar "
                        f"con la regla específica del producto '{product}' en guideline {j + 1}."
                    )
                    severity_score += 3

    # Calcular severidad
    severidad = _de.conflict_severity_level(severity_score)

    # Construir riesgo
    if severidad == "ALTA":
        riesgo = (
            "FIN puede comportarse de forma impredecible: escalar cuando no debe, "
            "contradecir respuestas anteriores o generar experiencias inconsistentes "
            "para el cliente. Requiere resolución inmediata antes de publicar."
        )
    elif severidad == "MEDIA":
        riesgo = (
            "FIN puede generar respuestas inconsistentes en escenarios específicos. "
            "El impacto es limitado pero puede erosionar la confianza del cliente "
            "si los casos conflictivos son frecuentes."
        )
    else:
        riesgo = (
            "Los conflictos detectados tienen bajo impacto operativo. "
            "Se recomienda revisar para mantener coherencia del conjunto de guidelines."
        )

    # Construir recomendaciones
    recommendations = []

    if any("escalar" in c for c in conflicts):
        recommendations.append(
            "Unificar criterios de escalamiento: definir condiciones únicas y explícitas."
        )

    if any("prohíbe" in c or "obliga" in c for c in conflicts):
        recommendations.append(
            "Revisar guidelines contradictorias sobre acciones permitidas y eliminar la redundante."
        )

    if any("condiciones" in c for c in conflicts):
        recommendations.append(
            "Delimitar con precisión los segmentos de cliente o escenarios a los que aplica cada guideline."
        )

    if any("prioridades" in c for c in conflicts):
        recommendations.append(
            "Establecer una jerarquía de prioridades única por escenario y documentarla."
        )

    if any("contradictorias" in c for c in conflicts):
        recommendations.append(
            "Consolidar guidelines que cubren el mismo caso en una sola regla canónica."
        )

    if any("duplicado" in c for c in conflicts):
        recommendations.append(
            "Eliminar o fusionar las guidelines duplicadas para reducir ambigüedad."
        )

    if any("global" in c for c in conflicts):
        recommendations.append(
            f"Documentar explícitamente qué reglas del producto '{product}' "
            "sobreescriben las reglas globales y cuáles las heredan."
        )

    if not recommendations:
        recommendations.append(
            "Continúa monitoreando el conjunto de guidelines a medida que crece."
        )

    # Construir respuesta
    if not conflicts:
        return "✅ No se detectaron conflictos entre las guidelines."

    result_parts = [
        f"**Detección de Conflictos — Producto: {product.upper()}**\n"
    ]

    if context:
        result_parts.append(
            f"**Contexto:** {context}\n"
        )

    result_parts.append(
        f"**Guidelines analizadas:** {len(guidelines)}\n"
    )

    result_parts.append("CONFLICTOS DETECTADOS\n")
    for conflict in conflicts:
        result_parts.append(f"- {conflict}")

    result_parts.append(f"\nSEVERIDAD\n\n{severidad}")

    result_parts.append(f"\nRIESGO\n\n{riesgo}")

    result_parts.append("\nRECOMENDACIÓN\n")
    for rec in recommendations:
        result_parts.append(f"- {rec}")

    return "\n".join(result_parts)


# ══════════════════════════════════════════════════════════════════════════════
# FIN KNOWLEDGE CORE — Fase 2
# ══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def audit_knowledge(
    article: str,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Audita un artículo de Base de Conocimiento y determina qué tan adecuado
    es para ser utilizado por FIN como fuente de resolución autónoma.
    Evalúa claridad, estructura, pasos, cobertura, ambigüedad, longitud,
    consistencia, terminología, usabilidad por FIN, escalamiento,
    mantenibilidad y riesgo operativo. Todas las métricas derivadas
    (Health Score, Risk, Automation Readiness, Resolution Capability,
    Deployment Decision) se calculan desde un único Knowledge Decision
    Engine para garantizar coherencia total entre ellas.
    """

    import re as _re

    text       = article.strip()
    text_lower = text.lower()
    words      = text.split()
    word_count = len(words)
    sentences  = [s.strip() for s in _re.split(r'[.!?]+', text) if s.strip()]
    lines      = [l.strip() for l in text.splitlines() if l.strip()]

    # ════════════════════════════════════════════════════════════════════════ #
    # FASE 1+2 — KNOWLEDGE DECISION ENGINE (KDE)                              #
    # ════════════════════════════════════════════════════════════════════════ #

    kde = _de.kde_score_article(text)

    # ── Extract from KDE
    clarity               = kde["clarity"]
    structure             = kde["structure"]
    steps_score           = kde["steps_score"]
    coverage              = kde["coverage"]
    ambiguity             = kde["ambiguity"]
    length_score          = kde["length_score"]
    consistency           = kde["consistency"]
    terminology           = kde["terminology"]
    fin_usability         = kde["fin_usability"]
    escalation_score      = kde["escalation_score"]
    maintainability       = kde["maintainability"]
    operational_risk_score= kde["operational_risk_score"]
    _raw_total            = kde["_raw_total"]
    kde_health            = kde["kde_health"]
    total                 = kde_health
    classification        = kde["classification"]
    class_emoji           = kde["class_emoji"]
    kde_risk              = kde["kde_risk"]
    kde_resolution        = kde["kde_resolution"]
    automation_readiness  = kde["automation_readiness"]
    automation_emoji      = kde["automation_emoji"]
    automation_justif     = kde["automation_justif"]
    deploy_decision       = kde["deploy_decision"]
    deploy_emoji          = kde["deploy_emoji"]
    deploy_motivo         = kde["deploy_motivo"]
    kde_blocker_flags     = kde["kde_blocker_flags"]
    _has_kde_blocker      = kde["has_kde_blocker"]
    loop_risk_level       = kde["loop_risk_level"]
    loop_hits             = kde["loop_hits"]
    loop_count            = kde["loop_count"]
    anti_escalation_rule  = kde["anti_escalation_rule"]
    has_escalation        = kde["has_escalation"]
    has_numbered_steps    = kde["has_numbered_steps"]
    has_sections          = kde["has_sections"]
    has_bullets           = kde["has_bullets"]
    vague_hits            = kde["vague_hits"]
    absolute_hits         = kde["absolute_hits"]
    step_hits             = kde["step_hits"]
    step_count            = len(_re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+\S', text))
    ambiguous_steps       = kde["ambiguous_steps"]
    cov_hits              = kde["cov_hits"]
    fin_blocker_hits      = kde["fin_blocker_hits"]
    risky_hits            = kde["risky_hits"]
    undefined_terms       = kde["undefined_terms"]
    date_refs             = kde["date_refs"]
    repetitions           = kde["repetitions"]
    res_factors           = kde["res_factors"]

    # ── Loop risk labels (not in kde dict)
    if loop_count == 0:
        loop_risk_emoji = "🟢"
        loop_risk_cause = "No se detectaron patrones de bucle. FIN puede guiar sin riesgo de repetición infinita."
    elif loop_count == 1:
        loop_risk_emoji = "⚠️"
        loop_risk_cause = f"Se detectó 1 patrón de bucle: '{loop_hits[0]}'. FIN podría entrar en un ciclo repetitivo."
    elif loop_count <= 3:
        loop_risk_emoji = "🔶"
        loop_risk_cause = f"Se detectaron {loop_count} patrones de bucle: {', '.join(repr(h) for h in loop_hits[:3])}. Alta probabilidad de que FIN repita instrucciones sin avanzar."
    else:
        loop_risk_emoji = "🔴"
        loop_risk_cause = f"Se detectaron {loop_count} patrones de bucle ({', '.join(repr(h) for h in loop_hits[:4])}...). FIN no puede romper el ciclo de forma autónoma."

    # ── Resolution labels (not in kde dict)
    if kde_resolution >= 80:
        resolution_label = "Alta"
        resolution_explanation = f"FIN puede resolver de forma autónoma con alta probabilidad ({kde_resolution}%). El artículo provee guía clara, pasos accionables y criterio de escalamiento."
    elif kde_resolution >= 60:
        resolution_label = "Media"
        resolution_explanation = f"FIN puede resolver parcialmente ({kde_resolution}%). " + (f"Factores limitantes: {', '.join(res_factors)}." if res_factors else "Aplicar optimizaciones recomendadas.")
    elif kde_resolution >= 40:
        resolution_label = "Baja"
        resolution_explanation = f"FIN tiene capacidad limitada de resolución ({kde_resolution}%). " + (f"Problemas principales: {', '.join(res_factors)}." if res_factors else "Requiere revisión completa.")
    else:
        resolution_label = "Muy baja"
        resolution_explanation = f"FIN no puede resolver de forma autónoma ({kde_resolution}%). " + (f"Bloqueadores: {', '.join(res_factors)}." if res_factors else "El artículo requiere reescritura.")

    # ── Variables needed by Phase 3 not returned by KDE
    contradictions = [
        ("activar", "desactivar"), ("habilitar", "deshabilitar"),
        ("guardar", "no guardar"), ("cerrar", "no cerrar"),
        ("contactar soporte", "no contactar soporte"),
    ]
    internal_contradiction = any(_ca in text_lower and _cb in text_lower for _ca, _cb in contradictions)
    fin_positive_hits = [p for p in _de.FIN_POSITIVE_SIGNALS if p in text_lower]
    english_terms = [w for w in words if _re.match(r'^[a-zA-Z]{4,}$', w) and w.lower() not in [
        "cufe", "dian", "login", "error", "click", "api", "token", "json", "xml", "nit",
    ]]
    foreign_term_ratio = len(english_terms) / max(word_count, 1)

    # ── Rebuild _problems and _recommendations from KDE signals
    _problems        = []
    _recommendations = []

    # 1. CLARIDAD
    if vague_hits:
        _problems.append(f"Frases vagas que reducen la claridad para FIN: {', '.join(repr(p) for p in vague_hits[:4])}.")
        _recommendations.append("Reemplaza las frases vagas por instrucciones concretas y verificables.")
    if word_count < 20:
        _problems.append("El artículo es demasiado corto para ser útil como fuente de resolución.")
        _recommendations.append("Amplía el artículo con pasos concretos y contexto de aplicación.")

    # 2. ESTRUCTURA
    if not has_numbered_steps:
        _problems.append("No se detectaron pasos numerados. FIN puede omitir pasos críticos.")
        _recommendations.append("Estructura el artículo con pasos numerados (1. 2. 3.).")
    if not has_sections:
        _problems.append("El artículo carece de secciones o encabezados diferenciados.")
        _recommendations.append("Agrega encabezados o secciones (Causa, Solución, Escalamiento).")
    if not has_bullets and not has_numbered_steps:
        _problems.append("Sin lista de pasos ni viñetas: FIN puede confundirse al leer párrafos densos.")
        _recommendations.append("Usa listas con viñetas o pasos numerados para instrucciones.")

    # 3. PASOS
    if not step_hits:
        _problems.append("No se detectaron verbos de acción en los pasos. FIN no podrá guiar al usuario paso a paso.")
        _recommendations.append("Incluye verbos de acción concretos en cada paso (Selecciona, Haz clic, Ingresa...).")
    if step_count == 0 and word_count > 60:
        _problems.append("El artículo tiene más de 60 palabras pero no estructura los pasos de forma numerada.")
        _recommendations.append("Numera los pasos para que FIN pueda seguirlos secuencialmente.")
    if ambiguous_steps:
        _problems.append(f"Pasos ambiguos o demasiado cortos detectados: {ambiguous_steps[:3]}.")
        _recommendations.append("Expande los pasos cortos con contexto y resultado esperado.")

    # 4. COBERTURA
    if len(cov_hits) < 2:
        _problems.append("Cobertura insuficiente: el artículo no menciona causa, solución ni resultado esperado.")
        _recommendations.append("Estructura el artículo con al menos: Causa, Pasos de solución, Resultado esperado.")
    elif len(cov_hits) < 4:
        _problems.append("Cobertura parcial: el artículo podría omitir causa, resultado o advertencias.")
        _recommendations.append("Añade secciones de Causa, Resultado esperado y Advertencias.")

    # 5. AMBIGÜEDAD
    if absolute_hits:
        _problems.append(f"Términos absolutos sin condición: {', '.join(repr(t) for t in absolute_hits)}.")
        _recommendations.append("Reemplaza los términos absolutos por condiciones específicas y verificables.")
    for _ca, _cb in contradictions:
        if _ca in text_lower and _cb in text_lower:
            _problems.append(f"Posible contradicción interna: el artículo menciona '{_ca}' y '{_cb}' sin distinción clara.")
            _recommendations.append(f"Aclara en qué contexto aplicar '{_ca}' vs '{_cb}'.")

    # 6. LONGITUD
    if word_count < 30:
        _problems.append(f"Artículo demasiado corto ({word_count} palabras). FIN no puede extraer pasos concretos.")
        _recommendations.append("El artículo debe tener al menos 80–200 palabras para ser procesable por FIN.")
    elif word_count < 60:
        _problems.append(f"Artículo corto ({word_count} palabras). Puede carecer de contexto suficiente.")
        _recommendations.append("Amplía el artículo con ejemplos, causas y pasos adicionales.")
    elif word_count > 800:
        _problems.append(f"Artículo muy extenso ({word_count} palabras). FIN puede perder el contexto relevante.")
        _recommendations.append("Divide el artículo en sub-artículos por escenario.")
    elif word_count > 400:
        _problems.append(f"Artículo extenso ({word_count} palabras). Considera dividirlo.")
        _recommendations.append("Verifica que cada sección sea independiente para que FIN pueda usarla de forma atómica.")

    # 7. CONSISTENCIA
    if repetitions > 0:
        _problems.append(f"Se detectaron {repetitions} sección(es) con contenido repetido (similitud ≥ 80%).")
        _recommendations.append("Elimina o consolida las secciones repetidas para evitar confusión en FIN.")
    uses_tu    = bool(_re.search(r'\b(haz|selecciona|entra|ve a|escribe|abre)\b', text_lower))
    uses_usted = bool(_re.search(r'\b(haga|seleccione|entre|vaya|escriba|abra)\b', text_lower))
    if uses_tu and uses_usted:
        _problems.append("El artículo mezcla tratamiento de 'tú' y 'usted'. Puede confundir a FIN.")
        _recommendations.append("Usa un único tratamiento (tú o usted) en todo el artículo.")

    # 8. TERMINOLOGÍA
    if undefined_terms:
        has_definitions = any(w in text_lower for w in ["significa", "es decir", "se refiere", "corresponde a", "definido como"])
        if not has_definitions:
            _problems.append(f"Términos técnicos sin definición detectados: {', '.join(undefined_terms[:5])}. FIN puede no saber cómo explicárselos al usuario.")
            _recommendations.append("Añade un glosario breve o explica los términos técnicos la primera vez que aparecen.")
    if foreign_term_ratio > 0.15:
        _problems.append(f"Alto porcentaje de términos en otro idioma ({round(foreign_term_ratio*100)}%). FIN puede tener dificultades para interpretar instrucciones mezcladas.")
        _recommendations.append("Traduce o adapta los términos en otro idioma al español.")

    # 9. USO POR FIN
    if not fin_positive_hits:
        _problems.append("El artículo no contiene señales de guía paso a paso que FIN pueda seguir autónomamente.")
        _recommendations.append("Redacta el artículo en segunda persona activa con condicionales claros para FIN.")
    if fin_blocker_hits:
        _problems.append(f"El artículo contiene acciones que FIN no puede ejecutar: {', '.join(repr(b) for b in fin_blocker_hits[:3])}.")
        _recommendations.append("Separa en un artículo diferente los pasos que requieren acceso de administrador y agrega una instrucción de escalamiento explícita.")

    # 10. ESCALAMIENTO
    if anti_escalation_rule:
        _problems.append("El artículo contiene una regla que prohíbe el escalamiento. FIN quedará atrapado sin salida al agotar los pasos.")
        _recommendations.append("Elimina la instrucción de no escalar y reemplaza con criterio de escalamiento condicional.")
    elif has_escalation:
        esc_cond = any(c in text_lower for c in ["si el problema persiste", "si no se resuelve", "si el error continúa", "si ninguno de los pasos"])
        if not esc_cond:
            _problems.append("Menciona escalamiento pero sin condición clara. FIN puede escalar prematuramente.")
            _recommendations.append("Agrega una condición explícita de escalamiento: 'Si el problema persiste luego de los pasos anteriores, escala al agente.'")
    else:
        _problems.append("El artículo no define cuándo escalar. FIN puede quedar sin instrucción al agotar los pasos.")
        _recommendations.append("Agrega al final: 'Si el problema persiste luego de seguir estos pasos, el agente FIN debe transferir al soporte humano incluyendo: [descripción del error, pasos realizados].'")

    # 11. MANTENIBILIDAD
    if date_refs:
        _problems.append(f"Referencias a fechas o versiones específicas detectadas: {date_refs[:3]}. El artículo puede desactualizarse rápidamente.")
        _recommendations.append("Remueve fechas específicas o agrega una nota de 'Última actualización'.")
    if word_count > 400:
        _problems.append("Artículos extensos son más difíciles de mantener actualizados.")
        _recommendations.append("Divide el artículo en sub-artículos para facilitar actualizaciones parciales.")

    # 12. RIESGO OPERATIVO
    if risky_hits:
        _problems.append(f"Acciones de alto riesgo detectadas: {', '.join(repr(r) for r in risky_hits[:4])}. Si FIN las guía sin advertencia previa, puede generar pérdida de datos.")
        has_warning = any(w in text_lower for w in ["advertencia", "precaución", "importante", "nota", "atención"])
        if not has_warning:
            _recommendations.append("Agrega una sección de ADVERTENCIA antes de los pasos destructivos.")

    # ════════════════════════════════════════════════════════════════════════ #
    # FASE 3 — FORTALEZAS, RIESGOS Y REPORTE                                  #
    # ════════════════════════════════════════════════════════════════════════ #

    # ── Fortalezas filtradas (nunca contradicen hallazgos del KDE)
    strengths = []
    if not vague_hits and not absolute_hits:
        strengths.append("Redacción directa: no se detectaron frases vagas ni términos absolutos.")
    if has_numbered_steps:
        strengths.append("Contiene pasos numerados: estructura fácil de seguir para FIN.")
    if has_sections:
        strengths.append("Organizado en secciones: facilita la extracción de información por FIN.")
    if len(step_hits) >= 3:
        strengths.append(f"Pasos con verbos de acción claros ({', '.join(step_hits[:3])}).")
    if len(cov_hits) >= 4:
        strengths.append(f"Buena cobertura temática: incluye {', '.join(cov_hits[:4])}.")
    if 60 <= word_count <= 400:
        strengths.append(f"Longitud adecuada ({word_count} palabras) para procesamiento por FIN.")
    if repetitions == 0:
        strengths.append("Sin repeticiones significativas de contenido detectadas.")
    if not undefined_terms:
        strengths.append("Terminología accesible: no se requieren definiciones adicionales.")
    if len(fin_positive_hits) >= 3 and not _has_kde_blocker:
        strengths.append("El artículo está orientado a guiar al usuario paso a paso, ideal para FIN.")
    if has_escalation and not anti_escalation_rule:
        _esc_cond = any(c in text_lower for c in ["si el problema persiste","si no se resuelve","si el error continúa","si ninguno de los pasos"])
        if _esc_cond:
            strengths.append("Incluye criterio de escalamiento condicional: FIN sabrá cuándo transferir.")
    if not date_refs:
        strengths.append("Sin referencias a fechas o versiones que puedan desactualizar el artículo.")
    # Riesgo operativo solo si NO hay bloqueadores ni loop alto/crítico
    if not risky_hits and not _has_kde_blocker and loop_risk_level not in ("ALTO", "CRÍTICO"):
        strengths.append("Sin acciones de alto riesgo operativo detectadas.")
    if risky_hits:
        has_warning = any(w in text_lower for w in ["advertencia","precaución","importante","nota","atención"])
        if has_warning:
            strengths.append("Incluye advertencias antes de acciones de alto riesgo.")

    # ── Riesgos basados en evidencia (sin frases genéricas)
    evidence_risks = []
    if loop_risk_level in ("ALTO", "CRÍTICO"):
        evidence_risks.append(
            f"Loop instruccional {loop_risk_level}: {loop_count} patrón(es) detectado(s) "
            f"({', '.join(repr(h) for h in loop_hits[:3])}). "
            "FIN puede repetir instrucciones indefinidamente sin avanzar hacia la resolución."
        )
    if anti_escalation_rule:
        evidence_risks.append(
            "Regla anti-escalamiento explícita: la instrucción de no escalar este tipo de casos "
            "impedirá que FIN transfiera al agente humano aunque el usuario no logre resolver."
        )
    if not has_escalation and not anti_escalation_rule:
        evidence_risks.append(
            "Ausencia de criterio de escalamiento: FIN no tiene instrucción de salida cuando agota los pasos. "
            "El usuario quedará bloqueado sin resolución ni transferencia."
        )
    if absolute_hits:
        evidence_risks.append(
            f"Términos absolutos ({', '.join(absolute_hits)}) sin condición verificable: FIN puede aplicar reglas "
            "de forma rígida en escenarios donde deberían aplicarse criterios contextuales."
        )
    if internal_contradiction:
        evidence_risks.append(
            "Contradicción interna detectada: FIN puede dar instrucciones opuestas en distintas "
            "conversaciones sobre el mismo problema."
        )
    if fin_blocker_hits:
        evidence_risks.append(
            f"Acciones de administrador no ejecutables por FIN ({', '.join(repr(b) for b in fin_blocker_hits[:2])}): "
            "FIN podría intentar guiar al usuario a través de pasos que requieren acceso de sistema."
        )
    if risky_hits:
        has_warning = any(w in text_lower for w in ["advertencia","precaución","importante","nota","atención"])
        if not has_warning:
            evidence_risks.append(
                f"Acciones de alto riesgo sin advertencia previa ({', '.join(repr(r) for r in risky_hits[:2])}): "
                "FIN puede guiar al usuario a través de pasos destructivos sin controles de seguridad."
            )
    if date_refs:
        evidence_risks.append(
            f"Referencias temporales específicas ({date_refs[:2]}): el artículo puede llevar a FIN a dar "
            "instrucciones desactualizadas al usuario."
        )
    if not evidence_risks:
        evidence_risks.append("Riesgo operativo bajo. El artículo no presenta hallazgos de riesgo críticos para el uso por FIN.")

    # ── Escalation Readiness
    escalation_issues   = []
    escalation_recs_ext = []
    if not has_escalation and not anti_escalation_rule:
        escalation_issues.append("Ausencia total de criterio de escalamiento.")
        escalation_recs_ext.append("Agrega un bloque de escalamiento explícito con condición, canal y datos requeridos.")
    elif has_escalation and not anti_escalation_rule:
        _esc_cond2 = any(c in text_lower for c in ["si el problema persiste","si no se resuelve","si el error continúa","si ninguno de los pasos"])
        if not _esc_cond2:
            escalation_issues.append("Escalamiento mencionado pero sin condición clara que active la transferencia.")
            escalation_recs_ext.append("Define la condición exacta: 'Si el problema persiste luego de X pasos, escala con: [datos]'.")
    if anti_escalation_rule:
        escalation_issues.append("Regla explícita que prohíbe el escalamiento. FIN quedará bloqueado sin salida.")
        escalation_recs_ext.append("Elimina la instrucción de no escalar y reemplaza con criterio condicional de escalamiento.")
    if absolute_hits:
        _esc_abs = [t for t in absolute_hits if t in ["nunca", "ninguno"]]
        if _esc_abs:
            escalation_issues.append(f"Términos absolutos ({_esc_abs}) que pueden bloquear la lógica de escalamiento de FIN.")
            escalation_recs_ext.append("Reemplaza los términos absolutos por condiciones específicas.")
    if not has_escalation and loop_risk_level in ("ALTO", "CRÍTICO"):
        escalation_issues.append("Sin escalamiento y con loop risk: FIN puede quedar atrapado repitiendo pasos indefinidamente.")
        escalation_recs_ext.append("Añade criterio de escalamiento inmediato si el usuario reporta que ya intentó el proceso.")
    if not escalation_issues:
        escalation_readiness_label = "Adecuada";   escalation_readiness_emoji = "✅"
    elif len(escalation_issues) == 1:
        escalation_readiness_label = "Parcial";    escalation_readiness_emoji = "⚠️"
    else:
        escalation_readiness_label = "Deficiente"; escalation_readiness_emoji = "🔴"

    # ── Riesgo Operativo expandido
    op_risk_items = []
    if not has_escalation or anti_escalation_rule:
        op_risk_items.append("Usuarios bloqueados sin salida: FIN no puede transferir al soporte humano.")
    if loop_risk_level in ("ALTO", "CRÍTICO"):
        op_risk_items.append(f"Bucle instruccional {loop_risk_level}: FIN repetirá los mismos pasos sin avanzar hacia la resolución.")
    if internal_contradiction:
        op_risk_items.append("Respuestas inconsistentes entre sesiones por contradicción interna detectada.")
    if fin_blocker_hits:
        op_risk_items.append("Bloqueo de resolución autónoma por pasos que requieren acceso de administrador.")
    if risky_hits:
        has_warning = any(w in text_lower for w in ["advertencia","precaución","importante","nota","atención"])
        if not has_warning:
            op_risk_items.append(f"Posible pérdida de datos: FIN puede ejecutar acciones destructivas ({', '.join(risky_hits[:2])}) sin advertencia previa.")

    # ── Health Score breakdown table
    hs_breakdown = [
        ("Claridad",         clarity,               12),
        ("Estructura",       structure,             10),
        ("Pasos",            steps_score,           12),
        ("Cobertura",        coverage,               8),
        ("Ambigüedad",       ambiguity,             10),
        ("Longitud",         length_score,           8),
        ("Consistencia",     consistency,            8),
        ("Terminología",     terminology,            8),
        ("Uso por FIN",      fin_usability,         10),
        ("Escalamiento",     escalation_score,       8),
        ("Mantenibilidad",   maintainability,        7),
        ("Riesgo operativo", operational_risk_score, 7),
    ]

    # ── Versión optimizada — reescritura completa con buenas prácticas para IA
    _title_m = _re.match(r'^#+\s*(.+?)$', text.strip(), _re.MULTILINE)
    _atitle   = _title_m.group(1).strip() if _title_m else (lines[0] if lines else "Error reportado")
    # Extract clean numbered steps (removing loop/absolute lines)
    _raw_steps = _re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+(.+)', text)
    _good_steps = []
    for _s in _raw_steps:
        _sl = _s.lower()
        if any(lp in _sl for lp in _de.LOOP_PATTERNS): continue
        if _re.search(r'nunca\s+(escal|contact)|no\s+existe\s+otra|no\s+importa\s+cu', _sl): continue
        for _at in absolute_hits:
            _s = _re.sub(r'\b' + _re.escape(_at) + r'\b', '', _s, flags=_re.IGNORECASE).strip()
        if len(_s.strip()) > 3:
            _good_steps.append(_s.strip())
    # If no numbered steps, extract action sentences
    if not _good_steps:
        for _sent in sentences:
            _sl = _sent.lower()
            if any(lp in _sl for lp in _de.LOOP_PATTERNS): continue
            if _re.search(r'nunca\s+(escal|contact)|no\s+existe\s+otra|no\s+importa\s+cu', _sl): continue
            if any(v in _sl for v in _de.STEP_VERBS[:12]) and len(_sent.split()) > 4:
                _good_steps.append(_sent.strip())
        _good_steps = _good_steps[:5]

    _opt = []
    _opt.append(f"# {_atitle}")
    _opt.append("")
    _opt.append("## Objetivo")
    _opt.append(f"Guiar al usuario paso a paso en la resolución de: {_atitle.lower()}.")
    _opt.append("")
    _opt.append("## Cuándo aplicar")
    _opt.append("Aplica cuando el usuario reporte este problema activamente durante la conversación.")
    _opt.append("")
    _opt.append("## Pasos")
    _opt.append("")
    if _good_steps:
        for _i, _st in enumerate(_good_steps, 1):
            _opt.append(f"{_i}. {_st}")
            _opt.append(f"   → Pregunta al usuario si el problema fue resuelto antes de continuar al siguiente paso.")
    else:
        _opt.append("1. Solicita al usuario que describa el error exacto que está viendo.")
        _opt.append("   → Confirma que tienes suficiente información para diagnosticar.")
        _opt.append("2. Guía al usuario a través de los pasos de resolución documentados para este caso.")
        _opt.append("   → Confirma con el usuario si el problema fue resuelto en cada intento.")
    _opt.append("")
    _opt.append("## Resultado esperado")
    _opt.append("El usuario confirma que el problema fue resuelto y puede continuar operando con normalidad.")
    _opt.append("")
    _opt.append("## Excepciones")
    _opt.append("- Si el usuario indica que el error ocurre en múltiples dispositivos o cuentas: puede ser un problema de plataforma, escala de inmediato.")
    _opt.append("- Si el usuario ya realizó estos pasos previamente sin éxito: escala sin repetir el proceso.")
    _opt.append("")
    _opt.append("## Criterio de escalamiento")
    _opt.append("Si el problema persiste luego de completar todos los pasos anteriores, transfiere la conversación al agente humano.")
    _opt.append("")
    _opt.append("## Información para el agente")
    _opt.append("Al escalar, incluye:")
    _opt.append(f"- Producto afectado: {product}")
    _opt.append("- Error reportado: [descripción exacta del error según el usuario]")
    _opt.append("- Pasos realizados: [indicar cuáles pasos se ejecutaron y cuál fue el resultado de cada uno]")
    _opt.append("- Número de intentos previos: [si el usuario ya intentó resolver antes de contactar]")
    optimized = "\n".join(_opt)

    # ── Resumen ejecutivo
    if deploy_decision == "LISTO":
        exec_q1 = f"Sí. El artículo está listo para uso autónomo por FIN (score {total}/100, {classification})."
    elif deploy_decision == "LISTO CON RECOMENDACIONES":
        exec_q1 = f"Con precaución. FIN puede usarlo (score {total}/100) si se aplican las recomendaciones antes del despliegue."
    elif deploy_decision == "NO LISTO":
        exec_q1 = f"No todavía. Score insuficiente ({total}/100). Requiere optimización antes del despliegue."
    else:
        exec_q1 = "No. El artículo está BLOQUEADO por problemas críticos que deben resolverse primero."

    if loop_risk_level == "CRÍTICO":
        exec_q2 = f"Riesgo principal: loop instruccional CRÍTICO ({loop_count} patrones). FIN repetirá instrucciones indefinidamente."
    elif anti_escalation_rule:
        exec_q2 = "Riesgo principal: regla que prohíbe el escalamiento. FIN no podrá transferir al agente humano en ningún caso."
    elif not has_escalation:
        exec_q2 = "Riesgo principal: ausencia de criterio de escalamiento. FIN no sabe cuándo transferir al agente humano."
    elif loop_risk_level == "ALTO":
        exec_q2 = f"Riesgo principal: loop risk ALTO ({loop_count} patrones). FIN puede entrar en ciclos repetitivos sin avanzar."
    elif absolute_hits:
        exec_q2 = f"Riesgo principal: términos absolutos ({', '.join(absolute_hits[:2])}) que bloquean la lógica de FIN."
    else:
        exec_q2 = f"Riesgo principal: calidad general ({total}/100). Aplicar las recomendaciones antes del despliegue."

    if loop_risk_level in ("CRÍTICO", "ALTO"):
        exec_q3 = "Prioridad 1: eliminar todos los patrones de bucle y añadir criterio de escalamiento condicional explícito."
    elif anti_escalation_rule:
        exec_q3 = "Prioridad 1: eliminar la regla que prohíbe el escalamiento y reemplazar con criterio condicional."
    elif not has_escalation:
        exec_q3 = "Prioridad 1: agregar bloque de escalamiento explícito con condición, canal y datos requeridos."
    elif absolute_hits:
        exec_q3 = f"Prioridad 1: reemplazar términos absolutos ({', '.join(absolute_hits[:2])}) por condiciones específicas."
    elif not step_hits:
        exec_q3 = "Prioridad 1: añadir verbos de acción concretos en cada paso."
    elif _problems:
        exec_q3 = f"Prioridad 1: {_problems[0][:100]}"
    else:
        exec_q3 = "No hay problemas críticos pendientes."

    _seen_r = set(); _unique_recs = []
    for rec in _recommendations:
        k = rec[:60]
        if k not in _seen_r:
            _seen_r.add(k); _unique_recs.append(rec)
    _potential = min(100, total + len(_unique_recs) * 5
                     + (20 if loop_risk_level in ("ALTO","CRÍTICO") else 0)
                     + (15 if anti_escalation_rule else 0))
    if _potential >= 78:
        exec_q4 = f"Si se aplican las {len(_unique_recs)} recomendaciones, el artículo podría alcanzar ~{_potential}/100, habilitando uso autónomo completo por FIN."
    else:
        exec_q4 = f"Aplicando las recomendaciones se espera mejorar el score a ~{_potential}/100. Se requiere revisión adicional para alcanzar el umbral de despliegue autónomo (78+)."

    # ────────────────────────────────────────────────────────────────────── #
    # CONSTRUCCIÓN DEL REPORTE                                               #
    # ────────────────────────────────────────────────────────────────────── #
    sep  = "=" * 48
    div2 = "─" * 40
    div3 = "·" * 40

    def row(label, score, max_score):
        dots = "." * max(1, 22 - len(label))
        return f"  {label} {dots} {score}/{max_score}"

    def hs_row(label, score, max_score):
        pct      = round(score / max_score * 100) if max_score else 0
        bar_full = round(pct / 10)
        bar      = "█" * bar_full + "░" * (10 - bar_full)
        sign     = f"+{score}" if score == max_score else f"+{score}/-{max_score - score}"
        dots     = "." * max(1, 20 - len(label))
        return f"  {label} {dots} [{bar}] {sign} ({pct}%)"

    parts = []

    parts += [sep, "AUDIT KNOWLEDGE v3 — FIN Knowledge Core", sep, ""]
    parts.append(f"PRODUCTO: {product.upper()}")
    parts.append(f"HEALTH SCORE: {class_emoji} {total}/100 — {classification}")
    parts.append(f"RIESGO GLOBAL: {kde_risk}")
    if context:
        parts.append(f"CONTEXTO: {context}")
    parts.append(f"LONGITUD: {word_count} palabras  |  SECCIONES: {len(lines)} líneas")
    parts.append("")

    parts += [div2, "RESUMEN EJECUTIVO", div2, ""]
    parts.append("  1. ¿Puede FIN usar este artículo?")
    parts.append(f"     {exec_q1}")
    parts.append("  2. ¿Cuál es el riesgo principal?")
    parts.append(f"     {exec_q2}")
    parts.append("  3. ¿Qué corregir primero?")
    parts.append(f"     {exec_q3}")
    parts.append("  4. ¿Cuál es el impacto esperado si se optimiza?")
    parts.append(f"     {exec_q4}")
    parts.append("")

    parts += [div2, "DECISIÓN DE DESPLIEGUE", div2, ""]
    parts.append(f"  {deploy_emoji} {deploy_decision}")
    parts.append(f"  {deploy_motivo}")
    if kde_blocker_flags:
        parts.append(f"  Bloqueadores KDE: {', '.join(kde_blocker_flags)}")
    parts.append("")

    parts += [div3, "CAPACIDAD DE RESOLUCIÓN", div3, ""]
    parts.append(f"  Probabilidad de resolución autónoma: {kde_resolution}% — {resolution_label}")
    parts.append(f"  {resolution_explanation}")
    parts.append("")

    parts += [div3, "AUTOMATION READINESS", div3, ""]
    parts.append(f"  {automation_emoji} {automation_readiness}")
    parts.append(f"  {automation_justif}")
    parts.append("")

    parts += [div3, "ESCALATION READINESS", div3, ""]
    parts.append(f"  {escalation_readiness_emoji} {escalation_readiness_label}")
    if escalation_issues:
        for ei in escalation_issues:
            parts.append(f"  ⚠️  {ei}")
        for er in escalation_recs_ext:
            parts.append(f"  → {er}")
    else:
        parts.append("  ✓ El artículo define correctamente cuándo y cómo FIN debe escalar.")
    parts.append("")

    parts += [div3, "LOOP RISK", div3, ""]
    parts.append(f"  {loop_risk_emoji} {loop_risk_level}")
    parts.append(f"  {loop_risk_cause}")
    if loop_hits:
        parts.append(f"  Patrones detectados: {', '.join(repr(h) for h in loop_hits[:5])}")
    parts.append("")

    parts += [div3, "RIESGO OPERATIVO", div3, ""]
    if op_risk_items:
        for ori in op_risk_items:
            parts.append(f"  🔴 {ori}")
    else:
        parts.append("  ✓ No se identificaron riesgos operativos adicionales.")
    parts.append("")

    parts += [div2, "HEALTH SCORE — DESGLOSE (KDE)", div2, ""]
    for lbl, sc, mx in hs_breakdown:
        parts.append(hs_row(lbl, sc, mx))
    parts.append(f"  {'─'*38}")
    parts.append(f"  Subtotal criterios {'.' * 15} {_raw_total}/100")
    if kde_health != _raw_total:
        _adj = kde_health - _raw_total
        parts.append(f"  Ajuste KDE {'.' * 23} {'+' if _adj >= 0 else ''}{_adj} pts")
    parts.append(f"  TOTAL KDE {'.' * 24} {total}/100")
    parts.append("")

    parts += [div2, "DESGLOSE DE CRITERIOS", div2, ""]
    parts.append(row("Claridad",            clarity,               12))
    parts.append(row("Estructura",          structure,             10))
    parts.append(row("Pasos",               steps_score,           12))
    parts.append(row("Cobertura",           coverage,               8))
    parts.append(row("Ambigüedad",          ambiguity,             10))
    parts.append(row("Longitud",            length_score,           8))
    parts.append(row("Consistencia",        consistency,            8))
    parts.append(row("Terminología",        terminology,            8))
    parts.append(row("Uso por FIN",         fin_usability,         10))
    parts.append(row("Escalamiento",        escalation_score,       8))
    parts.append(row("Mantenibilidad",      maintainability,        7))
    parts.append(row("Riesgo operativo",    operational_risk_score, 7))
    parts.append(f"  {'─'*28}")
    parts.append(f"  TOTAL {'.' * 16} {total}/100")
    parts.append("")

    parts += [div3, "FORTALEZAS", div3, ""]
    if strengths:
        for s in strengths:
            parts.append(f"  ✓ {s}")
    else:
        parts.append("  — No se identificaron fortalezas destacables en el estado actual del artículo.")
    parts.append("")

    parts += [div3, "PROBLEMAS DETECTADOS", div3, ""]
    _problem_tags = {
        "Pasos faltantes":            lambda: not step_hits,
        "Pasos ambiguos":             lambda: bool(ambiguous_steps),
        "Repeticiones":               lambda: repetitions > 0,
        "Contradicciones":            lambda: internal_contradiction,
        "Términos absolutos":         lambda: bool(absolute_hits),
        "Regla anti-escalamiento":    lambda: anti_escalation_rule,
        "Sin criterio escalamiento":  lambda: not has_escalation,
        "Loop risk detectado":        lambda: loop_count > 0,
        "Información desactualizada": lambda: bool(date_refs),
        "Artículo demasiado corto":   lambda: word_count < 30,
        "Artículo demasiado largo":   lambda: word_count > 800,
        "Acciones no ejecutables FIN":lambda: bool(fin_blocker_hits),
    }
    detected_tags = [lbl for lbl, chk in _problem_tags.items() if chk()]
    if detected_tags:
        parts.append("  Detectado automáticamente:")
        for lbl in detected_tags:
            parts.append(f"  🔍 {lbl}")
        parts.append("")
    if _problems:
        for p in _problems:
            parts.append(f"  ⚠️  {p}")
    else:
        parts.append("  ✅ No se detectaron problemas críticos.")
    parts.append("")

    parts += [div3, "RIESGOS", div3, ""]
    for r in evidence_risks:
        parts.append(f"  🔴 {r}")
    parts.append("")

    parts += [div3, "RECOMENDACIONES", div3, ""]
    if _unique_recs:
        for i, rec in enumerate(_unique_recs, 1):
            parts.append(f"  {i}. {rec}")
    else:
        parts.append("  — No se generaron recomendaciones adicionales.")
    parts.append("")

    parts += [div2, "VERSIÓN OPTIMIZADA DEL ARTÍCULO", div2, ""]
    parts.append(optimized)
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def optimize_article(
    article: str,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Recibe un artículo de Base de Conocimiento y devuelve una versión optimizada
    específicamente para FIN. No inventa información, no cambia el significado del
    artículo. Solo mejora estructura, claridad y utilidad para IA conversacional.
    Reutiliza la lógica de detección de audit_knowledge.
    """

    import re as _re

    text       = article.strip()
    text_lower = text.lower()
    words      = text.split()
    word_count = len(words)
    sentences  = [s.strip() for s in _re.split(r'[.!?]+', text) if s.strip()]
    lines      = [l.strip() for l in text.splitlines() if l.strip()]

    # ════════════════════════════════════════════════════════════════════════ #
    # DETECCIÓN — misma lógica que audit_knowledge                            #
    # ════════════════════════════════════════════════════════════════════════ #

    # Estructura
    has_numbered_steps = bool(_re.search(r'(?:^|\n)\s*\d+[\.\)]\s+\S', text))
    has_bullets        = bool(_re.search(r'(?:^|\n)\s*[-•*]\s+\S', text))
    has_sections       = bool(_re.search(r'(?:^|\n)\s*#{1,3}\s+\S|(?:^|\n)[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{3,}:', text))

    # Detección — usando constantes centralizadas
    step_hits       = [v for v in _de.STEP_VERBS if v in text_lower]
    absolute_hits   = _de.detect_absolute_hits(text_lower)
    vague_hits      = [p for p in _de.VAGUE_PHRASES if p in text_lower]
    has_escalation  = _de.detect_escalation(text_lower)
    anti_escalation_rule = _de.detect_anti_escalation(text_lower)
    loop_risk_level, loop_count, loop_hits = _de.detect_loop_risk(text_lower)
    undefined_terms = [t for t in _de.TECHNICAL_TERMS if t in text_lower]
    cov_hits        = [s for s in _de.COVERAGE_SIGNALS if s in text_lower]

    # Redundancias
    sentence_words = [frozenset(s.lower().split()) for s in sentences if len(s.split()) >= 5]
    repetitions = 0
    seen_sents  = []
    for sw in sentence_words:
        for prev in seen_sents:
            if sw and prev and len(sw & prev) / max(len(sw), len(prev)) >= 0.80:
                repetitions += 1
                break
        seen_sents.append(sw)

    # Párrafos largos
    long_paragraphs = [s for s in sentences if len(s.split()) > 40]

    # Contradicciones
    contradictions = [
        ("activar", "desactivar"), ("habilitar", "deshabilitar"),
        ("guardar", "no guardar"), ("cerrar", "no cerrar"),
    ]
    internal_contradiction = any(
        _ca in text_lower and _cb in text_lower for _ca, _cb in contradictions
    )

    # Título del artículo
    _title_m = _re.match(r'^#+\s*(.+?)$', text.strip(), _re.MULTILINE)
    _atitle   = _title_m.group(1).strip() if _title_m else (lines[0] if lines else "Artículo")

    # ════════════════════════════════════════════════════════════════════════ #
    # PROBLEMAS ENCONTRADOS                                                    #
    # ════════════════════════════════════════════════════════════════════════ #
    _problems_found = []

    if vague_hits:
        _problems_found.append(
            f"Ambigüedad: frases vagas detectadas ({', '.join(repr(p) for p in vague_hits[:3])}).")
    if not step_hits:
        _problems_found.append(
            "Pasos faltantes: no se detectaron verbos de acción (selecciona, ingresa, verifica...).")
    if not has_numbered_steps and word_count > 60:
        _problems_found.append(
            "Estructura deficiente: pasos sin numerar. FIN puede omitir pasos críticos.")
    if not has_sections:
        _problems_found.append(
            "Estructura deficiente: sin encabezados ni secciones diferenciadas.")
    if long_paragraphs:
        _problems_found.append(
            f"Párrafos largos: {len(long_paragraphs)} oración(es) con más de 40 palabras. Dificultan la lectura de FIN.")
    if absolute_hits:
        _problems_found.append(
            f"Términos absolutos sin condición: {', '.join(repr(t) for t in absolute_hits)}. Bloquean la lógica de FIN.")
    if anti_escalation_rule:
        _problems_found.append(
            "Regla anti-escalamiento: 'nunca escales' o equivalente. FIN quedará sin salida al agotar los pasos.")
    elif not has_escalation:
        _problems_found.append(
            "Ausencia de criterio de escalamiento: FIN no sabe cuándo transferir al agente humano.")
    if loop_count > 0:
        _problems_found.append(
            f"Loop instruccional {loop_risk_level}: {loop_count} patrón(es) de bucle detectado(s) "
            f"({', '.join(repr(h) for h in loop_hits[:3])}).")
    if repetitions > 0:
        _problems_found.append(
            f"Redundancias: {repetitions} oración(es) con contenido repetido (similitud ≥ 80%).")
    if undefined_terms:
        _problems_found.append(
            f"Lenguaje poco claro: términos técnicos sin definición ({', '.join(undefined_terms[:4])}).")
    if len(cov_hits) < 2:
        _problems_found.append(
            "Cobertura insuficiente: el artículo no menciona causa, solución ni resultado esperado.")
    if internal_contradiction:
        _problems_found.append(
            "Contradicción interna: el artículo menciona acciones opuestas sin distinción de contexto.")

    # ════════════════════════════════════════════════════════════════════════ #
    # CONSTRUCCIÓN DE VERSIÓN OPTIMIZADA                                      #
    # Solo reorganiza lo que existe. No inventa información.                  #
    # ════════════════════════════════════════════════════════════════════════ #

    # Extraer pasos del original, filtrar loops y reglas de no escalar
    _raw_steps = _re.findall(r'(?:^|\n)\s*\d+[\.\)]\s+(.+)', text)
    _good_steps = []
    for _s in _raw_steps:
        _sl = _s.lower()
        if any(lp in _sl for lp in _de.LOOP_PATTERNS): continue
        if _re.search(r'nunca\s+(escal|contact)|no\s+existe\s+otra|no\s+importa\s+cu', _sl): continue
        for _at in absolute_hits:
            _s = _re.sub(r'\b' + _re.escape(_at) + r'\b', '', _s, flags=_re.IGNORECASE).strip()
        if len(_s.strip()) > 3:
            _good_steps.append(_s.strip())

    # Si no hay pasos numerados, extraer oraciones con verbos de acción
    if not _good_steps:
        for _sent in sentences:
            _sl = _sent.lower()
            if any(lp in _sl for lp in _de.LOOP_PATTERNS): continue
            if _re.search(r'nunca\s+(escal|contact)|no\s+existe\s+otra|no\s+importa\s+cu', _sl): continue
            if any(v in _sl for v in _de.STEP_VERBS[:12]) and len(_sent.split()) > 4:
                _good_steps.append(_sent.strip())
        _good_steps = _good_steps[:6]

    # Artículo optimizado — secciones estándar para IA conversacional
    _opt = []
    _opt.append(f"# {_atitle}")
    _opt.append("")
    _opt.append("## Objetivo")
    _opt.append(f"Guiar al usuario paso a paso en la resolución de: {_atitle.lower()}.")
    _opt.append("")
    _opt.append("## Cuándo aplica")
    _opt.append("Aplica cuando el usuario reporte este problema activamente durante la conversación.")
    _opt.append("")
    _opt.append("## Pasos")
    _opt.append("")
    if _good_steps:
        for _i, _st in enumerate(_good_steps, 1):
            _opt.append(f"{_i}. {_st}")
            _opt.append(f"   → Pregunta al usuario si el problema fue resuelto antes de continuar.")
    else:
        _opt.append("1. Solicita al usuario que describa el error exacto que está viendo.")
        _opt.append("   → Confirma que tienes suficiente información para diagnosticar.")
        _opt.append("2. Aplica los pasos documentados para este caso.")
        _opt.append("   → Confirma con el usuario el resultado de cada paso.")
    _opt.append("")
    _opt.append("## Resultado esperado")
    _opt.append("El usuario confirma que el problema fue resuelto y puede continuar operando con normalidad.")
    _opt.append("")
    _opt.append("## Excepciones")
    _opt.append("- Si el usuario indica que el error ocurre en múltiples dispositivos o cuentas: puede ser un problema de plataforma. Escala de inmediato.")
    _opt.append("- Si el usuario ya realizó estos pasos previamente sin éxito: escala sin repetir el proceso.")
    _opt.append("")
    _opt.append("## Escalamiento")
    _opt.append("Si el problema persiste luego de completar todos los pasos anteriores, transfiere la conversación al agente humano.")
    _opt.append("")
    _opt.append("## Información para el agente")
    _opt.append("Al escalar, incluye:")
    _opt.append(f"- Producto afectado: {product}")
    _opt.append("- Error reportado: [descripción exacta del error según el usuario]")
    _opt.append("- Pasos realizados: [cuáles pasos se ejecutaron y cuál fue el resultado de cada uno]")
    _opt.append("- Intentos previos: [si el usuario ya intentó resolver antes de contactar]")
    optimized = "\n".join(_opt)

    # ════════════════════════════════════════════════════════════════════════ #
    # OPTIMIZACIONES APLICADAS                                                 #
    # ════════════════════════════════════════════════════════════════════════ #
    _applied = []
    if not has_numbered_steps and _good_steps:
        _applied.append("Se numeraron los pasos.")
    if not has_sections:
        _applied.append("Se reorganizó el flujo con secciones claras (Objetivo, Pasos, Resultado esperado, Escalamiento).")
    if anti_escalation_rule or not has_escalation:
        _applied.append("Se agregó criterio de escalamiento condicional explícito.")
    if absolute_hits:
        _applied.append(f"Se eliminaron términos absolutos ({', '.join(absolute_hits)}) que bloqueaban la lógica de FIN.")
    if loop_count > 0:
        _applied.append(
            f"Se eliminaron {loop_count} patrón(es) de bucle instruccional "
            f"({', '.join(repr(h) for h in loop_hits[:3])}).")
    if long_paragraphs:
        _applied.append("Se dividieron párrafos largos en pasos discretos.")
    if not step_hits or not _good_steps:
        _applied.append("Se mejoró el lenguaje para IA: pasos estructurados con verbos de acción y confirmaciones.")
    else:
        _applied.append("Se mejoró el lenguaje para IA: cada paso incluye confirmación de resolución.")
    _applied.append("Se separaron excepciones en sección propia.")
    _applied.append("Se agregó resultado esperado.")
    _applied.append("Se agregó sección de información para el agente al escalar.")

    # ════════════════════════════════════════════════════════════════════════ #
    # IMPACTO ESTIMADO                                                         #
    # ════════════════════════════════════════════════════════════════════════ #
    def _impact(count):
        if count >= 3: return "Alta"
        if count >= 1: return "Media"
        return "Baja"

    impact_clarity   = _impact(len(vague_hits) + (1 if absolute_hits else 0))
    impact_fin       = _impact(
        (1 if not has_numbered_steps else 0)
        + (1 if not has_sections else 0)
        + (1 if anti_escalation_rule or not has_escalation else 0)
    )
    impact_loops     = ("Alta" if loop_count >= 2 else "Media" if loop_count == 1 else "Sin cambios necesarios")
    impact_ambiguity = _impact(len(absolute_hits) + len(vague_hits))
    impact_maintain  = _impact((1 if not has_sections else 0) + (1 if repetitions > 0 else 0))

    # ════════════════════════════════════════════════════════════════════════ #
    # CALIDAD FINAL (del artículo optimizado)                                  #
    # ════════════════════════════════════════════════════════════════════════ #
    _opt_score = 70  # base: estructura estándar aplicada
    if _good_steps:                        _opt_score += 10
    if not _problems_found:                _opt_score += 10
    elif len(_problems_found) >= 5:        _opt_score -= 15
    elif len(_problems_found) >= 3:        _opt_score -= 5
    if anti_escalation_rule:               _opt_score -= 5
    if absolute_hits and len(absolute_hits) >= 2: _opt_score -= 5
    _opt_score = max(0, min(100, _opt_score))

    if _opt_score >= 85:
        final_quality = "Excelente";        quality_emoji = "✅"
    elif _opt_score >= 72:
        final_quality = "Muy buena";        quality_emoji = "🟢"
    elif _opt_score >= 58:
        final_quality = "Aceptable";        quality_emoji = "⚠️"
    elif _opt_score >= 40:
        final_quality = "Requiere revisión"; quality_emoji = "🔶"
    else:
        final_quality = "No apta";          quality_emoji = "🔴"

    # ════════════════════════════════════════════════════════════════════════ #
    # OBSERVACIONES                                                            #
    # ════════════════════════════════════════════════════════════════════════ #
    blockers_remaining = []
    if anti_escalation_rule:
        blockers_remaining.append(
            "la regla anti-escalamiento debe eliminarse del artículo fuente antes de publicar")
    if loop_count > 0:
        blockers_remaining.append("los patrones de bucle deben eliminarse del artículo fuente")
    if absolute_hits:
        blockers_remaining.append(
            f"los términos absolutos ({', '.join(absolute_hits)}) deben revisarse en el artículo fuente")

    if not blockers_remaining and _opt_score >= 72:
        observation = (
            "✅ El artículo optimizado puede publicarse para FIN. "
            "Se recomienda revisión humana de la versión optimizada antes del despliegue en producción."
        )
    elif not blockers_remaining:
        observation = (
            "⚠️ El artículo optimizado requiere revisión adicional antes de publicarse para FIN. "
            "Aplica las optimizaciones sobre el artículo fuente y verifica con audit_knowledge."
        )
    else:
        observation = (
            "🚫 El artículo NO puede publicarse para FIN en su estado actual. "
            f"Intervención humana requerida: {'; '.join(blockers_remaining)}. "
            "La versión optimizada muestra la estructura objetivo; el contenido fuente debe corregirse primero."
        )

    # ════════════════════════════════════════════════════════════════════════ #
    # CONSTRUCCIÓN DEL REPORTE                                                 #
    # ════════════════════════════════════════════════════════════════════════ #
    sep  = "=" * 48
    div2 = "─" * 40

    parts = []

    parts += [sep, "OPTIMIZE ARTICLE — FIN Knowledge Core", sep, ""]
    parts.append(f"PRODUCTO: {product.upper()}")
    if context:
        parts.append(f"CONTEXTO: {context}")
    parts.append("")

    # ── Versión original
    parts += [div2, "VERSIÓN ORIGINAL", div2, ""]
    parts.append(f"  Título    : {_atitle}")
    parts.append(f"  Longitud  : {word_count} palabras | {len(lines)} líneas")
    _struct_desc = []
    if has_sections:       _struct_desc.append("con secciones")
    else:                  _struct_desc.append("sin secciones")
    if has_numbered_steps: _struct_desc.append("pasos numerados")
    elif has_bullets:      _struct_desc.append("viñetas")
    else:                  _struct_desc.append("sin estructura de pasos")
    parts.append(f"  Estructura: {', '.join(_struct_desc)}")
    if anti_escalation_rule:
        parts.append("  Escalamiento: regla explícita que prohíbe escalar ⚠️")
    elif has_escalation:
        parts.append("  Escalamiento: mencionado")
    else:
        parts.append("  Escalamiento: no definido")
    if loop_count > 0:
        parts.append(f"  Loop risk : {loop_risk_level} ({loop_count} patrón(es) detectado(s))")
    else:
        parts.append("  Loop risk : BAJO")
    parts.append("")

    # ── Problemas encontrados
    parts += [div2, "PROBLEMAS ENCONTRADOS", div2, ""]
    if _problems_found:
        for p in _problems_found:
            parts.append(f"  ⚠️  {p}")
    else:
        parts.append("  ✅ No se detectaron problemas críticos en el artículo original.")
    parts.append("")

    # ── Optimizaciones aplicadas
    parts += [div2, "OPTIMIZACIONES APLICADAS", div2, ""]
    for a in _applied:
        parts.append(f"  ✓ {a}")
    parts.append("")

    # ── Versión optimizada
    parts += [div2, "VERSIÓN OPTIMIZADA", div2, ""]
    parts.append(optimized)
    parts.append("")

    # ── Comparación
    parts += [div2, "COMPARACIÓN", div2, ""]
    parts.append("  Original")
    if not has_sections and not has_numbered_steps:
        parts.append("    → Texto plano sin estructura. FIN no puede distinguir pasos de contexto.")
    elif not has_numbered_steps:
        parts.append("    → Tiene secciones pero pasos sin numerar. FIN puede omitir pasos.")
    else:
        parts.append("    → Estructura parcial con problemas detectados.")
    if loop_count > 0:
        parts.append(f"    → {loop_count} patrón(es) de bucle: FIN repite instrucciones sin avanzar.")
    if anti_escalation_rule:
        parts.append("    → Regla que prohíbe escalar: FIN queda bloqueado sin salida.")
    elif not has_escalation:
        parts.append("    → Sin escalamiento: FIN no tiene instrucción de salida.")
    parts.append("  ↓")
    parts.append("  Optimizado")
    parts.append("    → Estructura estándar: Objetivo → Pasos numerados → Resultado → Excepciones → Escalamiento.")
    parts.append("    → Cada paso incluye confirmación de resolución antes de avanzar.")
    parts.append("    → Criterio de escalamiento condicional explícito.")
    if loop_count > 0:
        parts.append("    → Sin patrones de bucle instruccional.")
    if absolute_hits:
        parts.append("    → Sin términos absolutos que bloqueen la lógica de FIN.")
    parts.append("")

    # ── Impacto estimado
    parts += [div2, "IMPACTO ESTIMADO", div2, ""]
    parts.append(f"  Mejora en claridad ............... {impact_clarity}")
    parts.append(f"  Mejora para FIN .................. {impact_fin}")
    parts.append(f"  Reducción de loops ............... {impact_loops}")
    parts.append(f"  Reducción de ambigüedad .......... {impact_ambiguity}")
    parts.append(f"  Facilidad de mantenimiento ....... {impact_maintain}")
    parts.append("")

    # ── Calidad final
    parts += [div2, "CALIDAD FINAL", div2, ""]
    parts.append(f"  {quality_emoji} {final_quality}")
    parts.append("")

    # ── Observaciones
    parts += [div2, "OBSERVACIONES", div2, ""]
    parts.append(f"  {observation}")
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def knowledge_review(
    product: str,
    articles: list,
    context: str = ""
) -> str:
    """
    Analiza el conjunto completo de artículos de conocimiento de un producto
    y genera un diagnóstico ejecutivo de preparación para FIN.
    Reutiliza la lógica de detección de audit_knowledge y optimize_article.
    No modifica los artículos. Solo analiza.
    """

    # ════════════════════════════════════════════════════════════════════════ #
    # VALIDACIÓN DE ENTRADA                                                    #
    # ════════════════════════════════════════════════════════════════════════ #
    if not articles:
        return "No se proporcionaron artículos para analizar."

    analyses = [_de.kde_score_article(str(a)) for a in articles]
    n = len(analyses)

    # ════════════════════════════════════════════════════════════════════════ #
    # MÉTRICAS AGREGADAS                                                       #
    # ════════════════════════════════════════════════════════════════════════ #
    avg_health         = round(sum(a["kde_health"] for a in analyses) / n)
    blocked_count      = sum(1 for a in analyses if a["deploy"] == "BLOQUEADO")
    not_ready_count    = sum(1 for a in analyses if a["deploy"] == "NO LISTO")
    ready_count        = sum(1 for a in analyses if a["deploy"] == "LISTO")
    ready_recs_count   = sum(1 for a in analyses if a["deploy"] == "LISTO CON RECOMENDACIONES")
    loop_articles      = [a for a in analyses if a["loop_risk_level"] in ("ALTO","CRÍTICO")]
    anti_esc_articles  = [a for a in analyses if a["anti_escalation_rule"]]
    no_esc_list        = [a for a in analyses if not a["has_escalation"] and not a["anti_escalation_rule"]]
    abs_articles       = [a for a in analyses if a["absolute_hits"]]

    # Madurez general
    if avg_health >= 85 and blocked_count == 0:
        maturity = "Excelente"; maturity_emoji = "✅"
    elif avg_health >= 70 and blocked_count == 0:
        maturity = "Alta";      maturity_emoji = "🟢"
    elif avg_health >= 55:
        maturity = "Media";     maturity_emoji = "🔵"
    elif avg_health >= 40:
        maturity = "Baja";      maturity_emoji = "🔶"
    else:
        maturity = "Crítica";   maturity_emoji = "🔴"

    # Conclusión global
    if blocked_count >= max(1, round(n * 0.3)) or avg_health < 40:
        conclusion = "BLOCKED";                concl_emoji = "🚫"
        concl_why  = (f"{blocked_count} de {n} artículos BLOQUEADOS. "
                      "La Base de Conocimiento presenta riesgos críticos que impedirán el funcionamiento autónomo de FIN.")
    elif avg_health < 55 or blocked_count > 0:
        conclusion = "NOT READY";              concl_emoji = "🔴"
        _why_parts = []
        if avg_health < 55:
            _why_parts.append(f"Score promedio insuficiente ({avg_health}/100).")
        if blocked_count > 0:
            _why_parts.append(f"{blocked_count} artículo(s) BLOQUEADO(s) que impiden el despliegue.")
        _why_parts.append("Se requieren correcciones antes del despliegue.")
        concl_why = " ".join(_why_parts)
    elif avg_health < 78 or not_ready_count > 0 or loop_articles:
        conclusion = "READY WITH RECOMMENDATIONS"; concl_emoji = "⚠️"
        concl_why  = (f"Score promedio aceptable ({avg_health}/100) con áreas de mejora. "
                      f"{ready_recs_count + not_ready_count} artículo(s) requieren optimización antes del despliegue completo.")
    else:
        conclusion = "READY";                  concl_emoji = "✅"
        concl_why  = (f"Score promedio {avg_health}/100. {ready_count} de {n} artículos listos para producción. "
                      "La Base de Conocimiento cumple los estándares para uso autónomo por FIN.")

    # ════════════════════════════════════════════════════════════════════════ #
    # COBERTURA TEMÁTICA                                                       #
    # ════════════════════════════════════════════════════════════════════════ #
    topic_keywords = {
        "Facturación":    ["factura","facturación","facturar","documento","cufe","dian","electrónica"],
        "Caja":           ["caja","cajero","apertura","cierre de caja","turno","cuadre"],
        "Inventario":     ["inventario","stock","producto","bodega","conteo","kardex"],
        "Sincronización": ["sincroniz","sincronización","sync","pendiente","offline"],
        "Permisos":       ["permiso","permisos","acceso","rol","perfil","autorización"],
        "Usuarios":       ["usuario","usuarios","contraseña","clave","cuenta","login","sesión"],
        "Integraciones":  ["integración","api","webhook","conector","tercero","erp"],
        "Reportes":       ["reporte","informe","estadística","exportar","resumen de ventas"],
        "Configuración":  ["configuración","configurar","ajuste","parámetro","setting"],
        "Ventas":         ["venta","ventas","transacción","cobro","pago"],
        "Soporte":        ["soporte","error","problema","fallo","incidente"],
    }
    coverage_map = {}
    for topic, kws in topic_keywords.items():
        matching = [a for a in analyses if any(kw in a["text_lower"] for kw in kws)]
        if not matching:
            coverage_map[topic] = ("Sin cobertura", [])
        else:
            avg_h = round(sum(m["kde_health"] for m in matching) / len(matching))
            lbl = "Alta" if avg_h >= 70 else "Media" if avg_h >= 50 else "Baja"
            coverage_map[topic] = (lbl, [m["title"] for m in matching])

    # ════════════════════════════════════════════════════════════════════════ #
    # ARTÍCULOS CRÍTICOS                                                       #
    # ════════════════════════════════════════════════════════════════════════ #
    critical_articles = [a for a in analyses if a["kde_health"] < 60 or a["has_kde_blocker"]]
    critical_articles.sort(key=lambda a: a["kde_health"])

    # ════════════════════════════════════════════════════════════════════════ #
    # DUPLICADOS (similitud ≥ 55%)                                            #
    # ════════════════════════════════════════════════════════════════════════ #
    duplicates = []
    checked = set()
    for i in range(n):
        for j in range(i+1, n):
            if (i,j) in checked: continue
            checked.add((i,j))
            ws_i = analyses[i]["words_set"]
            ws_j = analyses[j]["words_set"]
            if not ws_i or not ws_j: continue
            union = len(ws_i | ws_j)
            if union == 0: continue
            overlap = len(ws_i & ws_j) / union
            if overlap >= 0.55:
                keep_idx = i if analyses[i]["kde_health"] >= analyses[j]["kde_health"] else j
                drop_idx = j if keep_idx == i else i
                duplicates.append({
                    "title_i": analyses[i]["title"],
                    "title_j": analyses[j]["title"],
                    "overlap": round(overlap * 100),
                    "keep": analyses[keep_idx]["title"],
                    "drop": analyses[drop_idx]["title"],
                })

    # ════════════════════════════════════════════════════════════════════════ #
    # CONFLICTOS (mismo tema, instrucciones incompatibles)                    #
    # ════════════════════════════════════════════════════════════════════════ #
    conflicts = []
    for topic, kws in topic_keywords.items():
        grp = [a for a in analyses if any(kw in a["text_lower"] for kw in kws)]
        if len(grp) < 2: continue
        for ii in range(len(grp)):
            for jj in range(ii+1, len(grp)):
                ai, aj = grp[ii], grp[jj]
                if ai["anti_escalation_rule"] != aj["anti_escalation_rule"] and (ai["has_escalation"] or aj["has_escalation"]):
                    conflicts.append({
                        "topic": topic,
                        "desc": (f"'{ai['title']}' {'prohíbe escalar' if ai['anti_escalation_rule'] else 'incluye escalamiento'}, "
                                 f"mientras '{aj['title']}' {'prohíbe escalar' if aj['anti_escalation_rule'] else 'incluye escalamiento'}. "
                                 "FIN recibirá instrucciones contradictorias sobre cuándo transferir al agente humano.")
                    })

    # ════════════════════════════════════════════════════════════════════════ #
    # OPORTUNIDADES                                                            #
    # ════════════════════════════════════════════════════════════════════════ #
    opportunities = []
    for topic, (cov_lbl, _) in coverage_map.items():
        if cov_lbl == "Sin cobertura":
            opportunities.append(f"No existe artículo para: {topic}. FIN no podrá resolver consultas de este tipo.")
        elif cov_lbl == "Baja":
            opportunities.append(f"Hay muy poca documentación sobre: {topic}. FIN tendrá baja capacidad de resolución.")
    short_arts = [a for a in analyses if a["word_count"] < 60 and a["kde_health"] < 70]
    if short_arts:
        opportunities.append(
            f"{len(short_arts)} artículo(s) con contenido insuficiente (< 60 palabras): "
            f"{', '.join(repr(a['title']) for a in short_arts[:3])}. Ampliar para mejorar resolución de FIN."
        )
    if no_esc_list:
        opportunities.append(
            f"{len(no_esc_list)} artículo(s) sin criterio de escalamiento. "
            "FIN no tendrá instrucción de salida al agotar los pasos."
        )

    # ════════════════════════════════════════════════════════════════════════ #
    # PRIORIZACIÓN                                                             #
    # ════════════════════════════════════════════════════════════════════════ #
    priority_list = []
    for a in analyses:
        if a["has_kde_blocker"]:
            priority_list.append((0, f"CORREGIR '{a['title']}' — BLOQUEADO por: {', '.join(a['kde_blockers'])}."))
    for a in analyses:
        if a["loop_risk_level"] in ("ALTO","CRÍTICO") and not a["has_kde_blocker"]:
            priority_list.append((1, f"ELIMINAR LOOPS en '{a['title']}' — {a['loop_count']} patrón(es) detectado(s)."))
    for a in no_esc_list:
        priority_list.append((2, f"AGREGAR ESCALAMIENTO en '{a['title']}' — FIN no tiene instrucción de salida."))
    for topic, (cov_lbl, _) in coverage_map.items():
        if cov_lbl == "Sin cobertura":
            priority_list.append((3, f"CREAR ARTÍCULO para: {topic}."))
    blocked_titles = {a["title"] for a in analyses if a["has_kde_blocker"]}
    for a in sorted(analyses, key=lambda x: x["kde_health"]):
        if a["kde_health"] < 60 and a["title"] not in blocked_titles:
            priority_list.append((4, f"OPTIMIZAR '{a['title']}' — score {a['kde_health']}/100."))

    priority_list.sort(key=lambda x: x[0])
    unique_prios = []
    seen_prios = set()
    for _, desc in priority_list:
        k = desc[:80]
        if k not in seen_prios:
            seen_prios.add(k)
            unique_prios.append(desc)
    unique_prios = unique_prios[:10]

    # ════════════════════════════════════════════════════════════════════════ #
    # IMPACTO ESTIMADO                                                         #
    # ════════════════════════════════════════════════════════════════════════ #
    current_auto_res   = round(avg_health * 0.7)
    potential_auto_res = min(95, current_auto_res + len(unique_prios) * 4)
    esc_reduction      = min(60, blocked_count*15 + len(loop_articles)*10 + len(no_esc_list)*8)
    no_cov_count       = sum(1 for _, (lbl,_) in coverage_map.items() if lbl == "Sin cobertura")
    coverage_increase  = min(40, no_cov_count * 8)
    maintain_increase  = min(40, len(short_arts)*5 + len(duplicates)*8)

    # ════════════════════════════════════════════════════════════════════════ #
    # PLAN DE ACCIÓN                                                           #
    # ════════════════════════════════════════════════════════════════════════ #
    quick_wins = []
    medium_term = []
    long_term = []

    if anti_esc_articles:
        quick_wins.append(
            f"Eliminar la regla anti-escalamiento de {len(anti_esc_articles)} artículo(s): "
            f"{', '.join(repr(a['title']) for a in anti_esc_articles[:2])}.")
    if loop_articles:
        quick_wins.append(
            f"Eliminar patrones de bucle en {len(loop_articles)} artículo(s): "
            f"{', '.join(repr(a['title']) for a in loop_articles[:2])}.")
    if no_esc_list:
        quick_wins.append(
            f"Agregar criterio de escalamiento en {len(no_esc_list)} artículo(s) sin instrucción de salida.")
    if duplicates:
        quick_wins.append(
            f"Consolidar {len(duplicates)} par(es) de artículos duplicados para reducir confusión en FIN.")

    if abs_articles:
        medium_term.append(
            f"Reemplazar términos absolutos en {len(abs_articles)} artículo(s): "
            f"{', '.join(repr(a['title']) for a in abs_articles[:2])}.")
    no_cov_topics = [t for t,(lbl,_) in coverage_map.items() if lbl == "Sin cobertura"]
    if no_cov_topics:
        medium_term.append(
            f"Crear artículos para {len(no_cov_topics)} tema(s) sin cobertura: {', '.join(no_cov_topics[:4])}.")
    low_health_arts = [a for a in analyses if 50 <= a["kde_health"] < 70]
    if low_health_arts:
        medium_term.append(
            f"Optimizar {len(low_health_arts)} artículo(s) con score entre 50 y 70 "
            "para alcanzar el umbral de despliegue autónomo (≥ 78).")

    long_term.append("Establecer revisión periódica de la Base de Conocimiento (cada 30–60 días).")
    long_term.append("Usar audit_knowledge como paso de aprobación antes de publicar nuevos artículos para FIN.")
    if conflicts:
        long_term.append(f"Resolver {len(conflicts)} conflicto(s) de instrucciones entre artículos del mismo tema.")

    # ════════════════════════════════════════════════════════════════════════ #
    # CONSTRUCCIÓN DEL REPORTE                                                 #
    # ════════════════════════════════════════════════════════════════════════ #
    sep  = "=" * 48
    div2 = "─" * 40

    parts = []
    parts += [sep, "KNOWLEDGE REVIEW — FIN Knowledge Core", sep, ""]
    parts.append(f"PRODUCTO: {product.upper()}")
    if context:
        parts.append(f"CONTEXTO: {context}")
    parts.append(f"ARTÍCULOS ANALIZADOS: {n}")
    parts.append("")

    # Madurez general
    parts += [div2, "MADUREZ GENERAL", div2, ""]
    parts.append(f"  {maturity_emoji} Score promedio: {avg_health}/100 — {maturity}")
    parts.append(
        f"  LISTO: {ready_count}  |  "
        f"LISTO CON RECOMENDACIONES: {ready_recs_count}  |  "
        f"NO LISTO: {not_ready_count}  |  "
        f"BLOQUEADO: {blocked_count}"
    )
    parts.append("")

    # Resumen ejecutivo
    parts += [div2, "RESUMEN EJECUTIVO", div2, ""]
    if conclusion == "READY":
        parts.append("  ¿Preparada para FIN? Sí. La Base de Conocimiento cumple los estándares mínimos.")
    elif conclusion == "READY WITH RECOMMENDATIONS":
        parts.append("  ¿Preparada para FIN? Parcialmente. Requiere optimizaciones antes del despliegue completo.")
    elif conclusion == "NOT READY":
        parts.append("  ¿Preparada para FIN? No. Score insuficiente y artículos con problemas críticos sin resolver.")
    else:
        parts.append("  ¿Preparada para FIN? No. Bloqueadores críticos impiden cualquier despliegue.")

    if anti_esc_articles:
        parts.append(f"  Mayor riesgo: {len(anti_esc_articles)} artículo(s) con regla anti-escalamiento. FIN quedará sin salida al agotar los pasos.")
    elif loop_articles:
        parts.append(f"  Mayor riesgo: {len(loop_articles)} artículo(s) con loop instruccional. FIN puede repetir instrucciones indefinidamente.")
    elif no_esc_list:
        parts.append(f"  Mayor riesgo: {len(no_esc_list)} artículo(s) sin criterio de escalamiento. FIN no sabe cuándo transferir al agente humano.")
    else:
        parts.append(f"  Mayor riesgo: calidad general ({avg_health}/100). Aplicar recomendaciones para alcanzar el umbral de despliegue.")

    no_cov_list = [t for t,(lbl,_) in coverage_map.items() if lbl == "Sin cobertura"]
    low_cov_list = [t for t,(lbl,_) in coverage_map.items() if lbl == "Baja"]
    if no_cov_list:
        parts.append(f"  Mayor vacío: sin cobertura en {', '.join(no_cov_list[:4])}. FIN no podrá resolver consultas de estos temas.")
    elif low_cov_list:
        parts.append(f"  Mayor vacío: cobertura baja en {', '.join(low_cov_list[:3])}. FIN tendrá baja capacidad en esos temas.")
    else:
        parts.append("  Mayor vacío: calidad de artículos existentes. Mejorar los scores individuales para mayor resolución autónoma.")

    parts.append(
        f"  Impacto de mejorar: resolución autónoma podría subir de ~{current_auto_res}% a ~{potential_auto_res}% "
        f"aplicando las {len(unique_prios)} prioridades identificadas."
    )
    parts.append("")

    # Cobertura
    parts += [div2, "COBERTURA", div2, ""]
    cov_emoji = {"Alta": "🟢", "Media": "🔵", "Baja": "🔶", "Sin cobertura": "⬜"}
    cov_order = ["Alta", "Media", "Baja", "Sin cobertura"]
    for topic, (cov_lbl, titles) in sorted(coverage_map.items(), key=lambda x: cov_order.index(x[1][0])):
        parts.append(f"  {cov_emoji[cov_lbl]} {topic:<20} {cov_lbl}")
        if titles:
            parts.append(f"     └─ {', '.join(repr(t) for t in titles[:2])}")
    parts.append("")

    # Artículos críticos
    parts += [div2, "ARTÍCULOS CRÍTICOS", div2, ""]
    if critical_articles:
        for a in critical_articles[:8]:
            parts.append(f"  🔴 '{a['title']}' — score {a['kde_health']}/100")
            if a["problems"]:
                parts.append(f"     Motivo: {' | '.join(a['problems'][:4])}")
    else:
        parts.append("  ✅ No se detectaron artículos en estado crítico.")
    parts.append("")

    # Duplicados
    parts += [div2, "DUPLICADOS", div2, ""]
    if duplicates:
        for d in duplicates[:5]:
            parts.append(f"  ⚠️  Similitud {d['overlap']}%: '{d['title_i']}' ↔ '{d['title_j']}'")
            parts.append(f"     → Conservar: '{d['keep']}' | Revisar/eliminar: '{d['drop']}'")
    else:
        parts.append("  ✅ No se detectaron artículos con contenido duplicado.")
    parts.append("")

    # Conflictos
    parts += [div2, "CONFLICTOS", div2, ""]
    if conflicts:
        for c in conflicts[:5]:
            parts.append(f"  🔴 Tema: {c['topic']}")
            parts.append(f"     {c['desc']}")
    else:
        parts.append("  ✅ No se detectaron instrucciones incompatibles entre artículos.")
    parts.append("")

    # Oportunidades
    parts += [div2, "OPORTUNIDADES", div2, ""]
    if opportunities:
        for opp in opportunities[:8]:
            parts.append(f"  💡 {opp}")
    else:
        parts.append("  ✅ La Base de Conocimiento tiene cobertura suficiente en los temas analizados.")
    parts.append("")

    # Priorización
    parts += [div2, "PRIORIZACIÓN", div2, ""]
    if unique_prios:
        for idx, p in enumerate(unique_prios, 1):
            parts.append(f"  {idx}. {p}")
    else:
        parts.append("  ✅ No se identificaron acciones de alta prioridad.")
    parts.append("")

    # Impacto estimado
    parts += [div2, "IMPACTO ESTIMADO", div2, ""]
    parts.append(f"  Mejora en resolución autónoma .... +{potential_auto_res - current_auto_res}% (de ~{current_auto_res}% a ~{potential_auto_res}%)")
    parts.append(f"  Reducción de escalamientos ....... ~{esc_reduction}% menos transferencias innecesarias")
    parts.append(f"  Incremento de cobertura .......... +{coverage_increase} puntos porcentuales estimados")
    parts.append(f"  Incremento de mantenibilidad ..... +{maintain_increase} puntos porcentuales estimados")
    parts.append("")

    # Plan de acción
    parts += [div2, "PLAN DE ACCIÓN", div2, ""]
    parts.append("  Quick Wins (inmediato)")
    if quick_wins:
        for qw in quick_wins[:4]:
            parts.append(f"    → {qw}")
    else:
        parts.append("    → No se identificaron quick wins. La base está en buen estado general.")
    parts.append("")
    parts.append("  Mediano plazo (1–4 semanas)")
    if medium_term:
        for mt in medium_term[:4]:
            parts.append(f"    → {mt}")
    else:
        parts.append("    → Sin acciones de mediano plazo identificadas.")
    parts.append("")
    parts.append("  Largo plazo (proceso continuo)")
    for lt in long_term[:3]:
        parts.append(f"    → {lt}")
    parts.append("")

    # Conclusión
    parts += [div2, "CONCLUSIÓN", div2, ""]
    parts.append(f"  {concl_emoji} {conclusion}")
    parts.append(f"  {concl_why}")
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def repository_review(
    products: list,
    context: str = ""
) -> str:
    """
    Analiza el repositorio completo de un ecosistema FIN: guidelines y artículos de
    conocimiento de todos los productos. Genera un diagnóstico ejecutivo global con
    métricas consolidadas, Knowledge Debt, ranking de productos y roadmap de acción.

    products: lista de dicts con claves 'nombre', 'guidelines' (list[str]),
              'knowledge_articles' (list[str])
    context: contexto adicional opcional
    """

    import re
    import math

    # ── Per-product analysis ─────────────────────────────────────────────────

    product_results = []

    for prod in products:
        pname = prod.get("nombre", "Sin nombre")
        guidelines  = prod.get("guidelines", [])
        articles    = prod.get("knowledge_articles", [])

        # Guidelines analysis
        g_results = [_de.kde_score_guideline_fast(g) for g in guidelines]
        g_blocked_count   = sum(1 for r in g_results if r["blocked"])
        g_healths         = [r["health"] for r in g_results] if g_results else [100]
        g_avg_health      = round(sum(g_healths) / len(g_healths)) if g_healths else 100
        g_conflicts       = 0
        for i in range(len(g_results)):
            for j in range(i + 1, len(g_results)):
                sim = _de.jaccard(g_results[i]["words"], g_results[j]["words"])
                one_esc  = g_results[i]["has_escalation"] or g_results[j]["has_escalation"]
                one_anti = g_results[i]["anti_escalation"] or g_results[j]["anti_escalation"]
                if sim >= 0.30 and one_esc and one_anti:
                    g_conflicts += 1

        # Articles analysis
        a_results = [_de.kde_score_article_fast(a) for a in articles]
        a_blocked_count   = sum(1 for r in a_results if r["blocked"])
        a_critical_count  = sum(1 for r in a_results if r["risk"] == "ALTO")
        a_healths         = [r["health"] for r in a_results] if a_results else [100]
        a_avg_health      = round(sum(a_healths) / len(a_healths)) if a_healths else 100

        # Duplicates among articles
        a_dups = 0
        for i in range(len(a_results)):
            for j in range(i + 1, len(a_results)):
                if _de.jaccard(a_results[i]["words"], a_results[j]["words"]) >= 0.55:
                    a_dups += 1

        # Coverage
        all_art_text = " ".join(articles).lower()
        covered_cats   = [cat for cat, kws in _de.TOPIC_CATEGORIES.items() if any(k in all_art_text for k in kws)]
        missing_cats   = [cat for cat in _de.TOPIC_CATEGORIES if cat not in covered_cats]

        # Product-level health (weighted avg guidelines 40% + articles 60%)
        prod_health = round(g_avg_health * 0.4 + a_avg_health * 0.6)
        prod_blocked = (a_blocked_count > 0 or g_blocked_count > 0)
        if prod_blocked:
            prod_health = min(prod_health, 60)

        if prod_blocked or prod_health < 50:
            prod_risk = "ALTO"
        elif prod_health < 78:
            prod_risk = "MEDIO"
        else:
            prod_risk = "BAJO"

        product_results.append({
            "nombre": pname,
            "g_count": len(guidelines),
            "g_blocked": g_blocked_count,
            "g_avg_health": g_avg_health,
            "g_conflicts": g_conflicts,
            "a_count": len(articles),
            "a_blocked": a_blocked_count,
            "a_critical": a_critical_count,
            "a_avg_health": a_avg_health,
            "a_dups": a_dups,
            "covered_cats": covered_cats,
            "missing_cats": missing_cats,
            "prod_health": prod_health,
            "prod_blocked": prod_blocked,
            "prod_risk": prod_risk,
        })

    # ── Global aggregation ───────────────────────────────────────────────────

    total_products     = len(product_results)
    total_guidelines   = sum(r["g_count"]   for r in product_results)
    total_articles     = sum(r["a_count"]   for r in product_results)
    total_g_blocked    = sum(r["g_blocked"] for r in product_results)
    total_a_blocked    = sum(r["a_blocked"] for r in product_results)
    total_g_conflicts  = sum(r["g_conflicts"] for r in product_results)
    total_a_dups       = sum(r["a_dups"]   for r in product_results)
    total_a_critical   = sum(r["a_critical"] for r in product_results)

    # Global coverage
    all_text_global = " ".join(
        g for prod in products for g in prod.get("guidelines", [])
    ) + " " + " ".join(
        a for prod in products for a in prod.get("knowledge_articles", [])
    )
    globally_covered, globally_missing = _de.compute_coverage(all_text_global)
    global_coverage_pct = round(len(globally_covered) / len(_de.TOPIC_CATEGORIES) * 100)

    # Products blocked / at risk
    prod_blocked_count = sum(1 for r in product_results if r["prod_blocked"])
    prod_high_risk     = sum(1 for r in product_results if r["prod_risk"] == "ALTO")
    prod_medium_risk   = sum(1 for r in product_results if r["prod_risk"] == "MEDIO")
    prod_ready         = sum(1 for r in product_results if r["prod_risk"] == "BAJO" and not r["prod_blocked"])

    # Global health (avg of product healths)
    global_health = round(sum(r["prod_health"] for r in product_results) / total_products) if total_products else 100
    if prod_blocked_count > 0:
        global_health = min(global_health, 60)

    # Knowledge Debt
    knowledge_debt, _ = _de.compute_knowledge_debt(
        total_a_blocked, total_g_conflicts, total_a_dups,
        len(globally_missing), total_g_blocked,
        total_a_critical - total_a_blocked
    )
    debt_label, debt_emoji = _de.debt_label_emoji(knowledge_debt)

    # Global status
    global_status, global_emoji = _de.global_status_from_health(global_health, prod_blocked_count, prod_high_risk)

    # ── Ranking ──────────────────────────────────────────────────────────────

    ranked = sorted(product_results, key=lambda r: r["prod_health"], reverse=True)

    # ── Opportunities & Roadmap ───────────────────────────────────────────────

    quick_wins    = []
    sprint_items  = []
    medium_items  = []
    long_items    = []

    for r in product_results:
        pn = r["nombre"]
        if r["a_blocked"] > 0:
            sprint_items.append(f"[{pn}] Corregir {r['a_blocked']} artículo(s) BLOQUEADO(s) con anti-escalamiento o loop crítico")
        if r["g_blocked"] > 0:
            sprint_items.append(f"[{pn}] Revisar {r['g_blocked']} guideline(s) con regla que prohíbe escalamiento")
        if r["g_conflicts"] > 0:
            sprint_items.append(f"[{pn}] Resolver {r['g_conflicts']} conflicto(s) entre guidelines")
        if r["a_dups"] > 0:
            quick_wins.append(f"[{pn}] Consolidar {r['a_dups']} par(es) de artículos duplicados (Jaccard ≥ 55%)")
        if r["a_critical"] > r["a_blocked"]:
            medium_items.append(f"[{pn}] Mejorar {r['a_critical'] - r['a_blocked']} artículo(s) en riesgo ALTO")
        if r["missing_cats"]:
            medium_items.append(f"[{pn}] Crear artículos para: {', '.join(r['missing_cats'][:3])}")

    if globally_missing:
        long_items.append(f"Ampliar cobertura global a temas faltantes: {', '.join(globally_missing[:4])}")
    long_items.append("Implementar revisión trimestral de toda la base de conocimiento")
    long_items.append("Establecer proceso de versionado y auditoría continua de guidelines")

    top_opportunities = (sprint_items + quick_wins + medium_items)[:5]

    # ── Conclusion ────────────────────────────────────────────────────────────

    if prod_blocked_count > 0:
        conclusion     = "NOT READY"
        concl_emoji    = "🔴"
        concl_msg      = f"{prod_blocked_count} producto(s) BLOQUEADO(s) impiden el despliegue seguro del repositorio."
    elif prod_high_risk > 0 or knowledge_debt >= 45:
        conclusion     = "READY WITH RECOMMENDATIONS"
        concl_emoji    = "🟡"
        concl_msg      = f"El repositorio puede operar pero presenta {prod_high_risk} producto(s) en riesgo ALTO y Knowledge Debt {debt_label}."
    elif global_health >= 85 and knowledge_debt < 20:
        conclusion     = "READY"
        concl_emoji    = "🟢"
        concl_msg      = "El repositorio está en buen estado para operar con FIN. Mantener proceso de revisión continua."
    else:
        conclusion     = "READY WITH RECOMMENDATIONS"
        concl_emoji    = "🟡"
        concl_msg      = "El repositorio es funcional. Se recomienda atender las oportunidades de mejora identificadas."

    # ── Report ────────────────────────────────────────────────────────────────

    sep  = "=" * 70
    div1 = "─" * 70
    div2 = "─" * 40

    ctx_line = f"  Contexto: {context}" if context else ""

    parts = [sep]
    parts.append("  REPOSITORY REVIEW — FIN ARCHITECT")
    parts.append("  Análisis ejecutivo del repositorio completo")
    if ctx_line:
        parts.append(ctx_line)
    parts.append(sep)
    parts.append("")

    # RESUMEN EJECUTIVO
    parts += [div2, "RESUMEN EJECUTIVO", div2, ""]
    parts.append(f"  Estado global          : {global_emoji} {global_status}")
    parts.append(f"  Salud global           : {global_health}/100")
    parts.append(f"  Knowledge Debt         : {debt_emoji} {knowledge_debt}/100 ({debt_label})")
    parts.append(f"  Productos analizados   : {total_products}")
    parts.append(f"  Productos BLOQUEADOS   : {prod_blocked_count}")
    parts.append(f"  Productos en riesgo ALTO: {prod_high_risk}")
    parts.append(f"  Conclusión             : {concl_emoji} {conclusion}")
    parts.append("")

    # SALUD GENERAL
    parts += [div1, "SALUD GENERAL", div1, ""]
    _bar_filled = round(global_health / 10)
    _bar = "█" * _bar_filled + "░" * (10 - _bar_filled)
    parts.append(f"  [{_bar}] {global_health}/100")
    parts.append("")
    parts.append(f"  Guidelines totales : {total_guidelines}  |  Bloqueadas : {total_g_blocked}  |  Conflictos : {total_g_conflicts}")
    parts.append(f"  Artículos totales  : {total_articles}  |  Bloqueados : {total_a_blocked}  |  Duplicados : {total_a_dups}")
    parts.append(f"  Cobertura global   : {global_coverage_pct}%  ({len(globally_covered)}/{len(_de.TOPIC_CATEGORIES)} categorías)")
    parts.append("")

    # PRODUCTOS ANALIZADOS (tabla)
    parts += [div1, "PRODUCTOS ANALIZADOS", div1, ""]
    _hdr = f"  {'Producto':<22} {'Salud':>6} {'Riesgo':>8} {'G.':>4} {'G.Bloq':>7} {'Art.':>5} {'A.Bloq':>7} {'Dups':>5}"
    parts.append(_hdr)
    parts.append("  " + "-" * 66)
    for r in product_results:
        _risk_sym = "🔴" if r["prod_risk"] == "ALTO" else ("🟡" if r["prod_risk"] == "MEDIO" else "🟢")
        _bloq_sym = " ⛔" if r["prod_blocked"] else ""
        parts.append(
            f"  {r['nombre']:<22} {r['prod_health']:>5}/100 {_risk_sym+r['prod_risk']:>10} "
            f"{r['g_count']:>4} {r['g_blocked']:>7} {r['a_count']:>5} {r['a_blocked']:>7} {r['a_dups']:>5}{_bloq_sym}"
        )
    parts.append("")

    # RANKING DE PRODUCTOS
    parts += [div1, "RANKING DE PRODUCTOS", div1, ""]
    for idx, r in enumerate(ranked, 1):
        medal = ["🥇", "🥈", "🥉"][idx - 1] if idx <= 3 else f"  {idx}."
        _bloq = " ⛔ BLOQUEADO" if r["prod_blocked"] else ""
        parts.append(f"  {medal} {r['nombre']} — {r['prod_health']}/100{_bloq}")
    parts.append("")

    # COBERTURA GLOBAL
    parts += [div1, "COBERTURA GLOBAL", div1, ""]
    parts.append(f"  Cobertura : {global_coverage_pct}% ({len(globally_covered)}/{len(_de.TOPIC_CATEGORIES)} categorías)")
    parts.append(f"  Cubiertas : {', '.join(globally_covered) if globally_covered else 'Ninguna'}")
    parts.append(f"  Faltantes : {', '.join(globally_missing) if globally_missing else 'Ninguna — cobertura completa ✓'}")
    parts.append("")

    # GUIDELINES
    parts += [div1, "GUIDELINES", div1, ""]
    parts.append(f"  Total        : {total_guidelines}")
    parts.append(f"  Bloqueadas   : {total_g_blocked}")
    parts.append(f"  Conflictos   : {total_g_conflicts}")
    for r in product_results:
        if r["g_count"] > 0:
            _g_sym = "⛔" if r["g_blocked"] else ("⚠️" if r["g_conflicts"] else "✅")
            parts.append(f"    {_g_sym} [{r['nombre']}] {r['g_count']} guidelines — Salud promedio: {r['g_avg_health']}/100")
    parts.append("")

    # BASE DE CONOCIMIENTO
    parts += [div1, "BASE DE CONOCIMIENTO", div1, ""]
    parts.append(f"  Total artículos   : {total_articles}")
    parts.append(f"  BLOQUEADOS        : {total_a_blocked}")
    parts.append(f"  Riesgo ALTO       : {total_a_critical}")
    parts.append(f"  Duplicados        : {total_a_dups} par(es)")
    parts.append("")
    for r in product_results:
        if r["a_count"] > 0:
            _a_sym = "⛔" if r["a_blocked"] else ("⚠️" if r["a_critical"] > 0 else "✅")
            _missing_str = f" | Faltantes: {', '.join(r['missing_cats'][:2])}" if r["missing_cats"] else ""
            parts.append(
                f"    {_a_sym} [{r['nombre']}] {r['a_count']} artículos — "
                f"Salud prom: {r['a_avg_health']}/100 | Bloq: {r['a_blocked']}{_missing_str}"
            )
    parts.append("")

    # KNOWLEDGE DEBT
    parts += [div1, "KNOWLEDGE DEBT", div1, ""]
    _debt_bar_filled = round(knowledge_debt / 10)
    _debt_bar = "█" * _debt_bar_filled + "░" * (10 - _debt_bar_filled)
    parts.append(f"  {debt_emoji} [{_debt_bar}] {knowledge_debt}/100 — {debt_label}")
    parts.append("")
    parts.append("  Composición de la deuda:")
    parts.append(f"    • Artículos bloqueados    : {total_a_blocked} × 15 = {total_a_blocked * 15} pts")
    parts.append(f"    • Conflictos guidelines   : {total_g_conflicts} × 10 = {total_g_conflicts * 10} pts")
    parts.append(f"    • Artículos duplicados    : {total_a_dups} × 8  = {total_a_dups * 8} pts")
    parts.append(f"    • Categorías sin cubrir   : {len(globally_missing)} × 12 = {len(globally_missing) * 12} pts")
    parts.append(f"    • Guidelines bloqueadas   : {total_g_blocked} × 8  = {total_g_blocked * 8} pts")
    _non_blocked_critical = max(0, total_a_critical - total_a_blocked)
    parts.append(f"    • Críticos no bloqueados  : {_non_blocked_critical} × 5  = {_non_blocked_critical * 5} pts")
    _debt_raw = (total_a_blocked * 15 + total_g_conflicts * 10 + total_a_dups * 8
                 + len(globally_missing) * 12 + total_g_blocked * 8 + _non_blocked_critical * 5)
    parts.append(f"    Total raw: {_debt_raw} pts  →  Debt score: {knowledge_debt}/100")
    parts.append("")

    # TOP OPORTUNIDADES
    parts += [div1, "TOP OPORTUNIDADES", div1, ""]
    if top_opportunities:
        for i, opp in enumerate(top_opportunities, 1):
            parts.append(f"  {i}. {opp}")
    else:
        parts.append("  ✅ No se identificaron oportunidades críticas. El repositorio está en buen estado.")
    parts.append("")

    # ROADMAP
    parts += [div1, "ROADMAP DE ACCIÓN", div1, ""]
    parts.append("  🚀 Quick Wins (< 48 h)")
    if quick_wins:
        for qw in quick_wins[:4]:
            parts.append(f"    → {qw}")
    else:
        parts.append("    → Sin quick wins identificados.")
    parts.append("")
    parts.append("  ⚡ Sprint (1–2 semanas)")
    if sprint_items:
        for si in sprint_items[:5]:
            parts.append(f"    → {si}")
    else:
        parts.append("    → Sin ítems urgentes de sprint.")
    parts.append("")
    parts.append("  📋 Mediano plazo (1–4 semanas)")
    if medium_items:
        for mi in medium_items[:4]:
            parts.append(f"    → {mi}")
    else:
        parts.append("    → Sin acciones de mediano plazo identificadas.")
    parts.append("")
    parts.append("  🔭 Largo plazo (proceso continuo)")
    for lt in long_items[:3]:
        parts.append(f"    → {lt}")
    parts.append("")

    # MÉTRICAS GLOBALES
    parts += [div1, "MÉTRICAS GLOBALES", div1, ""]
    parts.append(f"  Salud global del repositorio : {global_health}/100")
    parts.append(f"  Knowledge Debt               : {knowledge_debt}/100 ({debt_label})")
    parts.append(f"  Cobertura temática           : {global_coverage_pct}%")
    parts.append(f"  Productos listos (BAJO)      : {prod_ready}/{total_products}")
    parts.append(f"  Productos en riesgo (ALTO)   : {prod_high_risk}/{total_products}")
    parts.append(f"  Productos bloqueados         : {prod_blocked_count}/{total_products}")
    parts.append(f"  Guidelines con conflicto     : {total_g_conflicts}")
    parts.append(f"  Artículos duplicados         : {total_a_dups} par(es)")
    parts.append("")

    # RECOMENDACIONES EJECUTIVAS
    parts += [div1, "RECOMENDACIONES EJECUTIVAS", div1, ""]
    parts.append("  👤 Director de Soporte")
    if prod_blocked_count > 0:
        parts.append(f"    → Detener despliegue: {prod_blocked_count} producto(s) presentan bloqueos críticos que generarían loops o cierres incorrectos.")
    elif prod_high_risk > 0:
        parts.append(f"    → Supervisar de cerca: {prod_high_risk} producto(s) en riesgo ALTO requieren atención antes de ampliar el alcance de FIN.")
    else:
        parts.append("    → El repositorio está en condiciones aceptables para operar. Mantener revisión periódica.")
    parts.append("")
    parts.append("  👤 Product Manager (FIN)")
    if knowledge_debt >= 45:
        parts.append(f"    → Priorizar reducción del Knowledge Debt ({knowledge_debt}/100 — {debt_label}) en el próximo sprint.")
    if globally_missing:
        parts.append(f"    → Planificar creación de contenido para {len(globally_missing)} categoría(s) sin cobertura.")
    if knowledge_debt < 20 and not globally_missing:
        parts.append("    → Repositorio maduro. Enfocarse en mantenimiento y mejora continua de calidad.")
    parts.append("")
    parts.append("  👤 Administrador FIN")
    if total_a_dups > 0:
        parts.append(f"    → Consolidar {total_a_dups} par(es) de artículos duplicados para evitar respuestas inconsistentes.")
    if total_g_conflicts > 0:
        parts.append(f"    → Resolver {total_g_conflicts} conflicto(s) entre guidelines antes de la próxima carga.")
    if total_a_dups == 0 and total_g_conflicts == 0:
        parts.append("    → Estructura del repositorio limpia. Continuar con el proceso de versionado establecido.")
    parts.append("")

    # CONCLUSIÓN
    parts += [div2, "CONCLUSIÓN", div2, ""]
    parts.append(f"  {concl_emoji} {conclusion}")
    parts.append(f"  {concl_msg}")
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def recommend_improvements(
    repository_review: str = "",
    knowledge_review: str = "",
    architect_review: str = "",
    context: str = ""
) -> str:
    """
    Analiza los resultados del ecosistema FIN Architect MCP y construye un plan
    priorizado de mejoras con el mayor retorno esperado para FIN.

    Toma decisiones, prioriza y recomienda. No audita, no puntúa, no revisa.

    repository_review: salida de la herramienta repository_review (str, opcional)
    knowledge_review : salida de la herramienta knowledge_review  (str, opcional)
    architect_review : salida de la herramienta architect_review  (str, opcional)
    context          : contexto adicional opcional
    """

    import re

    # ── Extracción de señales ────────────────────────────────────────────────

    combined = "\n".join([repository_review, knowledge_review, architect_review, context])
    cl = combined.lower()

    _metrics = _de.extract_metrics_from_reports(repository_review, knowledge_review, architect_review)
    global_health      = _metrics["global_health"]
    knowledge_debt     = _metrics["knowledge_debt"]
    prod_blocked       = _metrics["prod_blocked"]
    prod_high_risk     = _metrics["prod_high_risk"]
    total_a_blocked    = _metrics["total_a_blocked"]
    total_g_blocked    = _metrics["total_g_blocked"]
    total_g_conflicts  = _metrics["total_g_conflicts"]
    total_a_dups       = _metrics["total_a_dups"]
    coverage_pct       = _metrics["coverage_pct"]
    missing_cats_str   = _metrics["missing_cats_str"]
    missing_cats_count = _metrics["missing_cats_count"]
    has_rr             = _metrics["has_rr"]
    has_kr             = _metrics["has_kr"]
    has_ar             = _metrics["has_ar"]

    # ── Construcción de señales de mejora ────────────────────────────────────
    # Cada mejora: {nombre, desc, reason, impact, effort, roi, priority, tags}

    improvements = []

    def _add(nombre, desc, reason, impact, effort, tags=None):
        improvements.append({
            "nombre": nombre,
            "desc": desc,
            "reason": reason,
            "impact": impact,
            "effort": effort,
            "roi": _de.compute_roi(impact, effort),
            "tags": tags or [],
        })

    # Bloqueos de artículos
    if total_a_blocked > 0:
        _add(
            "Desbloquear artículos críticos",
            f"Corregir los {total_a_blocked} artículo(s) BLOQUEADO(s): eliminar reglas de anti-escalamiento absoluto y resolver loops instruccionales CRÍTICOS.",
            "Los artículos bloqueados generan cierres incorrectos y loops en FIN, dañando directamente la experiencia del cliente.",
            impact=5, effort=2,
            tags=["sprint", "knowledge", "blocker"]
        )

    # Bloqueos de guidelines
    if total_g_blocked > 0:
        _add(
            "Corregir guidelines bloqueadas",
            f"Revisar y reescribir las {total_g_blocked} guideline(s) con reglas absolutas que prohíben el escalamiento.",
            "Las guidelines bloqueadas instruyen a FIN a nunca escalar, lo que puede dejar casos sin resolver indefinidamente.",
            impact=5, effort=2,
            tags=["sprint", "guidelines", "blocker"]
        )

    # Conflictos entre guidelines
    if total_g_conflicts > 0:
        _add(
            "Resolver conflictos entre guidelines",
            f"Alinear las {total_g_conflicts} guideline(s) en conflicto: instrucciones de escalamiento contradictorias sobre el mismo tema.",
            "Los conflictos producen comportamiento impredecible de FIN: en el mismo escenario puede escalar o no según qué guideline aplique.",
            impact=4, effort=2,
            tags=["sprint", "guidelines"]
        )

    # Artículos duplicados
    if total_a_dups > 0:
        _add(
            "Consolidar artículos duplicados",
            f"Fusionar los {total_a_dups} par(es) de artículos con similitud ≥ 55% (Jaccard) en artículos únicos y completos.",
            "Los duplicados generan respuestas inconsistentes: FIN puede dar dos respuestas distintas al mismo problema según qué artículo recupere.",
            impact=3, effort=1,
            tags=["quick_win", "knowledge"]
        )

    # Cobertura temática
    if missing_cats_count > 0:
        _add(
            "Ampliar cobertura temática",
            f"Crear artículos y/o guidelines para las {missing_cats_count} categoría(s) sin cobertura: {missing_cats_str[:80]}.",
            "Las categorías sin cobertura son puntos ciegos de FIN: cuando un cliente consulta sobre esos temas, FIN no tiene información y escala o responde incorrectamente.",
            impact=4, effort=3,
            tags=["mediano_plazo", "knowledge", "producto"]
        )

    # Health score bajo
    if global_health < 70:
        _add(
            "Mejorar salud general del repositorio",
            "Aumentar el porcentaje de artículos con estructura completa (objetivo, pasos, resultado, escalamiento).",
            f"El repositorio tiene una salud de {global_health}/100. Artículos incompletos producen respuestas parciales y mayor tasa de escalamiento innecesario.",
            impact=4, effort=3,
            tags=["mediano_plazo", "knowledge"]
        )
    elif global_health < 85:
        _add(
            "Optimizar estructura de artículos existentes",
            "Revisar artículos con salud < 78 y completar las secciones faltantes (pasos, resolución, escalamiento).",
            f"Con salud actual {global_health}/100 hay margen para mejorar significativamente la resolución autónoma de FIN.",
            impact=3, effort=2,
            tags=["sprint", "knowledge"]
        )

    # Knowledge Debt alto
    if knowledge_debt >= 45:
        _add(
            "Reducir Knowledge Debt",
            f"Implementar un sprint dedicado a reducir el Knowledge Debt ({knowledge_debt}/100): priorizar bloqueos, conflictos y duplicados.",
            "Un Knowledge Debt alto indica deuda técnica acumulada que se compone con el tiempo: cada semana sin atención hace el problema más costoso de resolver.",
            impact=4, effort=3,
            tags=["sprint", "estratégico"]
        )

    # Productos en alto riesgo
    if prod_high_risk > 0:
        _add(
            f"Atender productos en riesgo ALTO",
            f"Priorizar los {prod_high_risk} producto(s) con riesgo ALTO: auditar artículos y guidelines producto por producto.",
            "Los productos en riesgo ALTO concentran la mayoría de los problemas. Atenderlos individualmente tiene el mayor impacto marginal sobre la salud global.",
            impact=4, effort=3,
            tags=["sprint", "estratégico"]
        )

    # Proceso de revisión periódica (siempre recomendable)
    _add(
        "Establecer revisión periódica del repositorio",
        "Implementar un ciclo trimestral de repository_review + knowledge_review para detectar degradación antes de que impacte en producción.",
        "Sin revisión periódica, el repositorio se degrada silenciosamente a medida que FIN opera y el negocio evoluciona.",
        impact=3, effort=1,
        tags=["quick_win", "proceso", "estratégico"]
    )

    # Versionado de guidelines
    _add(
        "Implementar versionado de guidelines y artículos",
        "Registrar la versión, autor y fecha de última revisión en cada guideline y artículo.",
        "Sin versionado es imposible saber qué guideline generó un comportamiento problemático ni cuándo fue introducido el error.",
        impact=3, effort=2,
        tags=["mediano_plazo", "proceso"]
    )

    # Completar con mejora de cobertura de escalamiento si no hay conflictos
    if total_g_conflicts == 0 and total_g_blocked == 0:
        _add(
            "Mapear rutas de escalamiento por producto",
            "Crear o revisar guidelines de escalamiento específicas para cada producto, asegurando que cada escenario de fallo tenga una ruta clara.",
            "Incluso sin conflictos, la ausencia de rutas de escalamiento explícitas deja a FIN sin instrucciones en los casos límite.",
            impact=3, effort=2,
            tags=["mediano_plazo", "guidelines"]
        )

    # Ordenar por ROI desc, luego impact desc
    improvements = _de.rank_improvements(improvements)

    # Top 10
    top10 = improvements[:10]

    # Asignar prioridad numérica
    for i, imp in enumerate(top10, 1):
        imp["priority"] = i

    # ── Segmentación ─────────────────────────────────────────────────────────

    quick_wins    = [i for i in top10 if i["impact"] >= 4 and i["effort"] <= 2]
    strategic     = [i for i in top10 if i["impact"] >= 4 and i["effort"] >= 3]
    defer_list    = [i for i in improvements[10:] if i["impact"] <= 2]

    # ── Simulación de impacto ─────────────────────────────────────────────────

    def _simulate(n: int) -> dict:
        selected = top10[:n]
        _tags_all = set(t for i in selected for t in i["tags"])

        # Health improvement
        _health_delta = 0
        if any("blocker" in i["tags"] for i in selected):
            _health_delta += min(20, total_a_blocked * 5 + total_g_blocked * 4)
        if any("guidelines" in i["tags"] for i in selected):
            _health_delta += min(8, total_g_conflicts * 3)
        if any("knowledge" in i["tags"] for i in selected):
            _health_delta += min(6, (85 - global_health) // 2)
        new_health = min(100, global_health + _health_delta)

        # Escalamiento reduction
        _esc_reduction = 0
        if total_a_blocked > 0 and any("blocker" in i["tags"] for i in selected):
            _esc_reduction += 15
        if total_g_conflicts > 0 and any("guidelines" in i["tags"] for i in selected):
            _esc_reduction += 8
        if total_a_dups > 0 and any("knowledge" in i["tags"] for i in selected):
            _esc_reduction += 5
        _esc_reduction = min(35, _esc_reduction)

        # Resolución autónoma
        _resolution_delta = round(_esc_reduction * 0.7)

        # Cobertura
        _cov_delta = 0
        if any("producto" in i["tags"] for i in selected):
            _cov_delta = min(missing_cats_count * 9, 25)
        new_coverage = min(100, coverage_pct + _cov_delta)

        # Knowledge Debt reduction
        _debt_delta = 0
        if any("blocker" in i["tags"] for i in selected):
            _debt_delta += total_a_blocked * 10 + total_g_blocked * 6
        if any("guidelines" in i["tags"] for i in selected):
            _debt_delta += total_g_conflicts * 7
        if any("knowledge" in i["tags"] for i in selected):
            _debt_delta += total_a_dups * 5 + missing_cats_count * 6
        _debt_reduction = min(knowledge_debt, round(_debt_delta / 2))
        new_debt = max(0, knowledge_debt - _debt_reduction)

        return {
            "health": new_health,
            "health_delta": new_health - global_health,
            "esc_reduction": _esc_reduction,
            "resolution_delta": _resolution_delta,
            "coverage": new_coverage,
            "coverage_delta": new_coverage - coverage_pct,
            "debt": new_debt,
            "debt_delta": _debt_reduction,
        }

    sim3  = _simulate(3)
    sim5  = _simulate(5)
    sim10 = _simulate(10)

    # ── Estimación global de mejora ───────────────────────────────────────────

    main_problem = ""
    top_action   = ""
    improvement_pct = sim10["health_delta"]

    if prod_blocked > 0 or total_a_blocked > 0 or total_g_blocked > 0:
        main_problem = f"Existen bloqueos activos ({total_a_blocked} artículo(s) y {total_g_blocked} guideline(s)) que impiden el funcionamiento correcto de FIN."
        top_action   = "Eliminar todos los bloqueos (anti-escalamiento absoluto y loops CRÍTICOS) antes de cualquier otra mejora."
    elif total_g_conflicts > 0:
        main_problem = f"Hay {total_g_conflicts} conflicto(s) entre guidelines que generan comportamiento impredecible de FIN."
        top_action   = "Resolver los conflictos de escalamiento entre guidelines para que FIN tenga instrucciones coherentes."
    elif knowledge_debt >= 45:
        main_problem = f"El Knowledge Debt acumulado ({knowledge_debt}/100) indica deuda técnica que se agrava con el tiempo."
        top_action   = "Ejecutar un sprint de reducción de Knowledge Debt: duplicados, cobertura y artículos en riesgo ALTO."
    elif global_health < 70:
        main_problem = f"La salud global del repositorio ({global_health}/100) está por debajo del umbral mínimo para operar con confianza."
        top_action   = "Mejorar la estructura de los artículos existentes para alcanzar un mínimo de 78/100 de salud promedio."
    else:
        main_problem = "El repositorio está en condiciones aceptables. El principal riesgo es la degradación silenciosa sin revisión periódica."
        top_action   = "Implementar un ciclo de revisión trimestral para mantener la calidad y detectar problemas antes de que escalen."

    # ── Roadmap ───────────────────────────────────────────────────────────────

    roadmap_week   = [i for i in top10 if "quick_win" in i["tags"] or ("sprint" in i["tags"] and i["effort"] <= 2)]
    roadmap_sprint = [i for i in top10 if "sprint" in i["tags"] and i not in roadmap_week]
    roadmap_month  = [i for i in top10 if "mediano_plazo" in i["tags"]]
    roadmap_qtr    = [i for i in improvements if "estratégico" in i["tags"] and i not in top10]

    # ── Riesgos si no se implementa ───────────────────────────────────────────

    risks = []
    if total_a_blocked > 0 or total_g_blocked > 0:
        risks.append(
            f"Si no se corrigen los {total_a_blocked + total_g_blocked} bloqueo(s), FIN continuará cerrando conversaciones sin resolver y generando loops: "
            "el cliente experimenta respuestas circulares sin salida, lo que daña la confianza y aumenta el volumen de escalamientos manuales."
        )
    if total_g_conflicts > 0:
        risks.append(
            f"Si no se resuelven los {total_g_conflicts} conflicto(s) entre guidelines, FIN tomará decisiones contradictorias según el orden de recuperación de documentos. "
            "Este comportamiento es difícil de diagnosticar y se manifiesta como inconsistencia percibida por el cliente."
        )
    if total_a_dups > 0:
        risks.append(
            f"Mantener {total_a_dups} par(es) de artículos duplicados sin consolidar genera respuestas inconsistentes a preguntas idénticas, "
            "erosionando la percepción de confiabilidad de FIN."
        )
    if missing_cats_count > 0:
        risks.append(
            f"Sin ampliar la cobertura a las {missing_cats_count} categoría(s) faltantes, FIN tendrá puntos ciegos permanentes. "
            "Cuando un cliente consulte sobre esos temas, FIN escalará innecesariamente o responderá con información genérica incorrecta."
        )
    if knowledge_debt >= 45:
        risks.append(
            f"El Knowledge Debt de {knowledge_debt}/100 se compone con el tiempo: cada ciclo de operación sin mejoras añade nuevos duplicados, "
            "amplía los gaps de cobertura y acumula más inconsistencias. En 3–6 meses el costo de corrección puede ser 3–5× mayor."
        )
    if not risks:
        risks.append(
            "El repositorio está en buen estado. El principal riesgo es la degradación silenciosa: sin revisión periódica, "
            "la calidad del repositorio disminuye gradualmente a medida que el negocio evoluciona y se agregan contenidos sin auditar."
        )

    # ── Reporte ───────────────────────────────────────────────────────────────

    sep  = "=" * 70
    div1 = "─" * 70
    div2 = "─" * 40

    def _impact_label(v):
        return ["", "Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"][v]

    def _effort_label(v):
        return ["", "Mínimo", "Bajo", "Medio", "Alto", "Muy alto"][v]

    ctx_line = f"  Contexto: {context}" if context else ""
    _sources = ", ".join(filter(None, [
        "repository_review" if has_rr else "",
        "knowledge_review"  if has_kr else "",
        "architect_review"  if has_ar else "",
    ])) or "sin datos externos (estimaciones base)"

    parts = [sep]
    parts.append("  RECOMMEND IMPROVEMENTS — FIN ARCHITECT")
    parts.append("  Plan priorizado de mejoras con mayor retorno para FIN")
    if ctx_line:
        parts.append(ctx_line)
    parts.append(f"  Fuentes: {_sources}")
    parts.append(sep)
    parts.append("")

    # RESUMEN EJECUTIVO
    parts += [div2, "RESUMEN EJECUTIVO", div2, ""]
    parts.append(f"  ❓ Principal problema")
    parts.append(f"     {main_problem}")
    parts.append("")
    parts.append(f"  🎯 Acción con mayor impacto")
    parts.append(f"     {top_action}")
    parts.append("")
    parts.append(f"  📈 Mejora esperada si se implementan las 10 recomendaciones")
    parts.append(f"     Health Score: {global_health}/100 → {sim10['health']}/100 (+{sim10['health_delta']} pts)")
    parts.append(f"     Knowledge Debt: {knowledge_debt}/100 → {sim10['debt']}/100 (-{sim10['debt_delta']} pts)")
    parts.append(f"     Escalamientos innecesarios: ↓ ~{sim10['esc_reduction']}%")
    parts.append(f"     Resolución autónoma: ↑ ~{sim10['resolution_delta']}%")
    parts.append("")

    # TOP RECOMENDACIONES
    parts += [div1, "TOP RECOMENDACIONES", div1, ""]
    for imp in top10:
        _impact_str = _impact_label(imp["impact"])
        _effort_str = _effort_label(imp["effort"])
        _roi_stars  = "★" * min(5, round(imp["roi"] * 2)) + "☆" * max(0, 5 - min(5, round(imp["roi"] * 2)))
        parts.append(f"  #{imp['priority']}  {imp['nombre']}")
        parts.append(f"      Descripción  : {imp['desc']}")
        parts.append(f"      Razón        : {imp['reason']}")
        parts.append(f"      Impacto      : {_impact_str} ({imp['impact']}/5)")
        parts.append(f"      Esfuerzo     : {_effort_str} ({imp['effort']}/5)")
        parts.append(f"      ROI          : {_roi_stars}  {imp['roi']}")
        parts.append(f"      Prioridad    : #{imp['priority']}")
        parts.append("")

    # QUICK WINS
    parts += [div1, "QUICK WINS  (Alto impacto · Bajo esfuerzo)", div1, ""]
    if quick_wins:
        for qw in quick_wins:
            parts.append(f"  ⚡ #{qw['priority']} {qw['nombre']}  — ROI {qw['roi']} | Impacto {qw['impact']}/5 | Esfuerzo {qw['effort']}/5")
            parts.append(f"       {qw['desc'][:100]}")
            parts.append("")
    else:
        parts.append("  No se identificaron quick wins con los datos disponibles.")
        parts.append("")

    # PROYECTOS ESTRATÉGICOS
    parts += [div1, "PROYECTOS ESTRATÉGICOS  (Muy alto impacto · Mediano–Alto esfuerzo)", div1, ""]
    if strategic:
        for st in strategic:
            parts.append(f"  🏗️  #{st['priority']} {st['nombre']}  — ROI {st['roi']} | Impacto {st['impact']}/5 | Esfuerzo {st['effort']}/5")
            parts.append(f"       {st['desc'][:100]}")
            parts.append("")
    else:
        parts.append("  No se identificaron proyectos estratégicos. El repositorio está en buen estado.")
        parts.append("")

    # NO HACER TODAVÍA
    parts += [div1, "NO HACER TODAVÍA", div1, ""]
    if defer_list:
        for d in defer_list[:5]:
            parts.append(f"  ⏸️  {d['nombre']}  — Impacto {d['impact']}/5 | Esfuerzo {d['effort']}/5")
            parts.append(f"       Por qué esperar: bajo impacto relativo al esfuerzo requerido (ROI {d['roi']}). "
                         "Atender primero los bloqueadores y quick wins antes de invertir aquí.")
            parts.append("")
    else:
        parts.append("  Todas las mejoras identificadas tienen ROI positivo. No hay ítems que diferir.")
        parts.append("")

    # SIMULACIÓN DE IMPACTO
    parts += [div1, "SIMULACIÓN DE IMPACTO", div1, ""]
    for label, sim, n in [("Top 3", sim3, 3), ("Top 5", sim5, 5), ("Top 10", sim10, 10)]:
        parts.append(f"  📊 Si implementas el {label}:")
        parts.append(f"     Health Score             : {global_health}/100 → {sim['health']}/100  (+{sim['health_delta']} pts)")
        parts.append(f"     Reducción escalamientos  : ↓ ~{sim['esc_reduction']}%")
        parts.append(f"     Resolución autónoma      : ↑ ~{sim['resolution_delta']}%")
        parts.append(f"     Cobertura temática       : {coverage_pct}% → {sim['coverage']}%  (+{sim['coverage_delta']} pp)")
        parts.append(f"     Knowledge Debt           : {knowledge_debt}/100 → {sim['debt']}/100  (-{sim['debt_delta']} pts)")
        parts.append("")

    # ROADMAP RECOMENDADO
    parts += [div1, "ROADMAP RECOMENDADO", div1, ""]
    parts.append("  📅 Esta semana")
    if roadmap_week:
        for r in roadmap_week[:4]:
            parts.append(f"     → #{r['priority']} {r['nombre']}")
    else:
        parts.append("     → Revisar el estado actual del repositorio con repository_review")
    parts.append("")
    parts.append("  ⚡ Próximo Sprint (1–2 semanas)")
    if roadmap_sprint:
        for r in roadmap_sprint[:4]:
            parts.append(f"     → #{r['priority']} {r['nombre']}")
    else:
        parts.append("     → Completar las acciones de esta semana")
    parts.append("")
    parts.append("  📋 Próximo Mes")
    if roadmap_month:
        for r in roadmap_month[:4]:
            parts.append(f"     → #{r['priority']} {r['nombre']}")
    else:
        parts.append("     → Revisión de cobertura y calidad general")
    parts.append("")
    parts.append("  🔭 Próximo Trimestre")
    if roadmap_qtr:
        for r in roadmap_qtr[:3]:
            parts.append(f"     → {r['nombre']}")
    else:
        parts.append("     → Auditoría completa y planificación del siguiente ciclo")
    parts.append("")

    # RECOMENDACIONES POR ROL
    parts += [div1, "RECOMENDACIONES POR ROL", div1, ""]

    parts.append("  👤 Director de Soporte")
    if prod_blocked > 0 or total_a_blocked > 0 or total_g_blocked > 0:
        parts.append(f"     Exigir la corrección inmediata de los {total_a_blocked + total_g_blocked} bloqueo(s) antes de ampliar el alcance de FIN.")
        parts.append("     No autorizar nuevos despliegues hasta que el repositorio esté libre de bloqueos.")
    elif prod_high_risk > 0:
        parts.append(f"     Supervisar los {prod_high_risk} producto(s) en riesgo ALTO. Solicitar plan de acción en el próximo sprint.")
    else:
        parts.append("     El repositorio está en condiciones aceptables. Mantener el ciclo de revisión periódica.")
    parts.append("")

    parts.append("  👤 Product Manager (FIN)")
    if knowledge_debt >= 45:
        parts.append(f"     Incluir reducción de Knowledge Debt ({knowledge_debt}/100) como ítem de sprint en el próximo ciclo.")
    if missing_cats_count > 0:
        parts.append(f"     Planificar la creación de contenido para {missing_cats_count} categoría(s) sin cobertura.")
    parts.append("     Priorizar el backlog de mejoras usando el ranking de ROI de este reporte.")
    parts.append("")

    parts.append("  👤 Administrador de FIN")
    if total_a_blocked > 0:
        parts.append(f"     Identificar y reescribir los {total_a_blocked} artículo(s) bloqueados esta semana.")
    if total_g_conflicts > 0:
        parts.append(f"     Resolver los {total_g_conflicts} conflicto(s) entre guidelines antes de la próxima carga de contenido.")
    if total_a_dups > 0:
        parts.append(f"     Consolidar los {total_a_dups} par(es) de artículos duplicados para eliminar inconsistencias.")
    if total_a_blocked == 0 and total_g_conflicts == 0 and total_a_dups == 0:
        parts.append("     Implementar el proceso de versionado y auditoría periódica del repositorio.")
    parts.append("")

    parts.append("  👤 Equipo de Knowledge")
    if missing_cats_count > 0:
        parts.append(f"     Redactar artículos para las {missing_cats_count} categoría(s) sin cobertura: {missing_cats_str[:60]}.")
    if total_a_blocked > 0:
        parts.append("     Al reescribir artículos bloqueados: asegurar secciones de objetivo, pasos, resultado y escalamiento.")
    parts.append("     Adoptar la herramienta optimize_article para garantizar calidad estructural antes de publicar.")
    parts.append("")

    parts.append("  👤 Equipo de Producto")
    parts.append("     Definir los SLA de calidad del repositorio: health mínimo aceptable, Knowledge Debt máximo tolerable.")
    parts.append("     Integrar audit_knowledge y knowledge_review en el proceso de aprobación de nuevos contenidos.")
    if global_health < 85:
        parts.append(f"     Establecer objetivo de health score ≥ 85/100 (actual: {global_health}/100) como meta de producto.")
    parts.append("")

    # RIESGOS
    parts += [div1, "RIESGOS SI NO SE IMPLEMENTAN LAS RECOMENDACIONES", div1, ""]
    for i, risk in enumerate(risks, 1):
        parts.append(f"  ⚠️  Riesgo {i}")
        parts.append(f"     {risk}")
        parts.append("")

    # CONCLUSIÓN
    parts += [div2, "CONCLUSIÓN", div2, ""]
    if top10:
        best = top10[0]
        parts.append(f"  🏆 Mejor inversión de tiempo para mejorar FIN:")
        parts.append(f"     «{best['nombre']}»")
        parts.append("")
        parts.append(f"     {best['reason']}")
        parts.append("")
        parts.append(f"     Con ROI {best['roi']} es la acción que ofrece el mayor retorno relativo al esfuerzo requerido.")
        if sim3["health_delta"] > 0:
            parts.append(f"     Solo el Top 3 elevaría la salud del repositorio de {global_health} a {sim3['health']}/100.")
    else:
        parts.append("  El repositorio no presenta problemas críticos. La mejor inversión es mantener el proceso de revisión periódica.")
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def fin_dashboard(
    products: list,
    context: str = ""
) -> str:
    """
    Dashboard Ejecutivo unificado del estado completo de FIN.
    Punto de entrada para cualquier líder que quiera conocer el estado del ecosistema.

    Reutiliza internamente la lógica de repository_review y recommend_improvements
    sin reimplementar ninguna lógica propia de análisis.

    products : lista de dicts con 'nombre', 'guidelines' (list[str]),
               'knowledge_articles' (list[str])
    context  : contexto adicional opcional
    """

    # ── Paso 1: ejecutar repository_review ───────────────────────────────────
    rr_output = await repository_review(products=products, context=context)

    # ── Paso 2: ejecutar recommend_improvements con la salida de rr ──────────
    ri_output = await recommend_improvements(
        repository_review=rr_output,
        knowledge_review="",
        architect_review="",
        context=context
    )

    # ── Paso 3: extraer métricas del texto generado ───────────────────────────
    import re

    _metrics = _de.extract_metrics_from_reports(rr_output, "", "")
    global_health      = _metrics["global_health"]
    knowledge_debt     = _metrics["knowledge_debt"]
    coverage_pct       = _metrics["coverage_pct"]
    total_g_conflicts  = _metrics["total_g_conflicts"]
    total_a_dups       = _metrics["total_a_dups"]
    total_a_blocked    = _metrics["total_a_blocked"]
    total_g_blocked    = _metrics["total_g_blocked"]
    prod_blocked_cnt   = _metrics["prod_blocked"]
    prod_high_risk     = _metrics["prod_high_risk"]
    total_articles     = _metrics["total_articles"]
    total_guidelines   = _metrics["total_guidelines"]
    missing_cats_str   = _metrics["missing_cats_str"]
    missing_cats_count = _metrics["missing_cats_count"]

    ril = ri_output.lower()

    # Simulación Top 5 desde recommend_improvements
    sim5_health  = _de.extract_int(r"top 5.*?health score\s*.*?→\s*(\d+)/100", ril, global_health)
    sim5_debt    = _de.extract_int(r"top 5.*?knowledge debt\s*.*?→\s*(\d+)/100", ril, knowledge_debt)
    sim5_esc     = _de.extract_int(r"top 5.*?reducción escalamientos\s*[:\|]+\s*↓\s*~(\d+)%", ril, 0)
    sim5_res     = _de.extract_int(r"top 5.*?resolución autónoma\s*[:\|]+\s*↑\s*~(\d+)%", ril, 0)
    sim5_cov     = _de.extract_int(r"top 5.*?cobertura temática\s*.*?→\s*(\d+)%", ril, coverage_pct)

    # Loop risk global (proxy: si hay artículos bloqueados → presencia de loop risk)
    loop_risk_level = "CRÍTICO" if total_a_blocked >= 3 else (
        "ALTO"   if total_a_blocked >= 1 else (
        "MEDIO"  if prod_high_risk >= 1 else "BAJO"))

    # Resolución autónoma esperada (baseline heurístico)
    _esc_avoidable = max(0, 30 - (total_g_conflicts * 3) - (total_a_blocked * 5))
    _resolution    = max(40, min(95, global_health - (total_a_blocked * 8) - (total_g_conflicts * 3)))

    # ── Paso 4: top risks y top opportunities desde recommend_improvements ────

    # Extraer top recomendaciones del texto de recommend_improvements
    _rec_blocks = re.findall(
        r"#(\d+)\s+(.+?)\n\s+Descripción\s*:\s*(.+?)\n.*?ROI\s*[:\|]+\s*[★☆ ]+\s*([\d.]+)",
        ri_output, re.DOTALL
    )
    top_opps = []
    for b in _rec_blocks[:5]:
        top_opps.append({
            "num": b[0], "nombre": b[1].strip(), "desc": b[2].strip()[:90], "roi": b[3]
        })

    # Quick wins desde recommend_improvements (sección QUICK WINS)
    qw_section = re.search(r"QUICK WINS.*?\n(.*?)(?=──────|PROYECTOS|$)", ri_output, re.DOTALL)
    qw_lines = []
    if qw_section:
        for line in qw_section.group(1).splitlines():
            line = line.strip()
            if line.startswith("⚡"):
                qw_lines.append(line.lstrip("⚡").strip())

    # Roadmap desde recommend_improvements
    roadmap_week_lines   = []
    roadmap_sprint_lines = []
    roadmap_month_lines  = []

    _rm_week  = re.search(r"Esta semana\n(.*?)(?=Próximo Sprint|Próximo Mes|🔭|$)", ri_output, re.DOTALL)
    _rm_sprint = re.search(r"Próximo Sprint.*?\n(.*?)(?=Próximo Mes|🔭|$)", ri_output, re.DOTALL)
    _rm_month  = re.search(r"Próximo Mes\n(.*?)(?=Próximo Trimestre|🔭|$)", ri_output, re.DOTALL)

    def _extract_arrows(block):
        if not block:
            return []
        return [l.strip().lstrip("→").strip() for l in block.group(1).splitlines()
                if l.strip().startswith("→")][:4]

    roadmap_week_lines   = _extract_arrows(_rm_week)
    roadmap_sprint_lines = _extract_arrows(_rm_sprint)
    roadmap_month_lines  = _extract_arrows(_rm_month)

    # ── Paso 5: scores por dimensión ─────────────────────────────────────────

    # Knowledge health (proxy: avg article health across products)
    _know_health = max(0, global_health - (total_a_blocked * 5) - (total_a_dups * 2))
    _know_health = min(100, _know_health)

    # Guideline health
    _guide_health = max(0, 100 - total_g_blocked * 15 - total_g_conflicts * 8)
    _guide_health = min(100, _guide_health)

    # Repository health (combo)
    _repo_health = round((_know_health * 0.6 + _guide_health * 0.4))
    if prod_blocked_cnt > 0:
        _repo_health = min(_repo_health, 60)

    # Recommendation health (how many top recs are quick wins = low effort)
    _ri_qw_count = len(qw_lines)
    _rec_health = min(100, 50 + _ri_qw_count * 10 + (20 if total_g_conflicts == 0 else 0))

    # Deployment readiness
    deploy_ready, deploy_emoji = _de.deployment_readiness(
        prod_blocked_cnt, total_a_blocked, total_g_blocked,
        global_health, knowledge_debt, prod_high_risk
    )

    # ── Semáforo por dimensión ────────────────────────────────────────────────

    s_knowledge  = _de.semaforo(_know_health)
    s_guidelines = _de.semaforo(_guide_health)
    s_repository = _de.semaforo(_repo_health)
    s_automation = _de.semaforo(_resolution, (55, 75))
    s_escalation = _de.semaforo(_esc_avoidable + 50, (60, 75))

    # Top risks (construidos a partir de señales)
    top_risks = []
    if total_a_blocked > 0:
        top_risks.append(f"⛔ {total_a_blocked} artículo(s) BLOQUEADO(s) generan loops y cierres incorrectos en FIN")
    if total_g_blocked > 0:
        top_risks.append(f"⛔ {total_g_blocked} guideline(s) con regla absoluta de no-escalamiento dejan casos irresolubles")
    if total_g_conflicts > 0:
        top_risks.append(f"⚠️  {total_g_conflicts} conflicto(s) entre guidelines producen comportamiento impredecible de FIN")
    if total_a_dups > 0:
        top_risks.append(f"⚠️  {total_a_dups} par(es) de artículos duplicados generan respuestas inconsistentes")
    if missing_cats_count > 0:
        top_risks.append(f"📌 {missing_cats_count} categoría(s) sin cobertura son puntos ciegos de FIN: {missing_cats_str[:60]}")
    if prod_high_risk > 0 and len(top_risks) < 5:
        top_risks.append(f"🔶 {prod_high_risk} producto(s) en riesgo ALTO concentran la mayoría de los problemas")
    if knowledge_debt >= 45 and len(top_risks) < 5:
        top_risks.append(f"📊 Knowledge Debt {knowledge_debt}/100 — deuda que se compone si no se atiende")
    top_risks = top_risks[:5]

    # Tabla de productos (desde product_results via re-análisis de la tabla en rr_output)
    prod_rows = re.findall(
        r"([\w\s]+?)\s{2,}(\d+)/100\s+[🟢🟡🔴]\w+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        rr_output
    )

    # ── Reporte ───────────────────────────────────────────────────────────────

    sep  = "=" * 70
    div1 = "─" * 70
    div2 = "─" * 40

    ctx_line = f"  Contexto: {context}" if context else ""

    parts = [sep]
    parts.append("  FIN EXECUTIVE DASHBOARD")
    parts.append("  Estado completo del ecosistema FIN")
    if ctx_line:
        parts.append(ctx_line)
    parts.append(sep)
    parts.append("")

    # RESUMEN GENERAL
    parts += [div2, "RESUMEN GENERAL", div2, ""]
    _hg_bar = "█" * round(global_health / 10) + "░" * (10 - round(global_health / 10))
    parts.append(f"  Health Score Global     : [{_hg_bar}] {global_health}/100")
    parts.append(f"  Deployment Readiness    : {deploy_emoji} {deploy_ready}")
    parts.append(f"  Knowledge Health        : {_know_health}/100")
    parts.append(f"  Guideline Health        : {_guide_health}/100")
    parts.append(f"  Repository Health       : {_repo_health}/100")
    parts.append(f"  Recommendation Health   : {_rec_health}/100")
    parts.append("")

    # SEMÁFORO EJECUTIVO
    parts += [div2, "SEMÁFORO EJECUTIVO", div2, ""]
    for label, (emoji, status) in [
        ("Knowledge  ", s_knowledge),
        ("Guidelines ", s_guidelines),
        ("Repository ", s_repository),
        ("Automation ", s_automation),
        ("Escalamientos", s_escalation),
    ]:
        parts.append(f"  {emoji} {label:<15} {status}")
    parts.append("")

    # MÉTRICAS PRINCIPALES
    parts += [div1, "MÉTRICAS PRINCIPALES", div1, ""]
    _debt_emoji = "🔴" if knowledge_debt >= 70 else ("🟠" if knowledge_debt >= 45 else ("🟡" if knowledge_debt >= 20 else "🟢"))
    _lr_emoji   = "🔴" if loop_risk_level == "CRÍTICO" else ("🟠" if loop_risk_level == "ALTO" else ("🟡" if loop_risk_level == "MEDIO" else "🟢"))
    parts.append(f"  Health Score              : {global_health}/100")
    parts.append(f"  Knowledge Debt            : {_debt_emoji} {knowledge_debt}/100")
    parts.append(f"  Cobertura temática        : {coverage_pct}%  ({missing_cats_count} categorías sin cubrir)")
    parts.append(f"  Conflictos (guidelines)   : {total_g_conflicts}")
    parts.append(f"  Duplicados (artículos)    : {total_a_dups} par(es)")
    parts.append(f"  Loop Risk global          : {_lr_emoji} {loop_risk_level}")
    parts.append(f"  Escalamientos evitables   : ~{_esc_avoidable}% del total")
    parts.append(f"  Resolución autónoma esp.  : ~{_resolution}%")
    parts.append("")

    # PRODUCTOS
    parts += [div1, "PRODUCTOS", div1, ""]
    _ph = f"  {'Producto':<22} {'Health':>7} {'Ready':>7} {'Know.':>6} {'Guide.':>7} {'Conflictos':>11} {'Cobertura':>10}"
    parts.append(_ph)
    parts.append("  " + "─" * 68)

    # Intentar parsear filas de la tabla rr; si falla, usar datos de products
    if prod_rows:
        for row in prod_rows:
            pname, health, g_count, g_bloq, a_count, a_bloq, dups = row
            _r_emoji = "🟢" if int(health) >= 85 else ("🟡" if int(health) >= 70 else "🔴")
            _ready = "✅" if int(a_bloq) == 0 and int(g_bloq) == 0 else "⛔"
            parts.append(
                f"  {pname.strip():<22} {int(health):>5}/100 {_ready:>7} {int(a_count):>6} {int(g_count):>7} {int(g_bloq):>11} {'—':>10}"
            )
    else:
        # Fallback: tabla derivada de los inputs
        for prod in products:
            pname = prod.get("nombre", "—")
            a_cnt = len(prod.get("knowledge_articles", []))
            g_cnt = len(prod.get("guidelines", []))
            parts.append(f"  {pname:<22} {'—':>7} {'—':>7} {a_cnt:>6} {g_cnt:>7} {'—':>11} {'—':>10}")
    parts.append("")

    # TOP RIESGOS
    parts += [div1, "TOP RIESGOS", div1, ""]
    if top_risks:
        for i, r in enumerate(top_risks, 1):
            parts.append(f"  {i}. {r}")
    else:
        parts.append("  ✅ No se identificaron riesgos críticos. El repositorio está en buen estado.")
    parts.append("")

    # TOP OPORTUNIDADES
    parts += [div1, "TOP OPORTUNIDADES", div1, ""]
    if top_opps:
        for opp in top_opps:
            parts.append(f"  #{opp['num']} {opp['nombre']}  (ROI {opp['roi']})")
            parts.append(f"       {opp['desc']}")
            parts.append("")
    else:
        # Fallback desde sección TOP RECOMENDACIONES del texto
        _raw_recs = re.findall(r"#\d+\s+.+", ri_output)
        for line in _raw_recs[:5]:
            parts.append(f"  {line.strip()}")
        parts.append("")

    # QUICK WINS
    parts += [div1, "QUICK WINS  (Alto impacto · Bajo esfuerzo)", div1, ""]
    if qw_lines:
        for qw in qw_lines:
            parts.append(f"  ⚡ {qw}")
        parts.append("")
    else:
        parts.append("  Sin quick wins identificados con los datos actuales.")
        parts.append("")

    # ROADMAP
    parts += [div1, "ROADMAP", div1, ""]
    parts.append("  📅 Esta semana")
    for item in (roadmap_week_lines or ["Revisar bloqueos y conflictos con repository_review"]):
        parts.append(f"     → {item}")
    parts.append("")
    parts.append("  ⚡ Próximo Sprint")
    for item in (roadmap_sprint_lines or ["Aplicar correcciones priorizadas por ROI"]):
        parts.append(f"     → {item}")
    parts.append("")
    parts.append("  📋 Próximo Mes")
    for item in (roadmap_month_lines or ["Ampliar cobertura y establecer revisión periódica"]):
        parts.append(f"     → {item}")
    parts.append("")

    # SIMULACIÓN
    parts += [div1, "SIMULACIÓN — Si implementas el Roadmap", div1, ""]
    parts.append(f"  Health esperado           : {global_health}/100 → {sim5_health}/100  (+{sim5_health - global_health} pts)")
    parts.append(f"  Knowledge Debt esperado   : {knowledge_debt}/100 → {sim5_debt}/100  (-{knowledge_debt - sim5_debt} pts)")
    parts.append(f"  Resolución autónoma esp.  : {_resolution}% → ~{min(95, _resolution + sim5_res)}%  (+{sim5_res} pp)")
    parts.append(f"  Reducción escalamientos   : ↓ ~{sim5_esc}%")
    parts.append(f"  Cobertura esperada        : {coverage_pct}% → {sim5_cov}%")
    parts.append("")

    # DECISIÓN EJECUTIVA
    parts += [div2, "DECISIÓN EJECUTIVA", div2, ""]
    parts.append(f"  {deploy_emoji} {deploy_ready}")
    parts.append("")

    if deploy_ready == "BLOCKED" or (prod_blocked_cnt > 0 or total_a_blocked + total_g_blocked > 0):
        _why = (
            f"El repositorio tiene {total_a_blocked} artículo(s) y {total_g_blocked} guideline(s) "
            f"BLOQUEADO(s). FIN generaría loops instruccionales o cierres incorrectos en producción. "
            f"Corregir los bloqueos es condición necesaria antes de cualquier despliegue."
        )
    elif deploy_ready == "READY WITH RECOMMENDATIONS":
        _issues = []
        if prod_high_risk > 0:
            _issues.append(f"{prod_high_risk} producto(s) en riesgo ALTO")
        if total_g_conflicts > 0:
            _issues.append(f"{total_g_conflicts} conflicto(s) entre guidelines")
        if knowledge_debt >= 45:
            _issues.append(f"Knowledge Debt {knowledge_debt}/100")
        _why = (
            f"FIN puede operar pero presenta: {', '.join(_issues)}. "
            f"Se recomienda atender las oportunidades identificadas antes de ampliar el alcance. "
            f"Monitorear de cerca durante las primeras semanas de operación."
        )
    else:
        _why = (
            f"El repositorio supera los umbrales mínimos: Health {global_health}/100, "
            f"Knowledge Debt {knowledge_debt}/100, cobertura {coverage_pct}%. "
            f"FIN está listo para operar. Mantener el ciclo de revisión periódica."
        )

    parts.append(f"  {_why}")
    parts.append("")
    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def score_guideline(
    guideline: str,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Evalúa la calidad de una guideline de FIN y devuelve una puntuación
    sobre 100 con desglose por criterio, fortalezas, debilidades,
    riesgo, justificación y recomendación de mejora.
    """

    text = guideline.lower()
    word_count = len(guideline.split())

    strengths = []
    weaknesses = []

    # ------------------------------------------------------------------ #
    # 1. Claridad (10 pts)                                                 #
    # ------------------------------------------------------------------ #
    clarity = 10

    vague_phrases = _de.GUIDELINE_VAGUE_PHRASES

    vague_hits = [p for p in vague_phrases if p in text]

    if vague_hits:
        clarity -= min(len(vague_hits) * 2, 6)
        weaknesses.append(
            f"Claridad reducida por frases vagas: {', '.join(repr(p) for p in vague_hits)}."
        )

    if len(guideline.strip()) < 20:
        clarity -= 4
        weaknesses.append("La guideline es demasiado corta para transmitir una instrucción clara.")

    if clarity == 10:
        strengths.append("Redacción clara, sin frases ambiguas detectadas.")

    clarity = max(clarity, 0)

    # ------------------------------------------------------------------ #
    # 2. Accionabilidad (10 pts)                                           #
    # ------------------------------------------------------------------ #
    actionability = 10

    action_verbs = _de.GUIDELINE_ACTION_VERBS

    has_action_verb = any(v in text for v in action_verbs)

    if not has_action_verb:
        actionability -= 6
        weaknesses.append(
            "No se detectó ningún verbo de acción claro. FIN puede no saber qué hacer."
        )
    else:
        strengths.append("Contiene verbos de acción que orientan el comportamiento de FIN.")

    if "si " not in text and "cuando " not in text and "solo si" not in text:
        actionability -= 3
        weaknesses.append(
            "Sin condiciones explícitas ('si', 'cuando'). La acción puede ejecutarse en cualquier contexto."
        )

    actionability = max(actionability, 0)

    # ------------------------------------------------------------------ #
    # 3. Ambigüedad (15 pts)                                               #
    # ------------------------------------------------------------------ #
    ambiguity = 15

    ambiguous_terms = _de.GUIDELINE_AMBIGUOUS_TERMS

    ambiguous_hits = [t for t in ambiguous_terms if t in text]

    if ambiguous_hits:
        penalty = min(len(ambiguous_hits) * 3, 12)
        ambiguity -= penalty
        weaknesses.append(
            f"Términos ambiguos o absolutos: {', '.join(repr(t) for t in ambiguous_hits)}."
        )
    else:
        strengths.append("No contiene términos absolutos ni ambiguos.")

    ambiguity = max(ambiguity, 0)

    # ------------------------------------------------------------------ #
    # 4. Criterios de escalamiento (15 pts)                                #
    # ------------------------------------------------------------------ #
    escalation_score = 15

    escalation_words = _de.GUIDELINE_ESCALATION_WORDS

    mentions_escalation = any(w in text for w in escalation_words)

    if mentions_escalation:
        has_condition = (
            "cuando " in text
            or "si " in text
            or "solo si" in text
            or "en caso de" in text
        )
        unconditional = any(
            w in text for w in ["siempre escala", "siempre escalar", "debe escalar siempre"]
        )

        if unconditional:
            escalation_score -= 10
            weaknesses.append(
                "Escalamiento incondicional ('siempre escala'). FIN escalará sin evaluar el contexto."
            )
        elif not has_condition:
            escalation_score -= 6
            weaknesses.append(
                "Se menciona escalamiento sin definir condición explícita ('cuando', 'si', 'solo si')."
            )
        else:
            strengths.append("El escalamiento está condicionado a criterios explícitos.")
    else:
        strengths.append("No requiere escalamiento; favorece la resolución autónoma.")

    escalation_score = max(escalation_score, 0)

    # ------------------------------------------------------------------ #
    # 5. Especificidad (10 pts)                                            #
    # ------------------------------------------------------------------ #
    specificity = 10

    specific_signals = _de.GUIDELINE_SPECIFIC_SIGNALS

    specific_hits = [s for s in specific_signals if s in text]

    if not specific_hits:
        specificity -= 5
        weaknesses.append(
            "No menciona escenarios, entidades o situaciones concretas."
        )
    elif len(specific_hits) >= 2:
        strengths.append(
            f"Alta especificidad: menciona contextos concretos ({', '.join(specific_hits[:3])})."
        )

    if "cualquier" in text or "todo" in text or "siempre" in text:
        specificity -= 3
        weaknesses.append(
            "El uso de 'cualquier', 'todo' o 'siempre' reduce la especificidad de la regla."
        )

    specificity = max(specificity, 0)

    # ------------------------------------------------------------------ #
    # 6. Consistencia interna (10 pts)                                     #
    # ------------------------------------------------------------------ #
    consistency = 10

    contradictions = _de.GUIDELINE_CONTRADICTION_PAIRS

    internal_contradiction = False

    for affirm, deny in contradictions:
        if affirm in text and deny in text:
            internal_contradiction = True

    if internal_contradiction:
        consistency -= 8
        weaknesses.append(
            "La guideline contiene instrucciones contradictorias internamente."
        )
    else:
        strengths.append("No se detectaron contradicciones internas.")

    consistency = max(consistency, 0)

    # ------------------------------------------------------------------ #
    # 7. Mantenibilidad (10 pts)                                           #
    # ------------------------------------------------------------------ #
    maintainability = 10

    if word_count > 80:
        maintainability -= 5
        weaknesses.append(
            f"La guideline es extensa ({word_count} palabras). Difícil de mantener y actualizar."
        )
    elif word_count > 50:
        maintainability -= 2
        weaknesses.append(
            f"La guideline supera las 50 palabras ({word_count}). Considera dividirla."
        )
    else:
        strengths.append("Longitud manejable; fácil de mantener.")

    nested_conditions = text.count(" si ") + text.count(" cuando ") + text.count(" excepto ")

    if nested_conditions >= 3:
        maintainability -= 3
        weaknesses.append(
            "Múltiples condiciones anidadas aumentan la complejidad de mantenimiento."
        )

    maintainability = max(maintainability, 0)

    # ------------------------------------------------------------------ #
    # 8. Longitud adecuada (5 pts)                                         #
    # ------------------------------------------------------------------ #
    length_score = 5

    if word_count < 5:
        length_score -= 4
        weaknesses.append("Demasiado corta (menos de 5 palabras). No es accionable.")
    elif word_count < 10:
        length_score -= 2
        weaknesses.append("Muy corta. Puede carecer de contexto suficiente.")
    elif word_count > 100:
        length_score -= 3
        weaknesses.append(
            f"Demasiado extensa ({word_count} palabras). Considera fragmentarla en reglas atómicas."
        )

    length_score = max(length_score, 0)

    # ------------------------------------------------------------------ #
    # 9. Seguridad operativa (10 pts)                                      #
    # ------------------------------------------------------------------ #
    security = 10

    risky_patterns = _de.GUIDELINE_RISKY_PATTERNS

    risky_hits = [r for r in risky_patterns if r in text]

    open_ended = (
        "cualquier solicitud" in text
        or "todo lo que pida" in text
        or "sin restricción" in text
        or "sin límite" in text
    )

    if risky_hits:
        security -= min(len(risky_hits) * 4, 8)
        weaknesses.append(
            f"Patrones de riesgo operativo: {', '.join(repr(r) for r in risky_hits)}."
        )
    if open_ended:
        security -= 4
        weaknesses.append(
            "Instrucción demasiado abierta. Puede habilitar acciones no previstas."
        )

    if security == 10:
        strengths.append("Sin patrones de riesgo operativo detectados.")

    security = max(security, 0)

    # ------------------------------------------------------------------ #
    # 10. Experiencia del usuario (5 pts)                                  #
    # ------------------------------------------------------------------ #
    ux = 5

    resolve_first = any(
        w in text for w in [
            "intenta resolver",
            "resolver primero",
            "antes de escalar",
            "resolución autónoma",
            "base de conocimiento",
            "solucionar",
        ]
    )

    if resolve_first:
        strengths.append("Favorece la resolución autónoma antes de escalar.")
    else:
        ux -= 3
        weaknesses.append(
            "No indica explícitamente que FIN debe intentar resolver antes de escalar."
        )

    empathy_signals = _de.GUIDELINE_EMPATHY_SIGNALS

    if any(e in text for e in empathy_signals):
        strengths.append("Incluye señales de empatía hacia el cliente.")
    else:
        ux -= 1

    ux = max(ux, 0)

    # ------------------------------------------------------------------ #
    # Score final                                                          #
    # ------------------------------------------------------------------ #
    total = (
        clarity
        + actionability
        + ambiguity
        + escalation_score
        + specificity
        + consistency
        + maintainability
        + length_score
        + security
        + ux
    )

    # Nivel de riesgo
    if total >= 85:
        risk = "BAJO"
    elif total >= 60:
        risk = "MEDIO"
    else:
        risk = "ALTO"

    # Interpretación
    if total >= 95:
        interpretation = "Excelente. Lista para producción."
    elif total >= 85:
        interpretation = "Muy buena. Solo requiere ajustes menores."
    elif total >= 70:
        interpretation = "Aceptable. Se recomienda revisión antes de publicar."
    elif total >= 50:
        interpretation = "Riesgo medio. Debe optimizarse antes de publicarse."
    else:
        interpretation = "No recomendada para producción. Requiere reescritura."

    # Justificación
    justification_parts = []

    if total >= 85:
        justification_parts.append(
            "La guideline es sólida: instrucción clara, condicionada y sin ambigüedades mayores."
        )
    elif total >= 70:
        justification_parts.append(
            "La guideline es funcional pero presenta áreas de mejora en claridad o especificidad."
        )
    else:
        justification_parts.append(
            "La guideline tiene deficiencias estructurales que pueden generar comportamiento impredecible en FIN."
        )

    if ambiguous_hits:
        justification_parts.append(
            f"Los términos {', '.join(repr(t) for t in ambiguous_hits)} reducen la precisión de la instrucción."
        )

    if product != "general":
        justification_parts.append(
            f"Evaluada en el contexto del producto '{product}'. "
            "Verifica que no colisione con reglas globales."
        )

    # Recomendación
    recommendation_parts = []

    if ambiguous_hits:
        recommendation_parts.append(
            f"Reemplaza {', '.join(repr(t) for t in ambiguous_hits)} por condiciones concretas y verificables."
        )

    if not has_action_verb:
        recommendation_parts.append(
            "Añade un verbo de acción explícito (escala, responde, informa, verifica, etc.)."
        )

    if mentions_escalation and not has_condition:
        recommendation_parts.append(
            "Define una condición clara para el escalamiento: 'solo si…', 'cuando…', 'en caso de…'."
        )

    if not resolve_first and mentions_escalation:
        recommendation_parts.append(
            "Añade una cláusula que indique intentar resolver antes de escalar."
        )

    if word_count > 80:
        recommendation_parts.append(
            "Divide la guideline en reglas más atómicas de una sola responsabilidad."
        )

    if not recommendation_parts:
        recommendation_parts.append(
            "Mantén esta guideline como referencia de calidad para el resto del conjunto."
        )

    # Formato del desglose alineado
    def row(label, score, max_score):
        dots = "." * max(1, 20 - len(label))
        return f"{label} {dots} {score}/{max_score}"

    breakdown_rows = [
        row("Claridad", clarity, 10),
        row("Accionabilidad", actionability, 10),
        row("Ambigüedad", ambiguity, 15),
        row("Escalamiento", escalation_score, 15),
        row("Especificidad", specificity, 10),
        row("Consistencia", consistency, 10),
        row("Mantenibilidad", maintainability, 10),
        row("Longitud", length_score, 5),
        row("Seguridad", security, 10),
        row("Experiencia Usuario", ux, 5),
    ]

    result_parts = [
        f"**Score de Guideline — Producto: {product.upper()}**\n"
    ]

    result_parts.append(
        f"**Guideline evaluada:**\n> {guideline}\n"
    )

    if context:
        result_parts.append(f"**Contexto:** {context}\n")

    result_parts.append(f"SCORE GENERAL\n\n{total}/100")

    result_parts.append("\nDESGLOSE\n")
    result_parts.extend(breakdown_rows)

    if strengths:
        result_parts.append("\nFORTALEZAS\n")
        for s in strengths:
            result_parts.append(f"- {s}")

    if weaknesses:
        result_parts.append("\nDEBILIDADES\n")
        for w in weaknesses:
            result_parts.append(f"- {w}")

    result_parts.append(f"\nRIESGO\n\n{risk}")

    result_parts.append("\nJUSTIFICACIÓN\n")
    for j in justification_parts:
        result_parts.append(f"- {j}")

    result_parts.append("\nRECOMENDACIÓN\n")
    for r in recommendation_parts:
        result_parts.append(f"- {r}")

    result_parts.append(f"\nINTERPRETACIÓN\n\n{total}/100 — {interpretation}")

    return "\n".join(result_parts)


@mcp.tool()
async def simulate_fin(
    conversation: str,
    guidelines: list = [],
    product: str = "general",
    context: str = ""
) -> str:
    """
    Simula el proceso de decisión que seguiría FIN para responder una
    conversación usando las guidelines suministradas. Detecta intención,
    emoción, prioridad, guidelines aplicables, decisión, respuesta,
    riesgo de escalamiento, conflictos y nivel de confianza.
    """

    text = conversation.lower()

    # ------------------------------------------------------------------ #
    # 1. Detectar intención principal                                      #
    # ------------------------------------------------------------------ #
    intention_map = _de.INTENTION_MAP

    intention = _de.detect_intention(text)
    if intention == "General":
        intention = "Otro"

    # ------------------------------------------------------------------ #
    # 2. Detectar emoción                                                  #
    # ------------------------------------------------------------------ #
    emotion = _de.detect_emotion(text)
    if emotion == "Neutral":
        # check for Confundido which is not in the centralized detect_emotion
        if any(w in text for w in ["no entiendo", "no sé", "confundido", "confundida", "cómo", "qué significa", "no comprendo"]):
            emotion = "Confundido"

    # ------------------------------------------------------------------ #
    # 3. Determinar prioridad                                              #
    # ------------------------------------------------------------------ #
    if emotion in ("Frustrado",) or any(w in text for w in ["no puedo facturar", "sistema caído", "pérdida", "bloqueado"]):
        priority = "CRÍTICA"
    elif emotion in ("Molesto", "Urgente") or intention in ("DIAN", "Seguridad", "Error técnico"):
        priority = "ALTA"
    elif intention in ("Facturación", "Caja", "Nómina", "Acceso"):
        priority = "MEDIA"
    else:
        priority = "BAJA"

    # ------------------------------------------------------------------ #
    # 4. Analizar guidelines recibidas                                     #
    # ------------------------------------------------------------------ #
    escalation_words   = _de.GUIDELINE_ESCALATION_WORDS
    resolve_words      = _de.GUIDELINE_RESOLVE_WORDS
    guide_words        = ["paso a paso", "guía", "instrucciones", "procedimiento", "pasos"]
    info_request_words = ["solicita", "pide", "solicitar información", "confirma", "pregunta"]

    applied_guidelines = []
    guideline_flags    = {"escalate": False, "resolve": False, "guide": False, "request_info": False}
    guideline_conflicts = []

    for i, g in enumerate(guidelines):
        g_lower = g.lower()
        applies = False

        # ¿Aplica al caso por intención o emoción?
        intent_keywords = [kw for _, kws in intention_map for kw in kws]
        emotion_keywords = [
            "frustración", "frustrado", "molesto", "enojado", "urgente",
            "emergencia", "error", "problema", "fallo",
        ]
        general_match = (
            any(k in g_lower for k in intent_keywords)
            or any(k in g_lower for k in emotion_keywords)
            or any(k in g_lower for k in ["siempre", "nunca", "todos", "cualquier", "todo cliente"])
        )

        if general_match or not guidelines:
            applies = True

        if applies:
            applied_guidelines.append(f"Guideline {i + 1}: \"{g}\"")

            if any(w in g_lower for w in escalation_words):
                guideline_flags["escalate"] = True
            if any(w in g_lower for w in resolve_words):
                guideline_flags["resolve"] = True
            if any(w in g_lower for w in guide_words):
                guideline_flags["guide"] = True
            if any(w in g_lower for w in info_request_words):
                guideline_flags["request_info"] = True

    # Detectar conflictos entre guidelines aplicadas
    if guideline_flags["escalate"] and guideline_flags["resolve"]:
        guideline_conflicts.append(
            "Una guideline indica escalar y otra indica intentar resolver primero."
        )

    if guideline_flags["escalate"] and guideline_flags["guide"]:
        guideline_conflicts.append(
            "Una guideline manda escalar pero otra indica guiar paso a paso."
        )

    # ------------------------------------------------------------------ #
    # 5. Decidir acción                                                    #
    # ------------------------------------------------------------------ #
    # Lógica de decisión en orden de prioridad
    needs_more_info = any(
        w in text for w in ["no sé", "no recuerdo", "no tengo", "cuál es", "dónde está", "cuándo"]
    )
    is_complex = len(conversation.split()) > 40 or any(
        w in text for w in ["paso a paso", "cómo hago", "proceso", "procedimiento", "tutorial"]
    )
    is_blocked = any(
        w in text for w in [
            "no puedo", "bloqueado", "sin acceso", "no responde", "caído",
            "error crítico", "perdí", "perdimos",
        ]
    )

    if guideline_flags["escalate"] and not guideline_flags["resolve"] and (
        emotion in ("Frustrado",) or priority == "CRÍTICA" or is_blocked
    ):
        decision = "Escalar"
        should_escalate = True
    elif needs_more_info or guideline_flags["request_info"]:
        decision = "Solicitar información"
        should_escalate = False
    elif is_complex or guideline_flags["guide"]:
        decision = "Guiar paso a paso"
        should_escalate = False
    elif is_blocked and not guideline_flags["resolve"]:
        decision = "Escalar"
        should_escalate = True
    else:
        decision = "Resolver"
        should_escalate = False

    # Forzar escalamiento si todas las guidelines lo indican y ninguna pide resolver
    if guideline_flags["escalate"] and not guideline_flags["resolve"] and not guideline_flags["guide"]:
        decision = "Escalar"
        should_escalate = True

    # ------------------------------------------------------------------ #
    # 6. Razonamiento paso a paso                                          #
    # ------------------------------------------------------------------ #
    reasoning_steps = []

    reasoning_steps.append(
        f"FIN identifica que el usuario consulta sobre '{intention}' "
        f"con un tono '{emotion}' y prioridad '{priority}'."
    )

    if applied_guidelines:
        reasoning_steps.append(
            f"FIN revisa {len(applied_guidelines)} guideline(s) aplicable(s) al caso."
        )
    else:
        reasoning_steps.append(
            "No se suministraron guidelines. FIN aplicará su comportamiento por defecto."
        )

    if guideline_flags["resolve"]:
        reasoning_steps.append(
            "Al menos una guideline indica intentar resolver antes de escalar. "
            "FIN prioriza la resolución autónoma."
        )
    if guideline_flags["escalate"]:
        reasoning_steps.append(
            "Al menos una guideline indica escalar. FIN evalúa si el caso cumple los criterios."
        )
    if guideline_flags["guide"]:
        reasoning_steps.append(
            "Hay una guideline que sugiere guiar paso a paso. FIN considera ese camino."
        )
    if guideline_conflicts:
        reasoning_steps.append(
            "FIN detecta conflictos entre guidelines y aplica el criterio más conservador "
            "(intentar resolver antes de escalar)."
        )

    if needs_more_info:
        reasoning_steps.append(
            "La consulta carece de información suficiente para resolverse. "
            "FIN solicitará datos adicionales."
        )

    reasoning_steps.append(
        f"FIN toma la decisión final: '{decision}'."
    )

    # ------------------------------------------------------------------ #
    # 7. Generar respuesta simulada de FIN                                 #
    # ------------------------------------------------------------------ #
    greeting_map = {
        "Frustrado": "Entiendo que esta situación es frustrante. Estoy aquí para ayudarte a resolverlo.",
        "Molesto":   "Lamento los inconvenientes. Voy a ayudarte de inmediato.",
        "Urgente":   "Entiendo que esto es urgente. Lo atiendo de inmediato.",
        "Confundido": "Con gusto te explico cómo funciona esto.",
        "Neutral":   "Hola, con gusto te ayudo.",
    }

    greeting = greeting_map.get(emotion, "Hola, con gusto te ayudo.")

    response_body_map = {
        "Resolver":             f"Voy a resolver tu consulta sobre {intention} ahora mismo.",
        "Solicitar información": f"Para ayudarte con tu consulta de {intention}, necesito un poco más de información.",
        "Guiar paso a paso":    f"Te voy a guiar paso a paso para resolver tu situación de {intention}.",
        "Escalar":              f"Tu caso de {intention} requiere la atención de un agente especializado. Voy a transferirte.",
    }

    response_body = response_body_map.get(decision, "Estoy revisando tu caso.")
    fin_response = f"{greeting} {response_body}"

    if context:
        fin_response += f" (Contexto: {context})"

    # ------------------------------------------------------------------ #
    # 8. Riesgo de escalamiento innecesario                                #
    # ------------------------------------------------------------------ #
    unnecessary_escalation_risk = "Bajo"

    if decision == "Escalar":
        if guideline_flags["resolve"] or guideline_flags["guide"]:
            unnecessary_escalation_risk = "Alto"
        elif emotion in ("Neutral", "Confundido") and priority in ("BAJA", "MEDIA"):
            unnecessary_escalation_risk = "Medio"
        else:
            unnecessary_escalation_risk = "Bajo"
    else:
        if guideline_flags["escalate"] and not is_blocked:
            unnecessary_escalation_risk = "Medio"

    # ------------------------------------------------------------------ #
    # 9. Nivel de confianza                                                #
    # ------------------------------------------------------------------ #
    confidence = 100

    if not guidelines:
        confidence -= 15

    if guideline_conflicts:
        confidence -= len(guideline_conflicts) * 10

    if decision == "Escalar" and guideline_flags["resolve"]:
        confidence -= 10

    if needs_more_info and decision != "Solicitar información":
        confidence -= 8

    if emotion == "Neutral" and priority == "CRÍTICA":
        confidence -= 5

    if unnecessary_escalation_risk == "Alto":
        confidence -= 10
    elif unnecessary_escalation_risk == "Medio":
        confidence -= 5

    confidence = max(confidence, 0)

    # ------------------------------------------------------------------ #
    # Construcción de la respuesta                                         #
    # ------------------------------------------------------------------ #
    result_parts = [
        f"**Simulación FIN — Producto: {product.upper()}**\n"
    ]

    result_parts.append(
        f"**Conversación simulada:**\n> {conversation}\n"
    )

    result_parts.append("SIMULACIÓN FIN")

    result_parts.append(f"\nPRODUCTO\n\n{product.upper()}")

    result_parts.append(f"\nINTENCIÓN DETECTADA\n\n{intention}")

    result_parts.append(f"\nEMOCIÓN\n\n{emotion}")

    result_parts.append(f"\nPRIORIDAD\n\n{priority}")

    result_parts.append("\nGUIDELINES APLICADAS\n")
    if applied_guidelines:
        for ag in applied_guidelines:
            result_parts.append(f"- {ag}")
    else:
        result_parts.append("- No se suministraron guidelines. FIN usa comportamiento por defecto.")

    result_parts.append("\nANÁLISIS\n")
    for step in reasoning_steps:
        result_parts.append(f"- {step}")

    result_parts.append(f"\nDECISIÓN FINAL\n\n{decision}")

    result_parts.append(f"\nRESPUESTA QUE FIN GENERARÍA\n\n{fin_response}")

    result_parts.append(f"\n¿ESCALAR?\n\n{'Sí' if should_escalate else 'No'}")

    justification_parts = []
    if should_escalate:
        justification_parts.append(
            f"El caso cumple criterios de escalamiento: emoción '{emotion}', prioridad '{priority}'."
        )
        if is_blocked:
            justification_parts.append("El usuario indica estar bloqueado sin solución disponible.")
    else:
        justification_parts.append(
            f"FIN puede gestionar el caso de '{intention}' de forma autónoma."
        )
        if guideline_flags["resolve"]:
            justification_parts.append(
                "Una guideline indica intentar resolver antes de escalar."
            )

    result_parts.append("\nJUSTIFICACIÓN\n")
    for j in justification_parts:
        result_parts.append(f"- {j}")

    result_parts.append(
        f"\nRIESGO DE ESCALAMIENTO INNECESARIO\n\n{unnecessary_escalation_risk.upper()}"
    )

    result_parts.append("\nCONFLICTOS DETECTADOS\n")
    if guideline_conflicts:
        for c in guideline_conflicts:
            result_parts.append(f"- {c}")
    else:
        result_parts.append("- No se detectaron conflictos entre las guidelines aplicadas.")

    result_parts.append(f"\nCONFIANZA\n\n{confidence}%")

    observations = []
    if not guidelines:
        observations.append(
            "Se recomienda suministrar guidelines específicas para mejorar la precisión de la simulación."
        )
    if guideline_conflicts:
        observations.append(
            "Resuelve los conflictos entre guidelines con detect_conflicts antes de usar esta simulación en producción."
        )
    if confidence < 70:
        observations.append(
            "Confianza baja. Revisa y optimiza las guidelines con optimize_guideline y score_guideline."
        )
    if not observations:
        observations.append(
            "Simulación de alta confianza. Las guidelines están bien definidas para este caso."
        )

    result_parts.append("\nOBSERVACIONES\n")
    for o in observations:
        result_parts.append(f"- {o}")

    return "\n".join(result_parts)


@mcp.tool()
async def generate_guideline(
    conversation: str,
    product: str = "general",
    objective: str = "",
    context: str = ""
) -> str:
    """
    Analiza una conversación real entre un cliente y FIN y genera una nueva
    guideline lista para incorporarse al repositorio de reglas. Detecta
    intención, problema, emoción, punto de fallo, comportamiento esperado,
    riesgos e impacto estimado.
    """

    text = conversation.lower()

    # ------------------------------------------------------------------ #
    # 1. Detectar intención principal                                      #
    # ------------------------------------------------------------------ #
    intention = _de.detect_intention(text)
    intention_keywords_found = []
    for label, keywords in _de.INTENTION_MAP:
        hits = [k for k in keywords if k in text]
        if hits:
            intention_keywords_found = hits
            break

    # ------------------------------------------------------------------ #
    # 2. Detectar emoción                                                  #
    # ------------------------------------------------------------------ #
    emotion = _de.detect_emotion(text)
    if emotion == "Neutral":
        if any(w in text for w in ["no entiendo", "no sé", "confundido", "cómo", "qué significa", "no comprendo"]):
            emotion = "Confundido"

    # ------------------------------------------------------------------ #
    # 3. Detectar problema principal                                       #
    # ------------------------------------------------------------------ #
    detected_problems = _de.detect_guideline_problems(text)

    main_problem = detected_problems[0] if detected_problems else "comportamiento de FIN no definido para este escenario"

    # ------------------------------------------------------------------ #
    # 4. Detectar punto de fallo de FIN                                    #
    # ------------------------------------------------------------------ #
    failure_map = _de.GUIDELINE_FAILURE_MAP
    _failure_map_full = dict(failure_map)
    _failure_map_full["comportamiento de FIN no definido para este escenario"] = "No se identificó un patrón de fallo claro. La guideline cubre el escenario preventivamente."
    failure_point = _failure_map_full.get(main_problem, _failure_map_full["comportamiento de FIN no definido para este escenario"])

    # ------------------------------------------------------------------ #
    # 5. Determinar comportamiento correcto de FIN                         #
    # ------------------------------------------------------------------ #
    behavior_map = _de.GUIDELINE_BEHAVIOR_MAP
    _behavior_map_full = dict(behavior_map)
    _behavior_map_full["comportamiento de FIN no definido para este escenario"] = (
        "FIN debe verificar si existe solución para el caso, guiar al usuario "
        "y escalar únicamente si la solución documentada no resuelve el problema."
    )
    expected_behavior = _behavior_map_full.get(main_problem, _behavior_map_full["comportamiento de FIN no definido para este escenario"])

    # ------------------------------------------------------------------ #
    # 6. Construir la guideline                                            #
    # ------------------------------------------------------------------ #
    # Detectar si hay urgencia explícita
    has_urgency    = emotion in ("Urgente",)
    has_tried_docs = any(s in text for s in ["ya seguí", "seguí los pasos", "intenté", "ya hice", "el artículo"])
    has_blockage   = any(w in text for w in ["no puedo", "bloqueado", "sin acceso", "no responde", "caído"])
    has_escalation = any(w in text for w in ["escalar", "agente", "transferir", "transfiere"])

    # Construir cláusulas de la guideline
    clauses = []

    if has_tried_docs:
        clauses.append(
            f"Si el usuario de {product} indica haber seguido los pasos documentados "
            f"para resolver un caso de {intention} sin resultado exitoso"
        )
    elif has_urgency:
        clauses.append(
            f"Si el usuario de {product} expresa urgencia en un caso de {intention}"
        )
    elif has_blockage:
        clauses.append(
            f"Si el usuario de {product} se encuentra bloqueado operativamente en {intention}"
        )
    else:
        clauses.append(
            f"Cuando FIN reciba una consulta de {intention} en {product}"
        )

    if has_tried_docs:
        clauses.append(
            "verifica que el usuario confirme haber intentado la solución documentada"
        )
        clauses.append(
            "y que el problema persista después de seguir los pasos indicados"
        )
        resolution_clause = (
            "escala al agente humano incluyendo: el error exacto reportado, "
            "los pasos que el usuario ya realizó y el resultado obtenido"
        )
    elif has_urgency:
        clauses.append("prioriza el caso de inmediato")
        resolution_clause = (
            "y si no es posible resolver en la primera interacción, "
            "escala al agente indicando la urgencia y el detalle del caso"
        )
    elif has_blockage:
        clauses.append("verifica si existe una solución documentada en la base de conocimiento")
        resolution_clause = (
            "guía al usuario paso a paso; únicamente cuando la solución documentada "
            "no resuelva el bloqueo, escala al agente con el contexto completo"
        )
    else:
        clauses.append("verifica primero si existe solución documentada")
        resolution_clause = (
            "e intenta resolver de forma autónoma antes de escalar"
        )

    # Ensamblar guideline
    if len(clauses) >= 3:
        guideline_text = (
            f"{clauses[0]}, {clauses[1]} {clauses[2]}: {resolution_clause}."
        )
    elif len(clauses) == 2:
        guideline_text = f"{clauses[0]}, {clauses[1]}: {resolution_clause}."
    else:
        guideline_text = f"{clauses[0]}: {resolution_clause}."

    # ------------------------------------------------------------------ #
    # 7. Justificación                                                     #
    # ------------------------------------------------------------------ #
    justification_parts = [
        f"La guideline cubre el escenario de '{intention}' donde {failure_point.lower()}",
        "Evita que FIN repita soluciones ya intentadas, reduciendo la fricción con el cliente.",
        "Establece condiciones claras sin términos absolutos, haciéndola mantenible y precisa.",
    ]

    if has_urgency:
        justification_parts.append(
            "Incorpora el criterio de urgencia como factor de priorización, mejorando la experiencia del cliente."
        )

    if has_tried_docs:
        justification_parts.append(
            "Exige que FIN transfiera contexto al agente (pasos realizados + resultado), "
            "reduciendo el tiempo de resolución por el agente."
        )

    # ------------------------------------------------------------------ #
    # 8. Riesgos                                                           #
    # ------------------------------------------------------------------ #
    risks = []

    if has_escalation and not has_tried_docs:
        risks.append(
            "Si FIN no verifica correctamente si el usuario intentó la solución, "
            "podría escalar casos que pueden resolverse de forma autónoma."
        )

    if has_urgency:
        risks.append(
            "La priorización por urgencia podría saturar al agente si muchos usuarios "
            "expresan urgencia sin que el caso sea crítico."
        )

    if len(detected_problems) > 1:
        risks.append(
            f"Se detectaron múltiples problemas en la conversación ({', '.join(detected_problems)}). "
            "Esta guideline cubre el principal; considera crear guidelines adicionales para los demás."
        )

    if not risks:
        risks.append(
            "No se identificaron riesgos mayores. "
            "Valida la guideline contra conversaciones reales antes de publicar."
        )

    # ------------------------------------------------------------------ #
    # 9. Calcular métricas de impacto                                      #
    # ------------------------------------------------------------------ #
    # Base de reducción de escalamientos
    escalation_reduction_base = 20

    if has_tried_docs:
        escalation_reduction_base += 25   # evita re-escalar por docs ya intentados
    if has_urgency:
        escalation_reduction_base += 10   # priorización reduce escalamientos de pánico
    if main_problem == "escalamiento sin criterios":
        escalation_reduction_base += 20
    if main_problem == "respuesta genérica de FIN":
        escalation_reduction_base += 10
    if len(detected_problems) > 2:
        escalation_reduction_base -= 10   # escenario complejo, impacto más incierto

    escalation_reduction = min(escalation_reduction_base, 75)

    # Base de mejora en resolución autónoma
    autonomous_base = 15

    if main_problem in ("falta de resolución documentada", "solución documentada insuficiente"):
        autonomous_base += 20
    if main_problem == "fallo técnico sin guía":
        autonomous_base += 25
    if has_blockage and not has_tried_docs:
        autonomous_base += 15
    if emotion in ("Confundido",):
        autonomous_base += 10
    if has_escalation and not has_tried_docs:
        autonomous_base -= 5   # el camino de escalamiento puede seguir siendo necesario

    autonomous_improvement = min(autonomous_base, 70)

    # ------------------------------------------------------------------ #
    # 10. Impacto esperado y prioridad                                     #
    # ------------------------------------------------------------------ #
    total_impact_score = escalation_reduction + autonomous_improvement

    _impact, _impl_prio = _de.guideline_impact_priority(total_impact_score)
    impact = _impact

    if emotion in ("Frustrado",) or main_problem == "escalamiento sin criterios" or has_blockage:
        implementation_priority = "Crítica"
    elif emotion in ("Urgente", "Molesto") or impact == "Alto":
        implementation_priority = "Alta"
    elif impact == "Medio":
        implementation_priority = "Media"
    else:
        implementation_priority = "Baja"

    # ------------------------------------------------------------------ #
    # Observaciones finales                                                #
    # ------------------------------------------------------------------ #
    observations = []

    if objective:
        observations.append(
            f"La guideline fue construida teniendo en cuenta el objetivo declarado: '{objective}'."
        )

    observations.append(
        "Valida esta guideline con audit_guideline y score_guideline antes de incorporarla al repositorio."
    )

    if len(detected_problems) > 1:
        observations.append(
            f"Considera generar guidelines adicionales para los otros problemas detectados: "
            f"{', '.join(detected_problems[1:])}."
        )

    if implementation_priority in ("Crítica", "Alta"):
        observations.append(
            "Por la prioridad asignada, se recomienda incorporar esta guideline antes del próximo despliegue de FIN."
        )

    # ------------------------------------------------------------------ #
    # Construcción de la respuesta                                         #
    # ------------------------------------------------------------------ #
    result_parts = [
        f"**Generación de Guideline — Producto: {product.upper()}**\n"
    ]

    result_parts.append(
        f"**Conversación analizada:**\n> {conversation}\n"
    )

    if context:
        result_parts.append(f"**Contexto:** {context}\n")

    result_parts.append("GENERACIÓN DE GUIDELINE")

    result_parts.append(f"\nPRODUCTO\n\n{product.upper()}")

    result_parts.append(f"\nINTENCIÓN DETECTADA\n\n{intention}")

    result_parts.append(f"\nPROBLEMA OBSERVADO\n\n{failure_point}")

    result_parts.append(f"\nCOMPORTAMIENTO ESPERADO\n\n{expected_behavior}")

    result_parts.append(f"\nGUIDELINE PROPUESTA\n\n{guideline_text}")

    result_parts.append("\nJUSTIFICACIÓN\n")
    for j in justification_parts:
        result_parts.append(f"- {j}")

    result_parts.append("\nRIESGOS\n")
    for r in risks:
        result_parts.append(f"- {r}")

    result_parts.append(f"\nIMPACTO ESPERADO\n\n{impact}")

    result_parts.append(
        f"\nREDUCCIÓN ESTIMADA DE ESCALAMIENTOS\n\n~{escalation_reduction}%"
    )

    result_parts.append(
        f"\nMEJORA ESTIMADA EN RESOLUCIÓN AUTÓNOMA\n\n~{autonomous_improvement}%"
    )

    result_parts.append(f"\nPRIORIDAD\n\n{implementation_priority}")

    result_parts.append("\nOBSERVACIONES\n")
    for o in observations:
        result_parts.append(f"- {o}")

    return "\n".join(result_parts)


@mcp.tool()
async def extract_guidelines(
    conversations: list,
    product: str = "general",
    context: str = ""
) -> str:
    """
    Analiza un conjunto de conversaciones reales entre clientes y FIN.
    FASE 1: Detecta eventos semánticos en cada conversación.
    FASE 2: Calcula similitud Jaccard entre conjuntos de eventos.
    FASE 3: Agrupa en clusters (umbral ≥ 70% similitud) usando union-find.
    FASE 4: Genera UNA guideline por cluster (no por conversación).
    FASE 5: Calcula métricas por cluster y deduplica patrones similares (>80%).
    """

    total = len(conversations)

    # ------------------------------------------------------------------ #
    # Caso especial: conversación única                                    #
    # ------------------------------------------------------------------ #
    if total == 1:
        return (
            f"**Extracción de Guidelines — Producto: {product.upper()}**\n\n"
            "ANÁLISIS DE CONVERSACIONES\n\n"
            f"PRODUCTO\n\n{product.upper()}\n\n"
            "CONVERSACIONES ANALIZADAS\n\n1\n\n"
            "RESUMEN GENERAL\n\n"
            "Solo se recibió 1 conversación. No es posible detectar patrones confiables "
            "con una única muestra. Se requieren al menos 3 conversaciones para identificar "
            "recurrencias significativas.\n\n"
            "RECOMENDACIONES GENERALES\n\n"
            "- Recopila más conversaciones reales del mismo escenario antes de extraer guidelines.\n"
            "- Usa generate_guideline para analizar esta conversación de forma individual.\n\n"
            "OBSERVACIONES\n\n"
            "- Con una sola conversación el análisis de patrones no es estadísticamente representativo."
        )

    from collections import defaultdict

    # ------------------------------------------------------------------ #
    # Taxonomía de intenciones                                             #
    # ------------------------------------------------------------------ #
    intention_map = _de.INTENTION_MAP

    # ------------------------------------------------------------------ #
    # Catálogo de eventos semánticos                                       #
    # ------------------------------------------------------------------ #
    EVENT_CATALOG = _de.GUIDELINE_EVENT_CATALOG

    # ------------------------------------------------------------------ #
    # FASE 1 — Detección de eventos por conversación                       #
    # ------------------------------------------------------------------ #
    def detect_events(text):
        found = []
        for ev in EVENT_CATALOG:
            if ev["id"] == "unnecessary_escalation_risk":
                continue
            if any(sig in text for sig in ev["signals"]):
                found.append(ev["id"])
        if "user_tried_docs" in found and "fin_repeats_solution" in found:
            found.append("unnecessary_escalation_risk")
        return found

    conv_data = []
    for i, conv in enumerate(conversations):
        raw = conv.get("text", conv) if isinstance(conv, dict) else conv
        t = raw.lower()
        intention = "General"
        for label, kws in intention_map:
            if any(k in t for k in kws):
                intention = label
                break
        events = detect_events(t)
        conv_data.append({
            "idx":       i + 1,
            "intention": intention,
            "events":    events,
            "event_set": frozenset(events),
            "text":      t,
        })

    # ------------------------------------------------------------------ #
    # FASE 2 — Similitud Jaccard entre conjuntos de eventos               #
    # ------------------------------------------------------------------ #
    def jaccard(set_a, set_b):
        return _de.jaccard(set(set_a), set(set_b))

    # ------------------------------------------------------------------ #
    # FASE 3 — Union-Find para construir clusters (umbral ≥ 70%)          #
    # ------------------------------------------------------------------ #
    CLUSTER_THRESHOLD = _de.GUIDELINE_CLUSTER_THRESHOLD

    parent = list(range(total))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(total):
        for j in range(i + 1, total):
            sim = _de.jaccard(conv_data[i]["event_set"], conv_data[j]["event_set"])
            if sim >= CLUSTER_THRESHOLD:
                union(i, j)

    raw_clusters = defaultdict(list)
    for i in range(total):
        raw_clusters[find(i)].append(i)
    clusters = list(raw_clusters.values())

    # ------------------------------------------------------------------ #
    # Nombrado de patrones                                                 #
    # ------------------------------------------------------------------ #
    def pattern_name_for(event_set):
        return _de.cluster_pattern_name(event_set)

    # ------------------------------------------------------------------ #
    # Guideline templates                                                  #
    # ------------------------------------------------------------------ #
    def guideline_for_events(event_set, intention):
        return _de.guideline_template_for(event_set)

    # ------------------------------------------------------------------ #
    # FASE 4+5 — Una guideline y métricas por cluster                     #
    # ------------------------------------------------------------------ #
    def dominant_event_label(indices):
        counts = defaultdict(int)
        for i in indices:
            for ev in conv_data[i]["events"]:
                counts[ev] += 1
        if not counts:
            return "Sin evento dominante"
        top_ev = max(counts, key=counts.get)
        label = next((e["label"] for e in EVENT_CATALOG if e["id"] == top_ev), top_ev)
        return label

    def avg_pairwise_similarity(indices):
        if len(indices) == 1:
            return 100
        sims = []
        for ii in range(len(indices)):
            for jj in range(ii + 1, len(indices)):
                sims.append(_de.jaccard(
                    conv_data[indices[ii]]["event_set"],
                    conv_data[indices[jj]]["event_set"],
                ))
        return round(sum(sims) / len(sims) * 100) if sims else 100

    cluster_patterns = []

    for cluster_indices in clusters:
        count = len(cluster_indices)
        frequency_pct = round(count / total * 100)

        # Unión de eventos del cluster (comportamiento representativo)
        all_ev_sets = [conv_data[i]["event_set"] for i in cluster_indices]
        # Intersección para eventos compartidos; unión como fallback si intersección es vacía
        shared_events = all_ev_sets[0]
        for s in all_ev_sets[1:]:
            shared_events = shared_events & s
        if not shared_events:
            shared_events = all_ev_sets[0]
            for s in all_ev_sets[1:]:
                shared_events = shared_events | s

        # Intención más frecuente en el cluster
        intention_counts_local = defaultdict(int)
        for i in cluster_indices:
            intention_counts_local[conv_data[i]["intention"]] += 1
        cluster_intention = max(intention_counts_local, key=intention_counts_local.get)

        # Métricas
        event_impacts = [ev["impact"] for ev in EVENT_CATALOG if ev["id"] in shared_events]
        base_impact = int(sum(event_impacts) / len(event_impacts)) if event_impacts else 25

        if frequency_pct >= 60:
            impact_score = min(base_impact + 20, 100)
        elif frequency_pct >= 30:
            impact_score = min(base_impact + 10, 100)
        else:
            impact_score = base_impact

        esc_risk_values = [ev["esc_risk"] for ev in EVENT_CATALOG if ev["id"] in shared_events]
        avg_esc_risk = int(sum(esc_risk_values) / len(esc_risk_values)) if esc_risk_values else 20

        if avg_esc_risk >= 55 or impact_score >= 65:
            risk = "ALTO"
        elif avg_esc_risk >= 35 or impact_score >= 45:
            risk = "MEDIO"
        else:
            risk = "BAJO"

        impact_label = "Alto" if impact_score >= 65 else ("Medio" if impact_score >= 45 else "Bajo")

        priority_score = frequency_pct * 0.3 + impact_score * 0.3 + avg_esc_risk * 0.4
        if priority_score >= 55 or risk == "ALTO":
            priority = "Crítica"
        elif priority_score >= 35 or risk == "MEDIO":
            priority = "Alta"
        elif priority_score >= 20:
            priority = "Media"
        else:
            priority = "Baja"

        pat_name = pattern_name_for(shared_events)
        guideline_text = guideline_for_events(shared_events, cluster_intention)
        esc_reduction = min(15 + frequency_pct // 2 + (avg_esc_risk // 5), 75)
        auto_improvement = min(10 + frequency_pct // 3 + (impact_score // 8), 65)
        justification_events = [ev["label"] for ev in EVENT_CATALOG if ev["id"] in shared_events]
        dom_label = dominant_event_label(cluster_indices)
        avg_sim = avg_pairwise_similarity(cluster_indices)

        cluster_patterns.append({
            "name":               pat_name,
            "intention":          cluster_intention,
            "count":              count,
            "frequency_pct":      frequency_pct,
            "impact_score":       impact_score,
            "impact_label":       impact_label,
            "risk":               risk,
            "priority":           priority,
            "guideline":          guideline_text,
            "esc_reduction":      esc_reduction,
            "auto_improvement":   auto_improvement,
            "events":             list(shared_events),
            "justification_events": justification_events,
            "conv_indices":       [conv_data[i]["idx"] for i in cluster_indices],
            "dominant_event":     dom_label,
            "avg_similarity":     avg_sim,
        })

    # ------------------------------------------------------------------ #
    # Deduplicación: fusionar patrones con similitud de guideline > 80%   #
    # ------------------------------------------------------------------ #
    def text_jaccard(a, b):
        return _de.jaccard(_de.word_set(a), _de.word_set(b))

    MERGE_THRESHOLD = _de.GUIDELINE_MERGE_THRESHOLD
    merged = []
    used = set()

    # Ordenar por count desc para que el representante sea el cluster más grande
    cluster_patterns.sort(key=lambda x: -x["count"])

    for i, pat_i in enumerate(cluster_patterns):
        if i in used:
            continue
        group = [pat_i]
        used.add(i)
        for j, pat_j in enumerate(cluster_patterns):
            if j in used or j == i:
                continue
            sim = text_jaccard(pat_i["guideline"], pat_j["guideline"])
            if sim > MERGE_THRESHOLD:
                group.append(pat_j)
                used.add(j)
        if len(group) == 1:
            merged.append(pat_i)
        else:
            # Fusionar: sumar counts, combinar índices de conversación, keep highest impact
            merged_count = sum(g["count"] for g in group)
            merged_freq  = round(merged_count / total * 100)
            merged_convs = []
            for g in group:
                merged_convs.extend(g["conv_indices"])
            best = max(group, key=lambda g: g["impact_score"])
            best = dict(best)
            best["count"]        = merged_count
            best["frequency_pct"] = merged_freq
            best["conv_indices"] = sorted(set(merged_convs))
            best["esc_reduction"] = min(15 + merged_freq // 2 + (best["avg_esc_risk"] if "avg_esc_risk" in best else best["esc_reduction"] // 2), 75)
            merged.append(best)

    scored_patterns = merged
    scored_patterns.sort(key=lambda x: (-x["impact_score"], -x["count"]))

    # ------------------------------------------------------------------ #
    # Conteos globales para resumen                                        #
    # ------------------------------------------------------------------ #
    intention_counts = defaultdict(int)
    for d in conv_data:
        intention_counts[d["intention"]] += 1

    all_events_flat = [ev for d in conv_data for ev in d["events"]]
    event_global_counts = defaultdict(int)
    for ev in all_events_flat:
        event_global_counts[ev] += 1

    fin_ok_count = sum(1 for d in conv_data if "problem_resolved" in d["events"])
    fin_fail_count = sum(
        1 for d in conv_data
        if any(e in d["events"] for e in [
            "user_tried_docs", "fin_repeats_solution", "problem_persists",
            "user_blocked", "unnecessary_escalation_risk",
        ])
    )

    top_intention    = max(intention_counts, key=intention_counts.get) if intention_counts else "General"
    top_event_id     = max(event_global_counts, key=event_global_counts.get) if event_global_counts else None
    top_event_label  = next(
        (ev["label"] for ev in EVENT_CATALOG if ev["id"] == top_event_id), "No detectado"
    ) if top_event_id else "No detectado"
    top_pattern_name = scored_patterns[0]["name"] if scored_patterns else "No detectado"

    summary_lines = [
        f"Se analizaron {total} conversaciones del producto {product}.",
        f"Intención más frecuente: {top_intention} ({intention_counts[top_intention]} de {total} conversaciones).",
        f"Evento más recurrente: {top_event_label} ({event_global_counts.get(top_event_id, 0)} de {total} conversaciones).",
        f"Clusters detectados: {len(clusters)}.",
        f"Patrones únicos tras deduplicación: {len(scored_patterns)}.",
        f"Patrón principal: {top_pattern_name}.",
        f"Conversaciones donde FIN respondió correctamente: {fin_ok_count}.",
        f"Conversaciones donde FIN probablemente falló: {fin_fail_count}.",
    ]

    global_events_sorted = sorted(
        [(ev, event_global_counts[ev]) for ev in event_global_counts if event_global_counts[ev] > 0],
        key=lambda x: -x[1],
    )

    # ------------------------------------------------------------------ #
    # Recomendaciones                                                      #
    # ------------------------------------------------------------------ #
    general_recs = []
    if fin_fail_count > fin_ok_count:
        general_recs.append(
            "La mayoría de conversaciones muestra fallos de FIN. "
            "Prioriza implementar las guidelines de mayor impacto antes del próximo despliegue."
        )
    else:
        general_recs.append(
            "FIN resuelve correctamente la mayoría de los casos. "
            "Las guidelines propuestas cubren los escenarios residuales."
        )
    if event_global_counts.get("user_frustration", 0) > total // 3:
        general_recs.append(
            "Un tercio o más de los usuarios expresa frustración. "
            "Implementar guidelines de escalamiento condicional mejorará la experiencia."
        )
    if event_global_counts.get("user_urgency", 0) > 0:
        general_recs.append(
            "Hay conversaciones con urgencia explícita. "
            "Asegúrate de que exista una guideline de priorización de urgencias."
        )
    if event_global_counts.get("unnecessary_escalation_risk", 0) > 0:
        general_recs.append(
            "Se detectaron escalamientos evitables. "
            "La guideline de 'FIN repite solución ya agotada' es prioritaria."
        )
    if len(scored_patterns) > 3:
        general_recs.append(
            "Se detectaron múltiples patrones. Implementa primero los de prioridad Crítica "
            "y valida cada guideline con audit_guideline y score_guideline."
        )
    if not general_recs:
        general_recs.append(
            "El conjunto de conversaciones es representativo. "
            "Valida cada guideline propuesta con el equipo antes de publicar."
        )

    priority_order  = [p for p in scored_patterns if p["priority"] == "Crítica"]
    priority_order += [p for p in scored_patterns if p["priority"] == "Alta"]
    priority_order += [p for p in scored_patterns if p["priority"] == "Media"]
    priority_order += [p for p in scored_patterns if p["priority"] == "Baja"]

    observations = []
    if total < 5:
        observations.append(
            f"Se analizaron solo {total} conversaciones. "
            "Con más muestras los patrones serán más confiables."
        )
    if not scored_patterns:
        observations.append(
            "No se detectaron patrones reconocibles. "
            "Verifica que las conversaciones incluyan texto suficiente."
        )
    else:
        observations.append(
            "Usa detect_conflicts para verificar que las guidelines propuestas "
            "no colisionen entre sí antes de incorporarlas al repositorio."
        )
    if context:
        observations.append(f"Contexto adicional considerado: {context}")

    # ------------------------------------------------------------------ #
    # Construcción de la respuesta                                         #
    # ------------------------------------------------------------------ #
    result_parts = [f"**Extracción de Guidelines — Producto: {product.upper()}**\n"]

    result_parts.append("ANÁLISIS DE CONVERSACIONES")
    result_parts.append(f"\nPRODUCTO\n\n{product.upper()}")
    result_parts.append(f"\nCONVERSACIONES ANALIZADAS\n\n{total}")

    result_parts.append("\nRESUMEN GENERAL\n")
    for line in summary_lines:
        result_parts.append(f"- {line}")

    result_parts.append("\nEVENTOS DETECTADOS\n")
    if global_events_sorted:
        for ev_id, ev_count in global_events_sorted:
            label = next((e["label"] for e in EVENT_CATALOG if e["id"] == ev_id), ev_id)
            result_parts.append(f"✓ {label} ({ev_count} de {total} conversaciones)")
    else:
        result_parts.append("No se detectaron eventos reconocibles.")

    # ---- NUEVA SECCIÓN: CLUSTERS DETECTADOS ----
    result_parts.append("\nCLUSTERS DETECTADOS\n")
    for c_idx, cluster_indices in enumerate(clusters, start=1):
        conv_nums = ", ".join(str(conv_data[i]["idx"]) for i in cluster_indices)
        dom = dominant_event_label(cluster_indices)
        avg_s = avg_pairwise_similarity(cluster_indices)
        result_parts.append(f"Cluster #{c_idx}\n")
        result_parts.append(f"Conversaciones\n\n{conv_nums}")
        result_parts.append(f"\nEvento dominante\n\n{dom}")
        result_parts.append(f"\nSimilitud promedio\n\n{avg_s}%")
        result_parts.append("\n----------------------------------")

    # ---- PATRONES DETECTADOS (uno por cluster, deduplicados) ----
    result_parts.append("\nPATRONES DETECTADOS\n")

    if not scored_patterns:
        result_parts.append(
            "No se detectaron patrones reconocibles. "
            "Proporciona conversaciones con más texto o señales de problema."
        )
    else:
        for idx, pat in enumerate(scored_patterns, start=1):
            result_parts.append(f"Patrón #{idx}\n")
            result_parts.append(f"Nombre\n\n{pat['name']}")
            conv_list = ", ".join(str(c) for c in pat["conv_indices"])
            result_parts.append(
                f"\nConversaciones en este patrón\n\n{conv_list}"
            )
            result_parts.append(
                f"\nFrecuencia\n\n"
                f"{pat['count']} de {total} conversaciones ({pat['frequency_pct']}%)"
            )
            result_parts.append(f"\nImpacto\n\n{pat['impact_label']}")
            result_parts.append(f"\nRiesgo\n\n{pat['risk']}")
            result_parts.append(f"\nGuideline propuesta\n\n{pat['guideline']}")
            result_parts.append("\nJustificación (basada en eventos)\n")
            for jev in pat["justification_events"]:
                result_parts.append(f"- {jev}")
            result_parts.append(f"\nPrioridad\n\n{pat['priority']}")
            result_parts.append(f"\nReducción estimada de escalamientos\n\n~{pat['esc_reduction']}%")
            result_parts.append(f"\nMejora estimada de resolución autónoma\n\n~{pat['auto_improvement']}%")
            result_parts.append("\n-----------------------------------")

    result_parts.append("\nRECOMENDACIONES GENERALES\n")
    for rec in general_recs:
        result_parts.append(f"- {rec}")

    result_parts.append("\nPRIORIDAD DE IMPLEMENTACIÓN\n")
    for i, pat in enumerate(priority_order, start=1):
        result_parts.append(
            f"{i}. [{pat['priority']}] {pat['name']} "
            f"— {pat['intention']} ({pat['frequency_pct']}%)"
        )

    result_parts.append("\nOBSERVACIONES\n")
    for obs in observations:
        result_parts.append(f"- {obs}")

    return "\n".join(result_parts)


@mcp.tool()
async def architect_review(
    product: str,
    conversations: list,
    current_guidelines: list = [],
    objective: str = ""
) -> str:
    """
    Orquestador del FIN Architect MCP v4. Reporte ejecutivo de arquitectura
    conversacional nivel empresarial. Pipeline completo + ARCHITECT DECISION ENGINE
    con cobertura funcional, métricas de repositorio, índice de mantenibilidad,
    confidence del análisis, guidelines huérfanas, matriz de cobertura, simulación
    de impacto y resúmenes ejecutivos diferenciados para PM y equipo de Soporte.
    """

    # ---
    import re as _re

    def extract_score(score_output):
        m = _re.search(r"(\d{1,3})/100", score_output)
        return int(m.group(1)) if m else 0

    def text_jaccard(a, b):
        return _de.jaccard(_de.word_set(a), _de.word_set(b))

    # PASO 1 — Extraer patrones
    extraction_output = await extract_guidelines(
        conversations=conversations,
        product=product,
        context=objective,
    )

    lines_ext = extraction_output.split("\n")
    patterns_block = []
    in_patterns = False
    for line in lines_ext:
        if line.strip() == "PATRONES DETECTADOS":
            in_patterns = True
            continue
        if in_patterns and line.strip() in ("RECOMENDACIONES GENERALES", "PRIORIDAD DE IMPLEMENTACIÓN"):
            break
        if in_patterns:
            patterns_block.append(line)

    events_detected = []
    in_events = False
    for line in lines_ext:
        if line.strip() == "EVENTOS DETECTADOS":
            in_events = True
            continue
        if in_events and line.strip() == "CLUSTERS DETECTADOS":
            break
        if in_events and line.strip().startswith("✓"):
            events_detected.append(line.strip())

    extracted_guidelines = []
    current_name = None
    for line in patterns_block:
        if line.startswith("Nombre"):
            current_name = None
        elif current_name is None and line.strip() and not line.startswith("-") \
                and not line.startswith("Patrón #") and not line.startswith("Frecuencia") \
                and not line.startswith("Impacto") and not line.startswith("Riesgo") \
                and not line.startswith("Prioridad") and not line.startswith("Reducción") \
                and not line.startswith("Mejora") and not line.startswith("Justificación") \
                and not line.startswith("Conversaciones") and not line.startswith("---"):
            current_name = line.strip()
        elif current_name and line.strip() and line.strip() != current_name \
                and not line.startswith("Guideline propuesta") and not line.startswith("Nombre") \
                and not line.startswith("Frecuencia") and not line.startswith("Impacto") \
                and not line.startswith("Riesgo") and not line.startswith("Prioridad") \
                and not line.startswith("Reducción") and not line.startswith("Mejora") \
                and not line.startswith("Justificación") and not line.startswith("Conversaciones") \
                and not line.startswith("Patrón #") and not line.startswith("---"):
            if len(line.strip()) > 40:
                extracted_guidelines.append(line.strip())
                current_name = None

    seen_g = set()
    extracted_guidelines = [g for g in extracted_guidelines if not (g in seen_g or seen_g.add(g))]

    # PASO 2 — Generar guidelines desde conversaciones
    generated_guidelines = []
    for conv in conversations[:5]:
        raw = conv.get("text", conv) if isinstance(conv, dict) else conv
        gen_out = await generate_guideline(conversation=raw, product=product, objective=objective)
        capturing_gl = False
        for line in gen_out.split("\n"):
            if "GUIDELINE PROPUESTA" in line.upper() or "GUIDELINE GENERADA" in line.upper():
                capturing_gl = True
                continue
            if capturing_gl and line.strip() and not line.startswith("RIESGO") \
                    and not line.startswith("IMPACTO") and not line.startswith("COMPORTAMIENTO") \
                    and not line.startswith("INTENCIÓN") and not line.startswith("EMOCIÓN") \
                    and not line.startswith("PROBLEMA") and not line.startswith("PRIORIDAD") \
                    and not line.startswith("PUNTO") and not line.startswith("OBSERV") \
                    and not line.startswith("RECOMEND") and not line.startswith("---") \
                    and not line.startswith("**"):
                generated_guidelines.append(line.strip())
                break

    all_guidelines = list(current_guidelines)
    for g in extracted_guidelines + generated_guidelines:
        if g and g not in all_guidelines:
            all_guidelines.append(g)

    if not all_guidelines:
        all_guidelines = [
            f"Cuando el usuario reporte un problema operativo en {product} "
            "y haya seguido los pasos documentados sin resultado, "
            "verifica el contexto antes de escalar al agente humano."
        ]

    # MEJORA 6 — Consolidar guidelines con similitud >= 90%
    CONSOLIDATION_THRESHOLD = 0.90

    consolidated = []
    merge_log = []
    used_idx = set()

    for i, gi in enumerate(all_guidelines):
        if i in used_idx:
            continue
        group = [gi]
        used_idx.add(i)
        for j, gj in enumerate(all_guidelines):
            if j in used_idx or j == i:
                continue
            if text_jaccard(gi, gj) >= CONSOLIDATION_THRESHOLD:
                group.append(gj)
                used_idx.add(j)
        if len(group) == 1:
            consolidated.append(gi)
        else:
            representative = max(group, key=len)
            consolidated.append(representative)
            for other in group:
                if other != representative:
                    merge_log.append((other, representative))

    all_guidelines = consolidated

    # PASO 3 — Auditoría
    audit_results = []
    for g in all_guidelines:
        audit_out = await audit_guideline(guideline=g, product=product)
        has_issues = "⚠️ Problemas detectados" in audit_out
        issues_lines = [l.strip() for l in audit_out.split("\n")
                        if l.strip().startswith("- ") and "⚠️" not in l and "💡" not in l
                        and "Recomendación" not in l]
        audit_results.append({
            "guideline": g,
            "has_issues": has_issues,
            "issues": issues_lines[:3],
        })

    guidelines_with_issues = [a for a in audit_results if a["has_issues"]]
    guidelines_clean       = [a for a in audit_results if not a["has_issues"]]

    # PASO 4 — Optimización
    optimized_map = {}
    for a in guidelines_with_issues:
        opt_out = await optimize_guideline(guideline=a["guideline"])
        for line in opt_out.split("\n"):
            if "VERSIÓN OPTIMIZADA" in line.upper():
                continue
            if line.strip() and "RECOMENDACIÓN" not in line.upper() \
                    and "PROBLEMAS" not in line.upper() and "GUIDELINE ORIGINAL" not in line.upper():
                optimized_map[a["guideline"]] = line.strip()
                break

    final_guidelines = [optimized_map.get(g, g) for g in all_guidelines if g]

    # PASO 5 — Clasificación
    classification_results = []
    for g in final_guidelines:
        cls_out = await classify_guideline(guideline=g, product=product)
        cat, sub, risk_cls, pri_cls = "General", "Instrucción Simple", "BAJO", "NORMAL"
        for line in cls_out.split("\n"):
            if "Categoría principal:" in line:
                cat = line.split(":", 1)[-1].strip().replace("**", "")
            elif "Subcategoría:" in line:
                sub = line.split(":", 1)[-1].strip().replace("**", "")
            elif "Nivel de riesgo:" in line:
                risk_cls = line.split(":", 1)[-1].strip().replace("**", "")
            elif "Prioridad:" in line:
                pri_cls = line.split(":", 1)[-1].strip().replace("**", "")
        classification_results.append({
            "guideline":   g,
            "category":    cat,
            "subcategory": sub,
            "risk":        risk_cls,
            "priority":    pri_cls,
        })

    # PASO 6 — Conflictos
    conflicts_output = await detect_conflicts(guidelines=final_guidelines, product=product)
    has_conflicts = "No se detectaron conflictos" not in conflicts_output \
                    and "sin conflictos" not in conflicts_output.lower()
    conflict_lines = [l.strip() for l in conflicts_output.split("\n")
                      if l.strip().startswith("- ") or l.strip().startswith("⚠")][:10]

    # PASO 7 — Puntaje
    score_results = []
    for g in final_guidelines:
        sc_out = await score_guideline(guideline=g, product=product)
        score_val = extract_score(sc_out)
        interpretation = ""
        for line in sc_out.split("\n"):
            if "/100 —" in line:
                interpretation = line.split("—", 1)[-1].strip()
                break
        score_results.append({"guideline": g, "score": score_val, "interpretation": interpretation})

    scores    = [r["score"] for r in score_results if r["score"] > 0]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    issue_penalty    = len(guidelines_with_issues) * 5
    conflict_penalty = 10 if has_conflicts else 0
    health_score = max(0, min(100, avg_score - issue_penalty - conflict_penalty))

    if health_score >= 80:
        health_label, health_emoji = "ÓPTIMA", "✅"
    elif health_score >= 60:
        health_label, health_emoji = "ACEPTABLE", "⚠️"
    elif health_score >= 40:
        health_label, health_emoji = "REQUIERE MEJORAS", "🔶"
    else:
        health_label, health_emoji = "CRÍTICA", "🔴"

    # HEALTH SCORE BREAKDOWN — contributions based on real values (deferred; filled below)
    _hs_quality  = min(35, round(avg_score * 0.35))
    _hs_coverage = 0   # filled after avg_cov is computed
    _hs_maint_b  = 0   # filled after maint_idx is computed
    _hs_conflict_pen = 0  # filled after n_conflicts_count is computed
    _hs_dup_pen  = 0      # filled after merge counts are computed
    _hs_abs_pen  = 0      # filled after gl_absolute_set is computed

    # PASO 8 — Simulación final
    rep_conv_raw = conversations[0]
    if isinstance(rep_conv_raw, dict):
        rep_conv_raw = rep_conv_raw.get("text", str(rep_conv_raw))
    simulation_output = await simulate_fin(
        conversation=rep_conv_raw,
        guidelines=final_guidelines,
        product=product,
        context=objective,
    )

    sim_values = {}
    sim_sections_map = {
        "INTENCIÓN DETECTADA": "intention",
        "EMOCIÓN DETECTADA":   "emotion",
        "PRIORIDAD":           "priority",
        "DECISIÓN DE FIN":     "decision",
        "RIESGO DE ESCALAMIENTO": "esc_risk",
        "NIVEL DE CONFIANZA":  "confidence",
    }
    sim_current = None
    for line in simulation_output.split("\n"):
        stripped = line.strip().upper()
        if stripped in sim_sections_map:
            sim_current = sim_sections_map[stripped]
            continue
        if sim_current and line.strip() and sim_current not in sim_values:
            sim_values[sim_current] = line.strip()

    # MEJORA 4 — Madurez del producto
    total_gl      = len(final_guidelines)
    n_high_risk   = sum(1 for c in classification_results if c["risk"] == "ALTO")
    n_conditional = sum(1 for c in classification_results if c["subcategory"] == "Flujo Condicional")
    n_urgente     = sum(1 for c in classification_results if c["priority"] == "URGENTE")
    n_clean       = len(guidelines_clean)
    n_issues      = len(guidelines_with_issues)

    mat_guidelines = max(0, min(100,
        round(avg_score * 0.7 + (n_clean / total_gl * 100 * 0.3) if total_gl else avg_score)
    ))

    esc_penalty    = round((n_high_risk / total_gl) * 40) if total_gl else 0
    mat_escalation = max(0, min(100, 85 - esc_penalty + (5 if not has_conflicts else 0)))

    mat_autonomous = max(0, min(100,
        round((n_conditional / total_gl) * 100) if total_gl else 50
    ))

    merge_penalty   = min(len(merge_log) * 8, 30)
    conflict_p      = 20 if has_conflicts else 0
    mat_consistency = max(0, min(100, 100 - merge_penalty - conflict_p))

    mat_global = round(
        mat_guidelines   * 0.30 +
        mat_escalation   * 0.25 +
        mat_autonomous   * 0.25 +
        mat_consistency  * 0.20
    )

    def mat_label(v):
        if v >= 80: return "Alta"
        if v >= 60: return "Media"
        if v >= 40: return "En desarrollo"
        return "Inicial"

    # MEJORA 1 — Hallazgos principales
    findings = []
    total_convs = len(conversations)

    if any("FIN repite" in l or "FIN repitió" in l for l in events_detected):
        findings.append(
            "✓ FIN repite soluciones ya agotadas en al menos una parte de las conversaciones analizadas, "
            "generando escalamientos evitables."
        )
    if any("urgencia" in l.lower() for l in events_detected):
        findings.append(
            "✓ Se detectaron conversaciones con urgencia explícita del usuario. "
            "El conjunto actual de guidelines no garantiza priorización inmediata."
        )
    if any("bloqueado" in l.lower() or "bloqueo" in l.lower() for l in events_detected):
        findings.append(
            "✓ Usuarios reportan bloqueo operativo sin que FIN ofrezca una ruta de escalamiento condicional clara."
        )
    if merge_log:
        findings.append(
            f"✓ Se identificaron {len(merge_log)} guideline(s) redundante(s) con similitud ≥ 90%. "
            "Fueron consolidadas automáticamente en este reporte."
        )
    if has_conflicts:
        findings.append(
            "✓ Existen conflictos semánticos entre guidelines que pueden generar comportamientos "
            "contradictorios en FIN si se despliegan sin resolución previa."
        )
    if avg_score >= 85:
        findings.append(
            f"✓ Las guidelines presentan buena calidad técnica (score promedio {avg_score}/100), "
            "lo que reduce el riesgo de interpretaciones incorrectas por parte de FIN."
        )
    elif avg_score >= 70:
        findings.append(
            f"✓ La calidad técnica de las guidelines es aceptable pero mejorable "
            f"(score promedio {avg_score}/100). Algunas requieren mayor precisión condicional."
        )
    else:
        findings.append(
            f"✓ La calidad técnica de las guidelines está por debajo del umbral recomendado "
            f"(score promedio {avg_score}/100). Se recomienda optimización antes del despliegue."
        )
    if mat_consistency >= 80:
        findings.append(
            "✓ El conjunto de guidelines es consistente internamente. "
            "No se detectaron contradicciones estructurales relevantes."
        )
    elif mat_consistency < 60:
        findings.append(
            "✓ La consistencia del conjunto de guidelines es baja. "
            "Fusionar y depurar antes del despliegue es la acción de mayor impacto."
        )
    if n_conditional < total_gl // 2 and total_gl > 1:
        findings.append(
            "✓ Menos de la mitad de las guidelines define criterios condicionales de escalamiento. "
            "FIN podría escalar casos que podría resolver de forma autónoma."
        )

    findings = findings[:8]
    while len(findings) < 5:
        findings.append(
            "✓ Se recomienda ampliar el conjunto de conversaciones para detectar patrones adicionales."
        )

    # MEJORA 2 — Resumen ejecutivo de consultoría
    what_happening = (
        f"El producto {product} presenta un patrón recurrente en el que FIN no logra resolver "
        "los casos de forma autónoma y termina repitiendo soluciones documentadas que el usuario "
        "ya intentó, lo que deriva en escalamientos innecesarios."
        if any("repite" in f or "repitió" in f for f in findings)
        else
        f"El análisis del producto {product} revela oportunidades de mejora en la cobertura "
        "y precisión de las guidelines que gobiernan el comportamiento de FIN."
    )
    why = (
        "Esto ocurre principalmente porque las guidelines actuales no contemplan el estado "
        "previo del usuario: FIN no verifica si el cliente ya intentó la solución antes de "
        "recomendarla nuevamente, ni establece un criterio claro para escalar cuando la "
        "documentación no resuelve el problema."
        if any("repite" in f or "repitió" in f for f in findings)
        else
        "La causa raíz está en la ausencia de condiciones explícitas en varias guidelines, "
        "lo que deja a FIN sin criterios objetivos para decidir cuándo resolver de forma "
        "autónoma y cuándo escalar."
    )
    impact_desc = (
        f"El impacto operativo es directo: cada escalamiento evitable incrementa la carga del "
        f"equipo de soporte humano, prolonga el tiempo de resolución del usuario y deteriora "
        f"la percepción del servicio. "
        f"{'Con conflictos no resueltos entre guidelines, el riesgo de comportamiento inconsistente de FIN es alto.' if has_conflicts else 'La calidad técnica de las guidelines es suficiente para sostener el despliegue con los ajustes recomendados.'}"
    )
    if merge_log and has_conflicts:
        action_summary = (
            "Se recomienda priorizar la consolidación del conjunto de guidelines, "
            "resolver los conflictos detectados y validar el comportamiento esperado "
            "mediante simulaciones antes del próximo despliegue en producción."
        )
    elif merge_log:
        action_summary = (
            "La acción inmediata de mayor impacto es adoptar las guidelines consolidadas "
            "generadas en este reporte, que eliminan la redundancia e incrementan la consistencia "
            "del conjunto sin reducir la cobertura."
        )
    elif has_conflicts:
        action_summary = (
            "La prioridad es resolver los conflictos semánticos entre guidelines para garantizar "
            "que FIN no reciba instrucciones contradictorias ante el mismo escenario."
        )
    else:
        action_summary = (
            "El conjunto de guidelines está en condiciones de despliegue. "
            "Se recomienda validar con simulate_fin usando conversaciones adicionales "
            "y programar una revisión periódica con architect_review."
        )

    executive_summary = f"{what_happening} {why} {impact_desc} {action_summary}"

    # Riesgos
    risks = []
    if any(r["risk"] == "ALTO" for r in classification_results):
        risks.append("Guidelines con riesgo ALTO detectadas. Deben revisarse antes del despliegue.")
    if guidelines_with_issues:
        risks.append(f"{len(guidelines_with_issues)} guideline(s) presentaron problemas en auditoría.")
    if has_conflicts:
        risks.append("Conflictos entre guidelines pueden generar comportamientos contradictorios en FIN.")
    if avg_score < 60:
        risks.append("Puntaje promedio por debajo del umbral recomendado (60/100).")
    if health_score < 50:
        risks.append("Salud general crítica. Optimización prioritaria antes de publicar.")
    if not risks:
        risks.append("No se identificaron riesgos críticos. El conjunto de guidelines es estable.")

    urgent = [c for c in classification_results if c["priority"] == "URGENTE"]
    high   = [c for c in classification_results if c["priority"] == "ALTA"]
    normal = [c for c in classification_results if c["priority"] not in ("URGENTE", "ALTA")]

    recommendations = []
    if merge_log:
        recommendations.append(
            "Adoptar las guidelines consolidadas de este reporte, que reemplazan las versiones redundantes previas."
        )
    if guidelines_with_issues:
        recommendations.append(
            "Reemplazar las guidelines con problemas por sus versiones optimizadas antes de publicar."
        )
    if has_conflicts:
        recommendations.append(
            "Resolver los conflictos detectados entre guidelines para garantizar comportamiento consistente."
        )
    if avg_score < 70:
        recommendations.append(
            "Mejorar puntaje promedio usando optimize_guideline en las guidelines con score < 70."
        )
    if n_conditional < total_gl // 2 and total_gl > 1:
        recommendations.append(
            "Agregar condiciones explícitas ('únicamente cuando…', 'si se cumplen…') a las guidelines que carecen de ellas."
        )
    recommendations.append(
        "Validar cada guideline de prioridad URGENTE en conversaciones reales antes del próximo despliegue."
    )
    recommendations.append(
        "Ejecutar audit_guideline periódicamente para detectar degradación en la calidad del conjunto."
    )

    # MEJORA 3 — Plan de acción priorizado
    action_plan = []
    if merge_log:
        action_plan.append({"action": "Adoptar guidelines consolidadas (fusión de duplicados)",
                            "impact": "Alto", "effort": "Bajo", "priority": "CRÍTICA"})
    if has_conflicts:
        action_plan.append({"action": "Resolver conflictos semánticos entre guidelines",
                            "impact": "Alto", "effort": "Medio", "priority": "CRÍTICA"})
    if guidelines_with_issues:
        action_plan.append({"action": "Reemplazar guidelines con problemas de auditoría por versiones optimizadas",
                            "impact": "Alto", "effort": "Bajo", "priority": "ALTA"})
    if n_conditional < total_gl // 2 and total_gl > 1:
        action_plan.append({"action": "Agregar condiciones explícitas a guidelines sin criterios de escalamiento",
                            "impact": "Alto", "effort": "Medio", "priority": "ALTA"})
    action_plan.append({"action": "Validar guidelines con simulate_fin usando más conversaciones representativas",
                        "impact": "Medio", "effort": "Bajo", "priority": "MEDIA"})
    action_plan.append({"action": "Programar revisión periódica con architect_review al incorporar nuevas guidelines",
                        "impact": "Medio", "effort": "Bajo", "priority": "MEDIA"})
    if avg_score < 85:
        action_plan.append({"action": "Optimizar guidelines con score < 85 para alcanzar estándar de producción",
                            "impact": "Medio", "effort": "Medio", "priority": "NORMAL"})

    priority_order_map = {"CRÍTICA": 0, "ALTA": 1, "MEDIA": 2, "NORMAL": 3}
    action_plan.sort(key=lambda x: priority_order_map.get(x["priority"], 9))

    # Próximos pasos
    next_steps = []
    if urgent:
        next_steps.append(f"Revisar {len(urgent)} guideline(s) de prioridad URGENTE antes de cualquier otro paso.")
    if merge_log:
        next_steps.append("Publicar las guidelines consolidadas generadas en este reporte al repositorio de FIN.")
    if guidelines_with_issues:
        next_steps.append("Aplicar las versiones optimizadas al repositorio de guidelines.")
    if has_conflicts:
        next_steps.append("Ejecutar detect_conflicts nuevamente tras resolver los conflictos identificados.")
    next_steps.append("Ejecutar simulate_fin con más conversaciones para validar el comportamiento esperado.")
    next_steps.append("Programar una revisión arquitectónica periódica con architect_review.")

    # MEJORA 5 — Conclusión del Arquitecto
    if health_score >= 80:
        estado = (
            f"El producto {product} se encuentra en un estado arquitectónico saludable. "
            "Las guidelines propuestas son técnicamente sólidas y cubren los escenarios dominantes detectados."
        )
    elif health_score >= 60:
        estado = (
            f"El producto {product} tiene una base funcional pero presenta brechas en la cobertura "
            "de ciertos escenarios y en la consistencia entre guidelines."
        )
    else:
        estado = (
            f"El producto {product} requiere intervención arquitectónica antes del despliegue. "
            "El conjunto de guidelines actual presenta riesgos operativos que impactan directamente la experiencia del usuario."
        )

    if has_conflicts:
        principal_risk = (
            "El principal riesgo es el despliegue de guidelines conflictivas: FIN podría recibir "
            "instrucciones contradictorias para el mismo escenario y actuar de forma impredecible."
        )
    elif merge_log:
        principal_risk = (
            "El principal riesgo es la redundancia sin consolidar: guidelines semánticamente equivalentes "
            "pueden generar ambigüedad en la decisión de FIN y dificultar el mantenimiento futuro."
        )
    elif guidelines_with_issues:
        principal_risk = (
            "El principal riesgo es la presencia de guidelines con criterios de escalamiento "
            "indefinidos, que pueden provocar escalamientos innecesarios o resoluciones incompletas."
        )
    else:
        principal_risk = (
            "El riesgo más relevante en este momento es la cobertura incompleta: "
            "existen escenarios que las guidelines no contemplan explícitamente, "
            "lo que deja a FIN sin instrucciones claras en casos límite."
        )

    if n_conditional >= total_gl * 0.7:
        oportunidad = (
            "La mayor oportunidad está en ampliar el corpus de conversaciones para descubrir "
            "patrones residuales y garantizar cobertura completa antes de escalar el despliegue."
        )
    else:
        oportunidad = (
            "La mayor oportunidad está en estructurar las guidelines existentes como reglas "
            "condicionales explícitas. Esto reduciría los escalamientos innecesarios "
            "y mejoraría la tasa de resolución autónoma de FIN de forma inmediata."
        )

    if merge_log and has_conflicts:
        immediate_rec = (
            "Consolidar los duplicados e implementar las versiones fusionadas en este reporte. "
            "Resolver los conflictos detectados antes de cualquier despliegue."
        )
    elif merge_log:
        immediate_rec = (
            "Publicar las guidelines consolidadas generadas en este reporte. "
            "No desplegar las versiones redundantes anteriores."
        )
    elif has_conflicts:
        immediate_rec = (
            "Resolver los conflictos semánticos identificados antes del próximo despliegue. "
            "Ninguna guideline conflictiva debe publicarse sin revisión."
        )
    else:
        immediate_rec = (
            "Validar el comportamiento esperado de FIN con simulate_fin usando conversaciones "
            "adicionales y proceder al despliegue de las guidelines aprobadas."
        )

    if health_score >= 80 and not has_conflicts:
        next_review = (
            "Se recomienda ejecutar una nueva revisión con architect_review en un plazo de "
            "30 días o cuando se incorporen más de 3 nuevas guidelines al repositorio."
        )
    else:
        next_review = (
            "Se recomienda ejecutar una nueva revisión con architect_review inmediatamente "
            "después de aplicar los cambios indicados en el plan de acción, y antes de cualquier despliegue."
        )

    # ARCHITECT DECISION ENGINE
    DECISION_PROD_THRESHOLD  = 90
    DECISION_ELIM_THRESHOLD  = 70
    DECISION_MERGE_THRESHOLD = 0.85

    conflicting_guidelines = set()
    for line in conflict_lines:
        refs = _re.findall(r'[Gg]uideline\s+(\d+)', line)
        for r in refs:
            idx_c = int(r) - 1
            if 0 <= idx_c < len(final_guidelines):
                conflicting_guidelines.add(final_guidelines[idx_c])

    gl_absolute_set = set()
    for g in final_guidelines:
        gl_lower = g.lower()
        if any(gl_lower.startswith(m.rstrip()) or f" {m.rstrip()}" in gl_lower for m in _de.ABSOLUTE_TERMS[:4]):
            sc_abs = next((s for s in score_results if s["guideline"] == g), {})
            if sc_abs.get("score", 100) < 85:
                gl_absolute_set.add(g)

    merge_pairs_engine = []
    used_engine_merge  = set()
    for i_e, gi_e in enumerate(final_guidelines):
        for j_e, gj_e in enumerate(final_guidelines):
            if j_e <= i_e or i_e in used_engine_merge or j_e in used_engine_merge:
                continue
            sim_e = text_jaccard(gi_e, gj_e)
            if sim_e >= DECISION_MERGE_THRESHOLD:
                consolidated_e = max([gi_e, gj_e], key=len)
                merge_pairs_engine.append({
                    "original_a":   gi_e,
                    "original_b":   gj_e,
                    "consolidated": consolidated_e,
                    "similarity":   round(sim_e * 100),
                })
                used_engine_merge.add(i_e)
                used_engine_merge.add(j_e)

    merged_in_engine = (
        {p["original_a"] for p in merge_pairs_engine} |
        {p["original_b"] for p in merge_pairs_engine}
    )

    gl_prod_ready   = []
    gl_to_modify    = []
    gl_to_eliminate = []

    for g_d in final_guidelines:
        sc_d    = next((s for s in score_results if s["guideline"] == g_d), {})
        aud_d   = next((a for a in audit_results if a["guideline"] == g_d), {})
        score_d = sc_d.get("score", 0)
        has_d   = aud_d.get("has_issues", False)

        if g_d in merged_in_engine:
            continue

        if score_d < DECISION_ELIM_THRESHOLD:
            gl_to_eliminate.append({
                "guideline": g_d, "score": score_d,
                "reason": (
                    f"Score {score_d}/100 — por debajo del umbral mínimo de producción "
                    f"({DECISION_ELIM_THRESHOLD}/100). No garantiza comportamiento confiable de FIN."
                ),
            })
            continue

        if g_d in gl_absolute_set:
            gl_to_eliminate.append({
                "guideline": g_d, "score": score_d,
                "reason": (
                    "Usa términos absolutos ('siempre', 'nunca') sin condiciones explícitas. "
                    "Está siendo reemplazada por versiones condicionales en este conjunto y "
                    "genera riesgo de escalamientos innecesarios."
                ),
            })
            continue

        if (score_d >= DECISION_PROD_THRESHOLD
                and not has_d
                and g_d not in conflicting_guidelines):
            gl_prod_ready.append({"guideline": g_d, "score": score_d})
            continue

        mod_reasons = []
        mod_actions = []
        if score_d < DECISION_PROD_THRESHOLD:
            mod_reasons.append(
                f"Score {score_d}/100 — requiere mejora para alcanzar estándar de producción ({DECISION_PROD_THRESHOLD}/100)."
            )
            mod_actions.append("Agregar condiciones explícitas y contexto de aplicación.")
        if has_d:
            issue_texts = aud_d.get("issues", [])
            if issue_texts:
                mod_reasons.append(issue_texts[0])
            mod_actions.append("Revisar y corregir los problemas detectados en auditoría.")
        if g_d in conflicting_guidelines:
            mod_reasons.append("Genera conflicto semántico con otras guidelines del conjunto.")
            mod_actions.append("Acotar el alcance o añadir condiciones de precedencia.")
        if not mod_reasons:
            mod_reasons.append("Score aceptable pero requiere revisión antes del despliegue.")
            mod_actions.append("Validar con simulate_fin antes de publicar.")

        gl_to_modify.append({
            "guideline": g_d,
            "score":     score_d,
            "reason":    "; ".join(mod_reasons),
            "action":    "; ".join(mod_actions),
            "impact":    "Alto" if g_d in conflicting_guidelines or score_d < 80 else "Medio",
        })

    # DECISIÓN DE DESPLIEGUE
    n_prod_ready_d = len(gl_prod_ready)
    n_modify_d     = len(gl_to_modify)
    n_eliminate_d  = len(gl_to_eliminate)
    n_merge_engine = len(merge_pairs_engine)
    total_final_d  = len(final_guidelines)
    total_approved = n_prod_ready_d + n_merge_engine

    prod_ratio = (n_prod_ready_d / total_final_d) if total_final_d else 0

    if (health_score >= 80
            and not has_conflicts
            and n_eliminate_d == 0
            and prod_ratio >= 0.70):
        deploy_status = "🟢 READY FOR PRODUCTION"
        deploy_color  = "green"
        deploy_just   = (
            f"El {round(prod_ratio * 100)}% de las guidelines supera el umbral de producción "
            f"({DECISION_PROD_THRESHOLD}/100). No se detectaron conflictos ni guidelines que "
            "requieran eliminación. El conjunto está listo para despliegue inmediato."
        )
    elif (health_score >= 60
          or (n_prod_ready_d >= total_final_d * 0.5 and not has_conflicts)):
        deploy_status = "🟡 READY WITH RECOMMENDATIONS"
        deploy_color  = "yellow"
        issues_s = []
        if n_modify_d > 0:
            issues_s.append(f"{n_modify_d} guideline(s) requieren modificación")
        if n_eliminate_d > 0:
            issues_s.append(f"{n_eliminate_d} guideline(s) deben eliminarse")
        if n_merge_engine > 0:
            issues_s.append(f"{n_merge_engine} par(es) deben fusionarse")
        deploy_just = (
            f"El conjunto puede avanzar a producción con las correcciones indicadas: "
            f"{', '.join(issues_s) if issues_s else 'ajustes menores recomendados'}. "
            "Desplegar únicamente las guidelines clasificadas como LISTAS PARA PRODUCCIÓN. "
            "No publicar las clasificadas como MODIFICAR o ELIMINAR sin revisión previa."
        )
    else:
        deploy_status = "🔴 NOT READY"
        deploy_color  = "red"
        blockers = []
        if has_conflicts:
            blockers.append("conflictos semánticos sin resolver")
        if n_eliminate_d > 0:
            blockers.append(f"{n_eliminate_d} guideline(s) con score crítico")
        if health_score < 60:
            blockers.append(f"salud general por debajo del umbral ({health_score}/100)")
        deploy_just = (
            f"El conjunto NO está listo para producción. Bloqueadores: "
            f"{', '.join(blockers) if blockers else 'múltiples problemas críticos'}. "
            "Resolver todos los bloqueadores y ejecutar una nueva revisión antes del despliegue."
        )

    # IMPACTO ESTIMADO
    n_conflicts_count = len(conflict_lines)

    # Fill deferred health score penalty components
    _hs_conflict_pen = -(min(15, n_conflicts_count * 5)) if has_conflicts else 0
    _hs_dup_pen      = -(min(10, (len(merge_log) + n_merge_engine) * 3))
    _hs_abs_pen      = -(min(8,  len(gl_absolute_set) * 4))

    n_absolute_elim   = sum(
        1 for el in gl_to_eliminate
        if "absolutos" in el.get("reason", "").lower()
        or "siempre" in el.get("reason", "").lower()
    )

    esc_base          = min(n_conflicts_count * 8 + n_absolute_elim * 10 + n_merge_engine * 5, 60)
    esc_reduction_str = f"~{esc_base}–{min(esc_base + 10, 70)}%"

    cond_ratio_d = n_conditional / total_final_d if total_final_d else 0
    auto_base    = round(cond_ratio_d * 40) + (5 if prod_ratio >= 0.6 else 0)
    auto_str     = f"~{auto_base}–{auto_base + 10}%"

    time_base = max(0, min(round((avg_score - 70) / 3) + n_merge_engine * 3, 35)) if avg_score > 70 else 0
    time_str  = f"~{time_base}–{min(time_base + 8, 40)}%"

    load_base = round(esc_base * 0.7)
    load_str  = f"~{load_base}–{min(load_base + 8, 55)}%"

    cons_base = min(n_merge_engine * 12 + (15 if has_conflicts else 0) + n_absolute_elim * 8, 50)
    cons_str  = f"~{cons_base}–{min(cons_base + 10, 60)}%"

    # ROADMAP
    roadmap = []

    phase1_tasks = []
    if gl_to_eliminate:
        phase1_tasks.append(
            f"Eliminar {len(gl_to_eliminate)} guideline(s) clasificada(s) para eliminación "
            "(ver sección DECISIONES ARQUITECTÓNICAS → ELIMINAR)."
        )
    if has_conflicts:
        phase1_tasks.append("Resolver conflictos semánticos identificados entre guidelines.")
    if not phase1_tasks:
        phase1_tasks.append("Verificar que no queden guidelines obsoletas en el repositorio.")
    roadmap.append({"phase": "Fase 1 — Depuración y Estabilización",
                    "obj": "Eliminar riesgos críticos antes del despliegue.",
                    "tasks": phase1_tasks, "duration": "1–2 días"})

    phase2_tasks = []
    if merge_pairs_engine:
        phase2_tasks.append(
            f"Fusionar {n_merge_engine} par(es) de guidelines con similitud ≥ 85% "
            "usando las versiones consolidadas generadas en este reporte."
        )
    if merge_log:
        phase2_tasks.append(
            f"Confirmar las {len(merge_log)} fusión/fusiones automáticas ≥ 90% "
            "generadas en este reporte."
        )
    if not phase2_tasks:
        phase2_tasks.append("Validar consistencia del conjunto de guidelines activo.")
    roadmap.append({"phase": "Fase 2 — Consolidación",
                    "obj": "Reducir redundancia y mejorar consistencia del repositorio.",
                    "tasks": phase2_tasks, "duration": "1–3 días"})

    phase3_tasks = []
    if gl_to_modify:
        phase3_tasks.append(
            f"Aplicar modificaciones a {n_modify_d} guideline(s) según las acciones "
            "recomendadas en la sección MODIFICAR."
        )
    if optimized_map:
        phase3_tasks.append(
            f"Incorporar las {len(optimized_map)} versión(es) optimizadas "
            "generadas en este análisis."
        )
    phase3_tasks.append(
        "Ejecutar score_guideline en las guidelines modificadas para verificar mejora."
    )
    roadmap.append({"phase": "Fase 3 — Optimización",
                    "obj": "Elevar la calidad técnica del conjunto al estándar de producción.",
                    "tasks": phase3_tasks, "duration": "2–4 días"})

    phase4_tasks = [
        "Ejecutar simulate_fin con las guidelines aprobadas y conversaciones representativas.",
        "Ejecutar architect_review con el conjunto final para confirmar estado de despliegue.",
        f"Desplegar las {total_approved} guideline(s) aprobadas al entorno de producción de FIN.",
        "Programar revisión arquitectónica periódica.",
    ]
    roadmap.append({"phase": "Fase 4 — Validación y Despliegue",
                    "obj": "Confirmar comportamiento esperado e implementar en producción.",
                    "tasks": phase4_tasks, "duration": "1–2 días"})

    # DECISIONES DEL ARQUITECTO (narrativa)
    arch_parts = []
    arch_parts.append(
        f"El análisis de {total_convs} conversación(es) sobre {product} revela que el conjunto de guidelines "
        + (
            "requiere intervención antes del despliegue."
            if deploy_color == "red"
            else "está en condiciones de avanzar con los ajustes indicados."
            if deploy_color == "yellow"
            else "está listo para producción."
        )
    )
    for el in gl_to_eliminate[:3]:
        short_el = el["guideline"][:80] + ("..." if len(el["guideline"]) > 80 else "")
        arch_parts.append(f"La guideline \"{short_el}\" no debería desplegarse. {el['reason']}")
    for mp in merge_pairs_engine[:3]:
        a_s = mp["original_a"][:60] + ("..." if len(mp["original_a"]) > 60 else "")
        b_s = mp["original_b"][:60] + ("..." if len(mp["original_b"]) > 60 else "")
        c_s = mp["consolidated"][:80] + ("..." if len(mp["consolidated"]) > 80 else "")
        arch_parts.append(
            f"Las guidelines \"{a_s}\" y \"{b_s}\" describen el mismo comportamiento "
            f"con una similitud del {mp['similarity']}%. "
            f"Deben fusionarse en: \"{c_s}\". "
            "La guideline consolidada cubre ambos escenarios con menor complejidad y menor riesgo operacional."
        )
    for mod in gl_to_modify[:2]:
        short_mod = mod["guideline"][:70] + ("..." if len(mod["guideline"]) > 70 else "")
        arch_parts.append(
            f"La guideline \"{short_mod}\" tiene potencial pero requiere ajuste: "
            f"{mod['reason']} Acción recomendada: {mod['action']}"
        )
    if gl_prod_ready:
        arch_parts.append(
            f"Se recomienda implementar únicamente las {n_prod_ready_d} guideline(s) "
            "clasificadas como listas para producción y repetir el análisis con "
            "architect_review después de incorporar nuevas conversaciones."
        )
    if deploy_color == "red":
        arch_parts.append(
            "Ninguna guideline debe desplegarse en su estado actual. "
            "El conjunto requiere depuración, resolución de conflictos y revalidación "
            "completa antes de ser entregado a producción."
        )
    elif deploy_color == "yellow":
        arch_parts.append(
            "El despliegue parcial es viable. Publicar exclusivamente las guidelines "
            "marcadas como LISTAS PARA PRODUCCIÓN. Las guidelines en MODIFICAR y FUSIONAR "
            "deben procesarse en el ciclo siguiente antes de incluirse."
        )
    else:
        arch_parts.append(
            "El conjunto está listo. El despliegue puede proceder con confianza. "
            "Mantener la cadencia de revisión periódica para detectar degradación "
            "conforme el producto evoluciona."
        )

    arch_decisions_narrative = "\n\n".join(arch_parts)

    # MÉTRICAS DE GOBERNANZA
    n_active_gov   = len(final_guidelines)
    n_new_gov      = len([g for g in final_guidelines if g not in current_guidelines])
    n_elim_gov     = n_eliminate_d
    n_merged_gov   = len(merge_log) + n_merge_engine
    n_modified_gov = len(optimized_map)
    coverage_gov   = round(
        min(100, (n_prod_ready_d + n_merge_engine) / max(total_final_d, 1) * 100
            + (10 if not has_conflicts else 0))
    )
    consistency_gov = mat_consistency
    complexity_raw  = total_final_d * 5 + n_conflicts_count * 10 + n_merged_gov * 3
    if complexity_raw < 30:
        complexity_label_gov = "Baja"
    elif complexity_raw < 70:
        complexity_label_gov = "Media"
    elif complexity_raw < 120:
        complexity_label_gov = "Alta"
    else:
        complexity_label_gov = "Muy Alta"

    if deploy_color == "green":
        gov_state = "✅ ESTABLE"
    elif deploy_color == "yellow":
        gov_state = "⚠️ EN PROGRESO"
    else:
        gov_state = "🔴 REQUIERE INTERVENCIÓN"

    # ================================================================== #
    # NUEVAS MÉTRICAS v4                                                  #
    # ================================================================== #

    # 1. COBERTURA FUNCIONAL
    area_kw = {
        "Caja":             ["caja", "turno", "cierre", "apertura"],
        "Facturación":      ["factura", "cufe", "nota crédito", "documento electrónico"],
        "Sincronización":   ["sincronizar", "sincronización", "sincroniza"],
        "Escalamiento":     ["escalar", "escala", "transfiere", "transferir", "agente humano"],
        "Urgencias":        ["urgencia", "urgente", "inmediato", "prioriza"],
        "Inventario":       ["inventario", "stock", "producto"],
        "Acceso":           ["acceso", "contraseña", "login", "usuario", "permiso"],
        "Configuración":    ["configurar", "configuración", "parámetro"],
        "Errores Técnicos": ["error", "falla", "reiniciar", "navega", "validar"],
        "Documentación":    ["artículo", "guía", "documentado", "pasos documentados"],
    }
    area_coverage = {}
    for area_name, keywords in area_kw.items():
        hits = sum(1 for g in final_guidelines if any(kw in g.lower() for kw in keywords))
        area_coverage[area_name] = min(100, hits * 25)

    def cov_bar(pct):
        filled = round(pct / 10)
        return "█" * filled + "░" * (10 - filled)

    covered_areas    = [a for a, p in area_coverage.items() if p >= 75]
    partial_areas    = [a for a, p in area_coverage.items() if 10 <= p < 75]
    uncovered_areas  = [a for a, p in area_coverage.items() if p < 10]
    overcovered_areas = [a for a, p in area_coverage.items() if p >= 100 and
                         sum(1 for g in final_guidelines if any(kw in g.lower() for kw in area_kw[a])) >= 4]

    # 2. MÉTRICAS DEL REPOSITORIO
    repo_total       = len(final_guidelines)
    repo_duplicated  = len(merge_log) + n_merge_engine
    repo_merged      = len(merge_log) + n_merge_engine
    repo_orphans_n   = 0
    repo_obsolete    = n_eliminate_d
    repo_conflicting = len(conflicting_guidelines)
    repo_conditional = n_conditional
    repo_absolute    = len(gl_absolute_set)
    repo_optimized   = len(optimized_map)
    repo_approved    = n_prod_ready_d
    repo_rejected    = n_eliminate_d

    # 3. ÍNDICE DE MANTENIBILIDAD
    dup_pen   = min((len(merge_log) + n_merge_engine) * 5, 25)
    conf_pen  = min(n_conflicts_count * 8, 25)
    comp_pen  = {"Baja": 0, "Media": 5, "Alta": 12, "Muy Alta": 20}.get(complexity_label_gov, 10)
    size_pen  = max(0, (repo_total - 12) * 2)
    cond_bon  = round(cond_ratio_d * 20)
    score_bon = round((avg_score - 70) / 3) if avg_score > 70 else 0

    maint_idx = max(0, min(100, 100 - dup_pen - conf_pen - comp_pen - size_pen + cond_bon + score_bon))

    if maint_idx >= 85:
        maint_label, maint_reason = "Excelente", "Repositorio limpio, pocos conflictos y alta proporción de reglas condicionales."
    elif maint_idx >= 70:
        maint_label, maint_reason = "Buena", "Repositorio manejable con oportunidades de simplificación."
    elif maint_idx >= 55:
        maint_label, maint_reason = "Media", "Duplicados y/o conflictos reducen la claridad operacional del conjunto."
    elif maint_idx >= 40:
        maint_label, maint_reason = "Baja", "Repositorio con alta complejidad estructural. Requiere depuración antes del despliegue."
    else:
        maint_label, maint_reason = "Crítica", "Repositorio inestable. Conflictos, duplicados y reglas absolutas comprometen el comportamiento de FIN."

    # 4. CONFIDENCE DEL ANÁLISIS
    n_conv_cf = len(conversations)
    n_pat_cf  = sum(1 for l in patterns_block if l.startswith("Patrón #"))
    avg_cov   = round(sum(area_coverage.values()) / len(area_coverage)) if area_coverage else 0

    conv_sc     = 30 if n_conv_cf >= 10 else (20 if n_conv_cf >= 5 else 10)
    pat_sc      = min(20, n_pat_cf * 5)
    cov_sc      = round(avg_cov * 0.20)
    conf_pen_cf = min(15, n_conflicts_count * 5)
    cons_sc     = round(mat_consistency * 0.15)

    confidence_raw = max(0, min(100, conv_sc + pat_sc + cov_sc + cons_sc - conf_pen_cf))

    if confidence_raw >= 85:
        conf_label  = "Muy Alta"
        conf_reason = f"Análisis basado en {n_conv_cf} conversaciones con alta consistencia interna y cobertura amplia."
    elif confidence_raw >= 70:
        conf_label  = "Alta"
        conf_reason = f"Análisis robusto. {n_conv_cf} conversaciones y {n_pat_cf} patrones detectados. Margenes de mejora menores."
    elif confidence_raw >= 50:
        conf_label  = "Media"
        conf_reason = f"Análisis válido pero limitado por el volumen de conversaciones ({n_conv_cf}) o la presencia de conflictos."
    elif confidence_raw >= 35:
        conf_label  = "Baja"
        conf_reason = f"Corpus de conversaciones insuficiente ({n_conv_cf}). Las decisiones deben validarse con más datos antes del despliegue."
    else:
        conf_label  = "Muy Baja"
        conf_reason = f"Muy pocas conversaciones ({n_conv_cf}). El análisis es orientativo. No desplegar sin ampliar el corpus."

    # CONFIDENCE REASONS — explicit bullet list
    _conf_reasons = []
    if n_conv_cf < 10:
        _conf_reasons.append(f"Solo se analizaron {n_conv_cf} conversaciones (se recomiendan ≥ 10).")
    if avg_cov < 50:
        _conf_reasons.append(f"Cobertura funcional parcial del producto ({avg_cov}% promedio).")
    if has_conflicts:
        _conf_reasons.append(f"Existen {n_conflicts_count} conflicto(s) activo(s) entre guidelines.")
    if (len(merge_log) + n_merge_engine) > 0:
        _conf_reasons.append(f"Se detectaron {len(merge_log) + n_merge_engine} guideline(s) duplicada(s).")
    if n_conv_cf < 5:
        _conf_reasons.append("Algunas conclusiones se basan en muy pocos ejemplos.")
    if n_pat_cf == 0:
        _conf_reasons.append("No se detectaron patrones recurrentes con suficiente frecuencia.")
    if mat_consistency < 60:
        _conf_reasons.append(f"Consistencia interna baja ({mat_consistency}%), lo que reduce la fiabilidad del análisis.")
    # If confidence is actually high, explain why instead
    if confidence_raw >= 70:
        _conf_reasons = [
            f"Corpus de {n_conv_cf} conversaciones analizado.",
            f"Cobertura funcional del {avg_cov}%.",
            f"{n_pat_cf} patrón(es) detectado(s) con recurrencia.",
            f"Consistencia interna del {mat_consistency}%.",
        ]
        if not has_conflicts:
            _conf_reasons.append("Sin conflictos activos entre guidelines.")

    # Complete health score breakdown (fill deferred fields after avg_cov/maint_idx are available)
    _hs_coverage = min(20, round(avg_cov * 0.20))
    _hs_maint_b  = min(10, round(maint_idx * 0.10))
    # Build breakdown list: (label, value, is_positive)
    _hs_breakdown = [
        ("Calidad promedio de guidelines",    _hs_quality,      True),
        ("Cobertura funcional",               _hs_coverage,     True),
        ("Mantenibilidad del repositorio",    _hs_maint_b,      True),
        ("Conflictos semánticos",             _hs_conflict_pen, False),
        ("Guidelines duplicadas",             _hs_dup_pen,      False),
        ("Reglas absolutas sin condición",    _hs_abs_pen,      False),
    ]
    # Remove zero-value negative items to keep the table clean
    _hs_breakdown = [(l, v, p) for l, v, p in _hs_breakdown if v != 0]

    # 5. GUIDELINES HUÉRFANAS
    all_conv_text = " ".join(
        (c.get("text", c) if isinstance(c, dict) else c).lower()
        for c in conversations
    )
    stopwords_h = {"si", "el", "la", "los", "las", "un", "una", "de", "del", "en", "es",
                   "y", "o", "a", "al", "que", "con", "por", "para", "no", "se", "su",
                   "lo", "le", "cuando", "donde", "como", "más", "pero", "ya", "muy",
                   "fin", "usuario", "cliente", "guideline", "artículo", "guía"}
    orphan_guidelines = []
    for g_h in final_guidelines:
        words_h   = {w for w in g_h.lower().split() if w not in stopwords_h and len(w) > 4}
        matches_h = sum(1 for w in words_h if w in all_conv_text)
        if len(words_h) > 3 and matches_h < 2:
            orphan_guidelines.append(g_h)
    repo_orphans_n = len(orphan_guidelines)

    # 6. MATRIZ DE COBERTURA
    matrix_scenarios = list(area_kw.keys())
    for kw_pair in [("sincroniz", "Sincronización"), ("caja", "Caja"), ("factura", "Facturación"),
                    ("inventario", "Inventario"), ("error", "Errores Técnicos"), ("urgencia", "Urgencias")]:
        if kw_pair[0] in all_conv_text and kw_pair[1] not in matrix_scenarios:
            matrix_scenarios.append(kw_pair[1])

    def scenario_status(scenario):
        kws   = area_kw.get(scenario, [scenario.lower()])
        count = sum(1 for g in final_guidelines if any(kw in g.lower() for kw in kws))
        if count >= 2:
            return "✅", "Cubierto"
        elif count == 1:
            return "⚠️", "Parcial"
        else:
            return "❌", "Sin cobertura"

    matrix_rows      = [(s, *scenario_status(s)) for s in matrix_scenarios]
    uncovered_matrix = [r[0] for r in matrix_rows if r[1] == "❌"]

    # 7. SIMULACIÓN DE IMPACTO
    curr_esc       = max(25, 100 - health_score)
    curr_autonomy  = mat_autonomous
    curr_conflicts = n_conflicts_count
    curr_dups      = len(merge_log) + n_merge_engine

    exp_esc       = max(10, curr_esc - esc_base)
    exp_autonomy  = min(90, curr_autonomy + auto_base)
    exp_conflicts = max(0, curr_conflicts - (n_conflicts_count if not has_conflicts else 2))
    exp_dups      = 0

    def arrow(curr, exp, lower_better=False):
        if lower_better:
            return "↓" if exp < curr else ("↑" if exp > curr else "→")
        return "↑" if exp > curr else ("↓" if exp < curr else "→")

    # 8. RESUMEN EJECUTIVO PARA PM
    pm_what = (
        f"FIN está escalando casos que podría resolver de forma autónoma en {product}. "
        f"Detectamos {n_conflicts_count} conflicto(s) entre reglas y {repo_duplicated} guideline(s) "
        "redundante(s) que generan comportamientos inconsistentes."
        if has_conflicts or repo_duplicated > 0
        else
        f"El sistema de reglas de FIN para {product} funciona correctamente en los escenarios documentados "
        "pero tiene brechas de cobertura que podrían generar escalamientos en casos no contemplados."
    )
    pm_why = (
        "Ocurre porque algunas reglas se contradicen entre sí y otras aplican sin condiciones, "
        "obligando a FIN a escalar aunque exista solución disponible."
        if has_conflicts
        else
        "La causa principal es que varias reglas carecen de condiciones explícitas. "
        "FIN no sabe cuándo aplicarlas, lo que genera decisiones inconsistentes."
    )
    pm_first = (
        f"Eliminar {n_eliminate_d} regla(s) obsoleta(s), resolver los conflictos y publicar únicamente "
        f"las {n_prod_ready_d} reglas validadas. Todo puede hacerse en menos de una semana."
        if n_eliminate_d > 0 or has_conflicts
        else
        f"Publicar las {n_prod_ready_d} reglas validadas e incorporar más conversaciones para ampliar cobertura."
    )
    pm_impact = (
        f"Se estima una reducción de {esc_reduction_str} en escalamientos y un incremento de "
        f"{auto_str} en resolución autónoma. Menos carga para el equipo de soporte humano."
    )
    pm_risk = (
        "Si no se actúa, FIN continuará escalando casos resolubles, incrementando el tiempo de atención "
        "y la carga operativa del equipo de soporte."
        if health_score < 75
        else
        "El riesgo actual es bajo. Sin embargo, no consolidar las reglas redundantes puede generar "
        "inconsistencias a medida que el conjunto de guidelines crece."
    )

    # 9. RESUMEN EJECUTIVO PARA SOPORTE
    support_fin_changes = (
        f"FIN verificará si el usuario ya intentó la solución antes de repetirla. "
        f"En los patrones detectados ({', '.join([str(i+1) for i in range(min(3, sum(1 for l in patterns_block if l.startswith('Patrón #'))))]) or 'los identificados'}), "
        "FIN escalará directamente al detectar intentos previos documentados."
    )
    support_agent_changes = (
        f"Los agentes recibirán {n_prod_ready_d} reglas nuevas o actualizadas. "
        "Los escalamientos incluirán más contexto: error exacto, pasos realizados y resultado. "
        f"Se espera una reducción de {esc_reduction_str} en volumen de escalamientos."
    )

    # PRIORITY SORT for gl_to_modify (multi-factor)
    def eng_priority(item):
        s      = item["score"]
        in_conf = 15 if any(kw in item["guideline"].lower() for kw in ["escal", "urgencia", "bloqueado", "caja"]) else 0
        ease   = 10 if len(item["guideline"].split()) < 25 else 5
        cov    = 10 if any(area.lower() in item["guideline"].lower() for area in covered_areas) else 0
        return s * 0.5 + in_conf + ease + cov
    gl_to_modify.sort(key=eng_priority, reverse=True)

    # GL index
    gl_index = {g: f"GL-{i+1}" for i, g in enumerate(final_guidelines)}

    # DEPLOYMENT BLOCKERS
    _blockers = []
    if has_conflicts:
        _blockers.append(("🔴", f"{n_conflicts_count} conflicto(s) semántico(s) sin resolver"))
    _n_abs_elim = len([e for e in gl_to_eliminate if any(t in e.get("reason", "").lower() for t in ["absolut", "siempre", "nunca"])])
    if _n_abs_elim:
        _blockers.append(("🔴", f"{_n_abs_elim} regla(s) con términos absolutos sin condición"))
    if health_score < 40:
        _blockers.append(("🔴", f"Salud general crítica ({health_score}/100 — mínimo requerido: 80)"))
    if n_eliminate_d > 0 and not _n_abs_elim:
        _blockers.append(("🔴", f"{n_eliminate_d} guideline(s) con score por debajo del mínimo de producción"))
    if confidence_raw < 50:
        _blockers.append(("🟠", f"Confidence del análisis menor al 50% ({confidence_raw}%)"))
    for _ua in uncovered_areas:
        _blockers.append(("🟠", f"Cobertura insuficiente en área: {_ua}"))
    if avg_score < 70:
        _blockers.append(("🟠", f"Score promedio de guidelines por debajo de 70 ({avg_score}/100)"))

    # TOP 5 ACTIONS by multi-factor impact score
    _all_actions = []

    # Eliminate actions
    for _el in gl_to_eliminate:
        _gl_ref_a = gl_index.get(_el["guideline"], "GL-?")
        _impact_s = 90 if any(t in _el.get("reason","").lower() for t in ["absolut","conflicto"]) else 70
        _all_actions.append({
            "type": "ELIMINAR",
            "ref": _gl_ref_a,
            "desc": f"Eliminar {_gl_ref_a}: {_el['guideline'][:60]}{'...' if len(_el['guideline'])>60 else ''}",
            "benefit": _el["reason"][:120],
            "impact_label": "Muy Alto" if _impact_s >= 85 else "Alto",
            "score": _impact_s,
        })

    # Conflict resolution
    if has_conflicts:
        _all_actions.append({
            "type": "RESOLVER CONFLICTO",
            "ref": "—",
            "desc": f"Resolver {n_conflicts_count} conflicto(s) semántico(s) entre guidelines",
            "benefit": "Elimina comportamientos contradictorios e impredecibles en FIN.",
            "impact_label": "Muy Alto",
            "score": 88,
        })

    # Merge actions
    for _mp in merge_pairs_engine[:3]:
        _gl_a = gl_index.get(_mp["original_a"], "GL-?")
        _gl_b = gl_index.get(_mp["original_b"], "GL-?")
        _all_actions.append({
            "type": "FUSIONAR",
            "ref": f"{_gl_a} + {_gl_b}",
            "desc": f"Fusionar {_gl_a} y {_gl_b} (similitud {_mp['similarity']}%)",
            "benefit": "Reduce redundancia y mejora consistencia del repositorio.",
            "impact_label": "Alto",
            "score": 72,
        })

    # Modify actions (top 3 by engine priority)
    for _mod in gl_to_modify[:3]:
        _gl_ref_m = gl_index.get(_mod["guideline"], "GL-?")
        _mod_sc = 65 if _mod["impact"] == "Alto" else 50
        _all_actions.append({
            "type": "MODIFICAR",
            "ref": _gl_ref_m,
            "desc": f"Modificar {_gl_ref_m}: {_mod['guideline'][:55]}{'...' if len(_mod['guideline'])>55 else ''}",
            "benefit": _mod["action"][:120],
            "impact_label": _mod["impact"],
            "score": _mod_sc,
        })

    # Coverage gaps
    for _uc in uncovered_areas[:2]:
        _all_actions.append({
            "type": "AMPLIAR COBERTURA",
            "ref": _uc,
            "desc": f"Crear guideline para área sin cobertura: {_uc}",
            "benefit": f"FIN tendrá instrucciones claras para escenarios de {_uc}.",
            "impact_label": "Medio",
            "score": 45,
        })

    _all_actions.sort(key=lambda x: -x["score"])
    _top5_actions = _all_actions[:5]

    # DEPLOYMENT DECISION — extended explanation
    if deploy_color == "red":
        _deploy_exec_motivo = (
            "El repositorio contiene reglas contradictorias"
            + (f" ({n_conflicts_count} conflicto(s))" if has_conflicts else "")
            + (f" y {_n_abs_elim} regla(s) absolutas" if _n_abs_elim else "")
            + " que pueden provocar comportamientos inconsistentes en FIN. "
            "Se deben resolver los Deployment Blockers antes del siguiente despliegue."
        )
    elif deploy_color == "yellow":
        _deploy_exec_motivo = (
            f"El repositorio puede avanzar a producción con {n_prod_ready_d} guideline(s) validadas, "
            "pero contiene elementos que deben corregirse antes de un despliegue completo. "
            "Aplicar las acciones de mayor impacto listadas en TOP ACCIONES."
        )
    else:
        _deploy_exec_motivo = (
            f"Todas las guidelines superan el umbral de producción ({DECISION_PROD_THRESHOLD}/100). "
            "No se detectaron conflictos ni reglas bloqueantes. "
            "El repositorio puede desplegarse con confianza."
        )

    # ARCHITECT FINAL SUMMARY — 4 questions
    _summary_sano = (
        "Sí." if health_score >= 80
        else f"No. Salud actual: {health_score}/100."
    )
    if has_conflicts and gl_to_eliminate:
        _summary_problema = (
            f"Conflictos semánticos activos ({n_conflicts_count}) combinados con {n_eliminate_d} regla(s) "
            "absolutas o de baja calidad que generan escalamientos innecesarios."
        )
    elif has_conflicts:
        _summary_problema = (
            f"{n_conflicts_count} conflicto(s) semántico(s) que provocan comportamientos "
            "contradictorios en FIN ante el mismo escenario."
        )
    elif gl_to_eliminate:
        _summary_problema = (
            f"{n_eliminate_d} guideline(s) con términos absolutos o score crítico que deben "
            "eliminarse antes del despliegue."
        )
    elif len(merge_log) + n_merge_engine > 0:
        _summary_problema = (
            f"{len(merge_log) + n_merge_engine} guideline(s) redundante(s) que incrementan "
            "la complejidad del repositorio sin aportar cobertura adicional."
        )
    else:
        _summary_problema = (
            f"Cobertura funcional incompleta en {len(uncovered_areas)} área(s). "
            "FIN carece de instrucciones para esos escenarios."
        )

    if _top5_actions:
        _t = _top5_actions[0]
        _summary_accion = f"{_t['type']} {_t['ref']}: {_t['desc'][:80]}."
    else:
        _summary_accion = "Ampliar el corpus de conversaciones y ejecutar una nueva revisión."

    _pct_esc = esc_base
    _summary_resultado = (
        f"Se estima una reducción de ~{_pct_esc}–{min(_pct_esc+10,70)}% en escalamientos "
        f"y un incremento de ~{auto_base}–{auto_base+10}% en resolución autónoma."
    )

    # ================================================================== #
    # CONSTRUCCIÓN DEL REPORTE v4                                         #
    # ================================================================== #
    sep  = "=" * 48
    div2 = "─" * 40
    div3 = "·" * 40
    parts = []

    # SECTION 1 — HEADER
    parts += [sep, "FIN ARCHITECT REVIEW  ·  v4.1", f"{sep}\n"]
    parts.append(
        f"PRODUCTO: {product.upper()}  |  SALUD: {health_emoji} {health_score}/100 — {health_label}"
    )
    parts.append(f"OBJETIVO: {objective if objective else 'No especificado'}")
    parts.append(
        f"CONVERSACIONES: {total_convs}  |  CONFIANZA: {conf_label} ({confidence_raw}%)  |  MANTENIBILIDAD: {maint_label} ({maint_idx}%)"
    )
    parts.append("")

    # SECTION 1b — HEALTH SCORE BREAKDOWN
    parts.append("HEALTH SCORE — Desglose del puntaje\n")
    _hs_col_w = 42
    for _lbl, _val, _pos in _hs_breakdown:
        _prefix = "+" if _pos else ""
        _sign   = f"{_prefix}{_val}"
        _dots   = "." * max(1, _hs_col_w - len(_lbl))
        parts.append(f"  {_lbl} {_dots} {_sign:>5}")
    parts.append(f"  {'─' * _hs_col_w}{'─' * 8}")
    parts.append(f"  {'TOTAL':>{_hs_col_w + 4}} {health_score:>5}")
    parts.append("")

    # SECTION 1c — CONFIDENCE BREAKDOWN
    parts.append(f"CONFIDENCE — {conf_label} ({confidence_raw}%)\n")
    if _conf_reasons:
        parts.append("  Motivos:")
        for _cr in _conf_reasons:
            parts.append(f"  • {_cr}")
    parts.append("")

    # SECTION 2 — RESUMEN EJECUTIVO PARA PRODUCT MANAGER
    parts += [div3, "RESUMEN EJECUTIVO PARA PRODUCT MANAGER", f"{div3}\n"]
    parts.append(f"¿Qué está pasando?\n  {pm_what}\n")
    parts.append(f"¿Por qué ocurre?\n  {pm_why}\n")
    parts.append(f"¿Qué hacer primero?\n  {pm_first}\n")
    parts.append(f"¿Qué impacto tendrá?\n  {pm_impact}\n")
    parts.append(f"¿Qué pasa si no se actúa?\n  {pm_risk}\n")

    # SECTION 3 — SIMULACIÓN DE IMPACTO
    parts += [div3, "SIMULACIÓN DE IMPACTO", f"{div3}\n"]
    parts.append(f"  {'Métrica':<35} {'Actual':>8}   {'Esperado':>8}   Tendencia")
    parts.append(f"  {'─'*35} {'─'*8}   {'─'*8}   {'─'*9}")
    parts.append(f"  {'Tasa de escalamiento':<35} {curr_esc:>7}%   {exp_esc:>7}%   {arrow(curr_esc, exp_esc, lower_better=True)}")
    parts.append(f"  {'Resolución autónoma':<35} {curr_autonomy:>7}%   {exp_autonomy:>7}%   {arrow(curr_autonomy, exp_autonomy)}")
    parts.append(f"  {'Conflictos activos':<35} {curr_conflicts:>8}   {exp_conflicts:>8}   {arrow(curr_conflicts, exp_conflicts, lower_better=True)}")
    parts.append(f"  {'Guidelines duplicadas':<35} {curr_dups:>8}   {exp_dups:>8}   {arrow(curr_dups, exp_dups, lower_better=True)}")
    parts.append("")

    # SECTION 4 — HALLAZGOS PRINCIPALES
    parts += [div3, "HALLAZGOS PRINCIPALES", f"{div3}\n"]
    for fi in findings[:6]:
        parts.append(f"  {fi}")
    parts.append("")

    # SECTION 5 — COBERTURA FUNCIONAL
    parts += [div3, "COBERTURA FUNCIONAL", f"{div3}\n"]
    for area_name, pct in area_coverage.items():
        bar = cov_bar(pct)
        parts.append(f"  {area_name:<20} [{bar}] {pct:>3}%")
    parts.append("")
    if covered_areas:
        parts.append(f"  Bien cubiertos: {', '.join(covered_areas)}")
    if partial_areas:
        parts.append(f"  Cobertura parcial: {', '.join(partial_areas)}")
    if uncovered_areas:
        parts.append(f"  Sin cobertura: {', '.join(uncovered_areas)}")
    if overcovered_areas:
        parts.append(f"  Sobrecubiertos (posible redundancia): {', '.join(overcovered_areas)}")
    parts.append("")

    # SECTION 6 — MATRIZ DE COBERTURA
    parts += [div3, "MATRIZ DE COBERTURA", f"{div3}\n"]
    parts.append(f"  {'Escenario':<22} {'Estado':<6} Observación")
    parts.append(f"  {'─'*22} {'─'*6} {'─'*20}")
    for row in matrix_rows:
        parts.append(f"  {row[0]:<22} {row[1]:<6} {row[2]}")
    parts.append("")

    # ARCHITECT DECISION ENGINE
    parts += [div2, "ARCHITECT DECISION ENGINE", f"{div2}\n"]

    # SECTION — DEPLOYMENT BLOCKERS
    parts.append("► DEPLOYMENT BLOCKERS\n")
    if _blockers:
        for _b_icon, _b_txt in _blockers:
            parts.append(f"  {_b_icon} {_b_txt}")
    else:
        parts.append("  No se identificaron bloqueadores para producción.")
    parts.append("")

    # SECTION — TOP ACCIONES
    parts.append("► TOP ACCIONES — Ordenadas por impacto esperado\n")
    if _top5_actions:
        for _idx_a, _act in enumerate(_top5_actions, 1):
            parts.append(f"  {_idx_a}. [{_act['type']}]  {_act['ref']}")
            parts.append(f"     Acción:  {_act['desc']}")
            parts.append(f"     Impacto: {_act['impact_label']}")
            parts.append(f"     Beneficio: {_act['benefit']}")
            parts.append("")
    else:
        parts.append("  No se identificaron acciones de impacto inmediato.\n")

    # SECTION 7 — DECISIONES ARQUITECTÓNICAS
    parts.append("► KEEP — Listas para producción sin cambios\n")
    if gl_prod_ready:
        for item_p in gl_prod_ready:
            gl_ref  = gl_index.get(item_p["guideline"], "GL-?")
            short_p = item_p["guideline"][:70] + ("..." if len(item_p["guideline"]) > 70 else "")
            parts.append(f"  ✅ {gl_ref}  [{item_p['score']}/100]  {short_p}")
        parts.append("")
        parts.append("  Justificación:")
        parts.append("  • Alta calidad técnica (score ≥ 90/100).")
        parts.append("  • Sin conflictos semánticos detectados.")
        parts.append("  • Sin problemas en auditoría.")
        parts.append("  • Cobertura adecuada del escenario que gobiernan.")
    else:
        parts.append("  — Ninguna guideline cumple todos los criterios de producción en este ciclo.")
    parts.append("")

    parts.append("► MODIFICAR\n")
    if gl_to_modify:
        for item_m in gl_to_modify:
            gl_ref  = gl_index.get(item_m["guideline"], "GL-?")
            short_m = item_m["guideline"][:70] + ("..." if len(item_m["guideline"]) > 70 else "")
            parts.append(f"  ⚙️  {gl_ref}  [{item_m['score']}/100]  {short_m}")
            parts.append(f"      Motivo:  {item_m['reason']}")
            parts.append(f"      Acción:  {item_m['action']}")
            parts.append(f"      Impacto: {item_m['impact']}")
            parts.append("")
    else:
        parts.append("  — No hay guidelines que requieran modificación en este ciclo.\n")

    parts.append("► FUSIONAR\n")
    all_fusion = []
    for orig_f, rep_f in merge_log:
        all_fusion.append({"original_a": orig_f, "original_b": None,
                           "consolidated": rep_f, "similarity": "≥ 90", "source": "auto-consolidación ≥ 90%"})
    for mp_f in merge_pairs_engine:
        all_fusion.append({"original_a": mp_f["original_a"], "original_b": mp_f["original_b"],
                           "consolidated": mp_f["consolidated"],
                           "similarity": str(mp_f["similarity"]), "source": f"similitud {mp_f['similarity']}%"})
    if all_fusion:
        for fi_f in all_fusion:
            a_f = fi_f["original_a"][:75] + ("..." if len(fi_f["original_a"]) > 75 else "")
            c_f = fi_f["consolidated"][:90] + ("..." if len(fi_f["consolidated"]) > 90 else "")
            parts.append(f"  📎 Similitud: {fi_f['similarity']}%  ({fi_f['source']})")
            parts.append(f"     Guideline A:     {a_f}")
            if fi_f["original_b"]:
                b_f = fi_f["original_b"][:75] + ("..." if len(fi_f["original_b"]) > 75 else "")
                parts.append(f"     Guideline B:     {b_f}")
            parts.append(f"     ↓")
            parts.append(f"     Guideline final: {c_f}")
            parts.append("")
    else:
        parts.append("  — No se detectaron pares candidatos a fusión en este ciclo.\n")

    parts.append("► ELIMINAR\n")
    if gl_to_eliminate:
        for item_e in gl_to_eliminate:
            gl_ref  = gl_index.get(item_e["guideline"], "GL-?")
            short_e = item_e["guideline"][:70] + ("..." if len(item_e["guideline"]) > 70 else "")
            parts.append(f"  🗑️  {gl_ref}  [{item_e['score']}/100]  {short_e}")
            parts.append(f"      Razón: {item_e['reason']}")
            parts.append("")
    else:
        parts.append("  — No hay guidelines que deban eliminarse en este ciclo.\n")

    if orphan_guidelines:
        parts.append("► GUIDELINES HUÉRFANAS\n")
        parts.append(f"  ({repo_orphans_n} guideline(s) sin respaldo en las conversaciones analizadas)")
        for g_o in orphan_guidelines[:5]:
            gl_ref = gl_index.get(g_o, "GL-?")
            short_o = g_o[:70] + ("..." if len(g_o) > 70 else "")
            parts.append(f"  🔍 {gl_ref}  {short_o}")
        parts.append("  Sugerencia: Ampliar el corpus de conversaciones o validar si estos escenarios son reales.")
        parts.append("")

    # SECTION 8 — DECISIÓN DE DESPLIEGUE
    parts += [div2, "DECISIÓN DEL ARQUITECTO\n"]
    parts.append(f"  {deploy_status}\n")
    parts.append(f"  Motivo:")
    parts.append(f"  {_deploy_exec_motivo}")
    parts.append("")
    if _blockers and deploy_color != "green":
        parts.append("  Se recomienda resolver los Deployment Blockers antes del siguiente despliegue.")
    elif deploy_color == "yellow":
        parts.append(f"  Desplegar únicamente las {n_prod_ready_d} guideline(s) clasificadas en KEEP.")
    parts.append("")

    # SECTION 9 — IMPACTO ESTIMADO
    parts += [div2, "IMPACTO ESTIMADO\n"]
    parts.append(f"  Reducción de escalamientos              {esc_reduction_str}")
    parts.append(f"  Incremento de resolución autónoma       {auto_str}")
    parts.append(f"  Reducción tiempo promedio de atención   {time_str}")
    parts.append(f"  Disminución de carga para agentes       {load_str}")
    parts.append(f"  Incremento esperado de consistencia     {cons_str}")
    parts.append("")

    # SECTION 10 — ROADMAP
    parts += [div2, "ROADMAP DE IMPLEMENTACIÓN\n"]
    for rm in roadmap:
        parts.append(f"  {rm['phase']}  [{rm['duration']}]")
        parts.append(f"  Objetivo: {rm['obj']}")
        for t_rm in rm["tasks"]:
            parts.append(f"    • {t_rm}")
        parts.append("")

    # SECTION 11 — DECISIONES DEL ARQUITECTO
    parts += [div2, "DECISIONES DEL ARQUITECTO\n"]
    for sentence in arch_parts:
        parts.append(f"  {sentence}")
        parts.append("")

    parts.append(div2)
    parts.append("")

    # SECTION 12 — MÉTRICAS DEL REPOSITORIO
    parts += [div3, "MÉTRICAS DEL REPOSITORIO", f"{div3}\n"]
    parts.append(f"  Total de guidelines           {repo_total}")
    parts.append(f"  Aprobadas para producción     {repo_approved}")
    parts.append(f"  Rechazadas / a eliminar       {repo_rejected}")
    parts.append(f"  Fusionadas (duplicados)       {repo_merged}")
    parts.append(f"  Huérfanas (sin soporte)       {repo_orphans_n}")
    parts.append(f"  En conflicto                  {repo_conflicting}")
    parts.append(f"  Con condiciones explícitas    {repo_conditional}")
    parts.append(f"  Con términos absolutos        {repo_absolute}")
    parts.append(f"  Optimizadas en este ciclo     {repo_optimized}")
    parts.append("")

    # SECTION 13 — ÍNDICE DE MANTENIBILIDAD
    parts += [div3, "ÍNDICE DE MANTENIBILIDAD", f"{div3}\n"]
    parts.append(f"  Índice: {maint_idx}/100 — {maint_label}")
    parts.append(f"  {maint_reason}")
    parts.append("")

    # SECTION 14 — MÉTRICAS DE GOBERNANZA
    parts += [div3, "MÉTRICAS DE GOBERNANZA", f"{div3}\n"]
    parts.append(f"  Guidelines activas          {n_active_gov}")
    parts.append(f"  Guidelines nuevas           {n_new_gov}")
    parts.append(f"  Guidelines eliminadas       {n_elim_gov}")
    parts.append(f"  Guidelines fusionadas       {n_merged_gov}")
    parts.append(f"  Guidelines modificadas      {n_modified_gov}")
    parts.append(f"  Cobertura estimada          {coverage_gov}%")
    parts.append(f"  Consistencia                {consistency_gov}%")
    parts.append(f"  Complejidad del repositorio {complexity_label_gov}")
    parts.append(f"  Estado general              {gov_state}")
    parts.append("")

    # SECTION 15 — RESUMEN EJECUTIVO PARA SOPORTE
    parts += [div2, "RESUMEN EJECUTIVO PARA SOPORTE", f"{div2}\n"]
    parts.append(f"¿Qué cambia para FIN?\n  {support_fin_changes}\n")
    parts.append(f"¿Qué cambia para los agentes?\n  {support_agent_changes}\n")

    parts.append(div2)
    parts.append("")

    # SECTION 16 — REFERENCIA TÉCNICA
    parts += [div3, "REFERENCIA TÉCNICA", f"{div3}\n"]

    # GUIDELINES INDEX
    parts.append("GUIDELINES INDEX\n")
    for g_r, gl_ref_r in gl_index.items():
        sc_r = next((s for s in score_results if s["guideline"] == g_r), {})
        score_r = sc_r.get("score", "—")
        short_r = g_r[:80] + ("..." if len(g_r) > 80 else "")
        parts.append(f"  {gl_ref_r}  {score_r}/100  {short_r}")
    parts.append("")

    # PATRONES DETECTADOS (condensado)
    parts.append("PATRONES DETECTADOS\n")
    pat_header_fields = {"Patrón #", "Nombre", "Frecuencia", "Riesgo", "Prioridad"}
    current_pat = {}
    for line in patterns_block:
        stripped = line.strip()
        if stripped.startswith("Patrón #"):
            if current_pat:
                parts.append(
                    f"  {current_pat.get('num', '?')} | {current_pat.get('name', '—')} | "
                    f"Freq: {current_pat.get('freq', '—')} | Riesgo: {current_pat.get('risk', '—')} | "
                    f"Prioridad: {current_pat.get('pri', '—')}"
                )
            current_pat = {"num": stripped}
        elif stripped.startswith("Nombre"):
            current_pat["name"] = stripped.split(":", 1)[-1].strip() if ":" in stripped else ""
        elif stripped.startswith("Frecuencia"):
            current_pat["freq"] = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
        elif stripped.startswith("Riesgo"):
            current_pat["risk"] = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
        elif stripped.startswith("Prioridad"):
            current_pat["pri"] = stripped.split(":", 1)[-1].strip() if ":" in stripped else stripped
    if current_pat and "num" in current_pat:
        parts.append(
            f"  {current_pat.get('num', '?')} | {current_pat.get('name', '—')} | "
            f"Freq: {current_pat.get('freq', '—')} | Riesgo: {current_pat.get('risk', '—')} | "
            f"Prioridad: {current_pat.get('pri', '—')}"
        )
    if not any(l.startswith("Patrón #") for l in patterns_block):
        parts.append("  — No se detectaron patrones con suficiente recurrencia.")
    parts.append("")

    # PUNTAJE DE CALIDAD
    parts.append("PUNTAJE DE CALIDAD\n")
    parts.append(f"  Promedio: {avg_score}/100  |  Máx: {max_score}/100  |  Mín: {min_score}/100\n")
    for sc_item in sorted(score_results, key=lambda x: -x["score"]):
        gl_ref_sc = gl_index.get(sc_item["guideline"], "GL-?")
        interp_s  = f" — {sc_item['interpretation']}" if sc_item["interpretation"] else ""
        parts.append(f"  {gl_ref_sc}  {sc_item['score']}/100{interp_s}")
    parts.append("")

    # MADUREZ DEL PRODUCTO
    parts.append("MADUREZ DEL PRODUCTO\n")
    parts.append(f"  Guidelines          {mat_guidelines}% — {mat_label(mat_guidelines)}")
    parts.append(f"  Escalamientos       {mat_escalation}% — {mat_label(mat_escalation)}")
    parts.append(f"  Resolución Autónoma {mat_autonomous}% — {mat_label(mat_autonomous)}")
    parts.append(f"  Consistencia        {mat_consistency}% — {mat_label(mat_consistency)}")
    parts.append(f"  Global              {mat_global}% — {mat_label(mat_global)}")
    parts.append("")

    # SIMULACIÓN FINAL
    parts.append("SIMULACIÓN FINAL\n")
    sim_label_map = {
        "intention": "Intención detectada",
        "emotion":   "Emoción",
        "priority":  "Prioridad",
        "decision":  "Decisión de FIN",
        "esc_risk":  "Riesgo de escalamiento",
        "confidence": "Nivel de confianza",
    }
    for sim_key, sim_label_s in sim_label_map.items():
        if sim_key in sim_values:
            parts.append(f"  {sim_label_s}: {sim_values[sim_key]}")
    parts.append("")

    # CONCLUSIÓN DEL ARQUITECTO (detallada)
    parts.append("CONCLUSIÓN DEL ARQUITECTO\n")
    parts.append(f"  Estado actual\n  {estado}\n")
    parts.append(f"  Principal riesgo\n  {principal_risk}\n")
    parts.append(f"  Mayor oportunidad\n  {oportunidad}\n")
    parts.append(f"  Recomendación inmediata\n  {immediate_rec}\n")
    parts.append(f"  Siguiente revisión\n  {next_review}\n")

    parts.append(sep)

    # RESUMEN FINAL DEL ARQUITECTO — 4 preguntas, máx 8 líneas
    parts += ["\n" + div2, "RESUMEN FINAL DEL ARQUITECTO", f"{div2}\n"]
    parts.append(f"  ¿El repositorio está sano?\n  {_summary_sano}\n")
    parts.append(f"  ¿Cuál es el principal problema?\n  {_summary_problema}\n")
    parts.append(f"  ¿Cuál es la acción más importante?\n  {_summary_accion}\n")
    parts.append(f"  ¿Qué resultado se espera después de aplicarla?\n  {_summary_resultado}\n")

    parts.append(sep)

    return "\n".join(parts)


@mcp.tool()
async def ecosystem_review(
    products: list,
    context: str = ""
) -> str:
    """
    Revisión cruzada del ecosistema FIN completo. Evalúa Knowledge, Guidelines,
    escalamiento y cobertura en todos los productos simultáneamente.

    Detecta conflictos cross-producto invisibles a repository_review y detect_conflicts,
    audita cumplimiento de la regla de escalamiento en todo el ecosistema, y produce
    un Ecosystem Health Score (EHS) compuesto que penaliza fallos inter-capa.

    products : lista de dicts con 'nombre', 'guidelines' (list[str]),
               'knowledge_articles' (list[str])
    context  : contexto adicional opcional
    """

    import re as _re

    sep  = "━" * 54
    sep2 = "─" * 54

    # ── Sub-call 1: repository_review ────────────────────────────────────────
    rr_output = await repository_review(products=products, context=context)

    # ── Sub-call 2: detect_conflicts por producto ─────────────────────────────
    intra_conflicts_total = 0
    intra_conflict_details = []
    for prod in products:
        pname      = prod.get("nombre", "Sin nombre")
        pg         = prod.get("guidelines", [])
        if not pg:
            continue
        dc_out = await detect_conflicts(guidelines=pg, product=pname, context=context)
        # Extraer conteo de conflictos del output
        m_cnt = _re.search(r"(\d+)\s+conflicto", dc_out, _re.IGNORECASE)
        cnt   = int(m_cnt.group(1)) if m_cnt else 0
        if cnt:
            intra_conflicts_total += cnt
            intra_conflict_details.append(f"[{pname}] {cnt} conflicto(s) intra-producto")

    # ── Sub-call 3: recommend_improvements ───────────────────────────────────
    ri_output = await recommend_improvements(
        repository_review=rr_output,
        knowledge_review="",
        architect_review="",
        context=context
    )

    # ── Extraer métricas de repository_review ────────────────────────────────
    _m = _de.extract_metrics_from_reports(rr_output, "", "")
    global_health      = _m["global_health"]
    knowledge_debt     = _m["knowledge_debt"]
    prod_blocked_cnt   = _m["prod_blocked"]
    prod_high_risk     = _m["prod_high_risk"]
    total_a_blocked    = _m["total_a_blocked"]
    total_g_blocked    = _m["total_g_blocked"]
    total_g_conflicts  = _m["total_g_conflicts"]
    total_a_dups       = _m["total_a_dups"]
    coverage_pct       = _m["coverage_pct"]
    missing_cats_str   = _m["missing_cats_str"]
    total_articles     = _m["total_articles"]
    total_guidelines   = _m["total_guidelines"]

    # ── Cross-product guideline analysis ─────────────────────────────────────
    # Construir pool de guidelines con etiqueta de producto
    pool = []
    for prod in products:
        pname = prod.get("nombre", "Sin nombre")
        for g in prod.get("guidelines", []):
            ws = _de.word_set(g)
            pool.append({
                "product": pname,
                "text":    g,
                "lower":   g.lower(),
                "words":   ws,
                "fast":    _de.kde_score_guideline_fast(g),
            })

    cross_conflicts    = []
    cross_conflict_cnt = 0

    # Solo comparar pares de productos distintos
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            if pool[i]["product"] == pool[j]["product"]:
                continue  # intra-producto: ya cubierto por detect_conflicts
            sim = _de.jaccard(pool[i]["words"], pool[j]["words"])
            if sim < 0.30:
                continue
            # Verificar si algún par de contradicción aplica
            ti, tj = pool[i]["lower"], pool[j]["lower"]
            for term_a, term_b in _de.GUIDELINE_CONTRADICTION_PAIRS:
                if ((term_a in ti and term_b in tj) or
                        (term_b in ti and term_a in tj)):
                    sev = _de.conflict_severity_level(
                        round(sim * 10) + (5 if "escalar" in term_a or "escalar" in term_b else 2)
                    )
                    cross_conflicts.append(
                        f"[{pool[i]['product']} ↔ {pool[j]['product']}] "
                        f"sim={sim:.2f} · '{term_a}' vs '{term_b}' · Severidad: {sev}"
                    )
                    cross_conflict_cnt += 1
                    break  # un conflicto por par de guidelines

    # ── Escalation compliance audit ───────────────────────────────────────────
    anti_esc_violations = []
    escalation_path_articles = []

    for prod in products:
        pname = prod.get("nombre", "Sin nombre")
        for g in prod.get("guidelines", []):
            if _de.detect_anti_escalation(g.lower(), use_repo_patterns=True):
                anti_esc_violations.append(f"[{pname}] Guideline con regla anti-escalamiento")
        for a in prod.get("knowledge_articles", []):
            if _de.detect_anti_escalation(a.lower(), use_repo_patterns=True):
                anti_esc_violations.append(f"[{pname}] Artículo con patrón anti-escalamiento")
            if _de.detect_escalation_repo(a.lower()):
                escalation_path_articles.append(pname)

    escalation_path_open = len(escalation_path_articles) > 0
    anti_esc_count       = len(anti_esc_violations)

    # Escalation health (0–100)
    esc_deduct_anti  = min(60, anti_esc_count * 20)
    esc_deduct_path  = 30 if not escalation_path_open else 0
    esc_deduct_cross = min(30, cross_conflict_cnt * 10)
    escalation_health = max(0, 100 - esc_deduct_anti - esc_deduct_path - esc_deduct_cross)

    if anti_esc_count == 0 and escalation_path_open and cross_conflict_cnt == 0:
        esc_compliance_status  = "COMPLIANT"
        esc_compliance_emoji   = "✅"
    elif anti_esc_count > 0 and not escalation_path_open:
        esc_compliance_status  = "CRITICAL VIOLATION"
        esc_compliance_emoji   = "🚫"
    elif anti_esc_count > 0 or not escalation_path_open:
        esc_compliance_status  = "VIOLATION DETECTED"
        esc_compliance_emoji   = "🔴"
    else:
        esc_compliance_status  = "COMPLIANT"
        esc_compliance_emoji   = "✅"

    # ── Attribute layer — completeness ────────────────────────────────────────
    attr_no_guidelines = [p.get("nombre","?") for p in products if not p.get("guidelines")]
    attr_no_articles   = [p.get("nombre","?") for p in products if not p.get("knowledge_articles")]
    attr_complete      = len(products) - len(set(attr_no_guidelines + attr_no_articles))

    # ── Ecosystem Health Score (EHS) ──────────────────────────────────────────
    # Components (weight without workflow: knowledge 0.35, guideline 0.30, escalation 0.30, coverage 0.05)
    guide_comp   = max(0, 100
                       - total_g_blocked    * 8
                       - intra_conflicts_total * 5
                       - cross_conflict_cnt * 10)
    guide_comp   = min(100, guide_comp)

    coverage_num = _de.compute_coverage(" ".join(
        a for prod in products for a in prod.get("knowledge_articles", [])
    ))
    ecosystem_coverage_pct = round(len(coverage_num[0]) / max(len(_de.TOPIC_CATEGORIES), 1) * 100)

    ehs_raw = round(
        global_health          * 0.35
        + guide_comp           * 0.30
        + escalation_health    * 0.30
        + ecosystem_coverage_pct * 0.05
    )

    # Hard caps
    if anti_esc_count > 0:
        ehs_raw = min(ehs_raw, 60)
    if not escalation_path_open:
        ehs_raw = min(ehs_raw, 40)
    if prod_blocked_cnt > 0:
        ehs_raw = min(ehs_raw, 70)

    ehs = ehs_raw

    if ehs >= 85:
        ehs_label, ehs_emoji = "SALUDABLE",   "🟢"
    elif ehs >= 70:
        ehs_label, ehs_emoji = "ACEPTABLE",   "🟡"
    elif ehs >= 50:
        ehs_label, ehs_emoji = "EN REVISIÓN", "🟠"
    else:
        ehs_label, ehs_emoji = "BLOQUEADO",   "🔴"

    global_status, gs_emoji = _de.global_status_from_health(
        global_health, prod_blocked_cnt, prod_high_risk
    )
    deploy_ready, deploy_emoji = _de.deployment_readiness(
        prod_blocked_cnt, total_a_blocked, total_g_blocked,
        global_health, knowledge_debt, prod_high_risk
    )

    debt_label, debt_emoji = _de.debt_label_emoji(knowledge_debt)

    # ── Plan de acción desde recommend_improvements ───────────────────────────
    _rc_bloq  = _re.search(r"CRÍTICO.*?\n(.*?)(?=──────|SPRINT|$)", ri_output, _re.DOTALL)
    _rc_spr   = _re.search(r"SPRINT.*?\n(.*?)(?=──────|MEJORAS|$)", ri_output, _re.DOTALL)
    _rc_mej   = _re.search(r"MEJORAS.*?\n(.*?)(?=──────|$)", ri_output, _re.DOTALL)

    def _extract_actions(block, n=3):
        if not block:
            return []
        lines = [l.strip() for l in block.group(1).splitlines() if l.strip()]
        return [l for l in lines if l and not l.startswith("━") and not l.startswith("─")][:n]

    plan_critico = _extract_actions(_rc_bloq)
    plan_sprint  = _extract_actions(_rc_spr)
    plan_mejoras = _extract_actions(_rc_mej)

    # Añadir hallazgos cross-producto al plan si los hay
    if cross_conflicts:
        plan_critico.insert(0, f"Resolver {cross_conflict_cnt} conflicto(s) cross-producto detectado(s)")
    if anti_esc_count:
        plan_critico.insert(0, f"Eliminar {anti_esc_count} regla(s) anti-escalamiento (Invariante 6)")

    # ── Composición del reporte ───────────────────────────────────────────────
    parts = []

    parts.append(sep)
    parts.append("  ECOSYSTEM REVIEW — FIN ARCHITECT")
    if context:
        parts.append(f"  {context}")
    total_prods = len(products)
    parts.append(
        f"  {total_prods} productos · "
        f"{total_guidelines} guidelines · "
        f"{total_articles} artículos"
    )
    parts.append(sep)

    # Sección 1 — EHS
    parts.append("")
    parts.append("SECCIÓN 1 — ECOSYSTEM HEALTH SCORE")
    parts.append(sep2)
    parts.append(f"  EHS              : {ehs}/100 {ehs_emoji}")
    parts.append(f"  Estado global    : {ehs_label}")
    parts.append(f"  Salud repositorio: {global_health}/100 {gs_emoji} — {global_status}")
    parts.append(f"  Despliegue       : {deploy_ready} {deploy_emoji}")
    parts.append("")

    # Sección 2 — Knowledge
    parts.append("SECCIÓN 2 — KNOWLEDGE LAYER")
    parts.append(sep2)
    parts.append(f"  Salud global       : {global_health}/100")
    parts.append(f"  Cobertura ecosistema: {ecosystem_coverage_pct}%")
    parts.append(f"  Knowledge Debt     : {knowledge_debt} — {debt_label} {debt_emoji}")
    parts.append(f"  Artículos bloqueados: {total_a_blocked}")
    parts.append(f"  Duplicados          : {total_a_dups} par(es)")
    if missing_cats_str:
        parts.append(f"  Categorías faltantes: {missing_cats_str}")
    parts.append("")

    # Sección 3 — Guideline
    parts.append("SECCIÓN 3 — GUIDELINE LAYER")
    parts.append(sep2)
    parts.append(f"  Conflictos intra-producto : {intra_conflicts_total}")
    parts.append(f"  Conflictos cross-producto : {cross_conflict_cnt}")
    parts.append(f"  Guidelines bloqueadas     : {total_g_blocked}")
    if intra_conflict_details:
        parts.append("")
        parts.append("  Detalle intra-producto:")
        for d in intra_conflict_details:
            parts.append(f"    · {d}")
    if cross_conflicts:
        parts.append("")
        parts.append("  Conflictos cross-producto:")
        for c in cross_conflicts[:5]:
            parts.append(f"    · {c}")
    parts.append("")

    # Sección 4 — Escalation Compliance
    parts.append("SECCIÓN 4 — ESCALATION COMPLIANCE")
    parts.append(sep2)
    parts.append(f"  Estado            : {esc_compliance_status} {esc_compliance_emoji}")
    parts.append(f"  Escalation Health : {escalation_health}/100")
    parts.append(f"  Violaciones anti-esc: {anti_esc_count}")
    parts.append(f"  Ruta de escalamiento: {'ABIERTA ✅' if escalation_path_open else 'CERRADA 🔴'}")
    if anti_esc_violations:
        parts.append("")
        parts.append("  Violaciones detectadas:")
        for v in anti_esc_violations[:5]:
            parts.append(f"    · {v}")
    parts.append("")

    # Sección 5 — Attribute Layer
    parts.append("SECCIÓN 5 — ATTRIBUTE LAYER")
    parts.append(sep2)
    parts.append(f"  Productos con cobertura completa: {attr_complete}/{total_prods}")
    if attr_no_guidelines:
        parts.append(f"  Sin guidelines  : {', '.join(attr_no_guidelines)}")
    if attr_no_articles:
        parts.append(f"  Sin artículos   : {', '.join(attr_no_articles)}")
    parts.append("")

    # Sección 6 — Plan de Acción
    parts.append("SECCIÓN 6 — PLAN DE ACCIÓN")
    parts.append(sep2)
    if plan_critico:
        parts.append("  CRÍTICO (resolver antes de operar):")
        for item in plan_critico:
            parts.append(f"    → {item}")
    if plan_sprint:
        parts.append("  SPRINT (próximo ciclo):")
        for item in plan_sprint:
            parts.append(f"    → {item}")
    if plan_mejoras:
        parts.append("  MEJORAS (siguiente versión):")
        for item in plan_mejoras:
            parts.append(f"    → {item}")
    if not (plan_critico or plan_sprint or plan_mejoras):
        parts.append("  Sin acciones prioritarias detectadas.")
    parts.append("")

    parts.append(sep)

    return "\n".join(parts)


# Transporte SSE para Claude
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:

        await mcp._mcp_server.run(
            streams[0],
            streams[1],
            mcp._mcp_server.create_initialization_options()
        )


# Healthcheck para Railway
async def health(request):
    return JSONResponse(
        {
            "status": "ok",
            "service": "fin-architect-mcp"
        }
    )


app = Starlette(
    routes=[
        Route("/", endpoint=health),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )
