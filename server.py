from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
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

    Args:
        guideline: Texto de la guideline a auditar.
        product: Producto Loggro (restobar, facturacion, inventario, alojamiento, general).
        context: Contexto adicional del caso de uso.
    """
    issues = []
    suggestions = []

    # Validaciones básicas
    if len(guideline.strip()) < 20:
        issues.append("La guideline es demasiado corta para ser accionable.")

    keywords_ambiguous = ["siempre", "nunca", "todos", "ninguno"]
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
        result_parts.append(f"**Contexto:** {context}\n")

    if issues:
        result_parts.append("**⚠️ Problemas detectados:**")
        for i in issues:
            result_parts.append(f"- {i}")
    else:
        result_parts.append("**✅ Sin problemas críticos detectados.**")

    if suggestions:
        result_parts.append("\n**💡 Sugerencias:**")
        for s in suggestions:
            result_parts.append(f"- {s}")

    result_parts.append(
        "\n**Recomendación:** Valida esta guideline contra conversaciones reales en Intercom antes de publicar."
    )

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


app = Starlette(
    routes=[
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
