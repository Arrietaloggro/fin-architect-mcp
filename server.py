from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn
import os

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

    keywords_ambiguous = [
        "siempre",
        "nunca",
        "todos",
        "ninguno"
    ]

    for word in keywords_ambiguous:
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
    absolute_words = [
        "siempre",
        "nunca",
        "todos",
        "ninguno",
        "cualquier"
    ]

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
    escalation_words = [
        "escalar",
        "escala",
        "transferir",
        "transfiere",
        "agente",
        "agente humano"
    ]

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
    if risk_score >= 7:
        risk = "ALTO"
    elif risk_score >= 4:
        risk = "MEDIO"
    else:
        risk = "BAJO"

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

    absolute_words = ["siempre", "nunca", "todos", "ninguno", "cualquier"]
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

    if risk_score >= 7:
        nivel_riesgo = "ALTO"
    elif risk_score >= 4:
        nivel_riesgo = "MEDIO"
    else:
        nivel_riesgo = "BAJO"

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

    escalation_words = ["escalar", "escala", "transferir", "transfiere", "agente humano"]
    resolve_words = ["resolver", "intenta resolver", "resuelve", "solucionar", "soluciona"]
    prohibition_words = ["no escalar", "no transferir", "no escales", "nunca escalar", "no ofrecer"]
    obligation_words = ["siempre escalar", "debe escalar", "escalar siempre", "siempre transferir"]
    priority_words = ["urgente", "alta prioridad", "prioridad alta", "prioridad baja", "baja prioridad", "normal"]

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
    condition_pairs = [
        ("frustración", "molesto"),
        ("primera vez", "reincidente"),
        ("plan básico", "plan premium"),
        ("sin contrato", "con contrato"),
    ]

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
    shared_scenarios = [
        "factura", "cobro", "pago", "error", "acceso", "contraseña", "cuenta"
    ]

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
    contradiction_pairs = [
        ("disculpa", "no disculpa"),
        ("ofrece descuento", "no ofrece descuento"),
        ("confirma el error", "niega el error"),
        ("da el número de caso", "no compartas el número"),
    ]

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
            words_i = set(texts[i].split())
            words_j = set(texts[j].split())
            if not words_i or not words_j:
                continue
            overlap = len(words_i & words_j) / max(len(words_i), len(words_j))
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
    if severity_score >= 10:
        severidad = "ALTA"
    elif severity_score >= 4:
        severidad = "MEDIA"
    else:
        severidad = "BAJA"

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

    vague_phrases = [
        "de alguna manera",
        "como sea posible",
        "en la medida",
        "según corresponda",
        "a discreción",
        "dependiendo",
        "podría",
        "quizás",
        "tal vez",
    ]

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

    action_verbs = [
        "escala", "escalar", "responde", "responder", "informa", "informar",
        "ofrece", "ofrecer", "solicita", "solicitar", "verifica", "verificar",
        "confirma", "confirmar", "transfiere", "transferir", "resuelve",
        "resolver", "indica", "indicar", "explica", "explicar",
    ]

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

    ambiguous_terms = [
        "siempre",
        "nunca",
        "normalmente",
        "generalmente",
        "etc",
        "si es posible",
        "rápidamente",
        "cuando sea necesario",
        "lo antes posible",
        "en lo posible",
        "suele",
        "a veces",
        "casi siempre",
    ]

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

    escalation_words = [
        "escalar", "escala", "transferir", "transfiere", "agente humano", "agente"
    ]

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

    specific_signals = [
        "factura", "cobro", "pago", "contraseña", "cuenta", "acceso",
        "error", "plan", "contrato", "módulo", "reporte", "usuario",
        "primera vez", "reincidente", "bloqueo", "cargo",
    ]

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

    contradictions = [
        ("escalar", "no escalar"),
        ("siempre", "solo si"),
        ("transfiere", "no transfieras"),
        ("informa", "no informes"),
    ]

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

    risky_patterns = [
        "comparte la contraseña",
        "da acceso",
        "otorga permiso",
        "sin verificar",
        "sin validar",
        "sin confirmar identidad",
        "sin autenticar",
        "proporciona datos personales",
        "envía el número de tarjeta",
    ]

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

    empathy_signals = [
        "disculpa", "lamentamos", "entendemos", "comprendo",
        "te ayudo", "con gusto", "con placer",
    ]

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
    intention_map = [
        ("Facturación",    ["factura", "cobro", "pago", "cargo", "reembolso", "cobrar", "facturar"]),
        ("Inventario",     ["inventario", "stock", "producto", "bodega", "existencia", "kardex"]),
        ("Caja",           ["caja", "cierre de caja", "apertura de caja", "caja menor", "arqueo"]),
        ("POS",            ["pos", "punto de venta", "terminal", "datafono", "tpv"]),
        ("Restobar",       ["restobar", "restaurante", "mesa", "pedido", "cocina", "comanda"]),
        ("DIAN",           ["dian", "factura electrónica", "cufe", "resolución dian", "rut"]),
        ("Nómina",         ["nómina", "empleado", "liquidación", "contrato", "devengado", "descuento"]),
        ("Reportes",       ["reporte", "informe", "exportar", "descargar", "estadística", "dashboard"]),
        ("Configuración",  ["configuración", "configurar", "ajuste", "parámetro", "módulo", "activar"]),
        ("Error técnico",  ["error", "fallo", "no funciona", "no carga", "pantalla", "bug", "problema técnico"]),
        ("Acceso",         ["contraseña", "acceso", "usuario", "sesión", "ingresar", "login", "clave"]),
        ("Seguridad",      ["seguridad", "fraude", "robo", "suplantación", "bloqueo", "permiso"]),
    ]

    intention = "Otro"
    for label, keywords in intention_map:
        if any(k in text for k in keywords):
            intention = label
            break

    # ------------------------------------------------------------------ #
    # 2. Detectar emoción                                                  #
    # ------------------------------------------------------------------ #
    if any(w in text for w in ["furioso", "harto", "no sirve", "pésimo", "terrible", "inaceptable"]):
        emotion = "Frustrado"
    elif any(w in text for w in ["molesto", "enojado", "molesta", "enojada", "fastidio", "mal servicio"]):
        emotion = "Molesto"
    elif any(w in text for w in ["urgente", "ya", "inmediatamente", "crítico", "emergencia", "no puedo esperar"]):
        emotion = "Urgente"
    elif any(w in text for w in ["no entiendo", "no sé", "confundido", "confundida", "cómo", "qué significa", "no comprendo"]):
        emotion = "Confundido"
    else:
        emotion = "Neutral"

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
    escalation_words   = ["escalar", "escala", "transferir", "transfiere", "agente humano", "agente"]
    resolve_words      = ["resolver", "intenta resolver", "resuelve", "solucionar", "base de conocimiento"]
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
    intention_map = [
        ("Facturación",   ["factura", "cobro", "pago", "cargo", "reembolso", "cobrar", "facturar", "cufe"]),
        ("Inventario",    ["inventario", "stock", "producto", "bodega", "existencia", "kardex"]),
        ("Caja",          ["caja", "cierre de caja", "apertura de caja", "arqueo"]),
        ("POS",           ["pos", "punto de venta", "terminal", "datafono"]),
        ("Restobar",      ["restobar", "restaurante", "mesa", "pedido", "cocina", "comanda"]),
        ("DIAN",          ["dian", "factura electrónica", "cufe", "resolución dian", "rut"]),
        ("Nómina",        ["nómina", "empleado", "liquidación", "contrato", "devengado"]),
        ("Reportes",      ["reporte", "informe", "exportar", "estadística", "dashboard"]),
        ("Configuración", ["configuración", "configurar", "ajuste", "parámetro", "activar"]),
        ("Error técnico", ["error", "fallo", "no funciona", "no carga", "bug", "problema técnico"]),
        ("Acceso",        ["contraseña", "acceso", "usuario", "sesión", "login", "clave"]),
        ("Seguridad",     ["seguridad", "fraude", "robo", "suplantación", "bloqueo"]),
    ]

    intention = "General"
    intention_keywords_found = []
    for label, keywords in intention_map:
        hits = [k for k in keywords if k in text]
        if hits:
            intention = label
            intention_keywords_found = hits
            break

    # ------------------------------------------------------------------ #
    # 2. Detectar emoción                                                  #
    # ------------------------------------------------------------------ #
    if any(w in text for w in ["furioso", "harto", "pésimo", "terrible", "inaceptable", "no sirve"]):
        emotion = "Frustrado"
    elif any(w in text for w in ["molesto", "enojado", "fastidio", "mal servicio"]):
        emotion = "Molesto"
    elif any(w in text for w in ["urgente", "hoy mismo", "inmediatamente", "emergencia", "no puedo esperar"]):
        emotion = "Urgente"
    elif any(w in text for w in ["no entiendo", "no sé", "confundido", "cómo", "qué significa", "no comprendo"]):
        emotion = "Confundido"
    else:
        emotion = "Neutral"

    # ------------------------------------------------------------------ #
    # 3. Detectar problema principal                                       #
    # ------------------------------------------------------------------ #
    problem_signals = {
        "escalamiento sin criterios": [
            "me pasaron con", "me transfirieron", "agente no supo",
            "escalaron sin", "nadie me ayudó"
        ],
        "falta de resolución documentada": [
            "no encuentro", "no hay artículo", "no existe documentación",
            "no hay guía", "no encontré nada"
        ],
        "solución documentada insuficiente": [
            "ya seguí los pasos", "seguí las instrucciones", "hice lo que dice",
            "intenté lo del artículo", "el artículo no funciona"
        ],
        "respuesta genérica de FIN": [
            "me dijo lo mismo", "misma respuesta", "respuesta repetida",
            "no me ayuda", "respuesta automática"
        ],
        "fallo técnico sin guía": [
            "error al", "no carga", "pantalla en blanco", "se traba",
            "no responde", "caído"
        ],
        "urgencia no atendida": [
            "hoy mismo", "urgente", "necesito ahora", "no puedo esperar",
            "es crítico"
        ],
    }

    detected_problems = []
    for problem, signals in problem_signals.items():
        if any(s in text for s in signals):
            detected_problems.append(problem)

    main_problem = detected_problems[0] if detected_problems else "comportamiento de FIN no definido para este escenario"

    # ------------------------------------------------------------------ #
    # 4. Detectar punto de fallo de FIN                                    #
    # ------------------------------------------------------------------ #
    failure_map = {
        "escalamiento sin criterios":         "FIN escaló o puede escalar sin verificar si existe solución documentada.",
        "falta de resolución documentada":    "FIN no cuenta con información suficiente para resolver el caso.",
        "solución documentada insuficiente":  "FIN repitió una solución que el usuario ya intentó sin éxito.",
        "respuesta genérica de FIN":          "FIN entregó una respuesta genérica que no resolvió el caso concreto.",
        "fallo técnico sin guía":             "FIN no guió al usuario paso a paso ante un error técnico.",
        "urgencia no atendida":               "FIN no priorizó ni aceleró la atención a pesar de la urgencia expresada.",
        "comportamiento de FIN no definido para este escenario": "No se identificó un patrón de fallo claro. La guideline cubre el escenario preventivamente.",
    }

    failure_point = failure_map.get(main_problem, failure_map["comportamiento de FIN no definido para este escenario"])

    # ------------------------------------------------------------------ #
    # 5. Determinar comportamiento correcto de FIN                         #
    # ------------------------------------------------------------------ #
    behavior_map = {
        "escalamiento sin criterios":
            "FIN debe verificar la base de conocimiento antes de escalar. "
            "Únicamente cuando no exista solución documentada o el usuario confirme haberla intentado sin éxito, FIN debe transferir al agente.",
        "falta de resolución documentada":
            "FIN debe indicar que no cuenta con una solución documentada para el caso "
            "y transferir al agente con el contexto completo de la conversación.",
        "solución documentada insuficiente":
            "Si el usuario confirma haber seguido los pasos documentados sin resultado, "
            "FIN no debe repetir la misma solución. Debe escalar con el detalle del intento fallido.",
        "respuesta genérica de FIN":
            "FIN debe identificar el escenario específico antes de responder "
            "y adaptar la respuesta al contexto concreto del usuario.",
        "fallo técnico sin guía":
            "Ante un error técnico, FIN debe guiar paso a paso al usuario. "
            "Si el error persiste tras los pasos documentados, debe escalar indicando el error exacto.",
        "urgencia no atendida":
            "Cuando el usuario exprese urgencia, FIN debe priorizar el caso, "
            "acortar el proceso de verificación y escalar si no puede resolver de inmediato.",
        "comportamiento de FIN no definido para este escenario":
            "FIN debe verificar si existe solución para el caso, guiar al usuario "
            "y escalar únicamente si la solución documentada no resuelve el problema.",
    }

    expected_behavior = behavior_map.get(main_problem, behavior_map["comportamiento de FIN no definido para este escenario"])

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

    if total_impact_score >= 80:
        impact = "Alto"
    elif total_impact_score >= 50:
        impact = "Medio"
    else:
        impact = "Bajo"

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
    intention_map = [
        ("Facturación",   ["factura", "cobro", "pago", "cargo", "reembolso", "facturar", "cufe"]),
        ("Inventario",    ["inventario", "stock", "producto", "bodega", "existencia", "kardex"]),
        ("Caja",          ["caja", "cierre de caja", "apertura de caja", "arqueo"]),
        ("POS",           ["pos", "punto de venta", "terminal", "datafono"]),
        ("Restobar",      ["restobar", "restaurante", "mesa", "pedido", "cocina", "comanda"]),
        ("DIAN",          ["dian", "factura electrónica", "cufe", "resolución dian", "rut"]),
        ("Nómina",        ["nómina", "empleado", "liquidación", "contrato", "devengado"]),
        ("Reportes",      ["reporte", "informe", "exportar", "estadística", "dashboard"]),
        ("Configuración", ["configuración", "configurar", "ajuste", "parámetro", "activar"]),
        ("Error técnico", ["error", "fallo", "no funciona", "no carga", "bug", "problema técnico"]),
        ("Acceso",        ["contraseña", "acceso", "usuario", "sesión", "login", "clave"]),
        ("Seguridad",     ["seguridad", "fraude", "robo", "suplantación", "bloqueo"]),
    ]

    # ------------------------------------------------------------------ #
    # Catálogo de eventos semánticos                                       #
    # ------------------------------------------------------------------ #
    EVENT_CATALOG = [
        {
            "id":      "user_tried_docs",
            "label":   "Usuario agotó solución documentada",
            "signals": [
                "ya seguí los pasos", "seguí las instrucciones", "hice lo que dice",
                "intenté lo del artículo", "el artículo no funciona",
                "ya hice todo lo que dice", "seguí la guía", "ya seguí la guía",
                "ya intenté la solución", "ya lo intenté", "hice los pasos",
                "ya hice todos los pasos", "ya consulté", "ya la hice",
                "ya la consulté", "ya lo hice", "ya intenté",
                "ya hice lo del", "hice todo lo del", "ya lo del artículo",
                "ya intenté la solución documentada", "ya intenté todo",
            ],
            "impact":   55,
            "esc_risk": 60,
        },
        {
            "id":      "fin_repeats_solution",
            "label":   "FIN repitió solución ya agotada",
            "signals": [
                "consulta este artículo", "consulta el artículo", "revisa este artículo",
                "revisa el artículo", "consulta la guía", "revisa la guía",
                "consulta nuevamente", "revisa nuevamente", "consulta nuevamente la guía",
                "te recomiendo revisar", "te invito a consultar",
                "revisa este mismo artículo", "consulta esta guía",
            ],
            "impact":   50,
            "esc_risk": 55,
        },
        {
            "id":      "problem_persists",
            "label":   "Usuario confirma que el problema continúa",
            "signals": [
                "continúa igual", "sigue igual", "no se solucionó", "continúa el error",
                "no funcionó", "no funciona", "no se resolvió", "persiste",
                "aún no funciona", "todavía no funciona", "el problema continúa",
                "no se ha resuelto", "no funcionó", "sigue sin",
                "el problema sigue", "continúa el problema",
            ],
            "impact":   50,
            "esc_risk": 50,
        },
        {
            "id":      "user_urgency",
            "label":   "Usuario expresa urgencia",
            "signals": [
                "hoy mismo", "urgente", "necesito ahora", "no puedo esperar",
                "es crítico", "antes de cerrar", "para terminar mi turno",
                "necesito resolver hoy", "con urgencia",
            ],
            "impact":   45,
            "esc_risk": 40,
        },
        {
            "id":      "user_frustration",
            "label":   "Usuario expresa frustración",
            "signals": [
                "furioso", "harto", "pésimo", "terrible", "inaceptable",
                "no sirve", "molesto", "enojado", "fastidio", "mal servicio",
                "no me ayuda", "frustr",
            ],
            "impact":   45,
            "esc_risk": 45,
        },
        {
            "id":      "fin_generic_response",
            "label":   "FIN no respondió la intención principal",
            "signals": [
                "me dijo lo mismo", "misma respuesta", "respuesta repetida",
                "respuesta automática", "no entiende", "no me respondió",
                "no respondió mi pregunta", "cambió de tema",
            ],
            "impact":   40,
            "esc_risk": 35,
        },
        {
            "id":      "fin_escalated",
            "label":   "FIN escaló el caso",
            "signals": [
                "me pasaron con", "me transfirieron", "agente humano",
                "escalaron", "me dejaron en espera", "espera mientras te conecto",
            ],
            "impact":   35,
            "esc_risk": 30,
        },
        {
            "id":      "problem_resolved",
            "label":   "Usuario confirma resolución exitosa",
            "signals": [
                "gracias", "resuelto", "funcionó", "listo", "perfecto",
                "excelente", "ya funciona", "se solucionó", "muchas gracias",
            ],
            "impact":   0,
            "esc_risk": 0,
        },
        {
            "id":      "fin_requests_info",
            "label":   "FIN solicitó información adicional",
            "signals": [
                "¿puedes indicarme", "¿podrías compartir", "necesito que me indiques",
                "¿cuál es el error", "¿qué mensaje", "por favor comparte",
                "¿tienes el número",
            ],
            "impact":   15,
            "esc_risk": 10,
        },
        {
            "id":      "user_multiple_attempts",
            "label":   "Usuario menciona múltiples intentos",
            "signals": [
                "varias veces", "dos veces", "tres veces", "muchas veces",
                "ya lo intenté varias", "lo he hecho varias",
            ],
            "impact":   45,
            "esc_risk": 50,
        },
        {
            "id":      "user_blocked",
            "label":   "Usuario está operativamente bloqueado",
            "signals": [
                "no puedo continuar", "no puedo trabajar", "no puedo operar",
                "no puedo cerrar", "no puedo emitir", "no puedo facturar",
                "bloqueado", "sin acceso", "no me deja", "no permite",
            ],
            "impact":   55,
            "esc_risk": 55,
        },
        {
            "id":      "unnecessary_escalation_risk",
            "label":   "Escalamiento evitable detectado",
            "signals": [],
            "impact":   50,
            "esc_risk": 65,
        },
    ]

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
        a, b = set(set_a), set(set_b)
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    # ------------------------------------------------------------------ #
    # FASE 3 — Union-Find para construir clusters (umbral ≥ 70%)          #
    # ------------------------------------------------------------------ #
    CLUSTER_THRESHOLD = 0.70

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
            sim = jaccard(conv_data[i]["event_set"], conv_data[j]["event_set"])
            if sim >= CLUSTER_THRESHOLD:
                union(i, j)

    raw_clusters = defaultdict(list)
    for i in range(total):
        raw_clusters[find(i)].append(i)
    clusters = list(raw_clusters.values())

    # ------------------------------------------------------------------ #
    # Nombrado de patrones                                                 #
    # ------------------------------------------------------------------ #
    PATTERN_NAMES = {
        frozenset(["user_tried_docs", "fin_repeats_solution", "problem_persists"]):
            "FIN repite solución ya agotada y el problema continúa",
        frozenset(["user_tried_docs", "fin_repeats_solution", "problem_persists", "user_urgency"]):
            "FIN repite solución ya agotada con urgencia del usuario",
        frozenset(["user_tried_docs", "fin_repeats_solution", "problem_persists", "user_blocked"]):
            "FIN repite solución ya agotada mientras el usuario está bloqueado",
        frozenset(["user_tried_docs", "fin_repeats_solution", "problem_persists",
                   "user_urgency", "user_blocked"]):
            "FIN repite solución ya agotada — usuario bloqueado y urgente",
        frozenset(["user_tried_docs", "fin_repeats_solution"]):
            "FIN repite solución ya agotada",
        frozenset(["user_tried_docs", "problem_persists"]):
            "Solución documentada insuficiente para el caso",
        frozenset(["user_urgency", "problem_persists"]):
            "Urgencia no atendida con problema persistente",
        frozenset(["user_urgency"]):
            "Urgencia del usuario no priorizada",
        frozenset(["user_frustration", "problem_persists"]):
            "Frustración del usuario ante problema no resuelto",
        frozenset(["user_blocked", "problem_persists"]):
            "Usuario operativamente bloqueado sin resolución",
        frozenset(["fin_generic_response"]):
            "FIN no respondió la intención principal del usuario",
        frozenset(["fin_escalated"]):
            "Caso escalado por FIN",
        frozenset(["user_multiple_attempts", "problem_persists"]):
            "Usuario intentó múltiples veces sin resolución",
        frozenset(["unnecessary_escalation_risk"]):
            "Escalamiento evitable: FIN no reconoció docs agotados",
    }

    def pattern_name_for(event_set):
        best_name, best_overlap = None, -1
        for key, name in PATTERN_NAMES.items():
            overlap = len(key & event_set)
            if overlap == len(key) and overlap > best_overlap:
                best_name = name
                best_overlap = overlap
        if best_name:
            return best_name
        for ev in sorted(EVENT_CATALOG, key=lambda e: -e["impact"]):
            if ev["id"] in event_set and ev["id"] != "problem_resolved":
                return f"Patrón: {ev['label']}"
        return "Comportamiento de FIN sin patrón catalogado"

    # ------------------------------------------------------------------ #
    # Guideline templates                                                  #
    # ------------------------------------------------------------------ #
    GUIDELINE_TEMPLATES = {
        "user_tried_docs+fin_repeats_solution": (
            "Si el usuario de {intention} indica haber seguido los pasos documentados "
            "sin resultado exitoso, verifica que el problema persista después de los pasos. "
            "Cuando se confirme, no repitas la misma solución: escala al agente humano "
            "incluyendo el error exacto, los pasos realizados y el resultado obtenido."
        ),
        "user_urgency": (
            "Cuando el usuario exprese urgencia en un caso de {intention}, "
            "prioriza la atención de inmediato. "
            "Si no es posible resolver en la primera interacción, "
            "escala al agente indicando la urgencia y el detalle del caso."
        ),
        "user_blocked": (
            "Cuando el usuario reporte un bloqueo operativo en {intention}, "
            "verifica si existe solución documentada y guía paso a paso. "
            "Únicamente cuando la solución no resuelva el bloqueo, "
            "escala al agente con el contexto completo."
        ),
        "fin_generic_response": (
            "Antes de responder un caso de {intention}, identifica el escenario específico "
            "del usuario y adapta la respuesta al contexto concreto "
            "en lugar de entregar una respuesta genérica o repetir el mismo artículo."
        ),
        "user_multiple_attempts": (
            "Si el usuario indica haber intentado la solución documentada múltiples veces "
            "en {intention} sin resultado, no repitas el mismo artículo. "
            "Escala al agente con el historial de intentos y el resultado obtenido."
        ),
        "fin_escalated": (
            "Antes de escalar un caso de {intention}, verifica si existe solución documentada "
            "y si el usuario aún no la ha intentado. "
            "Escala únicamente cuando la solución documentada no resuelva el problema."
        ),
        "default": (
            "Verifica el comportamiento de FIN para casos de {intention} "
            "donde el usuario reporta que el problema continúa tras seguir los pasos documentados."
        ),
    }

    def guideline_for_events(event_set, intention):
        if "user_tried_docs" in event_set and "fin_repeats_solution" in event_set:
            tpl = GUIDELINE_TEMPLATES["user_tried_docs+fin_repeats_solution"]
        elif "user_multiple_attempts" in event_set:
            tpl = GUIDELINE_TEMPLATES["user_multiple_attempts"]
        elif "user_blocked" in event_set:
            tpl = GUIDELINE_TEMPLATES["user_blocked"]
        elif "user_urgency" in event_set:
            tpl = GUIDELINE_TEMPLATES["user_urgency"]
        elif "fin_generic_response" in event_set:
            tpl = GUIDELINE_TEMPLATES["fin_generic_response"]
        elif "fin_escalated" in event_set:
            tpl = GUIDELINE_TEMPLATES["fin_escalated"]
        else:
            tpl = GUIDELINE_TEMPLATES["default"]
        return tpl.format(intention=intention)

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
                sims.append(jaccard(
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
        wa, wb = set(a.lower().split()), set(b.lower().split())
        if not wa and not wb:
            return 1.0
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)

    MERGE_THRESHOLD = 0.80
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
    Orquestador del FIN Architect MCP. Ejecuta el pipeline completo:
    extract_guidelines → generate_guideline → audit_guideline →
    optimize_guideline → classify_guideline → detect_conflicts →
    score_guideline → simulate_fin y produce un reporte ejecutivo unificado.
    """

    # ------------------------------------------------------------------ #
    # Helpers para extraer secciones de los resultados de otras tools     #
    # ------------------------------------------------------------------ #
    def section(text, header):
        """Extrae el bloque de texto que sigue a un encabezado hasta el siguiente."""
        lines = text.split("\n")
        capturing = False
        result = []
        for line in lines:
            if line.strip().upper() == header.upper():
                capturing = True
                continue
            if capturing:
                if line.strip() and line.strip().upper() == line.strip() and len(line.strip()) > 3:
                    # nuevo encabezado en mayúsculas → parar
                    if line.strip() not in ("---", "-----------------------------------"):
                        break
                result.append(line)
        return "\n".join(result).strip()

    def first_lines(text, n=3):
        return "\n".join(l for l in text.split("\n") if l.strip())[:400]

    def extract_score(score_output):
        """Extrae el puntaje numérico del output de score_guideline."""
        import re
        m = re.search(r"(\d{1,3})/100", score_output)
        return int(m.group(1)) if m else 0

    def extract_risk(text):
        for level in ("ALTO", "MEDIO", "BAJO"):
            if level in text.upper():
                return level
        return "DESCONOCIDO"

    def clean(text):
        """Elimina encabezados markdown y líneas vacías excesivas."""
        lines = [l for l in text.split("\n") if not l.startswith("**Extracción") and
                 not l.startswith("**Auditoría") and not l.startswith("**Clasificación") and
                 not l.startswith("**Optimización") and not l.startswith("**Score") and
                 not l.startswith("**Simulación")]
        return "\n".join(lines).strip()

    # ------------------------------------------------------------------ #
    # PASO 1 — Extraer patrones                                            #
    # ------------------------------------------------------------------ #
    extraction_output = await extract_guidelines(
        conversations=conversations,
        product=product,
        context=objective,
    )

    # Capturar patrones del texto de extracción
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

    # Extraer nombres de patrones y guidelines propuestas del output
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
        if line.startswith("Guideline propuesta"):
            pass  # siguiente línea no vacía
        elif current_name and line.strip() and line.strip() != current_name \
                and not line.startswith("Guideline propuesta") and not line.startswith("Nombre") \
                and not line.startswith("Frecuencia") and not line.startswith("Impacto") \
                and not line.startswith("Riesgo") and not line.startswith("Prioridad") \
                and not line.startswith("Reducción") and not line.startswith("Mejora") \
                and not line.startswith("Justificación") and not line.startswith("Conversaciones") \
                and not line.startswith("Patrón #") and not line.startswith("---"):
            # Heurística: líneas largas sin prefijo → probablemente texto de guideline
            if len(line.strip()) > 40:
                extracted_guidelines.append(line.strip())
                current_name = None

    # Deduplicar
    seen = set()
    unique_extracted = []
    for g in extracted_guidelines:
        if g not in seen:
            seen.add(g)
            unique_extracted.append(g)
    extracted_guidelines = unique_extracted

    # ------------------------------------------------------------------ #
    # PASO 2 — Generar guidelines desde cada conversación                  #
    # ------------------------------------------------------------------ #
    generated_guidelines = []
    for i, conv in enumerate(conversations[:5]):  # máximo 5 para no saturar
        raw = conv.get("text", conv) if isinstance(conv, dict) else conv
        gen_out = await generate_guideline(
            conversation=raw,
            product=product,
            objective=objective,
        )
        # Extraer la guideline generada del output
        gen_lines = gen_out.split("\n")
        capturing_gl = False
        for line in gen_lines:
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

    # Combinar: extraídas + generadas + actuales, sin duplicados
    all_guidelines = list(current_guidelines)
    for g in extracted_guidelines + generated_guidelines:
        if g and g not in all_guidelines:
            all_guidelines.append(g)

    # Asegurar que haya al menos una guideline para continuar el pipeline
    if not all_guidelines:
        all_guidelines = [
            f"Cuando el usuario reporte un problema operativo en {product} "
            "y haya seguido los pasos documentados sin resultado, "
            "verifica el contexto antes de escalar al agente humano."
        ]

    # ------------------------------------------------------------------ #
    # PASO 3 — Auditoría de cada guideline                                 #
    # ------------------------------------------------------------------ #
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
            "raw": audit_out,
        })

    guidelines_with_issues = [a for a in audit_results if a["has_issues"]]
    guidelines_clean = [a for a in audit_results if not a["has_issues"]]

    # ------------------------------------------------------------------ #
    # PASO 4 — Optimización de guidelines con problemas                    #
    # ------------------------------------------------------------------ #
    optimized_map = {}   # guideline_original → guideline_optimizada
    for a in guidelines_with_issues:
        opt_out = await optimize_guideline(guideline=a["guideline"])
        opt_lines = opt_out.split("\n")
        capturing_opt = False
        for line in opt_lines:
            if "VERSIÓN OPTIMIZADA" in line.upper():
                capturing_opt = True
                continue
            if capturing_opt and line.strip() and "RECOMENDACIÓN" not in line.upper():
                optimized_map[a["guideline"]] = line.strip()
                break

    # Reconstruir lista final con optimizadas aplicadas
    final_guidelines = []
    for g in all_guidelines:
        final_guidelines.append(optimized_map.get(g, g))
    final_guidelines = [g for g in final_guidelines if g]

    # ------------------------------------------------------------------ #
    # PASO 5 — Clasificación                                               #
    # ------------------------------------------------------------------ #
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
            "guideline": g,
            "category": cat,
            "subcategory": sub,
            "risk": risk_cls,
            "priority": pri_cls,
        })

    # ------------------------------------------------------------------ #
    # PASO 6 — Detectar conflictos                                         #
    # ------------------------------------------------------------------ #
    conflicts_output = await detect_conflicts(
        guidelines=final_guidelines,
        product=product,
    )
    has_conflicts = "No se detectaron conflictos" not in conflicts_output \
                    and "sin conflictos" not in conflicts_output.lower()
    conflict_lines = [l.strip() for l in conflicts_output.split("\n")
                      if l.strip().startswith("- ") or l.strip().startswith("⚠")][:10]

    # ------------------------------------------------------------------ #
    # PASO 7 — Puntaje de calidad de cada guideline                        #
    # ------------------------------------------------------------------ #
    score_results = []
    for g in final_guidelines:
        sc_out = await score_guideline(guideline=g, product=product)
        score_val = extract_score(sc_out)
        interpretation = ""
        for line in sc_out.split("\n"):
            if "/100 —" in line:
                interpretation = line.split("—", 1)[-1].strip()
                break
        score_results.append({
            "guideline": g,
            "score": score_val,
            "interpretation": interpretation,
        })

    scores = [r["score"] for r in score_results if r["score"] > 0]
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0

    # Salud general: pondera score, auditoría limpia y sin conflictos
    issue_penalty = len(guidelines_with_issues) * 5
    conflict_penalty = 10 if has_conflicts else 0
    health_score = max(0, min(100, avg_score - issue_penalty - conflict_penalty))

    if health_score >= 80:
        health_label = "ÓPTIMA"
        health_emoji = "✅"
    elif health_score >= 60:
        health_label = "ACEPTABLE"
        health_emoji = "⚠️"
    elif health_score >= 40:
        health_label = "REQUIERE MEJORAS"
        health_emoji = "🔶"
    else:
        health_label = "CRÍTICA"
        health_emoji = "🔴"

    # ------------------------------------------------------------------ #
    # PASO 8 — Simulación final con guidelines optimizadas                 #
    # ------------------------------------------------------------------ #
    # Usar la primera conversación como caso representativo
    rep_conv_raw = conversations[0]
    if isinstance(rep_conv_raw, dict):
        rep_conv_raw = rep_conv_raw.get("text", str(rep_conv_raw))
    simulation_output = await simulate_fin(
        conversation=rep_conv_raw,
        guidelines=final_guidelines,
        product=product,
        context=objective,
    )

    # Extraer secciones clave de la simulación
    sim_decision = ""
    sim_confidence = ""
    sim_risk = ""
    for line in simulation_output.split("\n"):
        if "DECISIÓN" in line.upper() and not sim_decision:
            sim_decision = line.strip()
        if "CONFIANZA" in line.upper() and not sim_confidence:
            sim_confidence = line.strip()
        if "ESCALAMIENTO" in line.upper() and "RIESGO" in line.upper() and not sim_risk:
            sim_risk = line.strip()

    # ------------------------------------------------------------------ #
    # Riesgos identificados                                                #
    # ------------------------------------------------------------------ #
    risks = []
    if any(r["risk"] == "ALTO" for r in classification_results):
        risks.append("Existen guidelines con riesgo ALTO. Deben revisarse antes del despliegue.")
    if guidelines_with_issues:
        n = len(guidelines_with_issues)
        risks.append(f"{n} guideline(s) presentaron problemas en auditoría.")
    if has_conflicts:
        risks.append("Se detectaron conflictos entre guidelines. Pueden generar comportamientos contradictorios en FIN.")
    if avg_score < 60:
        risks.append("El puntaje promedio de calidad está por debajo del umbral recomendado (60/100).")
    if health_score < 50:
        risks.append("La salud general del producto es crítica. Prioriza optimización antes de publicar.")
    if not risks:
        risks.append("No se identificaron riesgos críticos. El conjunto de guidelines es estable.")

    # ------------------------------------------------------------------ #
    # Prioridad de implementación                                          #
    # ------------------------------------------------------------------ #
    urgent = [c for c in classification_results if c["priority"] == "URGENTE"]
    high   = [c for c in classification_results if c["priority"] == "ALTA"]
    normal = [c for c in classification_results if c["priority"] not in ("URGENTE", "ALTA")]

    # ------------------------------------------------------------------ #
    # Recomendaciones finales                                              #
    # ------------------------------------------------------------------ #
    recommendations = []
    if guidelines_with_issues:
        recommendations.append(
            "Reemplaza las guidelines con problemas por sus versiones optimizadas antes de publicar."
        )
    if has_conflicts:
        recommendations.append(
            "Resuelve los conflictos detectados entre guidelines para evitar comportamientos inconsistentes."
        )
    if avg_score < 70:
        recommendations.append(
            "Mejora el puntaje promedio usando optimize_guideline en las guidelines con score < 70."
        )
    if len(final_guidelines) > 10:
        recommendations.append(
            "Considera consolidar guidelines similares para reducir la complejidad del conjunto de reglas."
        )
    recommendations.append(
        "Valida cada guideline Crítica o Urgente en conversaciones reales antes del próximo despliegue."
    )
    if not any("audit" in r.lower() for r in recommendations):
        recommendations.append(
            "Ejecuta audit_guideline periódicamente para detectar degradación en la calidad de las guidelines."
        )

    # ------------------------------------------------------------------ #
    # Próximos pasos                                                       #
    # ------------------------------------------------------------------ #
    next_steps = []
    if urgent:
        next_steps.append(
            f"Revisar {len(urgent)} guideline(s) de prioridad URGENTE antes de cualquier otro paso."
        )
    if guidelines_with_issues:
        next_steps.append(
            "Aplicar las versiones optimizadas generadas en este review al repositorio de guidelines."
        )
    if has_conflicts:
        next_steps.append(
            "Ejecutar detect_conflicts nuevamente después de resolver los conflictos identificados."
        )
    next_steps.append(
        "Ejecutar simulate_fin con más conversaciones representativas para validar el comportamiento esperado."
    )
    next_steps.append(
        "Programar una revisión arquitectónica periódica con architect_review cuando se agreguen nuevas guidelines."
    )

    # ------------------------------------------------------------------ #
    # Construcción del reporte ejecutivo                                   #
    # ------------------------------------------------------------------ #
    sep = "=" * 48

    parts = [
        f"{sep}",
        "FIN ARCHITECT REVIEW",
        f"{sep}\n",
    ]

    parts.append("PRODUCTO\n")
    parts.append(f"{product.upper()}\n")

    parts.append("OBJETIVO\n")
    parts.append(f"{objective if objective else 'No especificado'}\n")

    parts.append("RESUMEN EJECUTIVO\n")
    total_convs = len(conversations)
    total_gl = len(final_guidelines)
    parts.append(
        f"Se analizaron {total_convs} conversación(es) del producto {product}. "
        f"Se identificaron {len(all_guidelines)} guidelines (incluyendo actuales y nuevas propuestas). "
        f"Tras el pipeline completo, el conjunto final contiene {total_gl} guideline(s) con "
        f"un puntaje promedio de {avg_score}/100 y una salud general de {health_score}/100 ({health_label}).\n"
    )

    parts.append("SALUD GENERAL DEL PRODUCTO\n")
    parts.append(f"{health_emoji} {health_score}/100 — {health_label}\n")

    parts.append("CONVERSACIONES ANALIZADAS\n")
    parts.append(f"{total_convs} conversación(es)\n")

    # Patrones del extraction
    parts.append("PATRONES DETECTADOS\n")
    if patterns_block:
        for line in patterns_block:
            if line.strip():
                parts.append(line)
    else:
        parts.append("- No se detectaron patrones con suficiente recurrencia.\n")
    parts.append("")

    parts.append("NUEVAS GUIDELINES PROPUESTAS\n")
    if final_guidelines:
        for i, g in enumerate(final_guidelines, start=1):
            cl = next((c for c in classification_results if c["guideline"] == g), {})
            sc = next((s for s in score_results if s["guideline"] == g), {})
            score_str = f"Score: {sc.get('score', '—')}/100" if sc else ""
            cat_str = cl.get("category", "") if cl else ""
            pri_str = cl.get("priority", "") if cl else ""
            parts.append(f"{i}. {g}")
            if cat_str or score_str or pri_str:
                parts.append(f"   [{cat_str} | {pri_str} | {score_str}]")
    else:
        parts.append("- No se generaron nuevas guidelines.\n")
    parts.append("")

    parts.append("RESULTADO DE AUDITORÍA\n")
    if guidelines_clean:
        parts.append(f"✅ {len(guidelines_clean)} guideline(s) sin problemas críticos.")
    if guidelines_with_issues:
        parts.append(f"⚠️ {len(guidelines_with_issues)} guideline(s) con problemas detectados:")
        for a in guidelines_with_issues:
            short = a["guideline"][:80] + ("..." if len(a["guideline"]) > 80 else "")
            parts.append(f"- \"{short}\"")
            for issue in a["issues"]:
                parts.append(f"  {issue}")
    parts.append("")

    parts.append("OPTIMIZACIONES APLICADAS\n")
    if optimized_map:
        for original, optimized in optimized_map.items():
            orig_short = original[:70] + ("..." if len(original) > 70 else "")
            opt_short = optimized[:70] + ("..." if len(optimized) > 70 else "")
            parts.append(f"ANTES: {orig_short}")
            parts.append(f"DESPUÉS: {opt_short}\n")
    else:
        parts.append("- No fue necesario aplicar optimizaciones.\n")

    parts.append("CLASIFICACIÓN\n")
    for c in classification_results:
        short = c["guideline"][:70] + ("..." if len(c["guideline"]) > 70 else "")
        parts.append(
            f"- \"{short}\"\n"
            f"  Categoría: {c['category']} | Subcategoría: {c['subcategory']} "
            f"| Riesgo: {c['risk']} | Prioridad: {c['priority']}"
        )
    parts.append("")

    parts.append("CONFLICTOS DETECTADOS\n")
    if has_conflicts:
        parts.append("⚠️ Se detectaron conflictos entre guidelines:")
        for line in conflict_lines[:6]:
            parts.append(line)
    else:
        parts.append("✅ No se detectaron conflictos entre las guidelines.\n")

    parts.append("PUNTAJE DE CALIDAD\n")
    parts.append(f"Promedio: {avg_score}/100 | Máximo: {max_score}/100 | Mínimo: {min_score}/100\n")
    for s in sorted(score_results, key=lambda x: -x["score"]):
        short = s["guideline"][:65] + ("..." if len(s["guideline"]) > 65 else "")
        interp = f" — {s['interpretation']}" if s["interpretation"] else ""
        parts.append(f"- {s['score']}/100{interp}")
        parts.append(f"  \"{short}\"")
    parts.append("")

    parts.append("SIMULACIÓN FINAL\n")
    # Incluir secciones relevantes de la simulación
    sim_lines = simulation_output.split("\n")
    in_sim_section = False
    sim_sections_to_include = {
        "INTENCIÓN DETECTADA", "EMOCIÓN DETECTADA", "PRIORIDAD",
        "DECISIÓN DE FIN", "RIESGO DE ESCALAMIENTO", "NIVEL DE CONFIANZA",
    }
    current_sim_section = None
    sim_buffer = []
    for line in sim_lines:
        stripped = line.strip().upper()
        if stripped in sim_sections_to_include:
            if current_sim_section and sim_buffer:
                parts.append(f"{current_sim_section}")
                for bl in sim_buffer:
                    if bl.strip():
                        parts.append(bl)
            current_sim_section = line.strip()
            sim_buffer = []
        elif current_sim_section:
            sim_buffer.append(line)
    if current_sim_section and sim_buffer:
        parts.append(f"{current_sim_section}")
        for bl in sim_buffer[:3]:
            if bl.strip():
                parts.append(bl)
    parts.append("")

    parts.append("RIESGOS\n")
    for r in risks:
        parts.append(f"- {r}")
    parts.append("")

    parts.append("PRIORIDAD DE IMPLEMENTACIÓN\n")
    idx = 1
    for c in urgent:
        short = c["guideline"][:70] + ("..." if len(c["guideline"]) > 70 else "")
        parts.append(f"{idx}. [URGENTE] \"{short}\"")
        idx += 1
    for c in high:
        short = c["guideline"][:70] + ("..." if len(c["guideline"]) > 70 else "")
        parts.append(f"{idx}. [ALTA] \"{short}\"")
        idx += 1
    for c in normal:
        short = c["guideline"][:70] + ("..." if len(c["guideline"]) > 70 else "")
        parts.append(f"{idx}. [{c['priority']}] \"{short}\"")
        idx += 1
    parts.append("")

    parts.append("RECOMENDACIONES\n")
    for r in recommendations:
        parts.append(f"- {r}")
    parts.append("")

    parts.append("PRÓXIMOS PASOS\n")
    for i, step in enumerate(next_steps, start=1):
        parts.append(f"{i}. {step}")
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
