# FIN Architect Enterprise — Manual Oficial de Operación

**Versión:** 1.0  
**Fecha:** 27 de junio de 2026  
**Aplica a:** FIN Architect Enterprise v1.0 Beta en adelante  
**Audiencia:** Equipo de soporte y operaciones CX de Loggro  
**Referencia arquitectónica:** `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md`

---

## Índice

1. [Objetivo](#1-objetivo)
2. [Ciclo Semanal](#2-ciclo-semanal)
3. [KPIs Obligatorios](#3-kpis-obligatorios)
4. [Criterios de Priorización](#4-criterios-de-priorización)
5. [Gobierno del Cambio](#5-gobierno-del-cambio)
6. [Historial de Mejoras](#6-historial-de-mejoras)
7. [Cierre Semanal](#7-cierre-semanal)
8. [Filosofía Operacional](#8-filosofía-operacional)

---

## 1. Objetivo

FIN Architect Enterprise es la plataforma operacional que permite al equipo de soporte de Loggro supervisar, evaluar y mejorar de forma continua el comportamiento del agente de IA **Lia**, que opera sobre Intercom en los productos Restobar, Pymes, Nómina y Alojamientos.

### 1.1 Propósito operativo

El propósito de este manual es estandarizar el proceso semanal de operación del sistema. Su uso correcto garantiza que:

- Cada semana se analice evidencia real de conversaciones, no percepciones ni intuiciones.
- Las mejoras a pautas, workflows, atributos y artículos KB se realicen con criterios objetivos y trazables.
- El impacto de cada cambio se mida y registre para alimentar el ciclo de aprendizaje del sistema.
- El equipo tenga un lenguaje compartido y un proceso reproducible, independiente de quién lo ejecute.

### 1.2 Qué no es este manual

Este manual no describe cómo funciona Lia internamente, ni cómo configurar Intercom desde cero. Tampoco reemplaza el criterio del equipo operacional: es un marco que estructura ese criterio para que produzca resultados consistentes y medibles.

### 1.3 Roles involucrados

| Rol | Responsabilidad en el ciclo |
|-----|-----------------------------|
| Analista FIN | Ejecuta la extracción, corre el análisis, produce el informe |
| Líder de soporte | Prioriza hallazgos, aprueba Quick Wins, registra cambios |
| Responsable de KB | Implementa actualizaciones de artículos y workflows |
| Responsable de Pautas | Implementa actualizaciones de pautas y atributos |
| Revisor | Valida el informe semanal antes de distribuirlo |

En equipos pequeños, una misma persona puede ocupar varios roles. Lo que no es negociable es que cada acción registrada en el historial tenga un responsable identificado.

---

## 2. Ciclo Semanal

El ciclo operativo de FIN Architect Enterprise tiene una cadencia semanal fija de cinco días. Cada día tiene un propósito específico. No se deben mezclar actividades entre días sin documentar la excepción.

---

### Lunes — Extracción de datos

**Objetivo:** Recopilar la materia prima del análisis de la semana. El lunes no se analiza ni se concluye; solo se extrae.

#### 2.1.1 Extracción de conversaciones

Fuente: Intercom (`mcp__Intercom__search_conversations`)

Criterios mínimos de extracción para el período (semana anterior, lunes a domingo):

| Criterio | Valor |
|----------|-------|
| Período | Lunes anterior — Domingo anterior |
| Producto | Restobar (primario); ampliar a Pymes/Nómina cuando haya dataset |
| Participación del agente IA | `ai_agent_participated: true` |
| Conversaciones con escalación | Incluir todas (`escalated`) |
| Conversaciones con rating bajo | CSAT ≤ 3 — incluir todas |
| Conversaciones con alta frustración | Incluir cuando el atributo `Emociones` indique frustración alta |
| Conversaciones resueltas sin escalación | Muestra representativa (mínimo 10) |
| Volumen mínimo total | 25 conversaciones por ciclo |

Guardar los IDs de todas las conversaciones extraídas en el registro semanal antes de proceder.

#### 2.1.2 Extracción de métricas de la semana anterior

Registrar los siguientes valores para el período extraído:

- Total de conversaciones atendidas por Lia
- Total de conversaciones escaladas (número y porcentaje)
- Distribución de resultados: `confirmed_resolution` / `assumed_resolution` / `escalated`
- CSAT promedio de la semana (si disponible en Intercom)
- Distribución de ratings: 1, 2, 3, 4, 5
- Tiempo promedio de primera respuesta
- Tiempo promedio de resolución
- Top 5 motivos de escalación registrados

#### 2.1.3 Extracción del estado KB

Fuente: Intercom (`mcp__Intercom__list_articles`)

Registrar semanalmente:

- Artículos nuevos publicados en la semana
- Artículos actualizados en la semana
- Artículos que pasaron a estado borrador (draft)
- Artículos en draft con más de 30 días sin publicar
- Total de artículos por producto (comparar con semana anterior)

El objetivo no es auditar toda la KB cada semana — solo detectar variaciones que puedan afectar la cobertura de conocimiento de Lia.

---

### Martes — Análisis y generación del informe

**Objetivo:** Ejecutar FIN Architect Enterprise sobre las conversaciones extraídas y producir el informe ejecutivo semanal.

#### 2.2.1 Ejecución del análisis

Herramienta principal: `architect_review`

Parámetros mínimos recomendados:

| Parámetro | Valor |
|-----------|-------|
| `product` | `restobar` (o el producto del ciclo actual) |
| `conversations` | Lista de IDs extraídos el lunes |
| `mode` | `full` |
| `benchmark_target` | FIS objetivo del período (ej. 70 para inicio de operación) |

El análisis producirá:

1. FIS por conversación y promedio del período
2. Pautas que se activaron correctamente
3. Pautas que debieron activarse y no lo hicieron
4. Conflictos detectados entre pautas activas
5. Brechas en la cobertura KB (intenciones sin artículo de respaldo)
6. Propuestas de nuevas pautas
7. Propuestas de optimización de pautas existentes
8. Simulaciones de respuestas óptimas para casos críticos

#### 2.2.2 Generación del informe ejecutivo

El informe debe completarse ese mismo martes usando la estructura de la Sección 7 de este manual. No se distribuye hasta el viernes, pero se redacta el martes mientras el análisis está fresco.

---

### Miércoles — Priorización y selección de Quick Wins

**Objetivo:** Convertir los hallazgos del análisis en una lista priorizada de acciones concretas. El miércoles no se implementa nada; se decide qué se implementará.

#### 2.3.1 Revisión del listado de hallazgos

El Líder de soporte revisa con el Analista FIN todos los hallazgos producidos por el análisis. Para cada hallazgo se determina:

1. ¿Es un problema confirmado o una hipótesis?
2. ¿Cuántas conversaciones de la semana fueron afectadas?
3. ¿Es recurrente (apareció en semanas anteriores)?
4. ¿Tiene solución clara y ejecutable esta semana?
5. ¿Qué métrica mejorará si se implementa?

#### 2.3.2 Clasificación por prioridad

Aplicar los criterios de la Sección 4. Cada hallazgo queda clasificado como Crítico, Alto, Medio o Bajo.

#### 2.3.3 Selección de Quick Wins

Un **Quick Win** es una mejora que cumple simultáneamente:

- Prioridad Crítica o Alta
- Implementación estimada ≤ 2 horas
- Impacto medible en la siguiente semana
- Sin dependencias externas que bloqueen su ejecución

Seleccionar entre 2 y 5 Quick Wins para implementar el jueves. No más de 5: implementar muchos cambios a la vez dificulta medir el impacto de cada uno.

Documentar en el registro semanal:
- Quick Win seleccionado
- Hallazgo que lo origina
- Métrica que se espera mejorar
- Estimación del impacto (antes/después esperado)
- Responsable asignado

---

### Jueves — Implementación de mejoras

**Objetivo:** Ejecutar los Quick Wins seleccionados el miércoles y registrar cada cambio en el historial.

#### 2.4.1 Actualización de pautas

Antes de modificar cualquier pauta en Intercom:

1. Registrar el estado actual de la pauta en el historial (texto completo o referencia)
2. Registrar la justificación del cambio (hallazgo que lo origina, conversaciones afectadas)
3. Aplicar el cambio
4. Registrar el nuevo estado de la pauta
5. Asignar responsable y fecha

**Regla:** Ninguna pauta se modifica sin registro previo. Si no hay tiempo para registrar, no se implementa ese día.

#### 2.4.2 Actualización de atributos

Los atributos personalizados de Intercom (IACR, Escalamiento Agente Restobar, Emociones, Operational Urgency, TIPO DE PRODUCTO, etc.) son parte del sistema de diagnóstico de Lia. Su modificación tiene impacto directo en la clasificación de conversaciones.

Antes de modificar un atributo:

1. Verificar que el cambio no invalide datos históricos ya registrados
2. Confirmar con el Analista FIN que el atributo no sea referenciado por pautas activas
3. Registrar en el historial: nombre del atributo, cambio realizado, justificación

#### 2.4.3 Actualización de workflows

Los workflows de Intercom definen los flujos de atención de Lia. Son los más críticos para modificar porque afectan todas las conversaciones en curso.

Protocolo obligatorio:
- Ningún workflow se modifica en producción sin aprobación del Líder de soporte
- Los cambios de workflows deben documentarse con captura del estado anterior y posterior
- Si el cambio afecta el nodo inicial del workflow, notificar al equipo completo antes de implementar

#### 2.4.4 Actualización de artículos KB

Para cada artículo modificado:

1. Registrar en el historial: ID del artículo, título, tipo de cambio (actualización de contenido / corrección / ampliación / depreciación)
2. Indicar qué conversación o hallazgo originó el cambio
3. Si el artículo cubre una brecha detectada por FIN, marcarlo como "brecha resuelta" en el registro

---

### Viernes — Medición y cierre

**Objetivo:** Medir el impacto de los cambios implementados, comparar con la semana anterior, y cerrar el ciclo dejando todo registrado para la siguiente semana.

#### 2.5.1 Medición del impacto inmediato

Para cada Quick Win implementado el jueves, medir (en la medida en que el tiempo de un día lo permita):

- ¿Se activó la pauta modificada en alguna conversación del jueves?
- ¿Se produjo el resultado esperado?
- ¿Hay señales tempranas de mejora o de efecto no deseado?

El impacto real completo no será visible hasta el siguiente ciclo. El viernes se registra lo que se pueda observar; el lunes siguiente se completa la medición.

#### 2.5.2 Comparación con la semana anterior

Comparar los KPIs de esta semana contra los de la semana anterior. Registrar:

| KPI | Semana anterior | Esta semana | Delta | Tendencia |
|-----|-----------------|-------------|-------|-----------|
| FIS promedio | — | — | — | — |
| CSAT promedio | — | — | — | — |
| Tasa de escalación | — | — | — | — |
| Tasa de resolución confirmada | — | — | — | — |
| Tiempo primera respuesta (prom.) | — | — | — | — |
| Tiempo resolución (prom.) | — | — | — | — |

#### 2.5.3 Registro de resultados

Completar el registro semanal con:

- Quick Wins implementados y estado (completado / parcial / bloqueado)
- Hallazgos que quedaron pendientes para la siguiente semana
- Observaciones del ciclo (qué salió diferente de lo esperado, qué aprendió el equipo)
- Prioridades preliminares para el próximo lunes

Distribuir el informe ejecutivo semanal (estructura en Sección 7).

---

## 3. KPIs Obligatorios

Los siguientes indicadores deben medirse y registrarse **todas las semanas**, sin excepción. Son la base de comparación para detectar tendencias y validar el impacto de las mejoras.

### 3.1 KPIs de desempeño del agente

| Indicador | Descripción | Fuente |
|-----------|-------------|--------|
| **FIN Intelligence Score (FIS)** | Score compuesto de calidad de las conversaciones de Lia. Promedio semanal y distribución (mín./máx./p50/p90). | `architect_review` / `score_guideline` |
| **Tasa de resolución confirmada** | Porcentaje de conversaciones con estado `confirmed_resolution`. | Intercom |
| **Tasa de resolución asumida** | Porcentaje de conversaciones con estado `assumed_resolution`. | Intercom |
| **Tasa de escalación** | Porcentaje de conversaciones escaladas a humano. | Intercom |
| **Escalaciones evitables** | Conversaciones escaladas donde FIN identificó que existía una pauta o artículo KB capaz de resolver sin escalación. | `architect_review` |

### 3.2 KPIs de experiencia del cliente

| Indicador | Descripción | Fuente |
|-----------|-------------|--------|
| **CSAT promedio** | Calificación promedio de satisfacción del cliente en el período. | Intercom |
| **Distribución de ratings** | Conteo de ratings 1 / 2 / 3 / 4 / 5. Porcentaje de ratings ≤ 3. | Intercom |
| **Tiempo de primera respuesta** | Tiempo promedio entre el primer mensaje del cliente y la primera respuesta de Lia. | Intercom |
| **Tiempo de resolución** | Tiempo promedio entre inicio y cierre de la conversación. | Intercom |
| **Conversaciones con alta frustración** | Número de conversaciones donde el atributo `Emociones` registró frustración alta. | Intercom |

### 3.3 KPIs de deuda operacional

| Indicador | Descripción | Cómo medirlo |
|-----------|-------------|--------------|
| **Knowledge Debt (KD)** | Número de intenciones detectadas en conversaciones que no tienen un artículo KB de respaldo. Un KD de 0 significa cobertura completa. | `architect_review` — sección de brechas KB |
| **Guideline Debt (GD)** | Número de situaciones recurrentes identificadas que no tienen una pauta formalizada. | `architect_review` — sección de pautas faltantes |
| **Workflow Debt (WD)** | Número de flujos de atención identificados como subóptimos o incompletos. | Revisión manual + hallazgos de `architect_review` |
| **Draft Debt (DD)** | Número de artículos en estado borrador con más de 30 días sin publicar. | Estado KB del lunes |

### 3.4 KPIs de evolución del sistema

| Indicador | Descripción | Cadencia |
|-----------|-------------|----------|
| **FIS trending** | Dirección del FIS promedio en las últimas 4 semanas (subiendo / estable / bajando). | Mensual |
| **Pautas activas** | Total de pautas formalizadas y activas en el sistema. | Mensual |
| **Quick Wins acumulados** | Total de Quick Wins implementados desde el inicio de operación. | Mensual |
| **Mejoras con impacto medido** | Número de mejoras donde se midió el delta real entre antes y después. | Mensual |

---

## 4. Criterios de Priorización

Toda recomendación generada por FIN Architect Enterprise debe clasificarse antes de ser considerada para implementación. La clasificación determina en qué semana se implementa y qué nivel de aprobación requiere.

### 4.1 Escala de prioridad

#### 🔴 Crítico

**Definición:** El problema afecta activamente la experiencia del cliente o genera riesgo de churn confirmado.

**Criterios — se clasifica como Crítico si cumple al menos uno:**
- El mismo error ocurrió en 5 o más conversaciones en la semana
- Generó una escalación que el cliente calificó con rating 1 o 2
- El atributo `Emociones` registró frustración alta en más del 30% de las conversaciones afectadas
- La pauta involucrada tiene un conflicto activo que produce respuestas contradictorias
- Un artículo KB referenciado por Lia está desactualizado o fue eliminado

**Acción:** Implementar dentro de las 24 horas siguientes a la identificación, sin esperar al jueves del ciclo regular.

**Aprobación requerida:** Líder de soporte.

---

#### 🟠 Alto

**Definición:** El problema afecta la calidad de la experiencia del cliente de forma consistente pero sin riesgo inmediato de churn.

**Criterios — se clasifica como Alto si cumple al menos uno:**
- El mismo error ocurrió en 3 o más conversaciones en la semana
- Generó escalaciones evitables en más del 15% de los casos del período
- El FIS de las conversaciones afectadas está por debajo de 55
- La brecha de conocimiento cubre una funcionalidad de uso frecuente del producto
- El conflicto de pauta detectado produce comportamiento inconsistente (a veces funciona, a veces no)

**Acción:** Incluir como Quick Win prioritario en el jueves del ciclo actual.

**Aprobación requerida:** Líder de soporte.

---

#### 🟡 Medio

**Definición:** El problema reduce la calidad del servicio pero no genera impacto severo en la experiencia del cliente.

**Criterios — se clasifica como Medio si cumple al menos uno:**
- Ocurrió en 1 o 2 conversaciones en la semana
- El FIS de las conversaciones afectadas está entre 55 y 70
- La mejora implica una optimización de redacción de pauta, no un cambio de lógica
- El artículo KB existe pero podría mejorar su claridad o estructura

**Acción:** Incluir en la lista de Quick Wins del ciclo siguiente si el ciclo actual está completo.

**Aprobación requerida:** Analista FIN + Líder de soporte.

---

#### ⚪ Bajo

**Definición:** El problema es real pero su impacto en la experiencia del cliente es marginal o difícil de medir.

**Criterios:**
- Ocurrió en una sola conversación y no hay señal de recurrencia
- Se trata de una mejora estética o de consistencia de tono
- La pauta funciona correctamente pero podría formularse con mayor precisión
- El artículo KB es completo pero podría reorganizarse para mejorar escaneabilidad

**Acción:** Acumular en el backlog de mejoras. Implementar cuando no haya ítems Críticos o Altos pendientes.

**Aprobación requerida:** Analista FIN.

---

### 4.2 Reglas de escalación

- Un ítem clasificado como Bajo que reaparece sin cambios durante 3 ciclos consecutivos sube automáticamente a Medio.
- Un ítem clasificado como Medio que reaparece durante 2 ciclos consecutivos sube automáticamente a Alto.
- Ningún ítem puede permanecer clasificado como Crítico sin implementación por más de 48 horas desde su identificación.

---

## 5. Gobierno del Cambio

Ninguna modificación a pautas, workflows, atributos o artículos KB puede realizarse sin quedar formalmente registrada. Este principio no tiene excepciones.

### 5.1 Tipos de cambio y aprobaciones requeridas

| Tipo de cambio | Aprobación mínima | Tiempo máximo para implementar |
|----------------|-------------------|-------------------------------|
| Nueva pauta | Líder de soporte | Ciclo siguiente al de identificación |
| Modificación de pauta existente | Analista FIN + Líder de soporte | Mismo ciclo si es Crítico/Alto |
| Eliminación de pauta | Líder de soporte + revisión de conflictos | Dos ciclos de revisión antes de eliminar |
| Nuevo atributo | Líder de soporte | Requiere validación en entorno de prueba primero |
| Modificación de atributo | Analista FIN + Líder de soporte | Verificar impacto en datos históricos antes |
| Modificación de workflow (nodo no inicial) | Líder de soporte | Mismo ciclo si es Crítico/Alto |
| Modificación de workflow (nodo inicial) | Líder de soporte + notificación al equipo | Ciclo siguiente; implementar fuera de horario pico |
| Nuevo artículo KB | Responsable de KB | Mismo ciclo |
| Actualización de artículo KB | Responsable de KB | Mismo ciclo |
| Depreciación de artículo KB | Responsable de KB + Analista FIN | Verificar que ninguna pauta lo referencie activamente |

### 5.2 Principio de reversibilidad

Antes de implementar cualquier cambio, el responsable debe ser capaz de responder: *"¿Cómo reverto este cambio si produce efectos no deseados?"*

Si la respuesta es "no sé" o "no es posible revertir fácilmente", el cambio requiere aprobación adicional del Líder de soporte antes de proceder.

### 5.3 Ventana de implementación recomendada

Para cambios que afecten flujos activos (workflows, pautas de alto tráfico), la ventana recomendada de implementación es fuera del horario de mayor volumen de conversaciones. Verificar los horarios pico del producto antes de implementar cambios en producción.

---

## 6. Historial de Mejoras

El historial de mejoras es el registro permanente de todos los cambios realizados al sistema. Es la fuente de verdad para medir el impacto acumulado de FIN Architect Enterprise.

### 6.1 Estructura del registro

Cada entrada del historial debe contener los siguientes campos:

| Campo | Descripción | Obligatorio |
|-------|-------------|-------------|
| `ID` | Identificador único. Formato: `MEJORA-AAAA-NN` (ej. MEJORA-2026-01) | ✅ |
| `Fecha` | Fecha de implementación. Formato: `AAAA-MM-DD` | ✅ |
| `Semana operacional` | Número de semana desde el inicio de operación (ej. Semana 1) | ✅ |
| `Tipo` | Pauta / Atributo / Workflow / Artículo KB / Proceso interno | ✅ |
| `Elemento modificado` | Nombre o ID del elemento modificado | ✅ |
| `Descripción del cambio` | Qué se cambió y por qué. Máximo 3 párrafos. | ✅ |
| `Hallazgo origen` | Hallazgo de `architect_review` o identificación manual que originó el cambio | ✅ |
| `Conversaciones afectadas` | IDs o cantidad de conversaciones que evidenciaron el problema | ✅ |
| `Prioridad` | Crítico / Alto / Medio / Bajo | ✅ |
| `Responsable` | Nombre del responsable de la implementación | ✅ |
| `Aprobado por` | Nombre de quien aprobó el cambio | ✅ |
| `Estado anterior` | Descripción o referencia al estado antes del cambio | ✅ |
| `Estado nuevo` | Descripción o referencia al estado después del cambio | ✅ |
| `Impacto esperado` | Qué métrica debería mejorar y en qué magnitud | ✅ |
| `Impacto real` | Delta medido en el ciclo siguiente. Completar la semana siguiente. | ⏳ Se completa después |
| `Observaciones` | Notas adicionales, efectos secundarios observados, decisiones tomadas | Opcional |

### 6.2 Cómo usar el historial

**Al inicio de cada ciclo (lunes):** Revisar las entradas de la semana anterior que tienen `Impacto real` pendiente. Completarlas con los datos extraídos.

**Al final de cada mes:** Calcular el impacto acumulado del mes: total de cambios implementados, promedio de FIS antes y después, delta de CSAT, reducción de escalaciones.

**Cada trimestre:** Revisar el historial completo para identificar patrones: ¿qué tipo de cambios tienen mayor impacto? ¿Qué elementos se modifican más frecuentemente? ¿Qué hallazgos recurrentes no han sido resueltos?

### 6.3 Formato del registro

El historial puede mantenerse en el formato que el equipo prefiera (hoja de cálculo, documento, herramienta de gestión), siempre que:

- Esté accesible para todos los roles involucrados
- No pueda modificarse sin dejar rastro del cambio
- Permita filtrar por fecha, tipo, responsable y estado
- Se actualice como mínimo una vez por semana (viernes del ciclo)

---

## 7. Cierre Semanal

Al final de cada ciclo, el Analista FIN produce el **Informe Ejecutivo Semanal**. Su estructura es fija. No se abrevia ni se simplifica: la consistencia de formato es lo que permite comparar semanas entre sí.

---

### Plantilla: Informe Ejecutivo Semanal FIN Architect Enterprise

```
═══════════════════════════════════════════════════════════════
  FIN ARCHITECT ENTERPRISE — INFORME EJECUTIVO SEMANAL
  Semana: [Número] | Período: [AAAA-MM-DD] al [AAAA-MM-DD]
  Producto: [Restobar / Pymes / Nómina / Alojamientos]
  Analista: [Nombre]  |  Aprobado por: [Nombre]
═══════════════════════════════════════════════════════════════

━━━ 1. RESUMEN EJECUTIVO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[2–4 párrafos. Responder: ¿Cómo estuvo la semana? ¿Hubo algo
inusual? ¿Cuál fue el hallazgo más importante? ¿Qué se
implementó? ¿Cuál es la tendencia principal?]

━━━ 2. KPIs ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  FIN Intelligence Score (FIS)
  ├── Esta semana:        [valor] (prom.)   p50: [valor]   p90: [valor]
  ├── Semana anterior:    [valor]
  └── Delta:              [+/-valor]   Tendencia: [↑ / → / ↓]

  CSAT
  ├── Esta semana:        [valor] (prom.)
  ├── Semana anterior:    [valor]
  ├── Ratings ≤ 3:        [N] conversaciones ([%])
  └── Delta:              [+/-valor]   Tendencia: [↑ / → / ↓]

  Resolución
  ├── Confirmada:         [N] ([%])
  ├── Asumida:            [N] ([%])
  └── Escalada:           [N] ([%])   Evitables: [N]

  Tiempos
  ├── Primera respuesta:  [valor] (prom.)
  └── Resolución:         [valor] (prom.)

  Deuda operacional
  ├── Knowledge Debt:     [N] intenciones sin cobertura KB
  ├── Guideline Debt:     [N] situaciones sin pauta formalizada
  ├── Workflow Debt:      [N] flujos subóptimos identificados
  └── Draft Debt:         [N] artículos en borrador > 30 días

━━━ 3. HALLAZGOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Listar todos los hallazgos del análisis de esta semana,
  clasificados por prioridad. Para cada hallazgo:]

  🔴 [ID-HALLAZGO-N] — [Nombre corto]
  Prioridad: Crítico
  Conversaciones afectadas: [N] ([IDs si son pocas])
  Descripción: [Qué ocurrió, por qué es un problema]
  Pauta / Elemento involucrado: [nombre]
  Recomendación: [Qué debería cambiarse]

  🟠 [ID-HALLAZGO-N] — [Nombre corto]
  [Mismo formato]

  🟡 [ID-HALLAZGO-N] — [Nombre corto]
  [Mismo formato]

  ⚪ [ID-HALLAZGO-N] — [Nombre corto]
  [Mismo formato]

━━━ 4. QUICK WINS IMPLEMENTADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Para cada Quick Win implementado esta semana:]

  ✅ [MEJORA-AAAA-NN] — [Nombre corto]
  Tipo: [Pauta / Atributo / Workflow / Artículo KB]
  Hallazgo origen: [ID-HALLAZGO-N]
  Cambio realizado: [Descripción concisa]
  Impacto esperado: [Métrica que debería mejorar]
  Responsable: [Nombre]

━━━ 5. CAMBIOS IMPLEMENTADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Lista completa de todos los cambios del jueves, incluyendo
  los que no son Quick Wins. Referenciar el ID del historial.]

  MEJORA-AAAA-NN | [Tipo] | [Elemento] | [Responsable] | [Estado]

━━━ 6. IMPACTO MEDIDO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Completar el impacto real de los Quick Wins implementados
  la semana anterior. Si es la primera semana, indicar "N/A —
  primera semana de operación".]

  MEJORA-AAAA-NN — [Nombre]
  Impacto esperado:   [lo que se registró la semana pasada]
  Impacto real:       [delta medido esta semana]
  Evaluación:         [Logrado / Parcial / No logrado / No medible aún]
  Observaciones:      [Notas]

━━━ 7. PENDIENTES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Hallazgos identificados que no se implementarán esta semana:

  [ID] | [Nombre] | [Prioridad] | [Razón de postergación] | [Semana objetivo]

━━━ 8. PLAN PARA LA SIGUIENTE SEMANA ━━━━━━━━━━━━━━━━━━━━━━━━

  Foco principal:     [Qué producto o área tendrá prioridad]
  Quick Wins en fila: [Lista de los 2–5 ítems listos para implementar]
  Objetivo FIS:       [Target para el próximo ciclo]
  Objetivo CSAT:      [Target para el próximo ciclo]
  Alertas:            [Algo que el equipo debe monitorear de cerca]

═══════════════════════════════════════════════════════════════
  Generado el: [AAAA-MM-DD]  |  Distribuido el: [AAAA-MM-DD]
═══════════════════════════════════════════════════════════════
```

---

## 8. Filosofía Operacional

FIN Architect Enterprise opera bajo un modelo de **mejora continua basada en evidencia**.

Este principio tiene tres implicaciones prácticas que deben guiar cada decisión del equipo:

### 8.1 Toda decisión debe estar respaldada por datos

En el modelo de operación de FIN, "creo que Lia falló en este caso" no es suficiente para modificar una pauta. Lo que justifica un cambio es: *"En N conversaciones de la semana, Lia no activó la pauta X cuando debía haberlo hecho, lo que resultó en Y escalaciones evitables. El análisis de `architect_review` lo confirma."*

La diferencia no es burocrática — es epistémica. Los sistemas que cambian por intuición oscilan: mejoran en un área, empeoran en otra, y nunca acumulan aprendizaje porque no saben qué causó qué. Los sistemas que cambian por evidencia acumulan conocimiento real sobre qué funciona.

### 8.2 El impacto debe medirse siempre

Un cambio implementado sin medición posterior es un cambio que no existe en el modelo de aprendizaje del sistema. Puede haber funcionado o no; simplemente no se sabe. Y lo que no se sabe no puede replicarse ni evitarse.

El registro de impacto real en el historial no es una formalidad administrativa: es el mecanismo por el cual FIN Architect Enterprise se vuelve más inteligente con cada ciclo. Sin él, el equipo está operando en modo perpetuo de primera semana.

### 8.3 La mejora es continua, no un evento

FIN Architect Enterprise no es un proyecto que se completa. Es un sistema que opera indefinidamente mientras Lia atienda clientes. Cada semana produce datos nuevos; cada semana hay algo que puede mejorar. El objetivo no es llegar a un estado de perfección —es mantener una dirección consistente de mejora, semana tras semana, ciclo tras ciclo.

El equipo que opera FIN no es un equipo de mantenimiento. Es un equipo de mejora continua. La diferencia está en que el equipo de mantenimiento responde cuando algo falla; el equipo de mejora continua anticipa fallas antes de que ocurran, porque está leyendo los datos correctos con la frecuencia correcta.

---

*Este manual está vigente a partir de la versión FIN Architect Enterprise v1.0 Beta.*  
*Toda modificación a este documento debe ser aprobada por el Líder de soporte y registrada en el historial de mejoras.*  
*Versión del manual: 1.0 — Fecha: 27 de junio de 2026.*
