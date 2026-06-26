# FIN Architect Enterprise — Arquitectura de Producto v1.0

*Blueprint oficial | Fase 5 | 2026-06-26*

---

## Índice

1. [Visión del Producto](#1-visión-del-producto)
2. [Perfiles de Usuario](#2-perfiles-de-usuario)
3. [Dashboard Principal](#3-dashboard-principal)
4. [Páginas Secundarias](#4-páginas-secundarias)
5. [Sistema de KPIs](#5-sistema-de-kpis)
6. [FIN Intelligence Score](#6-fin-intelligence-score)
7. [Sistema de Recomendaciones](#7-sistema-de-recomendaciones)
8. [Sistema de Auditorías Automáticas](#8-sistema-de-auditorías-automáticas)
9. [Roadmap](#9-roadmap)
10. [Conclusión](#10-conclusión)

---

## 1. Visión del Producto

### El problema

Los equipos de soporte que operan agentes de IA conversacional como FIN enfrentan un problema estructural: **tienen visibilidad del resultado, pero no del sistema**.

Saben cuántas conversaciones se escalaron. No saben por qué FIN las escaló mal.  
Saben que un cliente dejó una calificación de 1. No saben en qué turno FIN tomó la decisión incorrecta.  
Pueden leer una conversación. No pueden leer el patrón de 500 conversaciones.

Intercom ofrece métricas operacionales. No ofrece inteligencia sobre el agente mismo.  
No hay una herramienta que responda: *¿El ecosistema de FIN está bien configurado?*

### La solución

**FIN Architect Enterprise** es la primera plataforma de inteligencia operacional diseñada específicamente para auditar, analizar y optimizar ecosistemas de agentes conversacionales construidos sobre FIN (Intercom AI).

No es un reporte. Es un sistema de control.  
No describe lo que pasó. Prescribe lo que debe cambiar.  
No audita conversaciones individuales. Audita el sistema que las generó.

### Propuesta de valor

| Para quién | Valor entregado |
|-----------|----------------|
| Director de Soporte | Visibilidad ejecutiva del performance del agente. Una sola métrica: FIN Intelligence Score. |
| Líder Operativo | Diagnóstico de qué está fallando hoy y qué acción tomar mañana. |
| Administrador Intercom | Inventario completo de pautas, workflows, atributos y KB con análisis de salud. |
| Arquitecto Conversacional | Blueprint de mejoras priorizadas con evidencia de conversaciones reales. |
| Product Manager | Evolución histórica del agente, benchmarks por producto y roadmap de optimización. |

### Principios de diseño del producto

1. **Evidencia primero.** Toda recomendación cita la conversación que la generó.
2. **Sin inventar datos.** Todo análisis se basa en conversaciones reales de Intercom.
3. **Accionable sobre informativo.** Cada sección termina con una acción concreta.
4. **Multi-producto.** Restobar, Pymes, Nómina, Alojamientos coexisten en el mismo sistema.
5. **Evolutivo.** El sistema aprende del historial. La semana 10 sabe más que la semana 1.

---

## 2. Perfiles de Usuario

### 2.1 Director de Soporte

**Contexto:** No opera Intercom directamente. Revisa resultados semanalmente. Toma decisiones de recursos y prioridad.

**Necesita ver:**
- FIN Intelligence Score global y por producto
- Tendencia semanal / mensual del score
- Top 3 problemas críticos sin resolver
- Riesgo de churn del período
- Comparación vs benchmark del sector o período anterior
- Una acción ejecutiva recomendada

**Vista principal:** Executive Dashboard — una sola pantalla con 6 números y un semáforo global.

**Frecuencia de uso:** Semanal. Revisión de 5 minutos.

---

### 2.2 Líder Operativo de Soporte

**Contexto:** Gestiona el equipo de agentes humanos. Decide qué escalar, qué automatizar, qué entrenar. Conoce Intercom pero no configura FIN.

**Necesita ver:**
- Qué intenciones están fallando más hoy
- Qué tipos de usuario tienen mayor frustración
- En qué horarios la calidad de FIN cae
- Cuántas escalaciones eran evitables
- Qué conversaciones específicas ejemplifican los problemas

**Vista principal:** Conversation Analytics + Escalation Analytics

**Frecuencia de uso:** Diaria. Revisión de 15–30 minutos.

---

### 2.3 Administrador Intercom

**Contexto:** Configura workflows, pautas, atributos y KB. Opera el sistema técnico de FIN. Es quien implementa los cambios.

**Necesita ver:**
- Pautas con bajo rendimiento o conflictos
- Artículos KB que FIN no está usando
- Atributos no detectados o mal clasificados
- Workflows con alta tasa de salida inesperada
- Lista de cambios pendientes con instrucciones exactas de implementación

**Vista principal:** Guideline Analytics + Workflow Analytics + Knowledge Analytics + Improvement Center

**Frecuencia de uso:** Varias veces por semana. Sesiones de trabajo.

---

### 2.4 Arquitecto Conversacional

**Contexto:** Diseña la arquitectura de FIN: qué pautas existir, cómo interactuar con el usuario, qué flujos manejar. Combina conocimiento del producto, del usuario y de IA conversacional.

**Necesita ver:**
- Mapa completo del ecosistema (pautas + workflows + atributos + KB)
- Patrones de conversación emergentes no cubiertos
- Conflictos estructurales entre componentes
- Brechas de cobertura funcional
- Sugerencias de nuevas pautas con redacción borrador

**Vista principal:** Ecosystem Review + Architect Review + Recommendations Center

**Frecuencia de uso:** Semanal. Sesiones de diseño.

---

### 2.5 Product Manager

**Contexto:** Define la hoja de ruta del producto Loggro. Quiere saber cómo FIN impacta en retención, NPS y costo de soporte.

**Necesita ver:**
- Evolución del FIN Intelligence Score en el tiempo
- Correlación entre calidad de FIN y churn
- Cobertura de producto: qué funcionalidades tienen soporte automatizado
- ROI estimado de las mejoras implementadas
- Roadmap de optimización del agente

**Vista principal:** Historical Evolution + AI Performance + Risk Center

**Frecuencia de uso:** Mensual. Revisión estratégica.

---

## 3. Dashboard Principal

El Dashboard principal es la pantalla de entrada de FIN Architect Enterprise. Contiene 12 indicadores agrupados en 3 filas.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  FIN ARCHITECT ENTERPRISE                          Restobar ▾  Últimos 30d ▾ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FIN INTELLIGENCE SCORE                                                      ║
║  ┌─────────────────────────────────────────────────────────────────────────┐ ║
║  │   62 / 100   REGULAR   ▼ -4 vs mes anterior   ◎ Target: 75             │ ║
║  └─────────────────────────────────────────────────────────────────────────┘ ║
║                                                                              ║
║  FILA 1 — SALUD DEL SISTEMA                                                  ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        ║
║  │ CONVERSATION │ │  KNOWLEDGE   │ │   WORKFLOW   │ │  GUIDELINE   │        ║
║  │    HEALTH    │ │    HEALTH    │ │    HEALTH    │ │    HEALTH    │        ║
║  │              │ │              │ │              │ │              │        ║
║  │   🟡 58      │ │   🔴 41      │ │   🟡 67      │ │   🟢 74      │        ║
║  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        ║
║                                                                              ║
║  FILA 2 — SALUD OPERACIONAL                                                  ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        ║
║  │  ATTRIBUTE   │ │  ESCALATION  │ │   CUSTOMER   │ │  AUTOMATION  │        ║
║  │    HEALTH    │ │    HEALTH    │ │  EXPERIENCE  │ │   COVERAGE   │        ║
║  │              │ │              │ │              │ │              │        ║
║  │   🟡 62      │ │   🔴 22      │ │   🔴 38      │ │   🟡 55      │        ║
║  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        ║
║                                                                              ║
║  FILA 3 — RIESGO Y COBERTURA                                                 ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        ║
║  │  KNOWLEDGE   │ │  OPERATIONAL │ │    CHURN     │ │     AI       │        ║
║  │   COVERAGE   │ │     RISK     │ │     RISK     │ │ PERFORMANCE  │        ║
║  │              │ │              │ │              │ │              │        ║
║  │   🟡 52      │ │   🔴 HIGH    │ │   🟡 MEDIUM  │ │   🟡 61      │        ║
║  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Descripción de cada indicador

---

#### FIN Intelligence Score (0–100)

El indicador maestro del ecosistema. Sintetiza todos los demás en un único número comparable en el tiempo y entre productos. No es un promedio simple: aplica ponderaciones, penalizaciones y hard caps (ver Sección 6).

**Interpretación:** 85+ Excelente · 70–84 Bueno · 55–69 Regular · 40–54 Deficiente · 0–39 Crítico.

---

#### Conversation Health (0–100)

Mide la calidad de las interacciones entre FIN y los usuarios finales. Integra: tasa de resolución real, calidad del diagnóstico, número de intentos por conversación, y coherencia del flujo.

**Bajo cuando:** FIN hace demasiadas preguntas sin resolver, o resuelve sin preguntar lo necesario, o tarda múltiples turnos en capturar el contexto.

---

#### Knowledge Health (0–100)

Mide la salud de la base de conocimiento como recurso activo de FIN. Integra: tasa de utilización de artículos, diversidad de artículos usados, cobertura temática y ratio de artículos publicados vs borradores.

**Bajo cuando:** FIN tiene artículos disponibles pero no los usa, o hay temas frecuentes sin artículo, o la mayoría del contenido está en borrador.

---

#### Workflow Health (0–100)

Mide la efectividad de los flujos conversacionales. Integra: tasa de salida exitosa por nodo, porcentaje de usuarios que completan el flujo sin reiniciarlo, y consistencia entre el nodo de inicio y el tema real de la conversación.

**Bajo cuando:** Los usuarios llegan al flujo equivocado, o abandonan el flujo a mitad, o el flujo redirige innecesariamente.

---

#### Guideline Health (0–100)

Mide la calidad del repositorio de pautas. Integra: cobertura de escenarios, tasa de pautas activas vs inactivas (muertas), índice de conflictos entre pautas, y calidad de redacción (evaluada por `score_guideline`).

**Bajo cuando:** Hay pautas que nunca se activan, o varias pautas se contradicen, o las pautas activas no resuelven los errores detectados.

---

#### Attribute Health (0–100)

Mide la calidad de la detección y uso de atributos de conversación. Integra: tasa de detección correcta de atributos clave (IACR, Urgencia, Emociones), porcentaje de conversaciones donde los atributos cambiaron el comportamiento de FIN, y consistencia de atributos entre conversaciones similares.

**Bajo cuando:** Conversaciones de alto riesgo no tienen IACR asignado, o el atributo de escalamiento no se activa cuando debería.

---

#### Escalation Health (0–100)

Mide la calidad del proceso de escalamiento. Integra: tasa de escalaciones evitables, delay promedio cuando el usuario pide agente, tasa de escalaciones correctas (FIN identificó bien cuándo escalar), y calidad del handoff al agente humano.

**Bajo cuando:** FIN demora el escalamiento cuando el usuario ya lo pidió, o escala sin suficiente contexto para el agente humano, o escala casos que podría haber resuelto.

---

#### Customer Experience (0–100)

Mide el impacto percibido por el cliente. Integra: rating promedio de conversaciones con calificación, nivel de frustración promedio del dataset, riesgo de churn promedio, y tasa de emociones negativas.

**Bajo cuando:** Los usuarios expresan frustración explícita, repiten el problema múltiples veces, o el rating promedio cae por debajo de 3.

---

#### Automation Coverage (0–100)

Mide qué porcentaje de las intenciones de los usuarios puede resolver FIN sin intervención humana. Integra: proporción de intenciones con workflow activo, cobertura de pautas por tipo de intención, y tasa de resolución por intención.

**Bajo cuando:** Hay tipos de consulta frecuentes que siempre terminan escalados, sin que exista una pauta o workflow que los atienda.

---

#### Knowledge Coverage (0–100)

Mide qué porcentaje de los temas de soporte tiene artículo de KB publicado y activo. Diferente de Knowledge Health: este mide cobertura temática (¿existe el artículo?), no utilización (¿FIN lo usa?).

**Bajo cuando:** Hay intenciones frecuentes en las conversaciones que no tienen artículo de KB correspondiente.

---

#### Operational Risk (ALTO / MEDIO / BAJO)

Nivel de riesgo operativo actual del ecosistema. Combina: porcentaje de conversaciones con IACR=Riesgo Operativo, tasa de escalaciones fuera de horario sin resolución, y casos activos con riesgo de impacto en negocio del cliente.

---

#### Churn Risk (ALTO / MEDIO / BAJO)

Nivel de riesgo de churn generado por las interacciones de FIN. Combina: riesgo de churn promedio del período, número de conversaciones con churn_risk > 70, y presencia de señales explícitas (cancelaciones, quejas de suscripción, facturación fallida).

---

#### AI Performance (0–100)

Mide la calidad intrínseca de las respuestas de FIN como agente de IA. Integra: calidad del diagnóstico promedio, precisión del contexto detectado, pertinencia de artículos utilizados, y adecuación del tono y longitud de respuestas.

---

## 4. Páginas Secundarias

Cada módulo secundario es una pantalla dedicada con su propio set de visualizaciones, filtros y acciones.

---

### 4.1 Conversation Analytics

**Propósito:** Análisis profundo de las conversaciones del período. Identifica patrones, outliers y tendencias.

**Secciones:**

- **Vista de conversaciones:** Tabla filtrable por producto, resultado, rating, rango de frustración, AI Title, fecha. Cada fila es clickeable y abre el transcript completo.
- **Distribución por resultado:** Gráfico de barras: confirmed / assumed / escalated. Desglosado por producto y por período.
- **Mapa de intenciones:** Tabla de intenciones (AI Title) con: frecuencia, tasa de resolución, tasa de escalación, frustración promedio, churn promedio. Ordenable por cualquier columna.
- **Análisis de turnos:** Histograma de número de partes por conversación. Identifica conversaciones anormalmente largas (outliers > P95).
- **Timeline de frustración:** Para conversaciones seleccionadas, gráfico del nivel de frustración por turno.
- **Análisis FUERA DE HORARIO:** Separación de métricas en horario vs fuera de horario. Muestra el delta de performance.
- **Heatmap de volumen:** Mapa de calor de conversaciones por día de la semana y hora del día.

**Filtros disponibles:** producto · período · resultado · rating · AI Title · IACR · frustración · churn · fuera de horario

**Acciones:** Exportar CSV · Marcar conversación como caso de estudio · Enviar a Improvement Center

---

### 4.2 Knowledge Analytics

**Propósito:** Estado completo de la base de conocimiento y su uso por FIN.

**Secciones:**

- **Inventario activo:** Tabla de todos los artículos publicados con: título, colección, producto, fecha última actualización, veces usado por FIN en el período.
- **Artículos más usados:** Top 20 artículos utilizados por FIN. Con conteo y en qué intenciones se usaron.
- **Artículos nunca usados:** Lista de artículos publicados que FIN no ha usado en el período. Potencialmente irrelevantes o mal conectados.
- **Brechas temáticas:** Lista de temas frecuentes en conversaciones que no tienen artículo de KB. Generada automáticamente desde el análisis de intenciones.
- **Artículos en borrador:** Lista de artículos en estado draft. Cuántos días llevan en draft. A quién pertenecen.
- **Distribución por producto:** Gráfico: cuántos artículos tiene cada producto vs cuántos se usan activamente.
- **Cobertura funcional:** Mapa de qué funcionalidades del producto (facturación, inventario, reportes, etc.) tienen cobertura de KB.

**Acciones:** Marcar artículo como prioritario para publicar · Proponer nuevo artículo · Vincular artículo a intención

---

### 4.3 Workflow Analytics

**Propósito:** Análisis de los flujos conversacionales de FIN.

**Secciones:**

- **Mapa de flujos activos:** Lista de workflows activos (Restobar IA, Alojamientos inicio chat FIN, etc.) con métricas por workflow: conversaciones, resolución, escalación, frustración promedio.
- **Análisis de nodos de entrada:** Qué nodos de inicio generan más problemas. Identificación de nodos con alta tasa de derivación inesperada.
- **Análisis de nodos de salida:** Cómo terminan las conversaciones por cada workflow. Cuántas terminan en el nodo esperado vs en nodo de error o escalamiento.
- **Flujos sin cobertura:** Intenciones frecuentes que no tienen workflow dedicado. FIN las atiende con el flujo genérico.
- **Análisis de redireccionamientos:** Cuántas veces un usuario es redirigido dentro del mismo flujo o a otro flujo. Indica confusión de diseño.
- **Comparativa entre productos:** Tabla: tasa de resolución por workflow y producto. Identifica qué producto tiene el workflow mejor diseñado.

---

### 4.4 Guideline Analytics

**Propósito:** Estado completo del repositorio de pautas.

**Secciones:**

- **Repositorio completo:** Tabla de todas las pautas con: ID, título, activaciones en el período, score (de `score_guideline`), conflictos detectados, fecha de creación.
- **Pautas más activas:** Top 15 pautas activadas. Indica qué comportamientos son más comunes.
- **Pautas muertas:** Pautas con cero activaciones en el período. Candidatas a revisión o deprecación.
- **Mapa de conflictos:** Grafo o tabla de qué pautas entran en conflicto entre sí. Severidad del conflicto (de `detect_conflicts`).
- **Cobertura por escenario:** Qué escenarios de soporte tiene cobertura de pauta y cuáles no.
- **Historial de pautas:** Cuándo se crearon, cuándo se modificaron, qué cambió. Tendencia de activaciones en el tiempo.
- **Score por pauta:** Distribución de scores del repositorio. Cuántas pautas están por debajo de 60/100.

**Acciones:** Ver detalle de pauta · Ejecutar `optimize_guideline` · Marcar para revisión · Proponer deprecación

---

### 4.5 Escalation Analytics

**Propósito:** Análisis profundo del proceso de escalamiento.

**Secciones:**

- **Volumen de escalaciones:** Total de escalaciones del período. Tendencia. Comparativa vs resoluciones.
- **Motivos de escalación:** Distribución de por qué se escaló (por pauta / por solicitud del usuario / por timeout / por urgencia).
- **Escalaciones evitables:** Conversaciones escaladas donde la intención era cubierta por KB o pautas. Estimado de cuántas escalaciones se habrían evitado con mejores pautas.
- **Delay de escalamiento:** Histograma de cuántos turnos pasaron entre que el usuario pidió un agente y FIN lo escaló efectivamente.
- **Calidad del handoff:** Análisis de qué contexto entregó FIN al agente humano. Conversaciones donde el agente tuvo que volver a pedir datos ya dados.
- **Performance por horario:** Tasa de escalación fuera de horario vs en horario. Identifica si FUERA DE HORARIO está bien manejado.
- **Top intenciones escaladas:** Las 10 intenciones que más se escalan. Con su tasa de resolución como referencia.

---

### 4.6 Attribute Analytics

**Propósito:** Análisis de la calidad de detección y uso de atributos de conversación.

**Secciones:**

- **Inventario de atributos:** Lista de todos los atributos configurados con: nombre, tipo, tasa de detección, distribución de valores.
- **Tasa de detección por atributo:** Qué porcentaje de conversaciones tiene cada atributo poblado. Identifica atributos que casi nunca se completan.
- **Inconsistencias:** Conversaciones donde el mismo tipo de situación generó atributos distintos. Indica que la detección no es consistente.
- **IACR Analysis:** Distribución de clasificaciones de riesgo (Riesgo Operativo / Riesgo Alto / Normal) y correlación con resultado de la conversación.
- **Emociones Analysis:** Distribución de valores de Emociones y correlación con rating y churn.
- **Urgencia Analysis:** Distribución de urgencia y cómo impactó en el comportamiento de FIN.
- **Atributos no detectados:** Situaciones en conversaciones donde debería haberse detectado un atributo pero no se detectó.

---

### 4.7 Improvement Center

**Propósito:** Centro de trabajo para el Administrador Intercom y el Arquitecto Conversacional. Convierte los insights en cambios concretos.

**Secciones:**

- **Cola de mejoras:** Lista priorizada de todas las mejoras identificadas (de todos los módulos). Con estado: Pendiente / En progreso / Implementada / Descartada.
- **Por tipo de mejora:**
  - Nueva pauta (con borrador de redacción)
  - Ajuste a pauta existente (con instrucción exacta de qué cambiar)
  - Nuevo artículo KB (con título, intención y contenido sugerido)
  - Nuevo atributo (con nombre, tipo y condición de activación)
  - Ajuste de workflow (con descripción de qué nodo modificar y cómo)
- **Impacto estimado:** Para cada mejora, cuántos puntos sumaría al FIN Intelligence Score si se implementa.
- **Historial de implementaciones:** Qué mejoras se implementaron, cuándo, y cuál fue el impacto real en las métricas post-implementación.
- **Generador de pautas:** Interfaz para usar `generate_guideline` a partir de un patrón de conversación detectado.

---

### 4.8 Recommendations Center

**Propósito:** Vista unificada de todas las recomendaciones del sistema, organizadas para toma de decisiones.

**Secciones:**

- **Recomendaciones críticas:** Requieren acción antes de 48h. Con evidencia de conversaciones específicas.
- **Quick Wins:** Alto impacto, baja complejidad. Implementables en < 2 horas.
- **Mejoras estructurales:** Cambios de mediano plazo con mayor impacto en el score.
- **Deuda técnica:** Componentes desactualizados, conflictos conocidos, pautas muertas. No urgente pero acumulativo.
- **Deuda conversacional:** Patrones de error recurrentes que no han sido abordados por ninguna pauta.
- **Deuda de conocimiento:** Brechas de KB identificadas que siguen sin artículo publicado.
- **Filtros:** Por producto · por categoría · por impacto estimado · por esfuerzo de implementación

---

### 4.9 Historical Evolution

**Propósito:** Seguimiento de la evolución del ecosistema en el tiempo.

**Secciones:**

- **Evolución del FIN Intelligence Score:** Gráfico de línea del score global y sus 6 dimensiones, por semana o mes.
- **Evolución de KPIs clave:** Líneas de tendencia para tasa de resolución, escalación, frustración, churn, rating.
- **Impacto de cambios:** Marcadores en la línea de tiempo indicando cuándo se implementó una mejora y el efecto en métricas.
- **Comparativa de períodos:** Vista lado a lado de dos períodos seleccionables.
- **Evolución de la KB:** Cuántos artículos se publicaron por período, cómo cambió la utilización.
- **Evolución del repositorio de pautas:** Cuántas pautas se agregaron/modificaron/deprecaron por período.

---

### 4.10 Benchmarks

**Propósito:** Contexto comparativo para interpretar los números propios.

**Secciones:**

- **Benchmarks internos:** Comparativa entre productos (Restobar vs Pymes vs Nómina vs Alojamientos). Cuál tiene el mejor FIN Intelligence Score. Cuál tiene mayor cobertura de KB.
- **Benchmarks temporales:** El mejor período histórico como referencia. ¿En qué semana el score fue más alto? ¿Qué había diferente?
- **Targets configurables:** El administrador puede definir targets por KPI. El sistema muestra el delta actual vs target.
- **Proyección:** Basado en la tendencia actual, cuándo se llegaría al target si se implementan las mejoras recomendadas.

---

### 4.11 Risk Center

**Propósito:** Vista unificada de todos los riesgos activos del ecosistema.

**Secciones:**

- **Riesgo operativo activo:** Conversaciones abiertas o recientes con IACR=Riesgo Operativo que no fueron resueltas satisfactoriamente.
- **Riesgo de churn activo:** Clientes con churn_risk > 70 en sus últimas conversaciones. Con nombre de empresa y tipo de plan.
- **Riesgo de escalamiento masivo:** Situaciones donde un mismo problema está afectando a múltiples clientes simultáneamente (posible incidente).
- **Riesgo de degradación:** Tendencia negativa del score por más de 2 semanas consecutivas. Alerta temprana.
- **Riesgo de cobertura cero:** Intenciones que han aparecido en el último período sin ninguna pauta ni artículo que las atienda.

---

### 4.12 AI Performance

**Propósito:** Análisis de FIN como sistema de IA: calidad de razonamiento, pertinencia de respuestas, uso de herramientas.

**Secciones:**

- **Calidad de diagnóstico:** Distribución del score de calidad de diagnóstico (0–100) de las conversaciones. Cuántas por debajo de 60.
- **Errores más frecuentes de FIN:** Clasificación de los errores principales detectados en el período. Cuántas conversaciones tienen el mismo tipo de error.
- **Análisis de causa raíz:** Agrupación de causas raíz detectadas. Qué tipo de causa raíz es más frecuente (falta de KB / pauta mal diseñada / workflow incorrecto / atributo no detectado).
- **Calidad de handoff:** Análisis de qué tan bien FIN prepara el contexto antes de escalar.
- **Pertinencia de artículos:** Análisis de si los artículos que FIN usa son los más relevantes para la intención, o si hay artículos más apropiados disponibles que no usa.
- **Tono y longitud:** Análisis de si las respuestas de FIN tienen el tono correcto (IACR, Emociones) y la longitud adecuada (no demasiado corta, no demasiado larga).

---

## 5. Sistema de KPIs

### Categoría A — Resolución y Eficiencia

---

**R1. Tasa de Resolución Real (TRR)**

- *Qué mide:* El porcentaje de conversaciones donde FIN resolvió el problema sin necesidad de agente humano.
- *Cómo se calcula:* `confirmed_resolutions / total_conversations × 100`
- *Cómo se interpreta:* Es el KPI más importante del sistema. Por debajo del 30% indica que FIN está fallando como agente autónomo. Por encima del 70% indica un ecosistema bien configurado. Se distingue de "assumed resolution" porque esta última puede ser falsa (el usuario se fue sin resolver).
- *Semáforo:* 🔴 < 30% · 🟡 30–60% · 🟢 > 60%

---

**R2. Tasa de Escalación (TE)**

- *Qué mide:* Qué proporción de conversaciones terminó en manos de un agente humano.
- *Cómo se calcula:* `escalated_conversations / total_conversations × 100`
- *Cómo se interpreta:* Alta escalación no siempre es mala si es apropiada (el caso genuinamente requería humano). El problema es la escalación evitable: casos que FIN podría haber resuelto.
- *Semáforo:* 🔴 > 70% · 🟡 40–70% · 🟢 < 40%

---

**R3. Tasa de Escalación Evitable (TEE)**

- *Qué mide:* De las conversaciones escaladas, cuántas tenían una intención cubierta por KB y pautas.
- *Cómo se calcula:* `escalaciones_donde_KB_y_pauta_existen / total_escalaciones × 100`
- *Cómo se interpreta:* Mide el desperdicio del sistema. Una TEE del 60% significa que 6 de cada 10 escalaciones no debieron ocurrir.
- *Semáforo:* 🔴 > 50% · 🟡 25–50% · 🟢 < 25%

---

**R4. Delay de Escalamiento (DE)**

- *Qué mide:* Cuántos turnos pasan entre que el usuario pide hablar con un agente y FIN lo escala.
- *Cómo se calcula:* Promedio de (turno de escalación efectiva − turno de primera solicitud de agente) en conversaciones donde el usuario pidió agente.
- *Cómo se interpreta:* Debería ser ≤ 1 turno. Cada turno adicional es frustración innecesaria. Un DE de 3 significa que FIN hizo 2 preguntas más después de que el usuario ya pidió un humano.
- *Semáforo:* 🔴 > 3 turnos · 🟡 2–3 · 🟢 ≤ 1

---

**R5. Índice de Conversación Eficiente (ICE)**

- *Qué mide:* Si la conversación resolvió el problema en el menor número de turnos posible.
- *Cómo se calcula:* `1 - (partes_reales / partes_esperadas_para_esa_intención)` donde partes_esperadas es el promedio de las conversaciones mejor resueltas de esa misma intención.
- *Cómo se interpreta:* Un ICE de 1.0 es perfecto. Un ICE negativo indica que la conversación tomó el doble de lo esperado.

---

### Categoría B — Experiencia del Cliente

---

**E1. Índice de Frustración Promedio (IFP)**

- *Qué mide:* El nivel promedio de frustración del usuario en las conversaciones del período.
- *Cómo se calcula:* Promedio del campo `frustration_score` (0–100) del dataset estructurado. Si no hay dataset, se estima desde señales del transcript: repetición del problema, solicitudes de agente, lenguaje explícito de frustración.
- *Cómo se interpreta:* Por encima de 65 indica que la mayoría de usuarios termina frustrada. Es un predictor de churn y de rating bajo.
- *Semáforo:* 🔴 > 65 · 🟡 40–65 · 🟢 < 40

---

**E2. Riesgo de Churn Promedio (RCP)**

- *Qué mide:* El riesgo promedio de cancelación o abandono del producto generado por las interacciones de FIN.
- *Cómo se calcula:* Promedio de `churn_risk` (0–100) del dataset.
- *Cómo se interpreta:* Un RCP de 50 significa que el agente está generando, en promedio, un riesgo moderado de churn. Correlacionar con tipo de plan (PREMIUM tiene mayor impacto de churn).
- *Semáforo:* 🔴 > 50 · 🟡 30–50 · 🟢 < 30

---

**E3. Rating Promedio Ponderado (RPP)**

- *Qué mide:* La satisfacción declarada por el usuario en las conversaciones que tienen calificación.
- *Cómo se calcula:* Promedio de ratings (1–5) de conversaciones con rating. Se pondera por tipo de plan (PREMIUM = doble peso).
- *Cómo se interpreta:* Por debajo de 3.5 hay un problema de satisfacción significativo. Por encima de 4.5 indica un agente muy bien percibido.
- *Semáforo:* 🔴 < 3.0 · 🟡 3.0–4.0 · 🟢 > 4.0

---

**E4. Cobertura de Rating (CR)**

- *Qué mide:* Qué porcentaje de conversaciones tiene calificación del usuario.
- *Cómo se calcula:* `conversaciones_con_rating / total_conversaciones × 100`
- *Cómo se interpreta:* Una cobertura baja hace que el rating promedio sea poco representativo. Por debajo del 15% el RPP es estadísticamente débil.

---

**E5. Tasa de Emoción Negativa (TEN)**

- *Qué mide:* Qué proporción de conversaciones tiene el atributo Emociones=Negative.
- *Cómo se calcula:* `conversaciones_con_emociones_negative / total × 100`
- *Cómo se interpreta:* Un indicador proxy de NPS. Una TEN de 80% indica que FIN está generando experiencias mayoritariamente negativas.
- *Semáforo:* 🔴 > 70% · 🟡 40–70% · 🟢 < 40%

---

### Categoría C — Calidad de FIN como Agente

---

**Q1. Calidad de Diagnóstico Promedio (CDP)**

- *Qué mide:* Qué tan bien FIN identifica y entiende el problema del usuario antes de responder.
- *Cómo se calcula:* Promedio de `calidad_diagnostico` (0–100) del dataset estructurado.
- *Cómo se interpreta:* Un diagnóstico de baja calidad lleva a respuestas irrelevantes. Por debajo de 50 indica que FIN frecuentemente malinterpreta la intención.
- *Semáforo:* 🔴 < 50 · 🟡 50–70 · 🟢 > 70

---

**Q2. Tasa de Error Repetido (TER)**

- *Qué mide:* Porcentaje de conversaciones donde se detectó el mismo tipo de error principal que en períodos anteriores.
- *Cómo se calcula:* Compara los `error_principal` del dataset actual vs el dataset del período anterior. Agrupa por tipo de error.
- *Cómo se interpreta:* Si el mismo error se repite período a período, ninguna mejora lo ha resuelto. Alta TER = deuda conversacional sin resolver.

---

**Q3. Índice de Número de Intentos (INI)**

- *Qué mide:* Cuántas veces el usuario tiene que repetir o reformular su problema antes de que FIN lo entienda.
- *Cómo se calcula:* Promedio del campo `numero_intentos_usuario` del dataset.
- *Cómo se interpreta:* Debería ser ≤ 2. Más de 3 intentos indica que FIN no está captando el contexto en los primeros turnos.
- *Semáforo:* 🔴 > 3 · 🟡 2–3 · 🟢 ≤ 2

---

### Categoría D — Pautas y Knowledge Base

---

**P1. Cobertura de Pautas (CP)**

- *Qué mide:* Qué porcentaje del repositorio de pautas se activó al menos una vez en el período.
- *Cómo se calcula:* `pautas_activadas_en_período / total_pautas_repositorio × 100`
- *Cómo se interpreta:* Pautas que nunca se activan son costo de mantenimiento sin beneficio. Una cobertura del 50% indica que la mitad del repositorio está inactiva.

---

**P2. Índice de Conflicto de Pautas (ICP)**

- *Qué mide:* Qué porcentaje de conversaciones activan pautas que están en conflicto entre sí.
- *Cómo se calcula:* `conversaciones_con_conflicto / total × 100`
- *Cómo se interpreta:* Cada conflicto es una incoherencia en el comportamiento de FIN. Un ICP alto explica respuestas contradictorias o impredecibles.

---

**K1. Tasa de Utilización de KB (TUK)**

- *Qué mide:* En qué porcentaje de conversaciones FIN usó al menos un artículo de KB.
- *Cómo se calcula:* `conversaciones_con_articulo_usado / total × 100`
- *Cómo se interpreta:* FIN tiene la KB disponible pero no siempre la usa. Una TUK baja indica que FIN responde desde el prompt/pautas en lugar de desde el conocimiento validado.
- *Semáforo:* 🔴 < 30% · 🟡 30–60% · 🟢 > 60%

---

**K2. Ratio de Brecha de KB (RBK)**

- *Qué mide:* Qué porcentaje de intenciones frecuentes no tiene artículo de KB publicado.
- *Cómo se calcula:* `intenciones_sin_articulo / total_intenciones_frecuentes × 100`
- *Cómo se interpreta:* Un RBK del 40% significa que 4 de cada 10 tipos de consulta no tienen soporte documental. FIN los atiende solo con pautas o prompt base.

---

## 6. FIN Intelligence Score

### Modelo completo de puntuación

El FIN Intelligence Score (FIS) es el indicador maestro del ecosistema. Se calcula como suma ponderada de 6 dimensiones, con penalizaciones, hard caps y bonificaciones.

---

### Dimensiones y pesos base

| # | Dimensión | Peso | KPIs que la alimentan |
|---|-----------|------|-----------------------|
| 1 | **Resolución** | 25% | TRR, TE, TEE, DE |
| 2 | **Experiencia del Cliente** | 25% | IFP, RCP, RPP, TEN |
| 3 | **Calidad de Diagnóstico** | 20% | CDP, TER, INI |
| 4 | **Cobertura de Conocimiento** | 15% | TUK, RBK, Knowledge Health |
| 5 | **Salud del Repositorio** | 10% | CP, ICP, Guideline Health |
| 6 | **Eficiencia Operacional** | 5% | avg_parts, ICE, Workflow Health |

---

### Cálculo por dimensión

```
D1_Resolución = (TRR × 0.50) + ((100 − TE) × 0.25) + ((100 − TEE) × 0.15) + ((100 − DE_norm) × 0.10)
  donde DE_norm = min(DE × 25, 100)

D2_Experiencia = ((100 − IFP) × 0.35) + ((100 − RCP) × 0.30) + (RPP_norm × 0.25) + ((100 − TEN) × 0.10)
  donde RPP_norm = (RPP − 1) / 4 × 100

D3_Diagnóstico = (CDP × 0.50) + ((100 − TER) × 0.30) + ((100 − INI_norm) × 0.20)
  donde INI_norm = min(INI × 20, 100)

D4_Conocimiento = (TUK × 0.50) + ((100 − RBK) × 0.30) + (Knowledge_Health × 0.20)

D5_Repositorio = (CP × 0.40) + ((100 − ICP) × 0.40) + (Guideline_Health × 0.20)

D6_Eficiencia = (ICE_norm × 0.50) + (Workflow_Health × 0.50)
  donde ICE_norm = max(ICE × 100, 0)
```

---

### Score base

```
FIS_base = (D1 × 0.25) + (D2 × 0.25) + (D3 × 0.20) + (D4 × 0.15) + (D5 × 0.10) + (D6 × 0.05)
```

---

### Penalizaciones (reducen el score)

| Condición | Penalización |
|-----------|-------------|
| Churn_risk > 70 en > 20% de conversaciones | −10 puntos |
| Rating promedio < 2.5 | −8 puntos |
| Delay de escalamiento > 4 turnos en promedio | −6 puntos |
| Tasa de conflicto de pautas > 40% | −5 puntos |
| KB utilization < 20% | −5 puntos |
| Error repetido en > 60% de conversaciones vs período anterior | −5 puntos |

---

### Hard Caps (el score no puede superar cierto valor si se cumplen estas condiciones)

| Condición | Hard Cap |
|-----------|---------|
| Tasa de resolución real < 10% | Score máximo: 40 |
| Churn risk promedio > 60 | Score máximo: 50 |
| Rating promedio < 2.0 con cobertura > 30% | Score máximo: 45 |
| Operational Risk = ALTO por > 3 semanas consecutivas | Score máximo: 55 |

---

### Bonificaciones (suman al score, máximo +10 puntos totales)

| Condición | Bonificación |
|-----------|-------------|
| TRR > 75% | +5 puntos |
| Tendencia positiva por 3 períodos consecutivos | +3 puntos |
| Rating promedio > 4.5 con cobertura > 30% | +3 puntos |
| Cero conflictos de pautas detectados | +2 puntos |

---

### Score final

```
FIS_final = clamp(FIS_base − penalizaciones + bonificaciones, 0, 100)
```

---

### Niveles de interpretación

| Score | Nivel | Color | Descripción | Acción esperada |
|-------|-------|-------|-------------|-----------------|
| 85–100 | **Excelente** | 🟢 | FIN opera como agente experto autónomo | Mantener y expandir cobertura |
| 70–84 | **Bueno** | 🟢 | Performance sólido con oportunidades de mejora | Optimización incremental |
| 55–69 | **Regular** | 🟡 | Problemas estructurales identificables | Plan de mejora activo en 2 semanas |
| 40–54 | **Deficiente** | 🟡 | Fallas sistémicas afectando la experiencia | Intervención urgente |
| 0–39 | **Crítico** | 🔴 | El agente está causando daño activo | Revisión inmediata del ecosistema completo |

---

### Benchmark de referencia

El sistema mantiene tres benchmarks:

1. **Benchmark histórico:** El mejor score alcanzado por el mismo producto en cualquier período previo.
2. **Benchmark de target:** Configurado manualmente por el administrador (ej. "queremos llegar a 75 para Q3").
3. **Benchmark entre productos:** Comparativa del score entre Restobar, Pymes, Nómina y Alojamientos.

---

## 7. Sistema de Recomendaciones

### Principios

1. Cada recomendación cita la evidencia que la generó (ID de conversación, turno específico).
2. Cada recomendación tiene un impacto estimado en puntos del FIS.
3. Las recomendaciones se actualizan automáticamente cada vez que se ejecuta una revisión.
4. Una recomendación implementada se valida en el siguiente período con las métricas reales.

---

### Niveles de prioridad

**CRÍTICO** — Requiere acción en < 24 horas

Criterios de asignación:
- Está generando daño activo (churn risk > 80, rating = 1)
- Un error se repite en > 50% de conversaciones del día
- Hay un riesgo operativo activo sin resolución
- El FIS cayó más de 15 puntos vs el período anterior

Formato: Alerta visual prominente en el Dashboard. Notificación push al líder operativo.

---

**ALTO** — Requiere acción en < 1 semana

Criterios de asignación:
- Afecta a > 30% de conversaciones del período
- Tiene impacto estimado en FIS de > 5 puntos
- Involucra una intención de alta frecuencia sin resolución

---

**MEDIO** — Requiere planificación en el próximo sprint

Criterios de asignación:
- Afecta a 10–30% de conversaciones
- Tiene impacto estimado de 2–5 puntos en FIS
- Es recurrente en más de 2 períodos

---

**BAJO** — Mejora de calidad, sin urgencia

Criterios de asignación:
- Afecta a < 10% de conversaciones
- Impacto < 2 puntos en FIS
- No hay señal de frustración o churn asociada

---

### Tipos de recomendación

**Quick Wins**  
Definición: Alto impacto estimado, baja complejidad de implementación.  
Criterio: Impacto ≥ 3 puntos FIS + tiempo de implementación ≤ 2 horas.  
Ejemplos: Ajustar el delay de escalamiento en una pauta. Publicar un artículo ya en borrador. Modificar el umbral de detección de un atributo.

**Mejoras Estructurales**  
Definición: Cambios de mediano plazo que requieren diseño y prueba.  
Criterio: Impacto ≥ 5 puntos FIS + tiempo de implementación de días o semanas.  
Ejemplos: Diseñar un nuevo workflow para una intención de alta frecuencia. Crear un conjunto de 5 pautas nuevas para un escenario no cubierto. Publicar 3 artículos de KB para cubrir una brecha temática identificada.

**Deuda Técnica**  
Definición: Componentes desactualizados o conflictos conocidos que no se han resuelto.  
Criterio: Detectada en > 2 períodos consecutivos sin acción.  
Ejemplos: Pautas en conflicto no resueltas. Atributos con baja tasa de detección desde hace meses. Workflows con nodos de salida inesperada recurrentes.

**Deuda Conversacional**  
Definición: Patrones de error de FIN que se repiten sin que ninguna pauta o mejora los haya abordado.  
Criterio: El mismo `error_principal` aparece en > 3 conversaciones en > 2 períodos.  
Ejemplos: FIN siempre hace las mismas 3 preguntas innecesarias antes de escalar. FIN siempre usa el artículo equivocado para una intención específica.

**Deuda de Conocimiento**  
Definición: Brechas de KB identificadas que persisten sin artículo publicado.  
Criterio: El mismo tema aparece como gap en > 2 períodos y tiene > 5 conversaciones asociadas.  
Ejemplos: "Anulación de POS desde caja cerrada" aparece en 8 conversaciones sin artículo. "PSE fallido en suscripción PLUS" tiene 6 conversaciones sin guía de troubleshooting.

---

### Formato estándar de una recomendación

```
┌────────────────────────────────────────────────────────────────────┐
│  [PRIORIDAD]  [TIPO]                       Impacto estimado: +X FIS│
├────────────────────────────────────────────────────────────────────┤
│  PROBLEMA                                                          │
│  [Descripción concisa del problema detectado]                      │
│                                                                    │
│  EVIDENCIA                                                         │
│  • Conv 215474859325975 [turno 14]: "ayuda de alguien por favor"  │
│    → FIN hizo 2 preguntas más antes de escalar                     │
│  • Conv 215474856178695 [turno 8]: misma secuencia                 │
│                                                                    │
│  ACCIÓN RECOMENDADA                                                │
│  [Instrucción exacta y ejecutable]                                 │
│                                                                    │
│  MÉTRICA DE ÉXITO                                                  │
│  Delay de escalamiento ≤ 1 turno en > 80% de conversaciones       │
│                                                                    │
│  ESFUERZO ESTIMADO: [Bajo / Medio / Alto]                          │
└────────────────────────────────────────────────────────────────────┘
```

---

## 8. Sistema de Auditorías Automáticas

FIN Architect Enterprise ejecuta auditorías programadas y bajo demanda. Cada auditoría produce un reporte específico y actualiza el estado de los indicadores relevantes.

---

### 8.1 Auditoría Diaria Rápida

**Frecuencia:** Automática, cada día hábil.  
**Duración estimada:** 2–3 minutos.  
**Alcance:** Últimas 24 horas de conversaciones.

**Qué revisa:**
- Variación del FIS vs día anterior
- Alertas críticas nuevas (churn_risk > 80, rating = 1, escalación de urgencia alta)
- Nuevas intenciones no reconocidas (AI Title no visto antes)
- Conversaciones outlier (> P99 de partes o de frustración)

**Output:** Resumen ejecutivo de una pantalla. Notificación al líder operativo si hay alertas críticas.

---

### 8.2 Auditoría Semanal Completa

**Frecuencia:** Lunes de cada semana, cubriendo la semana anterior.  
**Duración estimada:** 10–15 minutos.  
**Alcance:** Todos los módulos del sistema.

**Qué revisa:**
- FIS semanal con desglose de 6 dimensiones
- Todos los KPIs de las categorías A, B, C, D
- Top 5 recomendaciones nuevas
- Estado de recomendaciones previas (implementadas / pendientes / vencidas)
- Evolución de pautas: nuevas activaciones, pautas que dejaron de activarse
- Uso de KB: artículos nuevos usados, artículos que dejaron de usarse
- Resumen de escalaciones de la semana

**Output:** Reporte completo en formato texto. Actualización del Historical Evolution.

---

### 8.3 Auditoría Mensual Estratégica

**Frecuencia:** Primer día hábil de cada mes.  
**Duración estimada:** 20–30 minutos.  
**Alcance:** Mes completo + comparativa vs mes anterior.

**Qué revisa:**
- Todo lo de la auditoría semanal + comparativa de períodos
- Tendencias de 3 meses
- Análisis de deudas (técnica, conversacional, de conocimiento)
- Benchmarks: entre productos, vs histórico, vs target
- ROI de mejoras implementadas el mes anterior
- Propuesta de roadmap para el mes siguiente

**Output:** Reporte ejecutivo para PM + Director de Soporte. Actualización del benchmark histórico.

---

### 8.4 Auditoría Pre-Publicación

**Cuándo:** Antes de publicar cambios al ecosistema (nueva pauta, nuevo workflow, nuevo atributo, nuevo artículo KB).  
**Duración estimada:** 5 minutos.  
**Disparador:** Manual, iniciada por el Administrador Intercom.

**Qué revisa:**
- La nueva pauta/artículo/atributo vs el repositorio existente (`detect_conflicts`)
- Simulación del comportamiento de FIN con el nuevo componente (`simulate_fin`)
- Score de calidad del nuevo componente (`score_guideline`)
- Clasificación del nuevo componente (`classify_guideline`)
- Cobertura: ¿qué gap cubre el nuevo componente?

**Output:** Reporte de impacto potencial. Aprobación o advertencia antes de publicar.

---

### 8.5 Auditoría de Knowledge Base

**Frecuencia:** Mensual o bajo demanda.  
**Alcance:** Todo el inventario de KB (1,036 artículos en el estado actual).

**Qué revisa:**
- Artículos en borrador por más de 30 días
- Artículos no usados por FIN en > 60 días
- Artículos potencialmente desactualizados (última actualización > 6 meses)
- Artículos duplicados o con títulos muy similares
- Brechas temáticas: intenciones sin artículo
- Distribución de artículos por producto: ¿hay productos con KB insuficiente?
- Artículos sin descripción

**Output:** Reporte de salud de KB. Lista priorizada de acciones editoriales.

---

### 8.6 Auditoría de Atributos

**Frecuencia:** Mensual o ante cambio de workflow.  
**Alcance:** Todos los atributos de conversación configurados.

**Qué revisa:**
- Tasa de detección por atributo: ¿cuáles casi nunca se completan?
- Consistencia: misma situación → mismo atributo siempre
- Atributos que cambian el comportamiento de FIN vs atributos que nunca se usan en lógica
- IACR: ¿se clasifica correctamente el riesgo en conversaciones de alto riesgo?
- Fuera de Horario: ¿el flujo nocturno funciona como se espera?

**Output:** Reporte de salud de atributos. Propuestas de nuevos atributos o ajuste de condiciones.

---

### 8.7 Auditoría de Workflows

**Frecuencia:** Bimestral o ante cambio de flujo.  
**Alcance:** Todos los workflows activos por producto.

**Qué revisa:**
- Tasa de completitud de flujo: ¿los usuarios lo completan o lo abandonan?
- Nodos con alta tasa de salida inesperada
- Intenciones sin workflow dedicado que usan el flujo genérico
- Consistencia entre el nodo de entrada elegido por el usuario y la intención real
- Workflows con 0 conversaciones en el período (candidatos a deprecación)

**Output:** Mapa de salud de workflows. Propuestas de ajuste o nuevos flujos.

---

### 8.8 Auditoría de Escalamientos

**Frecuencia:** Semanal (integrada en la auditoría semanal) o bajo demanda.  
**Alcance:** Todas las conversaciones escaladas del período.

**Qué revisa:**
- Distribución por motivo de escalación
- Delay promedio de escalamiento
- Calidad del contexto entregado al agente humano en el handoff
- Horario de escalaciones: ¿cuándo ocurren los picos?
- Escalaciones por tipo de plan (PREMIUM vs base)
- Conversaciones donde el usuario tuvo que pedir el agente más de una vez

**Output:** Reporte de escalamientos. Propuestas para reducir escalaciones evitables.

---

### 8.9 Auditoría de Nuevas Pautas

**Cuándo:** 7 días después de publicar una nueva pauta.  
**Disparador:** Automático si el sistema sabe cuándo se publicó la pauta.

**Qué revisa:**
- ¿La pauta se activó al menos una vez?
- En las conversaciones donde se activó, ¿redujo el error que debía prevenir?
- ¿Generó algún efecto no deseado (conflicto con otra pauta, respuestas más largas, más escalaciones)?
- ¿El score de la pauta mejoró vs la evaluación pre-publicación?

**Output:** Reporte de impacto de pauta nueva. Confirmación de que funciona como se esperaba o alerta de ajuste necesario.

---

## 9. Roadmap

### v1 — FIN Architect Core (estado actual)

**Estado:** Implementado

- Herramientas MCP individuales: audit_guideline, optimize_guideline, classify_guideline, detect_conflicts, score_guideline, simulate_fin, generate_guideline, extract_guidelines, architect_review
- Dataset estructurado de 25 conversaciones reales
- Knowledge Digital Twin (1,036 artículos inventariados)
- Arquitectura de fin_intelligence_review()
- Documento de arquitectura Enterprise (este documento)

---

### v2 — FIN Intelligence Engine

**Objetivo:** Implementar el motor de inteligencia completo.  
**Prioridad:** Máxima.

Componentes:
- `fin_intelligence_review()` implementada con los 6 módulos internos
- FIN Intelligence Score calculado automáticamente
- Dashboard principal con los 12 indicadores
- Sistema de recomendaciones (3 capas)
- Auditoría semanal automática
- Exportación de reportes en texto estructurado

Métricas de éxito de v2:
- El FIS se puede calcular para cualquier período con datos reales
- El sistema genera al menos 5 recomendaciones accionables por período
- La auditoría semanal tarda menos de 15 minutos en ejecutarse

---

### v3 — FIN Analytics Platform

**Objetivo:** Añadir profundidad analítica y visualizaciones.

Componentes:
- Historical Evolution: tracking del FIS en el tiempo
- Benchmarks entre productos
- Conversation Analytics con filtros avanzados
- Escalation Analytics con análisis de delay
- Knowledge Analytics con mapa de brechas
- Auditoría de KB automática mensual
- Sistema de pre-publicación (auditoría antes de publicar cambios)

Métricas de éxito de v3:
- El equipo puede comparar el performance de FIN entre Restobar y Pymes
- La auditoría pre-publicación previene al menos 1 conflicto por mes
- Se puede ver la tendencia del FIS de los últimos 6 meses

---

### v4 — FIN Improvement System

**Objetivo:** Cerrar el ciclo: detectar → recomendar → implementar → validar.

Componentes:
- Improvement Center: cola de mejoras con estado y responsable
- Tracking de impacto: antes vs después de implementar una mejora
- Generador de pautas integrado en el flujo de recomendaciones
- Auditoría de nuevas pautas (7 días post-publicación)
- Risk Center: alertas de churn y operacionales en tiempo real
- Attribute Analytics completo

Métricas de éxito de v4:
- El tiempo entre detectar un problema y tener una pauta publicada baja a < 48h
- El ROI de las mejoras implementadas es medible y visible
- El FIS mejora en promedio 5 puntos por mes durante los primeros 3 meses

---

### Enterprise — FIN Architect Enterprise

**Objetivo:** Producto completo multi-producto, multi-usuario, con automatización total.

Componentes:
- Dashboard multi-producto: vista unificada de Restobar + Pymes + Nómina + Alojamientos
- Perfiles de usuario con vistas personalizadas (Director / Líder / Admin / Arquitecto / PM)
- Auditorías 100% automáticas (diaria, semanal, mensual)
- Sistema de alertas: notificaciones al equipo cuando el FIS cae o hay alerta crítica
- API de integración: el ecosistema de FIN Architect puede alimentar otras herramientas
- Modo simulación avanzado: predice el impacto de un cambio antes de implementarlo
- Memoria conversacional: el sistema recuerda patrones de períodos anteriores y ajusta sus recomendaciones
- Roadmap de optimización generado automáticamente para cada producto

Métricas de éxito Enterprise:
- El Director de Soporte revisa el FIS cada semana en < 5 minutos
- El Administrador Intercom implementa mejoras directamente desde el Improvement Center
- El FIS de todos los productos supera 70 en el primer año
- El número de escalaciones evitables cae un 40% respecto al estado inicial

---

## 10. Conclusión

### Por qué FIN Architect Enterprise supera la auditoría tradicional de Intercom

Una auditoría tradicional de Intercom es retrospectiva, manual y de baja frecuencia. Un analista revisa conversaciones manualmente, extrae conclusiones subjetivas, escribe un reporte y lo entrega. El ciclo dura semanas. El reporte envejece desde el momento en que se produce. Las recomendaciones carecen de priorización sistemática. No hay forma de medir si las mejoras funcionaron.

FIN Architect Enterprise es un sistema de control continuo.

**Continuo:** No es un reporte de fin de mes. Es un motor que corre todos los días, actualiza los indicadores y alerta cuando algo cambia.

**Sistémico:** No audita conversaciones individuales. Audita el sistema que las genera. Identifica por qué FIN toma las decisiones que toma, no solo qué resultado producen.

**Accionable:** Cada hallazgo viene con una instrucción concreta de qué cambiar, dónde cambiarlo, y cuánto impacto tendrá. El analista no tiene que interpretar: tiene que ejecutar.

**Medible:** Después de implementar un cambio, el sistema mide si funcionó. El ROI de cada mejora es visible. El equipo sabe si está avanzando o no.

**Evolutivo:** Cada período que pasa, el sistema tiene más datos, patrones más sólidos y recomendaciones más precisas. Aprende del historial.

**Multi-capa:** Cubre al mismo tiempo las pautas, la KB, los workflows, los atributos, los escalamientos y la experiencia del cliente. No hay punto ciego.

Una auditoría tradicional responde: *¿Qué pasó el mes pasado?*  
FIN Architect Enterprise responde: *¿Qué está pasando hoy, por qué, qué hacer mañana y cómo saber si funcionó?*

Esa es la diferencia entre una herramienta de reporte y una plataforma de inteligencia operacional.

---

*FIN Architect Enterprise — Blueprint Oficial v1.0*  
*Fase 5 | 2026-06-26*
