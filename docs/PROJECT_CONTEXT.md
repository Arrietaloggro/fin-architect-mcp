# FIN Architect MCP — Documentación Técnica del Proyecto

> Versión: 1.0  
> Última actualización: 2026-06-25  
> Repositorio: `Arrietaloggro/fin-architect-mcp`

---

## 1. Objetivo del Proyecto

**FIN Architect MCP** es un servidor de herramientas MCP (*Model Context Protocol*) diseñado para gobernar, auditar y optimizar el sistema de conocimiento y reglas de **FIN**, el agente conversacional de Loggro.

FIN resuelve consultas de clientes de forma autónoma usando dos fuentes principales:

- **Guidelines**: reglas de comportamiento que le dicen a FIN *cómo* actuar.
- **Artículos de Base de Conocimiento**: documentos que le dicen a FIN *qué* responder.

El objetivo del proyecto es garantizar que ambas fuentes sean coherentes, completas, seguras y aptas para el uso autónomo por FIN antes de llegar a producción.

---

## 2. Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     FIN Architect MCP                       │
│                   (FastMCP / Python)                        │
├────────────────────────┬────────────────────────────────────┤
│    GUIDELINE CORE      │         KNOWLEDGE CORE             │
│                        │                                    │
│  audit_guideline       │  audit_knowledge                   │
│  optimize_guideline    │  optimize_article                  │
│  classify_guideline    │  knowledge_review                  │
│  detect_conflicts      │                                    │
│  score_guideline       │                                    │
│  simulate_fin          │                                    │
│  generate_guideline    │                                    │
│  extract_guidelines    │                                    │
├────────────────────────┴────────────────────────────────────┤
│                   ORCHESTRATION LAYER                       │
│                   architect_review                          │
│         (Architect Decision Engine — ADE)                   │
└─────────────────────────────────────────────────────────────┘
```

El servidor se expone mediante SSE (*Server-Sent Events*) sobre HTTP usando `uvicorn` + `Starlette`, y es consumido por cualquier cliente compatible con el protocolo MCP (Claude Desktop, Claude Code, integraciones custom).

---

## 3. Filosofía de Diseño

| Principio | Descripción |
|---|---|
| **Un motor, todas las métricas** | Cada módulo tiene un único motor de decisión del que derivan todas las métricas. No existen cálculos independientes que puedan generar contradicciones. |
| **Sin invención** | Las herramientas nunca inventan información, asumen pasos ni cambian el significado del contenido original. Solo analizan, detectan y reorganizan. |
| **Evidencia explícita** | Cada riesgo, problema o recomendación cita evidencia concreta del contenido analizado (patrones detectados, frases específicas, conteos). |
| **Coherencia garantizada** | Las métricas derivadas (Health Score, Riesgo, Decisión de despliegue, Automation Readiness) nunca se contradicen entre sí. |
| **Reutilización de lógica** | La lógica de detección (loops, términos absolutos, escalamiento, verbos de acción) se escribe una vez y se reutiliza en todas las herramientas que la necesiten. |
| **API estable** | Los parámetros de cada herramienta no cambian entre versiones. Las mejoras se implementan dentro de la función sin romper la interfaz. |
| **Branch por feature** | Cada nueva herramienta o cambio significativo se desarrolla en una rama dedicada y se integra mediante Pull Request. |

---

## 4. Guideline Core

El **Guideline Core** es el conjunto de herramientas que gobierna las *reglas de comportamiento* de FIN.

### 4.1 Herramientas

| Herramienta | Parámetros principales | Propósito |
|---|---|---|
| `audit_guideline` | `guideline`, `product`, `context` | Audita una guideline individual. Detecta términos absolutos, escalamiento sin condición, longitud excesiva y colisiones potenciales. |
| `optimize_guideline` | `guideline` | Mejora automáticamente el texto de una guideline eliminando ambigüedades y reforzando su estructura para FIN. |
| `classify_guideline` | `guideline`, `product`, `context` | Clasifica una guideline por categoría (escalamiento, respuesta, restricción, etc.), subcategoría, nivel de riesgo y prioridad. |
| `detect_conflicts` | `guidelines` (lista), `product`, `context` | Analiza un conjunto de guidelines y detecta conflictos entre ellas: instrucciones contradictorias, duplicados, escalamiento incompatible, colisiones global vs producto. |
| `score_guideline` | `guideline`, `product`, `context` | Evalúa la calidad de una guideline y devuelve una puntuación sobre 100 con desglose por criterio, fortalezas, debilidades y recomendaciones. |
| `simulate_fin` | `conversation`, `guidelines` (lista), `product`, `context` | Simula el proceso de decisión de FIN ante una conversación real usando las guidelines suministradas. Devuelve intención, emoción, guideline aplicada, respuesta generada, riesgo de escalamiento y nivel de confianza. |
| `generate_guideline` | `conversation`, `product`, `objective`, `context` | Analiza una conversación real entre un cliente y FIN y genera una nueva guideline lista para incorporarse al repositorio. |
| `extract_guidelines` | `conversations` (lista), `product`, `context` | Procesa múltiples conversaciones, agrupa patrones similares mediante similitud Jaccard + union-find, y genera una guideline por cluster (no por conversación). Elimina duplicados. |

### 4.2 Flujo típico del Guideline Core

```
Conversaciones reales
        ↓
  extract_guidelines        ← Genera guidelines desde conversaciones
        ↓
  score_guideline           ← Evalúa calidad de cada guideline
        ↓
  classify_guideline        ← Categoriza y asigna prioridad
        ↓
  detect_conflicts          ← Detecta conflictos en el repositorio
        ↓
  simulate_fin              ← Valida comportamiento antes de publicar
        ↓
  architect_review          ← Revisión ejecutiva completa del sistema
```

---

## 5. Knowledge Core

El **Knowledge Core** es el conjunto de herramientas que gobierna los *artículos de Base de Conocimiento* que FIN usa para resolver consultas.

### 5.1 Herramientas

| Herramienta | Parámetros principales | Propósito |
|---|---|---|
| `audit_knowledge` | `article`, `product`, `context` | Audita un artículo individual. Calcula Health Score (0–100) mediante 12 criterios. Todas las métricas derivadas (Risk, Automation Readiness, Resolution Capability, Deploy Decision) fluyen del Knowledge Decision Engine (KDE). |
| `optimize_article` | `article`, `product`, `context` | Recibe un artículo y devuelve una versión reestructurada para FIN. No inventa información. Solo reorganiza usando la estructura estándar (Objetivo, Pasos, Resultado esperado, Excepciones, Escalamiento, Información para el agente). |
| `knowledge_review` | `product`, `articles` (lista), `context` | Analiza el repositorio completo de artículos de un producto. Genera diagnóstico ejecutivo con madurez general, cobertura temática, artículos críticos, duplicados, conflictos, oportunidades, priorización y plan de acción. |

### 5.2 Los 12 criterios de `audit_knowledge`

| # | Criterio | Peso (pts) | Qué evalúa |
|---|---|---|---|
| 1 | Claridad | 12 | Ausencia de frases vagas y longitud mínima |
| 2 | Estructura | 10 | Secciones, pasos numerados, viñetas |
| 3 | Pasos | 12 | Verbos de acción, pasos numerados, pasos no ambiguos |
| 4 | Cobertura | 8 | Presencia de causa, solución, resultado |
| 5 | Ambigüedad | 10 | Ausencia de términos absolutos y contradicciones |
| 6 | Longitud | 8 | Rango adecuado para FIN (60–400 palabras) |
| 7 | Consistencia | 8 | Sin repeticiones, tratamiento único (tú/usted) |
| 8 | Terminología | 8 | Términos técnicos definidos, mínimo idioma extranjero |
| 9 | Uso por FIN | 10 | Señales de guía paso a paso, ausencia de acciones no ejecutables |
| 10 | Escalamiento | 8 | Criterio de escalamiento condicional explícito |
| 11 | Mantenibilidad | 7 | Ausencia de fechas/versiones específicas |
| 12 | Riesgo operativo | 7 | Ausencia de acciones destructivas sin advertencia |
| | **Total** | **100** | |

### 5.3 Flujo típico del Knowledge Core

```
Artículo(s) de la Base de Conocimiento
        ↓
  audit_knowledge           ← Diagnóstico individual con KDE
        ↓
  optimize_article          ← Versión reestructurada para FIN
        ↓
  knowledge_review          ← Diagnóstico del repositorio completo
```

---

## 6. Decision Engines

### 6.1 Knowledge Decision Engine (KDE)

El KDE es el motor central de `audit_knowledge`. Garantiza que todas las métricas de un artículo sean internamente coherentes.

**Flujo del KDE:**

```
12 criterios individuales
        ↓
  _raw_total (0–100)
        ↓
  Detección de bloqueadores KDE:
    - Loop instruccional CRÍTICO (> 3 patrones)
    - Regla anti-escalamiento explícita ("nunca escales")
        ↓
  kde_health = _raw_total con penalizaciones globales:
    - Términos absolutos: -2 pts c/u (máx -8)
    - Loop ALTO: -8 pts
    - Loop CRÍTICO: -15 pts
    - Pasos ambiguos: -2 pts c/u (máx -6)
    - Bloqueador activo: hard cap ≤ 60
        ↓
  Desde kde_health derivan TODAS las métricas:
    ├─ Riesgo Global    (ALTO / MEDIO / BAJO)
    ├─ Resolution Cap.  (≤ 40% si bloqueador)
    ├─ Automation       (≤ Baja si bloqueador)
    └─ Deploy Decision  (BLOQUEADO / NO LISTO / LISTO CON RECOMENDACIONES / LISTO)
```

**Reglas hard cap:**

| Condición | Health | Resolution | Automation | Deploy |
|---|---|---|---|---|
| Bloqueador activo | ≤ 60 | ≤ 40% | ≤ Baja | BLOQUEADO |
| Loop ALTO | -8 pts | -15% | ≤ Media | LISTO CON RECOMENDACIONES |
| Health < 50 | — | — | ≤ Baja | NO LISTO |
| Health ≥ 78 | — | — | Alta / Excelente | LISTO |

### 6.2 Architect Decision Engine (ADE)

El ADE es el motor central de `architect_review`. Orquesta el pipeline completo del Guideline Core y produce un reporte ejecutivo de nivel empresarial.

**Capacidades del ADE:**

| Capacidad | Descripción |
|---|---|
| Cobertura funcional | Mapea cada conversación a las guidelines que la cubrirían |
| Métricas de repositorio | Score promedio, distribución de calidad, índice de mantenibilidad |
| Guidelines huérfanas | Detecta guidelines que ninguna conversación activaría |
| Matriz de cobertura | Cruza conversaciones × guidelines |
| Simulación de impacto | Estima mejora en resolución autónoma si se aplican recomendaciones |
| Resumen ejecutivo PM | Orientado a decisiones de negocio |
| Resumen equipo Soporte | Orientado a acciones técnicas inmediatas |

---

## 7. Flujo Recomendado de Uso

### Caso 1: Incorporar un nuevo artículo de conocimiento

```
1. audit_knowledge(article, product)
   → ¿Deploy = LISTO? → Publicar directamente
   → ¿Deploy = LISTO CON RECOMENDACIONES? → optimize_article → Re-auditar
   → ¿Deploy = BLOQUEADO? → Intervención humana obligatoria
```

### Caso 2: Revisar la Base de Conocimiento completa

```
1. knowledge_review(product, articles)
   → Identificar artículos BLOQUEADOS (prioridad 1)
   → Identificar vacíos de cobertura
   → Seguir plan de acción generado
```

### Caso 3: Incorporar nuevas reglas desde conversaciones

```
1. extract_guidelines(conversations, product)
   → Genera guidelines desde patrones detectados
2. score_guideline(guideline) por cada una
   → Filtra las de score < 60
3. detect_conflicts(all_guidelines, product)
   → Verifica que no haya colisiones con el repositorio existente
4. simulate_fin(sample_conversation, guidelines)
   → Valida comportamiento esperado
5. architect_review(product, conversations, guidelines)
   → Reporte ejecutivo antes de publicar
```

### Caso 4: Revisión arquitectónica completa del sistema

```
1. architect_review(product, conversations, current_guidelines)
   → Diagnóstico ejecutivo completo (ADE)
   → Resumen para PM + Resumen para equipo de Soporte
   → Roadmap de optimización
```

---

## 8. Roadmap del Proyecto

### 8.1 Herramientas implementadas

| Módulo | Herramienta | Estado | PR |
|---|---|---|---|
| Guideline Core | `audit_guideline` | ✅ Producción | — |
| Guideline Core | `optimize_guideline` | ✅ Producción | — |
| Guideline Core | `classify_guideline` | ✅ Producción | — |
| Guideline Core | `detect_conflicts` | ✅ Producción | — |
| Guideline Core | `score_guideline` | ✅ Producción | — |
| Guideline Core | `simulate_fin` | ✅ Producción | — |
| Guideline Core | `generate_guideline` | ✅ Producción | — |
| Guideline Core | `extract_guidelines` | ✅ Producción | — |
| Orchestration | `architect_review` | ✅ Producción | — |
| Knowledge Core | `audit_knowledge` v3 (KDE) | ✅ Producción | #17 |
| Knowledge Core | `optimize_article` | ✅ Producción | #18 |
| Knowledge Core | `knowledge_review` | ✅ Producción | #19 |

### 8.2 Herramientas futuras (propuestas)

| Herramienta | Módulo | Propósito estimado |
|---|---|---|
| `compare_articles` | Knowledge Core | Comparar dos versiones del mismo artículo y mostrar delta de calidad |
| `validate_knowledge_base` | Knowledge Core | Validación cross-check entre guidelines y artículos (¿las guidelines tienen artículos de soporte?) |
| `generate_article` | Knowledge Core | Generar un artículo estructurado desde una conversación real |
| `fin_readiness_report` | Orchestration | Reporte ejecutivo unificado: Guidelines + Knowledge + Cobertura + Riesgos |
| `changelog_review` | Governance | Detectar cambios entre versiones de guidelines/artículos y evaluar impacto sobre FIN |

---

## 9. Convenciones de Desarrollo

### 9.1 Cómo crear una nueva herramienta

1. **Abrir `server.py`** y localizar el punto de inserción (antes de la siguiente herramienta del mismo módulo, o al final antes del bloque de rutas HTTP).
2. **Decorar con `@mcp.tool()`** y definir la función como `async`.
3. **Incluir docstring** describiendo el propósito, entradas y salida.
4. **No modificar ninguna otra herramienta** durante el desarrollo de la nueva.
5. **Reutilizar la lógica de detección** existente (ver sección 9.2).
6. **Validar sintaxis**: `python3 -c "import py_compile; py_compile.compile('server.py', doraise=True)"`.
7. **Ejecutar prueba real** con `asyncio.run()` antes de hacer commit.
8. **Trabajar en rama dedicada** (ver sección 9.3).
9. **Crear PR automáticamente** al terminar.

### 9.2 Cómo reutilizar lógica

La lógica de detección está definida en `audit_knowledge` y debe replicarse (no importarse) en herramientas que la necesiten, ya que Python no permite llamadas directas entre funciones `async` en el mismo scope sin un event loop adicional. Las variables clave a reutilizar son:

| Variable / Patrón | Descripción |
|---|---|
| `loop_patterns` | Lista de patrones de bucle instruccional |
| `absolute_terms` | Términos absolutos sin condición |
| `vague_phrases` | Frases que reducen la claridad |
| `escalation_signals` | Señales de criterio de escalamiento |
| `anti_escalation_rule` | Regex para regla que prohíbe escalar |
| `step_verbs_es` | Verbos de acción en español |
| `kde_blocker_flags` | Lógica de bloqueadores críticos |
| Hard caps KDE | `min(kde_health, 60)` y `min(kde_resolution, 40)` |

**Patrón de reutilización:**

```python
# Dentro de la nueva herramienta, definir una función interna:
def _analyze(article_text):
    # Copiar aquí los bloques de detección relevantes de audit_knowledge
    # Retornar dict con los campos necesarios
    return { "kde_health": ..., "loop_risk_level": ..., ... }

analyses = [_analyze(a) for a in articles]
```

### 9.3 Convención de nombres de ramas

| Tipo de cambio | Prefijo | Ejemplo |
|---|---|---|
| Nueva herramienta | `feature/` | `feature/audit-knowledge-kde` |
| Mejora a herramienta existente | `feature/` | `feature/audit-knowledge-v2` |
| Documentación | `docs/` | `docs/project-context` |
| Corrección de bug | `fix/` | `fix/kde-health-cap` |
| Refactor | `refactor/` | `refactor/loop-detection` |

### 9.4 Estructura de reportes

Todos los reportes del proyecto siguen la misma estructura visual para garantizar consistencia entre herramientas:

```
================================================   ← sep (= × 48)
NOMBRE DE LA HERRAMIENTA — FIN [Módulo] Core
================================================

METADATOS (producto, contexto, etc.)

────────────────────────────────────────          ← div2 (─ × 40)
SECCIÓN PRINCIPAL
────────────────────────────────────────

  Contenido con sangría de 2 espacios.

········································          ← div3 (· × 40, para subsecciones)
SUBSECCIÓN
········································

  Contenido.

================================================
```

**Reglas de formato:**

- Todos los emojis de estado siguen la escala: `✅ 🟢 🔵 ⚠️ 🔶 🔴 🚫`
- Los scores siempre se expresan como `X/100`
- Las listas de problemas usan `⚠️` y las de riesgos usan `🔴`
- Las fortalezas usan `✓` y las recomendaciones usan numeración `1. 2. 3.`
- Los bloqueadores críticos siempre aparecen al inicio del reporte

---

## 10. Principios del Proyecto

### P1 — Coherencia ante todo
Ninguna métrica puede contradecir a otra. Si un artículo está BLOQUEADO, su Health Score no puede ser Alto, su Riesgo no puede ser BAJO y sus Fortalezas no pueden ignorar los bloqueadores activos.

### P2 — Evidencia, no suposición
Cada problema detectado debe citar el patrón exacto encontrado en el contenido. Frases como "el artículo podría tener problemas" están prohibidas. La forma correcta es: "Se detectó 'nunca escales' en la línea X. FIN quedará sin salida al agotar los pasos."

### P3 — Sin invención
Las herramientas no inventan pasos, no completan información faltante, no asumen conocimiento de negocio. Si falta información, se reporta el vacío. Si sobra información peligrosa, se elimina solo en la versión optimizada.

### P4 — La API es un contrato
Los parámetros de entrada y el tipo de retorno de cada herramienta son un contrato estable. Las mejoras internas nunca rompen la interfaz externa. Los clientes que usan estas herramientas no deben actualizar su código cuando se mejora la lógica interna.

### P5 — FIN primero
Toda decisión de diseño se evalúa desde la perspectiva de FIN: ¿este artículo/guideline permite que FIN resuelva de forma autónoma, segura y sin bucles? Si la respuesta es no, la herramienta lo detecta y lo reporta.

### P6 — Una rama, un cambio
Cada cambio significativo vive en su propia rama. Nunca se modifican múltiples herramientas en la misma rama a menos que el cambio sea atómicamente inseparable.

### P7 — El reporte es el producto
El valor de cada herramienta está en la calidad de su reporte. Un reporte debe ser legible por un desarrollador que nunca vio el artículo o guideline analizado, y debe permitirle tomar una decisión de negocio sin necesidad de leer el contenido original.
