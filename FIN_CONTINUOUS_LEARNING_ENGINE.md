# FIN Continuous Learning Engine — Arquitectura v1.0

*Blueprint oficial | FIN Architect Fase 6 | 2026-06-26*

---

## Índice

1. [Visión del Motor](#1-visión-del-motor)
2. [Detección de Patrones Nuevos](#2-detección-de-patrones-nuevos)
3. [Identificación de Intenciones No Cubiertas](#3-identificación-de-intenciones-no-cubiertas)
4. [Detección de Artículos Obsoletos o Poco Efectivos](#4-detección-de-artículos-obsoletos-o-poco-efectivos)
5. [Evaluación de Pautas Inactivas o con Resultados Negativos](#5-evaluación-de-pautas-inactivas-o-con-resultados-negativos)
6. [Evaluación de Atributos y Workflows en el Tiempo](#6-evaluación-de-atributos-y-workflows-en-el-tiempo)
7. [Medición de Tendencias Semanales y Mensuales](#7-medición-de-tendencias-semanales-y-mensuales)
8. [Sistema de Recomendaciones Automáticas Priorizadas](#8-sistema-de-recomendaciones-automáticas-priorizadas)
9. [Historial de Mejoras y Demostración de Evolución](#9-historial-de-mejoras-y-demostración-de-evolución)
10. [Métricas de Aprendizaje Continuo](#10-métricas-de-aprendizaje-continuo)
11. [El Ciclo de Mejora Continua](#11-el-ciclo-de-mejora-continua)
12. [Arquitectura de Datos del Motor](#12-arquitectura-de-datos-del-motor)

---

## 1. Visión del Motor

### Qué es

El FIN Continuous Learning Engine (CLE) es la capa de inteligencia evolutiva de FIN Architect Enterprise. Mientras las herramientas existentes (architect_review, fin_intelligence_review, etc.) analizan un estado puntual del ecosistema, el CLE analiza el **cambio en el tiempo**: qué está apareciendo que antes no existía, qué está dejando de funcionar, qué señales débiles se están convirtiendo en problemas estructurales.

No reemplaza las auditorías. Las convierte en insumo de un proceso iterativo y acumulativo.

### Qué problema resuelve

Un ecosistema de FIN sin aprendizaje continuo degenera. Las pautas diseñadas para el producto de hace 6 meses no cubren las funcionalidades lanzadas hoy. Los artículos escritos para los usuarios de hace un año no reflejan el lenguaje de los usuarios actuales. Los workflows diseñados en la fase inicial no anticiparon los escenarios que emergieron después.

Sin un motor de aprendizaje, el equipo opera reactivamente: corrige después de que el problema ya afectó a cientos de usuarios. Con el CLE, el equipo opera proactivamente: detecta la señal antes de que se convierta en patrón, actúa antes de que el patrón genere daño.

### Principio fundamental

> El ecosistema de FIN es un sistema vivo. El CLE es su sistema inmunológico: detecta anomalías, genera respuesta y desarrolla memoria para no repetir el error.

### Diferencia vs las herramientas existentes

| Dimensión | Herramientas existentes | FIN CLE |
|-----------|------------------------|---------|
| Horizonte temporal | Un período puntual | Múltiples períodos comparados |
| Tipo de análisis | Estado actual | Cambio y tendencia |
| Señales que detecta | Problemas manifiestos | Señales débiles emergentes |
| Acción | Recomendación para hoy | Plan de aprendizaje para el sistema |
| Memoria | Sin estado entre ejecuciones | Memoria acumulativa persistente |
| Aprendizaje | Ninguno — análisis siempre fresco | Cada ciclo enriquece el siguiente |

---

## 2. Detección de Patrones Nuevos en Conversaciones

### Definición de patrón nuevo

Un patrón nuevo es cualquier combinación de señales en las conversaciones recientes que no aparecía en el período de referencia anterior. Puede ser:

- Una intención que emerge con frecuencia creciente
- Un tipo de error de FIN que aparece por primera vez
- Una combinación de atributos que no se había visto antes
- Un comportamiento del usuario (ej. solicitar agente en el turno 2 sistemáticamente) que es nuevo

### Mecanismo de detección

**Paso 1 — Fingerprinting de conversación**

Cada conversación procesada por el CLE genera un "fingerprint" estructurado que captura sus señales clave:

```
Fingerprint = {
  intencion:         AI Title normalizado
  resultado:         escalated | confirmed | assumed
  error_principal:   categoría del error detectado
  patron_solicitud:  [turno en que pidió agente, veces que lo pidió]
  patron_frustracion: [nivel, turno pico]
  atributos:         {iacr, urgencia, emociones, fuera_horario}
  pautas:            set de IDs activados
  kb:                set de artículos usados
  partes:            número de turnos
}
```

**Paso 2 — Clustering incremental**

El CLE agrupa los fingerprints del período actual en clusters usando similitud estructural (no embeddings de texto — solo similitud de campos). Un cluster es un grupo de conversaciones con fingerprints similares.

Algoritmo de similitud entre dos fingerprints:
```
similitud(A, B) =
  (intencion_match × 0.30) +
  (resultado_match × 0.20) +
  (error_match × 0.20) +
  (atributos_similares × 0.15) +
  (patron_solicitud_similar × 0.10) +
  (pautas_jaccard × 0.05)
```

Un par con similitud > 0.70 pertenece al mismo cluster.

**Paso 3 — Comparación vs período de referencia**

Para cada cluster del período actual, el CLE busca si existe un cluster equivalente en el período de referencia (semana anterior, mes anterior, o baseline histórico).

- **Cluster existente:** No es patrón nuevo. Se registra si creció (tendencia positiva) o encogió (tendencia negativa).
- **Cluster nuevo:** Es un patrón emergente. Se registra con la fecha de primera aparición, tamaño inicial y tasa de crecimiento.
- **Cluster desaparecido:** Era un patrón que ya no ocurre. Puede indicar que una mejora funcionó o que cambió el tipo de usuarios.

**Paso 4 — Clasificación del patrón nuevo**

Cada patrón nuevo detectado se clasifica automáticamente por:

| Dimensión | Valores posibles |
|-----------|-----------------|
| Urgencia | Inmediata / Emergente / Latente |
| Tipo | Intención nueva / Error nuevo / Comportamiento nuevo / Combinación de atributos nueva |
| Cobertura actual | Cubierto / Parcialmente cubierto / Sin cobertura |
| Tendencia | Creciente / Estable / Decreciente |
| Señal asociada | Frustración / Escalación / Churn / Rating bajo |

**Paso 5 — Umbral de señal vs ruido**

No todo patrón nuevo es relevante. El CLE aplica un umbral mínimo para reportar un patrón como emergente:

- Frecuencia mínima: ≥ 3 conversaciones en el período
- Tasa de crecimiento: ≥ 50% respecto al período anterior (o primera aparición)
- Señal negativa asociada: al menos uno de {escalación, frustración > 60, churn_risk > 50}

Patrones que no superen estos umbrales se registran en el log de señales débiles pero no generan alerta activa.

---

## 3. Identificación de Intenciones No Cubiertas por la KB

### Qué significa "no cubierta"

Una intención no está cubierta por la KB cuando el usuario expresa una necesidad operativa para la cual no existe artículo publicado que FIN pueda usar como fuente de respuesta. El resultado típico es que FIN responde desde el prompt base o desde pautas generales, sin citar conocimiento validado — lo que aumenta el riesgo de respuesta incorrecta o incompleta.

### Flujo de identificación

**Etapa 1 — Extracción del universo de intenciones**

El CLE construye el universo de intenciones del período a partir de:
- El atributo `AI Title` de cada conversación (intención clasificada por FIN)
- Los temas detectados en transcripts de conversaciones donde `AI Title` es nulo
- Los temas de las conversaciones de alto volumen aunque tengan AI Title

**Etapa 2 — Cruce con KB disponible**

Para cada intención del universo, el CLE verifica:

```
tiene_cobertura_kb = ¿existe al menos un artículo publicado cuyo título o descripción
                      contiene palabras clave de la intención?

fin_lo_uso = ¿FIN usó un artículo de KB en al menos el 30% de conversaciones
              de esa intención?

articulo_pertinente = ¿el artículo usado es el más específico disponible,
                       o FIN usó un artículo genérico cuando existía uno específico?
```

**Etapa 3 — Clasificación de cobertura**

| Estado | Condición | Acción del CLE |
|--------|-----------|----------------|
| Cobertura completa | `tiene_cobertura_kb = true AND fin_lo_uso ≥ 30%` | Registrar como cubierta. Monitorear utilización. |
| Cobertura disponible sin uso | `tiene_cobertura_kb = true AND fin_lo_uso < 30%` | Alerta: artículo existe pero FIN no lo usa. Revisar configuración de content sources. |
| Cobertura parcial | `tiene_cobertura_kb = true AND articulo_pertinente = false` | Alerta: FIN usa artículo genérico. Crear artículo específico. |
| Sin cobertura | `tiene_cobertura_kb = false` | Brecha de KB. Priorizar creación de artículo. |

**Etapa 4 — Priorización de brechas**

Las intenciones sin cobertura se priorizan por:

```
Prioridad_brecha = (frecuencia × 0.40) + (escalacion_rate × 0.30) +
                   (frustration_avg / 100 × 0.20) + (churn_risk_avg / 100 × 0.10)
```

Las 10 intenciones con mayor prioridad_brecha se incluyen en el reporte semanal del CLE con propuesta de título y estructura para el artículo faltante.

**Etapa 5 — Seguimiento de brechas en el tiempo**

Cada brecha identificada entra al registro histórico del CLE con:
- Fecha de primera detección
- Frecuencia acumulada de conversaciones afectadas
- Estado: Pendiente / En creación / Publicado / Resuelto
- Fecha de resolución (cuando se publica el artículo)
- Impacto post-resolución (¿FIN usó el artículo? ¿bajó la escalación de esa intención?)

---

## 4. Detección de Artículos Obsoletos o Poco Efectivos

### Definición de obsolescencia y baja efectividad

**Obsoleto:** Un artículo es obsoleto cuando el contenido que describe ya no corresponde al estado actual del producto (funcionalidad modificada, proceso cambiado, pantalla rediseñada). La obsolescencia es silenciosa: el artículo se ve publicado y activo, pero la información que contiene lleva al usuario al error.

**Poco efectivo:** Un artículo es poco efectivo cuando está disponible, FIN lo usa, pero su uso no mejora el resultado de la conversación (la conversación igual termina escalada, con frustración alta, o con el usuario sin resolver).

### Señales de obsolescencia

El CLE no lee el contenido de los artículos (eso requeriría procesamiento de texto costoso). En su lugar, detecta señales indirectas:

| Señal | Cómo se detecta | Interpretación |
|-------|----------------|----------------|
| **Artículo usado → conversación escalada igualmente** | `kb_article_id` presente en conversación con `ai_state=escalated` | El artículo no resolvió. Puede ser obsoleto o irrelevante. |
| **Artículo usado → frustración no disminuye** | `kb_article_id` presente en conversación con `frustration_score > 65` | El artículo no tranquilizó ni orientó al usuario. |
| **Artículo usado → usuario repite la pregunta** | El mismo topic aparece en > 2 turnos del usuario después de que FIN citó el artículo | El usuario no encontró la respuesta en el artículo. |
| **Artículo con fecha de actualización > 6 meses** | `updated_at` del knowledge_inventory | Posible obsolescencia por cambio de producto. Cruzar con frecuencia de uso y resultado. |
| **Artículo usado en intención equivocada** | La intención de la conversación no coincide con el título/descripción del artículo | FIN está usando el artículo de manera incorrecta, lo que sugiere que el artículo no está bien posicionado. |

### Índice de Efectividad de Artículo (IEA)

El CLE calcula un IEA por artículo en cada período:

```
IEA = (conversaciones_resueltas_con_articulo / total_conversaciones_con_articulo) × 100

donde "resueltas" = ai_state = confirmed_resolution
```

Clasificación:

| IEA | Estado | Acción |
|-----|--------|--------|
| ≥ 70 | Efectivo | Mantener. Monitorear. |
| 40–69 | Moderado | Investigar por qué no resuelve siempre. |
| 20–39 | Poco efectivo | Revisar contenido. Posible obsolescencia. |
| < 20 | Inefectivo | Candidato a revisión urgente o retirada. |

### Artículos sin uso

Artículos publicados que FIN no ha usado en el período de análisis se clasifican en dos tipos:

1. **No conectados:** FIN no tiene acceso a ellos en su configuración de content sources. Acción: revisar configuración de FIN.
2. **Irrelevantes para el período:** La intención que cubren no apareció en el período. No es un problema — es contexto. Se monitorea si permanece así por > 3 períodos.

### Protocolo de alerta de obsolescencia

Cuando un artículo tiene IEA < 20 durante 2 períodos consecutivos Y tiene fecha de actualización > 4 meses, el CLE genera una alerta de revisión prioritaria. La alerta incluye:
- ID y título del artículo
- Número de conversaciones afectadas
- Ejemplos de conversaciones donde el artículo falló
- Fecha de última actualización
- Propuesta: revisar contenido / reescribir / retirar / reemplazar por nuevo artículo

---

## 5. Evaluación de Pautas Inactivas o con Resultados Negativos

### Ciclo de vida de una pauta

```
CREADA → ACTIVA → [EFECTIVA | POCO EFECTIVA | INACTIVA | CONFLICTIVA] → REVISIÓN → [AJUSTADA | DEPRECADA]
```

El CLE rastrea cada pauta a lo largo de su ciclo de vida completo.

### Pautas inactivas

**Definición:** Una pauta inactiva es aquella que nunca se activa en el período de análisis. No aparece en ningún `fin_guidance_applied` event.

**Causas posibles:**
1. La condición de activación es demasiado específica y ese escenario no ocurrió
2. La condición de activación tiene un error — siempre evalúa como falsa
3. La pauta fue diseñada para un escenario que ya no existe (producto cambiado)
4. La pauta está siendo bloqueada por otra pauta con mayor prioridad

**Clasificación del CLE:**

| Períodos inactiva | Clasificación | Acción recomendada |
|-------------------|--------------|-------------------|
| 1 período | Temporal | Monitorear. Puede ser contexto del período. |
| 2–3 períodos | Latente | Revisar condición de activación. |
| 4+ períodos | Muerta | Candidata a deprecación o rediseño. |

### Pautas con resultados negativos

**Definición:** Una pauta genera resultados negativos cuando su activación correlaciona con peores resultados que su ausencia.

El CLE detecta esto comparando:

```
Para cada pauta P:
  grupo_con_P = conversaciones donde P se activó
  grupo_sin_P = conversaciones similares donde P no se activó

  delta_escalacion = escalation_rate(con_P) - escalation_rate(sin_P)
  delta_frustracion = avg_frustration(con_P) - avg_frustration(sin_P)
  delta_diagnostico = avg_calidad_diagnostico(con_P) - avg_calidad_diagnostico(sin_P)

  score_impacto_P = -(delta_escalacion × 0.40) - (delta_frustracion × 0.30) +
                     (delta_diagnostico × 0.30)
```

Si `score_impacto_P < -10`, la pauta está generando daño neto.

**Nota sobre correlación vs causalidad:** El CLE distingue entre pautas que se activan *en* conversaciones malas (correlación) y pautas que *generan* conversaciones malas (causalidad). Una pauta de escalamiento, por ejemplo, naturalmente se activa en conversaciones problemáticas. El CLE controla por esto usando el grupo de control (conversaciones similares sin la pauta).

### Pautas sobreutilizadas

Una pauta que se activa en > 80% de conversaciones puede estar siendo demasiado genérica — se activa siempre, no aporta diferenciación. El CLE la marca para revisión de especificidad.

### Pautas en conflicto persistente

Si `detect_conflicts` identifica el mismo par de pautas en conflicto en > 3 períodos consecutivos sin que ninguna haya sido modificada, el CLE marca ese conflicto como "deuda técnica estructural" y lo escala en prioridad de la recomendación.

---

## 6. Evaluación de Atributos y Workflows en el Tiempo

### Evaluación de atributos

**Dimensiones de evaluación:**

**6.1 Consistencia de detección**

El CLE compara la tasa de detección del mismo atributo entre períodos equivalentes (mismas intenciones, mismo volumen):

```
consistencia(attr, periodo_actual, periodo_anterior) =
  |detection_rate_actual - detection_rate_anterior| < 0.10
```

Una caída de detección > 10% sin cambio de volumen indica que algo en la configuración de FIN cambió — o que el flujo conversacional cambió y el atributo ya no se está completando.

**6.2 Poder discriminante**

Un atributo tiene poder discriminante si su valor predice de manera significativa el resultado de la conversación:

```
poder_discriminante(attr, valor_X) =
  |escalation_rate(attr=X) - escalation_rate(attr≠X)|
```

Si el poder discriminante de un atributo cae por debajo de 5% durante 3 períodos, el atributo ya no diferencia comportamientos — puede haber perdido relevancia o estar siendo completado de manera inconsistente.

**6.3 Evolución de distribución de valores**

El CLE registra la distribución de valores de cada atributo por período. Un cambio significativo en la distribución (ej. IACR=Riesgo Operativo sube del 20% al 45%) es una señal de cambio en el tipo de conversaciones — puede reflejar un incidente de producto, un cambio en el perfil de clientes, o un ajuste en la lógica de clasificación.

---

### Evaluación de workflows

**6.4 Tasa de completitud de flujo**

```
completitud(workflow_W) =
  conversaciones_que_completan_flujo_W / total_conversaciones_en_workflow_W
```

Una completitud < 60% indica que muchos usuarios abandonan el flujo antes de llegar al nodo de resolución. El CLE registra en qué nodo ocurre el abandono más frecuentemente.

**6.5 Tasa de derivación inesperada**

Conversaciones que entran por el flujo A pero terminan siendo atendidas como si pertenecieran al flujo B. Indica que el nodo de entrada del flujo no captura bien la intención del usuario.

**6.6 Índice de redireccionamiento**

Número promedio de veces que un usuario es re-dirigido dentro o entre flujos en una conversación. Un índice > 1.5 indica fricción de diseño conversacional.

**6.7 Tendencia de efectividad por workflow**

El CLE calcula la tasa de resolución por workflow en cada período y trazas la tendencia:

```
tendencia_workflow(W, n_periodos) =
  regresión lineal de resolution_rate(W) en los últimos n períodos
```

Pendiente negativa sostenida (> 3 períodos) → el workflow está degradando. Requiere revisión.

**6.8 Nuevas intenciones sin workflow dedicado**

Si una intención nueva (detectada en Sección 2) supera un volumen de 10 conversaciones sin tener un workflow específico, el CLE genera una alerta de brecha de workflow.

---

## 7. Medición de Tendencias Semanales y Mensuales

### Estructura temporal del CLE

El CLE opera en tres horizontes temporales simultáneos:

```
HORIZONTE CORTO:  Semana actual vs semana anterior
HORIZONTE MEDIO:  Mes actual vs mes anterior
HORIZONTE LARGO:  Trimestre actual vs trimestre anterior (o vs baseline)
```

Cada KPI del sistema se mide en los tres horizontes.

### Tipos de tendencia

**Tendencia de primer orden:** Dirección del cambio (sube / baja / estable).  
**Tendencia de segundo orden:** Aceleración del cambio (¿está subiendo más rápido o frenando?).  
**Tendencia estructural:** Patrón que se repite consistentemente en el mismo período (ej. el FIS siempre cae los lunes porque el volumen de conversaciones fuera de horario del fin de semana entra ese día).

### Indicadores de tendencia del CLE

Para cada KPI, el CLE calcula:

| Indicador | Cálculo | Interpretación |
|-----------|---------|---------------|
| `delta_absoluto` | `valor_actual - valor_anterior` | Cambio en puntos o porcentaje |
| `delta_relativo` | `(valor_actual - valor_anterior) / valor_anterior × 100` | Cambio porcentual |
| `velocidad` | Promedio de `delta_absoluto` en los últimos 4 períodos | Ritmo de cambio sostenido |
| `aceleracion` | `velocidad_actual - velocidad_anterior` | ¿El cambio se está acelerando o frenando? |
| `proyeccion_4periodos` | `valor_actual + (velocidad × 4)` | Dónde estará el KPI en 4 períodos si continúa la tendencia |
| `distancia_al_target` | `target - valor_actual` | Cuánto falta para llegar al objetivo |
| `periodos_para_target` | `distancia_al_target / velocidad` | A este ritmo, cuándo se llegaría al target |

### Señales de alerta de tendencia

El CLE activa alertas de tendencia cuando:

| Condición | Tipo de alerta |
|-----------|---------------|
| FIS cae > 5 puntos en una semana | Degradación aguda |
| FIS cae > 2 puntos por 3 semanas consecutivas | Degradación sostenida |
| Tasa de escalación sube > 10pp en un mes | Deterioro operacional |
| Frustración promedio sube > 15 puntos en un mes | Deterioro de experiencia |
| Un KPI que estaba en 🟢 pasa a 🔴 directamente | Ruptura de umbral |
| La proyección a 4 períodos de cualquier KPI crítico cruza un hard cap | Alerta preventiva |

### Estacionalidad y contexto

El CLE mantiene un registro de factores contextuales que pueden explicar variaciones sin que sean señales de degradación:

- **Fin de mes:** Mayor volumen de consultas de facturación y cuadre de caja
- **Inicio de período fiscal:** Mayor volumen de configuración y onboarding
- **Actualizaciones de producto:** Picos de consultas sobre funcionalidades nuevas
- **Feriados:** Menor volumen, pero mayor proporción de FUERA DE HORARIO

Cuando una variación ocurre en un contexto marcado por un factor conocido, el CLE la anota como "variación contextual explicada" en lugar de "señal de degradación".

---

## 8. Sistema de Recomendaciones Automáticas Priorizadas por Impacto

### Principio de priorización

No todas las mejoras valen lo mismo. El CLE prioriza por impacto esperado en el FIN Intelligence Score, no por urgencia subjetiva ni por facilidad de implementación. La facilidad se usa como desempate, nunca como criterio primario.

### Modelo de impacto esperado

Para cada recomendación R, el CLE estima su impacto en el FIS:

```
impacto_esperado(R) =
  delta_D1 × 0.25 +   # impacto en Resolución
  delta_D2 × 0.25 +   # impacto en Experiencia
  delta_D3 × 0.20 +   # impacto en Diagnóstico
  delta_D4 × 0.15 +   # impacto en Conocimiento
  delta_D5 × 0.10 +   # impacto en Pautas
  delta_D6 × 0.05     # impacto en Eficiencia

donde cada delta_Di es el cambio estimado en esa dimensión si se implementa R
```

Los deltas se estiman a partir del comportamiento histórico: si una recomendación similar fue implementada en el pasado, el CLE usa el impacto real observado como base.

### Pipeline de generación de recomendaciones

```
FUENTE DE SEÑAL          ANÁLISIS CLE            RECOMENDACIÓN GENERADA
──────────────────────────────────────────────────────────────────────────
Patrón nuevo detectado → Clasificación           → Nueva pauta sugerida
                       → Estimación de impacto   → Borrador de pauta
                       → Cálculo de prioridad    → Instrucción de implementación

Intención sin KB       → Frecuencia acumulada    → Nuevo artículo sugerido
                       → Intenciones relacionadas → Estructura propuesta del artículo
                       → Impacto en TUK, RBK     → Prioridad editorial

Artículo inefectivo    → IEA del artículo        → Revisión de contenido
                       → Conversaciones fallidas  → Ejemplos de dónde falla
                       → Alternativas disponibles → Artículo alternativo sugerido

Pauta muerta           → Períodos inactiva        → Revisar condición / deprecar
                       → Escenario que debía cubrir → Pauta alternativa o fusionada

Workflow degradado     → Nodo de quiebre          → Rediseñar nodo específico
                       → Intención sin workflow   → Nuevo workflow propuesto

Tendencia negativa     → KPIs en caída            → Plan de intervención urgente
                       → Causa raíz probable      → Acción específica por causa
```

### Scoring de recomendaciones

Cada recomendación se puntúa con 4 dimensiones:

```
score_recomendacion = (impacto_fis × 0.50) +
                      (urgencia_temporal × 0.25) +
                      (confianza_estimacion × 0.15) +
                      (facilidad_implementacion × 0.10)
```

Donde:
- `impacto_fis`: puntos estimados de mejora en FIS (0–10+)
- `urgencia_temporal`: 4=crítico, 3=esta semana, 2=este mes, 1=cuando se pueda
- `confianza_estimacion`: 1.0=basada en caso histórico, 0.7=basada en patrón similar, 0.4=estimación teórica
- `facilidad_implementacion`: 1.0=< 1 hora, 0.7=horas, 0.4=días, 0.1=semanas

### Agrupación por sprint de trabajo

El CLE no solo genera una lista priorizada — agrupa las recomendaciones en sprints de trabajo accionables:

**Sprint Inmediato (hoy / mañana):**
- Máximo 3 acciones
- Total de esfuerzo estimado: ≤ 4 horas
- Solo recomendaciones con `urgencia_temporal = 4` o `impacto_fis > 7`

**Sprint Semanal:**
- Máximo 5 acciones
- Total de esfuerzo estimado: ≤ 1 día de trabajo
- Recomendaciones con `score_recomendacion` en el top 5 del período

**Sprint Mensual:**
- Lista completa de mejoras estructurales del mes
- Incluye deuda técnica y conversacional acumulada
- Ordenada por impacto total acumulado

---

## 9. Historial de Mejoras y Demostración de Evolución

### Por qué el historial es estratégico

El historial de mejoras no es solo un log de cambios. Es la evidencia de que FIN Architect genera valor real. Permite:

1. Demostrar ROI al Director de Soporte y al PM
2. Calibrar las estimaciones de impacto futuras con datos reales
3. Evitar repetir errores ("esta pauta ya se intentó y no funcionó porque...")
4. Identificar qué tipos de mejora tienen mayor impacto real vs estimado

### Estructura del registro de mejora

Cada mejora implementada queda registrada en el historial del CLE con:

```
Mejora {
  id:                    UUID único
  fecha_recomendacion:   cuándo el CLE la generó
  fecha_implementacion:  cuándo se implementó
  tipo:                  Pauta | Artículo KB | Atributo | Workflow | Prompt
  descripcion:           qué se hizo exactamente
  impacto_estimado_fis:  puntos FIS estimados al momento de recomendar
  impacto_real_fis:      puntos FIS reales medidos 30 días después
  precision_estimacion:  |estimado - real| / estimado (qué tan precisa fue la estimación)
  kpis_afectados: {
    escalation_rate:     {antes, despues, delta}
    frustration_avg:     {antes, despues, delta}
    resolution_rate:     {antes, despues, delta}
    calidad_diagnostico: {antes, despues, delta}
    kb_utilization:      {antes, despues, delta}
  }
  conversaciones_impactadas: N
  estado:                Exitosa | Neutral | Contraproducente | Pendiente medicion
  notas:                 contexto adicional
}
```

### Ventana de medición de impacto

El impacto de una mejora no se puede medir de inmediato. El CLE usa una ventana de medición de 30 días: compara las métricas de las 4 semanas posteriores a la implementación vs las 4 semanas anteriores.

Para mejoras de KB (nuevos artículos), la ventana es de 21 días: los artículos tardan menos en mostrar impacto porque FIN los empieza a usar de inmediato.

Para mejoras de workflow, la ventana es de 45 días: los cambios estructurales de flujo tardan más en mostrar su impacto real.

### Dashboard de evolución

El CLE mantiene un dashboard de evolución que muestra:

**Línea de tiempo del FIN Intelligence Score**
```
FIS
100 │
 80 │           ╭──────────────────────────╮
 70 │      ╭────╯   ↑ Pauta nueva          ╰──────────
 60 │  ╭───╯      ↑ Artículo KB          ↑ Workflow
 50 │──╯                                 ajustado
    └────────────────────────────────────────────────►
    Sem1  Sem4   Sem8   Sem12   Sem16   Sem20   Sem24
```

**Tabla de ROI por tipo de mejora (acumulado)**

| Tipo | Mejoras implementadas | FIS ganado | Horas invertidas | FIS/hora |
|------|----------------------|------------|-----------------|---------|
| Pautas nuevas | 12 | +18 pts | 24h | 0.75 |
| Artículos KB | 8 | +11 pts | 16h | 0.69 |
| Ajuste workflows | 3 | +7 pts | 12h | 0.58 |
| Nuevos atributos | 2 | +4 pts | 6h | 0.67 |

**Matriz de precisión de estimaciones**

Muestra qué tan bien el CLE estima el impacto de sus propias recomendaciones. Si la precisión es baja (estimaciones muy distintas de los resultados reales), el modelo de estimación necesita recalibrarse.

### Memoria de patrones resueltos

El CLE mantiene una memoria de patrones que ya fueron abordados por una mejora. Cuando detecta un patrón que ya fue resuelto en el pasado, verifica si la solución anterior sigue activa. Si la solución fue revertida o el patrón reapareció, lo marca como "recurrente" — una señal de que la solución no fue suficientemente profunda.

---

## 10. Métricas de Aprendizaje Continuo

El CLE almacena un conjunto de métricas propias — no de FIN, sino del motor de aprendizaje mismo. Estas métricas permiten evaluar si el CLE está funcionando bien y mejorando con el tiempo.

### Métricas de Detección

| Métrica | Qué mide | Unidad |
|---------|---------|--------|
| `patrones_detectados_periodo` | Cuántos patrones nuevos identificó el CLE en el período | entero |
| `patrones_verdaderos_positivos` | De los patrones detectados, cuántos resultaron en una mejora exitosa | entero |
| `patrones_falsos_positivos` | Patrones detectados que resultaron ser ruido o no accionables | entero |
| `precision_deteccion` | `verdaderos_positivos / (verdaderos_positivos + falsos_positivos)` | % |
| `senales_debiles_capturadas` | Patrones que estaban por debajo del umbral pero fueron registrados | entero |
| `tiempo_hasta_alerta` | Días desde primera aparición de un patrón hasta que el CLE lo reporta | días |

### Métricas de Cobertura de Análisis

| Métrica | Qué mide | Unidad |
|---------|---------|--------|
| `conversaciones_analizadas` | Total de conversaciones procesadas en el período | entero |
| `cobertura_fingerprinting` | % de conversaciones con fingerprint completo | % |
| `intenciones_cubiertas_analisis` | % de intenciones del período con análisis de cobertura KB | % |
| `pautas_evaluadas` | % del repositorio evaluado en el período | % |
| `atributos_evaluados` | % de atributos con evaluación de consistencia | % |
| `workflows_evaluados` | % de workflows con evaluación de efectividad | % |

### Métricas de Recomendaciones

| Métrica | Qué mide | Unidad |
|---------|---------|--------|
| `recomendaciones_generadas` | Total de recomendaciones producidas en el período | entero |
| `recomendaciones_implementadas` | De las generadas, cuántas se implementaron | entero |
| `tasa_implementacion` | `implementadas / generadas` | % |
| `tiempo_hasta_implementacion` | Días promedio desde recomendación hasta implementación | días |
| `impacto_estimado_total` | Suma de FIS estimado de todas las mejoras del período | puntos |
| `impacto_real_total` | Suma de FIS real medido de las mejoras implementadas | puntos |
| `precision_impacto` | `1 - |estimado - real| / estimado` | % |

### Métricas de Calidad del Motor

| Métrica | Qué mide | Unidad |
|---------|---------|--------|
| `patrones_nuevos_periodo` | Velocidad de descubrimiento de nuevos patrones | entero/período |
| `brechas_resueltas_acumuladas` | Total de brechas de KB cerradas desde el inicio | entero |
| `deuda_conversacional_acumulada` | Patrones recurrentes no resueltos por > 3 períodos | entero |
| `vida_util_recomendacion` | Cuántos períodos sigue siendo relevante una recomendación no implementada | períodos |
| `recurrencia_patron` | % de patrones detectados que ya aparecieron antes | % |
| `mejoras_contraproducentes` | Mejoras implementadas que empeoraron las métricas | entero |

### Métricas de Memoria del Sistema

| Métrica | Qué mide | Unidad |
|---------|---------|--------|
| `clusters_en_memoria` | Total de clusters históricos almacenados | entero |
| `brechas_kb_en_registro` | Total de brechas de KB rastreadas (abiertas + cerradas) | entero |
| `pautas_deprecadas_acumuladas` | Total de pautas marcadas para deprecación | entero |
| `mejoras_en_historial` | Total de mejoras registradas con medición de impacto | entero |
| `periodos_de_datos_disponibles` | Ventana histórica del sistema | períodos |
| `factores_contextuales_registrados` | Factores estacionales o contextuales conocidos | entero |

---

## 11. El Ciclo de Mejora Continua

El CLE no es un análisis que se ejecuta y termina. Es un ciclo que se repite indefinidamente, enriqueciéndose con cada vuelta.

### El Ciclo Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                      FIN CONTINUOUS LEARNING CYCLE                         │
│                                                                             │
│   ┌──────────────┐                                          ┌────────────┐ │
│   │  OBSERVAR    │                                          │  MEDIR     │ │
│   │              │                                          │            │ │
│   │ • Nuevas     │◄─────────── CICLO SEMANAL ─────────────►│ • Impacto  │ │
│   │   conversac. │                                          │   real     │ │
│   │ • Nuevos     │                                          │ • FIS      │ │
│   │   patrones   │                                          │   actual   │ │
│   │ • Anomalías  │                                          │ • Tendencia│ │
│   └──────┬───────┘                                          └─────┬──────┘ │
│          │                                                        │        │
│          ▼                                                        ▲        │
│   ┌──────────────┐                                          ┌─────┴──────┐ │
│   │  ANALIZAR    │                                          │  APRENDER  │ │
│   │              │                                          │            │ │
│   │ • Fingerprint│                                          │ • Actualiz.│ │
│   │ • Clustering │                                          │   modelos  │ │
│   │ • Comparar   │                                          │ • Calibrar │ │
│   │   vs histor. │                                          │   estimac. │ │
│   │ • Tendencias │                                          │ • Registrar│ │
│   └──────┬───────┘                                          │   en memo. │ │
│          │                                                  └─────┬──────┘ │
│          ▼                                                        ▲        │
│   ┌──────────────┐                                          ┌─────┴──────┐ │
│   │  RECOMENDAR  │                                          │  VALIDAR   │ │
│   │              │          ┌─────────────────┐            │            │ │
│   │ • Priorizar  │─────────►│   IMPLEMENTAR   │───────────►│ • 30 días  │ │
│   │ • Estimar    │          │                 │            │   después  │ │
│   │   impacto    │          │ Administrador   │            │ • Delta vs │ │
│   │ • Sprint     │          │ Intercom        │            │   estimado │ │
│   │   sugerido   │          │ ejecuta cambios │            │ • Exitosa? │ │
│   └──────────────┘          └─────────────────┘            └────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Descripción de cada fase del ciclo

**OBSERVAR (automático, continuo)**  
El CLE ingiere las conversaciones del período. Construye fingerprints. Detecta patrones nuevos. Evalúa artículos, pautas y workflows. Registra señales débiles. No genera recomendaciones todavía.

**ANALIZAR (automático, semanal)**  
Compara el período actual vs histórico. Calcula tendencias. Identifica brechas. Evalúa impacto de cambios anteriores. Prepara insumos para las recomendaciones.

**RECOMENDAR (automático, semanal)**  
Genera las recomendaciones priorizadas. Calcula el impacto estimado de cada una. Agrupa en sprints de trabajo. Entrega el reporte al equipo.

**IMPLEMENTAR (humano, según sprint)**  
El Administrador Intercom o el Arquitecto Conversacional implementa las mejoras recomendadas. Registra la implementación en el historial del CLE.

**VALIDAR (automático, 30 días después)**  
El CLE mide el impacto real de la mejora implementada. Compara con el estimado. Registra en el historial. Actualiza los modelos de estimación si la precisión fue baja.

**APRENDER (automático, al final de cada ciclo)**  
El CLE actualiza su memoria: nuevos patrones resueltos, nuevos factores contextuales registrados, calibración del modelo de estimación de impacto. El próximo ciclo parte de un sistema más informado que el anterior.

### Frecuencia del ciclo

| Fase | Frecuencia | Duración estimada |
|------|-----------|-------------------|
| OBSERVAR | Continuo (procesamiento diario) | Automático |
| ANALIZAR | Semanal | 2–3 minutos automáticos |
| RECOMENDAR | Semanal (lunes) | 3–5 minutos automáticos |
| IMPLEMENTAR | Según sprint (días o semanas) | Según esfuerzo de cada mejora |
| VALIDAR | 30 días post-implementación | Automático |
| APRENDER | Al final de cada ciclo semanal | Automático |

### El ciclo de maduración del sistema

El CLE mejora con el tiempo. En las primeras semanas, las estimaciones de impacto son teóricas (confianza 0.4). A medida que se acumula historial de mejoras implementadas y validadas, las estimaciones se vuelven empíricas (confianza 0.7–1.0).

```
Semanas 1–4:   Modo calibración. El CLE aprende el ecosistema.
               Las recomendaciones son tentativas.
               
Semanas 5–12:  Modo operacional básico. Primeros patrones estables.
               Las recomendaciones tienen base empírica parcial.
               
Semanas 13–26: Modo operacional avanzado. Historial de 25+ mejoras.
               Las estimaciones de impacto tienen precisión > 70%.
               
Semana 27+:    Modo experto. El sistema conoce el ecosistema mejor
               que ninguna persona individual. Puede predecir
               tendencias y recomendar preventivamente.
```

---

## 12. Arquitectura de Datos del Motor

### Estructuras de datos persistentes

El CLE requiere un conjunto de estructuras de datos que se mantienen entre ejecuciones. Estas estructuras son el "estado" del motor — su memoria.

**12.1 Registro de Fingerprints Históricos**

```
fingerprints_historicos = [
  {
    id:               UUID de la conversación
    periodo:          semana o mes del fingerprint
    intencion:        string normalizado
    resultado:        enum
    error_principal:  string categorizado
    atributos:        dict
    pautas:           set de IDs
    kb_articles:      set de IDs
    partes:           int
    frustration:      float
    churn_risk:       float
    cluster_id:       ID del cluster al que pertenece
  }
]
```

**12.2 Registro de Clusters**

```
clusters = [
  {
    id:               UUID del cluster
    primer_periodo:   cuando apareció por primera vez
    ultimo_periodo:   cuando se vio por última vez
    tamaño_historico: {periodo: cantidad de conversaciones}
    tendencia:        creciente | estable | decreciente | desaparecido
    estado:           nuevo | conocido | resuelto | recurrente
    mejora_asociada:  ID de la mejora que lo resolvió (si aplica)
    fingerprint_repr: fingerprint representativo del cluster
  }
]
```

**12.3 Registro de Brechas de KB**

```
brechas_kb = [
  {
    id:               UUID de la brecha
    intencion:        string de la intención sin cobertura
    primer_deteccion: fecha
    frecuencia_acum:  total de conversaciones afectadas
    prioridad:        float (calculada)
    estado:           pendiente | en_creacion | publicado | resuelto
    articulo_creado:  ID del artículo cuando se resuelve
    fecha_resolucion: fecha
    impacto_post:     {escalation_delta, frustration_delta}
  }
]
```

**12.4 Historial de Mejoras**

(Estructura completa definida en Sección 9)

**12.5 Estado de Pautas**

```
estado_pautas = {
  pauta_id: {
    periodos_activa:     lista de períodos donde se activó
    periodos_inactiva:   lista de períodos donde no se activó
    estado_ciclo_vida:   activa | latente | muerta | deprecada
    score_impacto_hist:  lista de {periodo, score_impacto}
    conflictos_activos:  lista de IDs de pautas en conflicto
    recomendacion_pend:  ID de recomendación pendiente si la hay
  }
}
```

**12.6 Factores Contextuales**

```
factores_contextuales = [
  {
    nombre:          "Fin de mes"
    descripcion:     "Aumento en consultas de facturación y cuadre de caja"
    patron_temporal: {semana_del_mes: [4, 5], dia_semana: null}
    kpis_afectados:  ["conversation_volume", "escalation_rate"]
    magnitud_tipica: {escalation_rate: +0.08, volume: +0.30}
  }
]
```

**12.7 Modelos de Estimación Calibrados**

```
modelos_estimacion = {
  "nueva_pauta": {
    impacto_base_fis:      3.5,   # promedio histórico de pautas nuevas
    varianza:              2.1,
    casos_en_historia:     12,
    precision_estimaciones: 0.68
  },
  "nuevo_articulo_kb": {
    impacto_base_fis:      2.8,
    varianza:              1.4,
    casos_en_historia:     8,
    precision_estimaciones: 0.74
  },
  ...
}
```

### Volumen estimado de datos

| Estructura | Tamaño inicial | Crecimiento semanal | Tamaño a 1 año |
|------------|---------------|--------------------|----|
| Fingerprints | 25 registros | ~50/semana | ~2,600 registros |
| Clusters | 10 clusters | ~5/semana | ~260 clusters |
| Brechas KB | 15 brechas | ~3/semana | ~156 brechas |
| Historial mejoras | 0 | ~5/semana | ~260 mejoras |
| Estado pautas | 1 registro/pauta | Estable | ~100 registros |

Volumen total a 1 año: manejable en archivos JSON locales. No requiere base de datos externa.

---

*FIN Continuous Learning Engine — Blueprint Oficial v1.0*  
*Fase 6 | FIN Architect Enterprise | 2026-06-26*
