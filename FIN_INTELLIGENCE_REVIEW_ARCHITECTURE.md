# FIN Intelligence Review — Arquitectura Funcional v1.0

*Documento técnico de diseño | FIN Architect Fase 4*  
*Fecha: 2026-06-26 | Autor: FIN Architect*

---

## 1. Visión General

`fin_intelligence_review()` es la herramienta de inteligencia operacional de FIN Architect.  
No audita pautas individuales (eso lo hace `architect_review`).  
Audita el **ecosistema completo de FIN** en un momento dado: qué tan bien está funcionando el agente como sistema, qué está fallando estructuralmente, y qué palancas específicas moverían el performance.

Su salida es un reporte ejecutivo multi-capa con score global, KPIs accionables y recomendaciones priorizadas — listo para consumo directo por PM, equipo de soporte y arquitectos de FIN.

---

## 2. Entradas

### Parámetros obligatorios

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `product` | `str` | Producto a revisar: `"Restobar"`, `"Pymes"`, `"Nomina"`, `"Alojamientos"` |
| `conversations` | `list[dict]` | Lista de conversaciones recientes. Mínimo 10, recomendado 25–50. Cada elemento debe incluir transcript, custom attributes, pautas aplicadas, resultado. |

### Parámetros opcionales

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `guidelines` | `list[dict]` | `[]` | Lista de pautas activas del producto (id, título, contenido) |
| `kb_articles` | `list[dict]` | `[]` | Catálogo de artículos KB disponibles (del knowledge_inventory) |
| `period_days` | `int` | `30` | Ventana temporal de análisis en días |
| `mode` | `str` | `"full"` | `"full"` / `"quick"` / `"executive"` |
| `benchmark_target` | `dict` | `{}` | Targets de KPIs deseados (ej. `{"escalation_rate": 0.20, "resolution_rate": 0.75}`) |
| `focus_areas` | `list[str]` | `[]` | Áreas de foco específico: `["escalation", "kb_usage", "emotion", "churn"]` |

### Formato esperado de cada conversación en `conversations`

```python
{
  "id": "215474859325975",
  "fecha": "2026-06-26T16:43:27Z",
  "ai_state": "escalated",          # escalated | confirmed_resolution | assumed_resolution
  "rating": None,                    # 1–5 o None
  "workflow": "Restobar IA",
  "ai_title": "Anulación de POS",
  "iacr": "Riesgo Operativo",
  "emociones": "Negative",
  "escalamiento": "Escalar inmediato",
  "fuera_horario": "NO HAY AGENTES DISPONIBLES",
  "pautas_aplicadas": ["635548", "657943", "884123"],
  "articulos_kb": ["Cómo anular una factura de venta en Restobar"],
  "partes": 70,
  "ttfa": 205,
  "ttc": None,
  "transcript": [...],              # Lista de mensajes {role, body, ts}
  "frustration_score": 75,          # Del dataset de Fase 3 si disponible
  "churn_risk": 40,
  "calidad_diagnostico": 55,
  "error_principal": "...",
}
```

---

## 3. Fuentes de Información

```
┌─────────────────────────────────────────────────────────────────────┐
│                   fin_intelligence_review()                          │
│                                                                      │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐ │
│  │   CONVERSACIONES  │   │  KNOWLEDGE BASE   │   │    PAUTAS       │ │
│  │  (input directo) │   │ knowledge_invent. │   │ (input directo) │ │
│  │  • Transcripts   │   │ • Artículos pub.  │   │ • ID + título   │ │
│  │  • Custom attrs  │   │ • Artículos draft │   │ • Contenido     │ │
│  │  • Escalamientos │   │ • Colecciones     │   │ • Cobertura     │ │
│  │  • Ratings       │   │ • Distribución    │   │ • Conflictos    │ │
│  └──────────────────┘   └──────────────────┘   └─────────────────┘ │
│                                                                      │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐ │
│  │  HERRAMIENTAS    │   │  ATRIBUTOS       │   │  WORKFLOWS      │ │
│  │  EXISTENTES      │   │  DETECTADOS      │   │  ACTIVOS        │ │
│  │  • score_guide.. │   │  • IACR          │   │  • Restobar IA  │ │
│  │  • detect_conf.. │   │  • Emociones     │   │  • Nodos start/ │ │
│  │  • classify_g..  │   │  • Urgencia      │   │    end          │ │
│  │  • simulate_fin  │   │  • Fuera horario │   │  • Tasas exit   │ │
│  └──────────────────┘   └──────────────────┘   └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Detalle por fuente

| Fuente | Datos utilizados | Para calcular |
|--------|-----------------|---------------|
| **Conversaciones** | ai_state, rating, ttfa, ttc, partes, escalamiento, emociones | Tasas de resolución, escalación, tiempos, NPS proxy |
| **Transcripts** | Mensajes USER, FIN, ADMIN | Patrones de error, intentos, frustración, calidad diagnóstico |
| **Custom attributes** | IACR, Urgencia, FUERA DE HORARIO, Emociones, Flujo activo | Segmentación de problemas, contexto operativo |
| **Pautas aplicadas** | IDs activados por conversación | Cobertura de pautas, pautas muertas, pautas sobreutilizadas |
| **Knowledge Base** | Artículos utilizados vs disponibles | Brecha KB, artículos no explotados, gaps temáticos |
| **Atributo AI Title** | Título clasificatorio de la conversación | Clustering por intención, distribución de temas |
| **Workflows** | source_title, nodo_inicial, nodo_final | Análisis de flujo, puntos de quiebre |

---

## 4. Métricas Calculadas

### 4.1 Métricas de Resolución

| Métrica | Fórmula | Unidad |
|---------|---------|--------|
| `resolution_rate` | `confirmed_resolutions / total_convs` | % |
| `assumed_resolution_rate` | `assumed_resolutions / total_convs` | % |
| `escalation_rate` | `escalated_convs / total_convs` | % |
| `true_resolution_rate` | `confirmed / (confirmed + escalated)` | % |
| `escalation_by_user_request_rate` | `convs donde user pidió agente / total` | % |
| `escalation_by_guidance_rate` | `convs con escalation_reason=guidance / total` | % |

### 4.2 Métricas de Tiempo

| Métrica | Fórmula | Unidad |
|---------|---------|--------|
| `avg_ttfa` | promedio `time_to_first_admin_reply` | segundos |
| `avg_ttc` | promedio `time_to_last_close` (excluyendo null) | segundos |
| `avg_parts` | promedio `count_conversation_parts` | entero |
| `median_parts` | mediana de partes | entero |
| `p95_parts` | percentil 95 de partes | entero |
| `escalation_delay_index` | promedio de turnos antes de escalar cuando user pide agente | turnos |

### 4.3 Métricas de Calidad FIN

| Métrica | Fuente | Descripción |
|---------|--------|-------------|
| `avg_diagnostico_quality` | dataset Fase 3 | Promedio calidad_diagnostico 0–100 |
| `avg_frustration_score` | dataset Fase 3 | Promedio nivel_frustracion 0–100 |
| `avg_churn_risk` | dataset Fase 3 | Promedio riesgo_churn 0–100 |
| `high_frustration_rate` | frustracion > 60 / total | % |
| `high_churn_risk_rate` | churn_risk > 50 / total | % |
| `rating_avg` | promedio de ratings no-null | 1.0–5.0 |
| `rating_coverage` | convs con rating / total | % |

### 4.4 Métricas de Pautas

| Métrica | Descripción |
|---------|-------------|
| `pauta_activation_rate` | promedio de pautas activas por conversación |
| `pauta_coverage` | % de pautas del repositorio que se activaron al menos una vez |
| `top_pautas` | las 10 pautas más frecuentes |
| `dead_pautas` | pautas que nunca se activaron en el período |
| `pauta_conflict_index` | % de conversaciones con al menos un conflicto detectado |
| `pautas_faltantes_frecuencia` | pautas identificadas como "debieron activarse" más frecuentes |

### 4.5 Métricas de Knowledge Base

| Métrica | Descripción |
|---------|-------------|
| `kb_utilization_rate` | % de conversaciones donde FIN usó al menos un artículo |
| `kb_article_diversity` | número de artículos distintos utilizados |
| `kb_coverage_ratio` | artículos usados / artículos disponibles para el producto |
| `top_kb_articles` | artículos más utilizados |
| `missing_kb_rate` | % de convs donde se identificó artículo faltante |
| `kb_gap_topics` | temas frecuentes sin artículo asociado |

### 4.6 Métricas de Distribución por Intención

Basado en el atributo `AI Title`:

| Métrica | Descripción |
|---------|-------------|
| `top_intentions` | top 10 intenciones más frecuentes |
| `intention_resolution_rate` | resolución por tipo de intención |
| `intention_escalation_rate` | escalación por tipo de intención |
| `intention_frustration_avg` | frustración promedio por intención |
| `critical_intentions` | intenciones con escalación > 70% |

### 4.7 Métricas de Contexto Operativo

| Métrica | Descripción |
|---------|-------------|
| `fuera_horario_rate` | % de convs con FUERA DE HORARIO activo |
| `escalation_fuera_horario_rate` | escalación cuando FUERA DE HORARIO está activo |
| `iacr_distribution` | distribución: Riesgo Operativo / Riesgo Alto / Normal |
| `urgency_distribution` | Baja / Alta por convs |
| `emotion_negative_rate` | % convs con Emociones=Negative |

---

## 5. KPIs Mostrados en el Dashboard

El reporte mostrará un dashboard con 6 bloques:

```
╔══════════════════════════════════════════════════════════════════╗
║           FIN INTELLIGENCE REVIEW — Restobar                     ║
║           Período: últimos 30 días | N=25 conversaciones         ║
╠══════════════════════════════════════════════════════════════════╣
║  RESOLUCIÓN          │  TIEMPOS            │  EXPERIENCIA        ║
║  ─────────────────── │  ───────────────────│  ──────────────────║
║  Tasa Resolución 12% │  TTFA avg   205s    │  Rating avg   N/A  ║
║  Tasa Escalación 88% │  Partes avg  94     │  Frustración   71  ║
║  Por user request 76%│  P95 partes 154     │  Riesgo churn  48  ║
║  Por pauta        24%│  Escalat delay 3.2T │  Negativas    100% ║
╠══════════════════════════════════════════════════════════════════╣
║  PAUTAS                       │  KNOWLEDGE BASE                  ║
║  ────────────────────────────│  ──────────────────────────────  ║
║  Activas en período:  14/XX  │  KB Utilization      52%         ║
║  Pautas muertas:       X     │  Artículos usados:    8 distintos ║
║  Cobertura:           XX%    │  Gaps detectados:     6 temas     ║
║  Conflictos:          XX%    │  Artículos faltantes: 4 comunes   ║
╠══════════════════════════════════════════════════════════════════╣
║  TOP INTENCIONES (por frecuencia + escalación)                   ║
║  #1 Anulación POS (N=4, esc=100%, frust=72)                     ║
║  #2 Facturación Electrónica (N=3, esc=100%, frust=68)           ║
║  ...                                                             ║
╚══════════════════════════════════════════════════════════════════╝
```

### KPIs con semáforo (🔴🟡🟢)

| KPI | 🔴 Crítico | 🟡 Atención | 🟢 OK |
|-----|-----------|-------------|-------|
| Tasa de resolución | < 30% | 30–60% | > 60% |
| Tasa de escalación | > 70% | 40–70% | < 40% |
| Frustración promedio | > 65 | 40–65 | < 40 |
| Riesgo churn promedio | > 50 | 30–50 | < 30 |
| Rating promedio | < 3.0 | 3.0–4.0 | > 4.0 |
| KB utilization | < 30% | 30–60% | > 60% |
| Delay de escalamiento | > 3 turnos | 2–3 | ≤ 1 |

---

## 6. Score Global

### Composición del FIN Intelligence Score (0–100)

El score global integra 6 dimensiones ponderadas:

```
FIN_INTELLIGENCE_SCORE =
    (Resolución         × 0.25) +
    (Experiencia        × 0.25) +
    (Calidad Diagnóstico× 0.20) +
    (Cobertura KB       × 0.15) +
    (Cobertura Pautas   × 0.10) +
    (Eficiencia         × 0.05)
```

### Detalle por dimensión

| Dimensión | Peso | Cálculo | Rango |
|-----------|------|---------|-------|
| **Resolución** | 25% | `true_resolution_rate × 100` | 0–100 |
| **Experiencia** | 25% | `(100 - avg_frustration) × 0.5 + rating_norm × 50` | 0–100 |
| **Calidad Diagnóstico** | 20% | `avg_calidad_diagnostico` (del dataset Fase 3) | 0–100 |
| **Cobertura KB** | 15% | `kb_utilization_rate × 100` | 0–100 |
| **Cobertura Pautas** | 10% | `pauta_coverage × 100` | 0–100 |
| **Eficiencia** | 5% | `100 - clamp(avg_parts / 2, 0, 100)` | 0–100 |

### Interpretación

| Score | Nivel | Descripción |
|-------|-------|-------------|
| 85–100 | **Excelente** | FIN opera como experto autónomo |
| 70–84 | **Bueno** | Performance sólido con áreas de mejora |
| 55–69 | **Regular** | Problemas estructurales identificables |
| 40–54 | **Deficiente** | Intervención urgente requerida |
| 0–39 | **Crítico** | El sistema está causando daño activo |

---

## 7. Recomendaciones Automáticas

La herramienta generará recomendaciones priorizadas en tres capas:

### Capa 1 — Acciones Inmediatas (Impacto en < 48h)

Detectadas por reglas determinísticas:

| Condición detectada | Recomendación generada |
|--------------------|----------------------|
| `escalation_delay_index > 2` | "Ajustar pauta ESCALAMIENTO POR SOLICITUD: FIN está esperando X turnos antes de escalar cuando el user ya pidió agente." |
| `fuera_horario_rate > 40% AND escalation_rate > 80%` | "Activar workflow nocturno específico: el X% de conversaciones fuera de horario escalan sin resolución. Rediseñar flujo para contexto FUERA DE HORARIO." |
| `kb_utilization_rate < 30%` | "FIN no está usando KB en el X% de conversaciones. Revisar configuración de content sources para el workflow [workflow_name]." |
| `high_churn_risk_rate > 30%` | "X% de conversaciones tienen riesgo de churn alto. Activar pauta de detección de riesgo de churn con escalación prioritaria." |
| `dead_pautas.count > 5` | "X pautas nunca se activaron en el período. Revisar condiciones de activación o considerar deprecarlas." |

### Capa 2 — Mejoras Estructurales (1–2 semanas)

Detectadas por análisis de patrones:

- **Nueva pauta sugerida**: basada en los errores principales más frecuentes del dataset
- **Ajuste a pauta existente**: cuando la misma pauta se activa pero el error persiste
- **Artículo KB faltante**: por tema frecuente sin artículo asociado
- **Nuevo atributo sugerido**: cuando hay contexto operativo no capturado que cambiaría la respuesta
- **Rediseño de nodo de workflow**: cuando un nodo específico tiene alta tasa de salida frustrada

### Capa 3 — Evolución del Sistema (1+ mes)

Basada en tendencias y benchmarks:

- Comparación vs período anterior (si hay datos históricos)
- Benchmark vs target configurado en `benchmark_target`
- Propuesta de nuevos workflows para intenciones críticas sin workflow dedicado
- Propuesta de segmentación de audiencias (PREMIUM vs base, horario vs fuera de horario)

### Formato de cada recomendación

```
[PRIORIDAD: CRÍTICA|ALTA|MEDIA|BAJA]
[CATEGORÍA: Pauta|KB|Workflow|Atributo|Prompt]
[IMPACTO ESTIMADO: +X puntos en FIN_INTELLIGENCE_SCORE]

Problema detectado:
  [descripción basada en evidencia de las conversaciones]

Acción recomendada:
  [instrucción específica y ejecutable]

Evidencia:
  - Conv [ID]: [fragmento del transcript relevante]
  - Conv [ID]: [fragmento del transcript relevante]

Métrica de éxito:
  [cómo medir si la mejora funcionó]
```

---

## 8. Reutilización de Herramientas Existentes

### Herramientas que `fin_intelligence_review()` invocará internamente

| Herramienta existente | Cómo se reutiliza | Cuándo se invoca |
|----------------------|-------------------|-----------------|
| `score_guideline()` | Puntuar las pautas identificadas como problemáticas | Para cada pauta en `dead_pautas` o con alta tasa de error |
| `detect_conflicts()` | Detectar conflictos entre pautas activas | Una sola vez sobre el conjunto de pautas del producto |
| `classify_guideline()` | Clasificar pautas nuevas sugeridas | Para validar que las recomendaciones de nuevas pautas no dupliquen existentes |
| `extract_guidelines()` | Extraer patrones de las conversaciones | Para alimentar la capa de recomendaciones estructurales |
| `architect_review()` | Obtener análisis narrativo profundo | En modo `"full"` únicamente, como sub-análisis |

### Datos que se reutilizan directamente (sin re-procesamiento)

| Dataset existente | Campos reutilizados |
|-------------------|-------------------|
| `dataset_fin_25_conversaciones.json` | `frustration_score`, `churn_risk`, `calidad_diagnostico`, `error_principal`, `causa_raiz`, `nueva_pauta_sugerida`, `articulo_conocimiento_faltante`, `severidad_problema` |
| `knowledge_inventory.json` | `id`, `title`, `product`, `state`, `tiene_descripcion` para validar artículos sugeridos |
| `KNOWLEDGE_DIGITAL_TWIN.md` | Estadísticas de cobertura por producto |

---

## 9. Componentes Nuevos Requeridos

### 9.1 Módulo de Agregación y Métricas

**Nombre:** `_compute_metrics(conversations, guidelines, kb_articles)`  
**Responsabilidad:** Calcular las ~40 métricas definidas en la Sección 4.  
**Input:** Las tres fuentes de datos.  
**Output:** Dict estructurado con todas las métricas.  
**Dependencias:** Ninguna externa. Cálculos en Python puro.

### 9.2 Motor de Semáforos

**Nombre:** `_apply_thresholds(metrics, benchmark_target)`  
**Responsabilidad:** Asignar estado 🔴/🟡/🟢 a cada KPI.  
**Input:** Dict de métricas + targets configurables.  
**Output:** Dict con `{kpi: {valor, estado, delta_vs_target}}`.  
**Dependencias:** `_compute_metrics`.

### 9.3 Motor de Score Global

**Nombre:** `_compute_fin_score(metrics)`  
**Responsabilidad:** Calcular el FIN_INTELLIGENCE_SCORE con sus 6 dimensiones.  
**Input:** Dict de métricas.  
**Output:** `{score_global, dimensiones: {nombre, peso, valor, puntaje}}`.  
**Dependencias:** `_compute_metrics`.

### 9.4 Motor de Recomendaciones

**Nombre:** `_generate_recommendations(metrics, conversations, guidelines, kb_articles)`  
**Responsabilidad:** Generar recomendaciones priorizadas en 3 capas.  
**Input:** Métricas + datos crudos para evidencia.  
**Output:** Lista ordenada de objetos recomendación con prioridad, categoría, impacto estimado, evidencia y métrica de éxito.  
**Dependencias:** `_compute_metrics`, herramientas existentes.

### 9.5 Renderizador de Reporte

**Nombre:** `_render_report(metrics, kpis, score, recommendations, mode)`  
**Responsabilidad:** Producir el output final en formato texto enriquecido.  
**Modos:** `"full"` (todo), `"quick"` (score + top 5 recomendaciones), `"executive"` (una página para PM).  
**Input:** Outputs de los 4 módulos anteriores.  
**Output:** String con el reporte completo.

### 9.6 Clusterizador de Intenciones

**Nombre:** `_cluster_intentions(conversations)`  
**Responsabilidad:** Agrupar conversaciones por `ai_title` y calcular métricas por grupo.  
**Método:** Agrupación exacta por `ai_title`; fallback a keyword clustering si `ai_title` es nulo.  
**Output:** Dict `{intention: {count, escalation_rate, avg_frustration, avg_churn, top_errors}}`.

---

## 10. Diagrama de Flujo de Ejecución

```
fin_intelligence_review(product, conversations, guidelines, kb_articles, ...)
│
├─► [Validación de inputs]
│     • Verificar mínimo de conversaciones (≥10)
│     • Verificar campos requeridos por conversación
│     • Warning si faltan campos opcionales (frustration_score, etc.)
│
├─► [PASO 1] _compute_metrics()
│     • Métricas de resolución
│     • Métricas de tiempo
│     • Métricas de calidad
│     • Métricas de pautas
│     • Métricas de KB
│     • Métricas de distribución por intención
│     • Métricas de contexto operativo
│
├─► [PASO 2] _apply_thresholds()
│     • Semáforos por KPI
│     • Delta vs benchmark_target
│
├─► [PASO 3] _compute_fin_score()
│     • 6 dimensiones ponderadas
│     • Score global 0–100
│     • Nivel interpretativo
│
├─► [PASO 4] _cluster_intentions()
│     • Agrupación por ai_title
│     • Ranking de intenciones críticas
│
├─► [PASO 5] _generate_recommendations()
│     │
│     ├─► Capa 1 (reglas determinísticas)
│     │     └─► detect_conflicts() [si hay pautas]
│     │
│     ├─► Capa 2 (análisis de patrones)
│     │     └─► extract_guidelines() [si mode="full"]
│     │
│     └─► Capa 3 (tendencias y benchmarks)
│
└─► [PASO 6] _render_report()
      • mode="executive" → 1 página
      • mode="quick"     → score + top 5 recomendaciones
      • mode="full"      → reporte completo multi-sección
```

---

## 11. Contrato de Output (modo "full")

```
════════════════════════════════════════════════════════════════════
  FIN INTELLIGENCE REVIEW — [PRODUCT]
  Período: [period_days] días | N=[n] conversaciones
  Score Global: [score]/100 — [nivel]
════════════════════════════════════════════════════════════════════

SECCIÓN 1 — DASHBOARD EJECUTIVO
[Tabla KPIs con semáforos]

SECCIÓN 2 — SCORE GLOBAL DESGLOSADO
[6 dimensiones con valores y pesos]

SECCIÓN 3 — DISTRIBUCIÓN POR INTENCIÓN
[Tabla top intenciones: frecuencia, escalación, frustración, churn]

SECCIÓN 4 — ANÁLISIS DE PAUTAS
[Cobertura, pautas muertas, pautas más activas, conflictos]

SECCIÓN 5 — ANÁLISIS DE KNOWLEDGE BASE
[Utilización, gaps, artículos faltantes]

SECCIÓN 6 — ANÁLISIS DE CONTEXTO OPERATIVO
[FUERA DE HORARIO, IACR, urgencia]

SECCIÓN 7 — RECOMENDACIONES PRIORIZADAS
[Capa 1: Inmediatas]
[Capa 2: Estructurales]
[Capa 3: Evolución]

SECCIÓN 8 — RESUMEN EJECUTIVO PARA PM
[Una sola pantalla: score, 3 KPIs críticos, top 3 acciones]
```

---

## 12. Diferencias vs Herramientas Existentes

| Dimensión | `architect_review()` | `fin_intelligence_review()` |
|-----------|---------------------|----------------------------|
| **Unidad de análisis** | Repositorio de pautas | Ecosistema completo de FIN |
| **Entradas** | Transcripts + pautas | Conversaciones estructuradas + KB + pautas |
| **Foco** | Calidad de pautas individuales | Performance del sistema como un todo |
| **Score** | Por pauta individual | Score único del sistema |
| **KPIs** | Cobertura funcional + mantenibilidad | Resolución, experiencia, diagnóstico, KB, eficiencia |
| **Recomendaciones** | Nuevas pautas y optimizaciones | Multi-capa: pautas + KB + workflows + atributos |
| **Reutilización** | Herramienta standalone | Orquesta herramientas existentes |
| **Audiencia** | Arquitecto de FIN | PM + Soporte + Arquitecto |

---

*FIN Architect — Fase 4 | Documento de arquitectura funcional*  
*Próximo paso: implementación una vez aprobado este diseño*
