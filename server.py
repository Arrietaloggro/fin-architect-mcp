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
