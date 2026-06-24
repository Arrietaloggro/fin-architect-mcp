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
