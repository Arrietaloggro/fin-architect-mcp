# INFORME EJECUTIVO — FIN ARCHITECT · JUNIO 2026

**Alcance temporal:** 1–30 de junio de 2026
**Generado:** 2 de julio de 2026
**Fuente:** Totalidad de artefactos reales del repositorio `fin-architect-mcp` (datasets de conversaciones extraídos de Intercom, inventario de Base de Conocimiento, auditoría operacional de agente humano, documentación de arquitectura, changelog e historial de commits)
**Analista:** FIN Architect (revisión consolidada)

---

## Nota metodológica — léase antes de usar este informe

Este informe se construyó exclusivamente con datos reales existentes en el repositorio del proyecto. **No contiene cifras estimadas, inventadas o extrapoladas.** Donde el proyecto no genera o no almacena un dato, se declara explícitamente como **"NO DISPONIBLE"** en vez de aproximarlo.

Tres precisiones estructurales que condicionan todo el informe:

1. **El proyecto "FIN Architect MCP" nació en junio 2026.** Los 120 commits del repositorio van del 24 al 30 de junio de 2026. No existe línea base de meses anteriores — por lo tanto **no hay evolución histórica que comparar** (Sección 1) más allá de la propia progresión interna del mes.
2. **No existe un registro del volumen total de conversaciones que FIN gestionó en junio.** Los únicos datos reales de conversaciones son dos muestras extraídas manualmente de Intercom el 26 de junio de 2026:
   - **25 conversaciones** (`dataset_fin_25_conversaciones.md/csv/json`), 100% del producto Restobar, 100% con escalamiento a humano (`escaló = Sí` en las 25). Es una muestra **deliberadamente sesgada hacia casos escalados/problemáticos**, no una muestra aleatoria del volumen total.
   - **5 conversaciones adicionales** (`auditoria_fin_5_conversaciones.md`), las más recientes del sistema al 26 de junio — 3 de Restobar, 2 de Alojamientos.
   - Una conversación (ID `215474851839804`, RIOPARK BEACH HOTEL) aparece en ambas muestras. **Total de conversaciones únicas analizadas: 29.**
   - Todo lo que este informe reporta sobre "chats", "temas", "pautas", "atributos" y "calidad conversacional" se basa en esas **29 conversaciones**, no en el universo completo de interacciones de FIN durante junio, cuyo volumen total **no está disponible** en el proyecto.
3. **Existe una auditoría real independiente sobre un agente HUMANO**, no sobre el bot FIN: `reports/auditoria_diana_zarate_jun2026.md`, 54 casos gestionados por Diana Milena Zarate Beltrán en el inbox "Diagnóstico Restobar" entre el 1 y el 25 de junio de 2026. Se cita en este informe donde es relevante (SLA de escalamiento humano), pero **no se mezcla con el desempeño de FIN** porque mide a una persona, no al bot.

Donde el informe propone pautas, atributos o mejoras nuevas (Secciones 8, 9 y 13), estas son **generadas por el analista a partir de patrones reales documentados en las 29 conversaciones** — cada una cita el caso de origen. No son speculación sin base.

---

## 1. RESUMEN EJECUTIVO

### 1.1 Estado general del mes

Junio 2026 fue el mes de **construcción completa** del sistema FIN Architect MCP — la plataforma de auditoría y mejora continua del agente conversacional FIN (bot "Lia", `admin_id 9218425`). En 7 días de desarrollo activo (24–30 de junio) se construyeron:

| Entregable | Estado al 30 de junio |
|---|---|
| 15 herramientas MCP (`server.py`, 6,636 líneas) | ✅ Implementadas y en producción interna |
| Motor de decisión centralizado (`decision_engine.py`, 1,264 líneas, 34 funciones, 45 constantes) | ✅ Consolidado (3 sprints de refactor, ~1,353 líneas duplicadas eliminadas) |
| Inventario completo de Base de Conocimiento (`knowledge_inventory.json/csv`, `KNOWLEDGE_DIGITAL_TWIN.md`) | ✅ 1,036 artículos catalogados |
| Dataset de entrenamiento (25 conversaciones Restobar, 36 campos c/u) | ✅ Completo |
| Auditoría profunda de 5 conversaciones recientes (19 campos c/u) | ✅ Completa |
| Blueprints de arquitectura (`FIN_ARCHITECT_ENTERPRISE.md` v1.1, `FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md`, `FIN_CONTINUOUS_LEARNING_ENGINE.md`) | ✅ Diseñados, **no implementados en código** |
| `FIN_ARCHITECT_OPERATIONS_MANUAL.md` | ✅ Publicado (plantilla operativa, sin datos ejecutados aún) |
| Auditoría operacional de agente humano (Diana Zarate, 54 casos) | ✅ Completa |
| Portal Interno de Incidencias Loggro (proyecto relacionado, sincroniza con Intercom) | ✅ MVP desplegado a producción (27–30 de junio), sin datos de uso real todavía |

El propio proyecto ejecutó su **Final Acceptance Test (FAT)** el 27 de junio de 2026, evaluando la madurez del software (no el desempeño de FIN con clientes):

> **Score de madurez global: 64/100 — Veredicto: 🟠 BETA.**
> Desglose: Implementación funcional 75/100 (peso 30%), Cobertura de productos 25/100 (peso 20%), Calidad del conocimiento 85/100 (peso 15%), Arquitectura e integración 90/100 (peso 15%), Datos de entrenamiento 60/100 (peso 10%), Documentación 95/100 (peso 10%).

El sistema quedó formalmente **congelado para nuevas funcionalidades** a partir del 27 de junio, entrando en modo de "validación operacional": se puede ejecutar y analizar, pero no se agregarán módulos hasta calibrar los modelos de scoring existentes con datos reales.

### 1.2 Evolución respecto a periodos anteriores

**NO DISPONIBLE.** No existe ningún artefacto de mayo de 2026 o anterior en el repositorio. Junio es el mes cero del proyecto — no hay línea base contra la cual medir evolución. Cualquier afirmación de "mejora respecto al mes anterior" sería inventada. Lo que sí puede observarse es la **progresión interna dentro de junio**: el proyecto pasó de no tener herramientas (semana del 24) a tener 15 herramientas, un motor de decisión consolidado y dos auditorías reales de conversaciones (semana del 26).

### 1.3 Hallazgos más importantes

De las 29 conversaciones reales analizadas:

- **Calidad promedio de diagnóstico (25 conversaciones escaladas):** 47.4/100 (mínimo 20, máximo 70). Esta cifra corresponde **solo a la muestra de casos escalados**, no a la calidad general de FIN.
- **Calidad promedio (5 conversaciones auditadas, muestra distinta y no sesgada por escalamiento):** 68.6/100 (rango 38–95).
- De las 25 conversaciones escaladas: **9 terminaron resueltas por el agente humano (36%)**, 4 parcialmente resueltas (16%), 5 sin resolver (20%), 4 derivadas a áreas especializadas sin resolución confirmada (16%), 1 abandono (4%), 1 sin completar por causa externa —caída de DIAN— (4%), 1 escaló hasta queja formal (4%).
- **7 patrones de error recurrentes de FIN** fueron documentados con evidencia (ver Sección 2.6): demora en escalar tras solicitud explícita repetida, respuestas iniciales incorrectas por falta de pregunta de clarificación, tiempos de primera respuesta superiores a 20 minutos en sesiones de asesoría, repetición de la misma respuesta sin escalar, información técnicamente incorrecta, bucle circular sin progresión, y escalamiento sin artículo de contexto.
- La Base de Conocimiento tiene **1,036 artículos**, de los cuales 44 están en borrador, 7 sin descripción, 7 grupos duplicados y 5 huérfanos sin colección — pero **0 marcados como obsoletos** por antigüedad.
- Un caso de **riesgo de churn crítico documentado con evidencia textual**: RIOPARK BEACH HOTEL S.A.S. amenazó explícitamente con migrar a Siigo tras una experiencia de escalamiento fallido (calificación 1/5).

### 1.4 Riesgos encontrados

| Riesgo | Evidencia |
|---|---|
| **Cobertura operacional limitada a un producto.** El dataset de entrenamiento y la mayoría del análisis cubren solo Restobar; Alojamientos tiene 2 casos, Pymes y Nómina no tienen ningún caso analizado. | `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md`: "Cobertura de productos: 25/100" |
| **Modelos de scoring sin calibrar.** El FIS (FIN Intelligence Score) y el PCS (Predicted CSAT Score) están definidos matemáticamente pero no se han contrastado con evaluación humana real. | FAT: "Madurez del scoring (FIS): Definido, no calibrado con datos reales" |
| **Dependencia total de Intercom sin almacenamiento propio.** Todo el análisis se ejecuta bajo demanda contra la API de Intercom; no existe base de datos persistente del proyecto. | `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` §7.2 |
| **Fricción de escalamiento documentada con evidencia textual.** En el caso RIOPARK, FIN respondió con una contrapregunta ("¿podrías contarme un poco más?") en lugar de escalar al primer y segundo pedido explícito de asesor humano. | `auditoria_fin_5_conversaciones.md`, Conv. 5, turnos 17–20 |
| **Riesgo de churn no detectado por el sistema.** La empresa RIOPARK tenía plan "EXTRACCION" (señal explícita de proceso de abandono) visible en los datos, y FIN no activó ningún protocolo de retención. | `auditoria_fin_5_conversaciones.md`, Conv. 5 |
| **Base de Conocimiento con huecos activos.** 7 artículos priorizados como faltantes fueron identificados directamente por casos reales sin solución documentada (Sección 10). | `dataset_fin_25_conversaciones.md`, sección "Patrones Globales" |
| **Diagnóstico inicial defectuoso como patrón, no como excepción.** 4 de 25 conversaciones (16%) muestran que FIN dio una respuesta inicial incorrecta por no preguntar una variable de bifurcación obvia antes de responder (ej. "¿el pedido ya fue pagado?", "¿tiene recetas configuradas?"). | Convs. 03, 16, 20, 24 del dataset + Conv. 1 y 2 de la auditoría de 5 |

### 1.5 Oportunidades detectadas

- **7 artículos de KB priorizados** ya identificados con evidencia de conversación real que los necesitó (Sección 10).
- **~15 propuestas concretas de nuevos atributos inteligentes** surgidas directamente del análisis caso por caso (Sección 9).
- **1 caso benchmark de excelencia documentado** (Conv. 3 de la auditoría de 5, Alojamientos, 95/100, resolución en 5 minutos, calificación 5/5) que puede usarse como plantilla de entrenamiento.
- Instrumentación ya diseñada (aunque no implementada) para calibrar el FIS y el PCS — el camino técnico ya existe, falta ejecutarlo (`FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` §9.2, objetivos a 30/90 días).

---

## 2. ANÁLISIS DE CHATS

> **Advertencia de alcance:** Los datos de esta sección provienen de las **29 conversaciones reales** descritas en la Nota Metodológica. El volumen total de conversaciones gestionadas por FIN en junio **no está disponible** en el proyecto — no existe ningún artefacto que lo reporte. Todas las cifras de esta sección son porcentajes **sobre la muestra de 29**, no sobre el total mensual.

### 2.1 Cantidad total de chats analizados

**29 conversaciones únicas** (25 del dataset principal + 5 de la auditoría profunda, con 1 caso compartido entre ambas fuentes).

| Fuente | Conversaciones | Periodo cubierto | Sesgo de muestra |
|---|---|---|---|
| `dataset_fin_25_conversaciones.md` | 25 | 2026-06-11 a 2026-06-26 | 100% escalado a humano (muestra dirigida a casos problemáticos) |
| `auditoria_fin_5_conversaciones.md` | 5 (4 nuevas + 1 compartida) | 2026-06-26 (mismo día, ventana de ~40 minutos) | Las 5 conversaciones más recientes del sistema al momento de la extracción — no filtradas por resultado |

### 2.2 Distribución por producto

| Producto | Conversaciones | % de la muestra (29) |
|---|---|---|
| Restobar | 27 | 93.1% |
| Alojamientos | 2 | 6.9% |
| Pymes | 0 | 0% |
| Nómina | 0 | 0% |

**NO DISPONIBLE:** distribución por producto sobre el volumen total de junio — el sesgo hacia Restobar es del diseño de la muestra (`FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` confirma que solo Restobar tiene dataset estructurado; Pymes y Nómina no tienen ningún caso).

### 2.3 Distribución por tipo de consulta (categorías temáticas)

Construida agrupando el campo real `intención_principal` de las 29 conversaciones (detalle completo en Sección 3):

| Categoría | Conversaciones | % de la muestra |
|---|---|---|
| Facturación electrónica (habilitación, activación, vinculación, cupos, errores DIAN) | 6 | 20.7% |
| Configuración y operación general (costos, combos, proveedores, logo) | 5 | 17.2% |
| Facturación POS (anulación, duplicación, visibilidad, sincronización represada) | 4 | 13.8% |
| Comanda, impresión y sincronización operativa (mesas, comandas) | 4 | 13.8% |
| Suscripción y pagos (vencimiento, cobro automático, PSE) | 3 | 10.3% |
| Gestión de pedidos y ventas | 2 | 6.9% |
| Alojamientos (facturación combinada, importación de servicios) | 2 | 6.9% |
| Integración con terceros (Siigo) | 1 | 3.4% |
| Cierre de caja / cuadre | 2 | 6.9%* |

*Nota: "Cierre de caja" se cuenta también dentro de comanda/sincronización en algunos casos por relación operativa directa; el total de filas puede no sumar exactamente 29 por solapamiento temático entre categorías vecinas (ej. cierre de caja bloqueado por sincronización).

### 2.4 Distribución por prioridad / urgencia

FIN no usa una etiqueta de "prioridad" estándar en las 25 conversaciones del dataset; el campo real disponible es **urgencia operativa** (`Urgency`) y **severidad del problema** (escala 1–5, definida por el analista al auditar):

| Urgencia (atributo detectado por FIN) | Conversaciones (de 25) |
|---|---|
| Baja | 18 |
| Media | 2 |
| No disponible / no capturada | 5 |

| Severidad del problema (1=leve, 5=crítico) | Conversaciones (de 25) |
|---|---|
| 1 | 1 |
| 2 | 9 |
| 3 | 9 |
| 4 | 5 |
| 5 | 1 |

**Severidad promedio: 2.76/5.** El caso de severidad 5 es la Conv. 25 (facturas represadas, contador experto, queja formal, riesgo de churn 60/100).

### 2.5 Distribución por categoría (IACR — Intención/Atributo de Contexto y Riesgo)

Frecuencia real de la categoría IACR detectada por FIN en las 25 conversaciones del dataset:

| Categoría IACR | Frecuencia |
|---|---|
| Usuario Básico | 11 |
| Riesgo Operativo | 4 |
| Cambio de Intención | 4 |
| Usuario Avanzado | 2 |
| No especificada en el registro | 4 |

La categoría "Cambio de Intención" (4 casos) es una señal de alerta: en los 4 casos donde aparece, el analista documentó que FIN **perdió el hilo de la conversación real** del usuario en algún punto (Convs. 05, 13, 16, 20).

### 2.6 Tendencias detectadas y cambios durante el mes

- **Concentración temporal fuerte:** 24 de las 25 conversaciones del dataset ocurrieron entre el 25 y el 26 de junio (últimas 48 horas antes de la extracción); solo 1 es del 11 de junio. **Esto impide identificar una tendencia real intra-mes** — la muestra no está distribuida uniformemente a lo largo de junio, así que no se puede afirmar si la calidad de FIN mejoró o empeoró durante el mes.
- **7 patrones de error recurrentes**, documentados con evidencia y frecuencia real (`dataset_fin_25_conversaciones.md`, sección "Patrones Globales Identificados"):

| Error recurrente | Frecuencia | Conversaciones afectadas |
|---|---|---|
| Demora en escalar tras pedido explícito de agente (>2 veces) | Alta | 01, 05, 07, 12 |
| Respuesta inicial incorrecta por falta de pregunta de clarificación | Alta | 03, 16, 20, 24 |
| Tiempo a primera respuesta (ttfa) > 20 minutos en sesiones de asesoría | Media | 05, 10, 15, 24 |
| Repetición de la misma respuesta sin escalar | Media | 07, 12 |
| Información técnicamente incorrecta | Baja | 15 |
| Bucle circular sin progresión | Baja | 22 |
| Escalamiento sin artículo de contexto para el agente humano | Media | 02, 09, 14 |

- **Tiempo de primera respuesta:** promedio 682 segundos (11.4 min) sobre las 25 conversaciones, con un máximo de 2,614 segundos (43.6 min, Conv. 15). **NO DISPONIBLE** el tiempo total de resolución agregado — el campo `tiempo_total_seg` está vacío ("N/D") en varios registros del dataset.

---

## 3. TEMAS MÁS FRECUENTES

> Con solo 29 casos reales, no existen literalmente "20 motivos" distintos con volumen estadístico — se listan los **motivos de contacto reales identificados**, agrupados y ordenados por frecuencia real observada. Cada fila cita la conversación de origen para trazabilidad.

### 3.1 Motivos de contacto (ordenados por frecuencia real)

| # | Motivo | Frecuencia | Producto | Severidad/Impacto | Criticidad |
|---|---|---|---|---|---|
| 1 | Habilitar/activar/vincular facturación electrónica | 6 (convs. 02, 03, 06, 17, 18, 22) | Restobar | Severidad 2–3 | Media |
| 2 | Anulación / duplicación / visibilidad de facturas POS | 4 (convs. 01, 07, 12, 25) | Restobar | Severidad 3–5 | Alta (conv. 25 = queja formal) |
| 3 | Comanda: impresión, instalación, versión, acceso | 4 (convs. 04, 05, 14, 24) | Restobar | Severidad 2–3 | Media-Alta |
| 4 | Configuración operativa (costos, combos, proveedores, logo) | 4 (convs. 10, 15, 20, 21) + audit conv. 2 | Restobar | Severidad 2 | Baja-Media |
| 5 | Suscripción / pagos (vencimiento, cobro automático, PSE) | 3 (convs. 13, 16, 19) | Restobar | Severidad 1–4 | Alta (conv. 13 = riesgo de churn 70/100) |
| 6 | Cierre de caja / cuadre | 2 (convs. 09, 23) | Restobar | Severidad 3–4 | Alta (bloqueo operativo directo) |
| 7 | Gestión de pedidos/ventas (eliminar, borrar) | 2 (conv. 08 + audit conv. 1) | Restobar | Severidad 2–3 | Media |
| 8 | Facturación electrónica combinada / importación de servicios | 2 (audit convs. 3, 4) | Alojamientos | N/D | Baja (conv. 3 fue caso benchmark positivo) |
| 9 | Integración con terceros (Siigo) | 1 (conv. 11) | Restobar | Severidad 3 | Media |

### 3.2 Top incidencias (casos con mayor impacto documentado)

| Incidencia | Caso | Impacto |
|---|---|---|
| Suscripción vencida bloqueando operación activa con clientes en el local | Audit conv. 5 / dataset conv. 13 (RIOPARK) | Amenaza de churn explícita, calificación 1/5 |
| Facturas represadas sin sincronizar a Pymes | Conv. 25 | Queja formal escrita, calificación 1/5, riesgo de churn 60/100 |
| Duplicación de factura con faltante real en cuadre de caja | Conv. 07 | Riesgo operativo/contable, sin resolución confirmada |
| Versión de comanda desactualizada no diagnosticada | Conv. 24 | 37 minutos de ttfa, calificación 2/5, sin resolución |
| Problema de impresión de comanda con rechazo de instalación remota | Conv. 05 | Calificación 2/5, sin resolución |

### 3.3 Top preguntas repetidas (mismo motivo, múltiples ocurrencias)

- "¿Cómo habilito/activo la facturación electrónica?" — 3 ocurrencias directas (convs. 02, 17, 22) más 2 relacionadas (03, 18).
- Problemas de impresión/configuración de comanda — 4 ocurrencias (convs. 04, 05, 14, 24).
- Consultas de suscripción/pago — 3 ocurrencias (convs. 13, 16, 19).

### 3.4 Top problemas funcionales (fallas del sistema, no del usuario)

| Problema funcional | Evidencia |
|---|---|
| Combos solo permiten una zona de impresión (limitación de plataforma no documentada) | Conv. 15 |
| Costo de producto sin recetas no se actualiza automáticamente (mecanismo no explicado con claridad) | Audit conv. 2 |
| Mesa queda abierta después de facturar (bug de sincronización) | Conv. 14 |
| Ícono de nube bloqueando cierre de caja sin explicación clara | Conv. 09 |
| No existe plantilla de importación masiva de servicios (Alojamientos) | Audit conv. 4 |

### 3.5 Top problemas de configuración

- Permisos de rol/usuario que bloquean visibilidad de facturas o mesas (convs. 12, audit conv. 5).
- Configuración de zonas de impresión para combos (conv. 15).
- Configuración de recetas para actualización automática de costos (audit conv. 2).
- Configuración de resolución de facturación electrónica y límites de plan (conv. 18).

### 3.6 Top solicitudes comerciales / de producto

- Solicitud de plantilla de importación masiva de servicios — funcionalidad inexistente (audit conv. 4), documentada como oportunidad de producto, no solo de soporte.
- Solicitud de excepción de acceso durante suscripción vencida (audit conv. 5) — rechazada, generó amenaza de churn.

### 3.7 Top solicitudes de soporte técnico

- Errores de integración con Siigo Nube (conv. 11).
- Errores de sincronización Restobar–Pymes (convs. 03, 25).
- Errores de backend en carga de logo (conv. 21) y asociación de resolución de facturación electrónica (conv. 06).

---

## 4. RENDIMIENTO DE LAS PAUTAS

Analizado sobre las **25 conversaciones del dataset principal** (fuente única con IDs de pauta reales y trazables; la auditoría de 5 usa nombres de pauta sin ID numérico consistente en todos los casos).

### 4.1 Pautas más utilizadas (top 15 de 55 pautas distintas identificadas)

| ID | Pauta | Frecuencia (de 25 convs.) |
|---|---|---|
| 884013 | Personalidad | 23 |
| 805165 | Detección emocional | 20 |
| 878283 | Continuidad de la respuesta | 19 |
| 880386 | Adaptación comunicativa | 19 |
| 881675 | Eliminación de ruido comunicacional | 19 |
| 883970 | Claridad progresiva | 19 |
| 878286 | Precisión comunicativa | 18 |
| 657943 | Resumen | 16 |
| 884123 | Escalamiento humano | 16 |
| 878262 | Reducción de ruido | 15 |
| 884168 | Contención de espera | 12 |
| 884062 | Uso de base de conocimiento | 11 |
| 881687 | Prevención de frustración | 10 |
| 628279 | Resolución progresiva | 8 |
| 628310 | Escalamiento por persistencia | 8 |
| 675465 | Escalamiento por intento fallido | 8 |

**Frecuencia de aplicación:** las 10 pautas "base" de comunicación (personalidad, emoción, continuidad, adaptación, ruido, claridad, precisión) se activan en 72–92% de las conversaciones — son el núcleo estable del comportamiento de FIN. Las pautas de diagnóstico y escalamiento específico (diagnóstico previo, resolución progresiva, escalamiento por persistencia) se activan en 16–32% de los casos, dependiendo del tipo de problema.

### 4.2 Cumplimiento y efectividad — pautas con evidencia de falla

De las 25 conversaciones, se documentaron explícitamente **12 instancias** donde una pauta **debió activarse y no lo hizo**, o se activó tarde:

| Pauta | Caso donde falló | Naturaleza de la falla |
|---|---|---|
| [628310] Escalamiento por persistencia | Convs. 01, 05, 07, 12 | Se activa demasiado tarde (al 3er intento en vez del 2do) |
| [884026] Obtención de contexto | Convs. 09, 16 | No pregunta la intención real antes de asumir (consulta vs. acción) |
| [884168] Contención de espera | Convs. 09, 13 | Ausente en casos de emergencia operativa real |
| [884123] Escalamiento humano | Conv. 23 | No aparece en la lista de pautas activadas pese a haber escalado (escaló por trigger de workflow, no por la pauta) |
| [635548] Diagnóstico previo | Conv. 03 | No detecta señal de conflicto Pymes/Restobar a tiempo |
| [635546] Diagnóstico | Conv. 20 | No pregunta tipo de proveedor antes de responder |

En la auditoría de 5 conversaciones, el caso más grave (Conv. 5, RIOPARK) documenta que la pauta **"Escalamiento por solicitud de atención humana" existe pero no se ejecutó al primer ni al segundo pedido explícito del usuario** — se ejecutó recién al tercero, tras dos contrapreguntas adicionales que generaron frustración medible (calificación final 1/5).

### 4.3 Clasificación de pautas por desempeño

| Clasificación | Pautas | Justificación |
|---|---|---|
| **Excelente** | [884013] Personalidad, [878283] Continuidad, [883970] Claridad progresiva | Se activan consistentemente (19–23 de 25 casos) sin ninguna falla documentada en su ejecución |
| **Buena** | [657943] Resumen, [878262] Reducción de ruido, [884062] Uso de KB | Alta frecuencia de uso, sin fallas de ejecución directamente atribuidas, pero co-ocurren con casos de baja calidad de diagnóstico |
| **Regular** | [628310] Escalamiento por persistencia, [884123] Escalamiento humano | Existen y se usan, pero fallan en el *timing* en 4–8 de los casos donde debían activarse — el problema no es la ausencia de la pauta sino su umbral de activación |
| **Deficiente** | Pauta de "Escalamiento por solicitud de atención humana" (ejecución observada en audit conv. 5) | En el único caso con evidencia detallada turno a turno, la pauta fue ignorada dos veces seguidas pese a instrucción explícita y repetida del usuario |

**NO DISPONIBLE:** una medición de cumplimiento porcentual agregado por pauta sobre el volumen total de junio — el cálculo anterior es exclusivamente sobre los 25–29 casos con evidencia documentada.

---

## 5. RENDIMIENTO DE LOS ATRIBUTOS

### 5.1 Atributos inteligentes con frecuencia real (25 conversaciones del dataset)

| Atributo | Frecuencia |
|---|---|
| Urgency Baja | 18 |
| IACR Usuario Básico | 11 |
| Validación Parcial | 9 |
| IACR Riesgo Operativo | 4 |
| IACR Cambio de Intención | 4 |
| Correctamente Validado | 4 |
| Urgency Media | 2 |
| IACR Usuario Avanzado | 2 |
| Emociones Negative | 3 |
| Fuera de horario | 2 |

### 5.2 Precisión — casos mal clasificados o ambiguos

| Atributo | Problema documentado | Caso |
|---|---|---|
| IACR Cambio de Intención | Se detecta correctamente el síntoma (el usuario cambió de tema) pero FIN no siempre reacciona bien a la señal — en la conv. 13/audit conv. 5, tras detectar "Cambio de Intención" diagnosticó *erróneamente* un problema de permisos cuando la causa real era la suscripción vencida | Audit conv. 5 |
| IACR (sin capturar) | En 4 de 25 conversaciones el campo IACR queda vacío o no especificado | Convs. 09, 14, 16, 19 (parcial) |
| Nivel de insatisfacción | Nunca se detectó como valor pese a frustración expresada explícitamente por el usuario en varios turnos | Audit conv. 1 |
| Riesgo de Churn (Restobar) | No se activó pese a que el atributo `Plan empresa = EXTRACCION` (señal de churn en curso) estaba visible en los datos de la cuenta | Audit conv. 5 |

### 5.3 Casos sin clasificación

- Audit conv. 4 (Alojamientos): el campo IACR quedó completamente vacío pese a que el analista determinó que correspondía a "Limitación de Producto" o "Funcionalidad No Disponible" — categoría que **no existe** en el catálogo actual de atributos.
- Convs. 02, 09, 19 del dataset principal: campo "Emociones" marcado como "No disponible".

### 5.4 Recomendación de gestión por atributo

| Atributo | Recomendación | Justificación |
|---|---|---|
| IACR Cambio de Intención | **Modificarse** — debe disparar una re-evaluación completa del diagnóstico, no solo un registro pasivo | Falla activa documentada en audit conv. 5 |
| Urgency (Baja/Media) | **Dividirse** — falta un nivel "Crítica/P1" que capture emergencias operativas con clientes activos | Conv. 13 y audit conv. 5 muestran urgencia real subestimada como "Media" |
| Nivel de insatisfacción | **Mantenerse, pero forzar su captura** — actualmente existe como campo pero queda vacío en la mayoría de los casos donde sería más útil | Audit convs. 1, 4 |
| IACR Usuario Básico / Usuario Avanzado | **Fusionarse en un atributo `nivel_usuario` de 4 valores** (básico/intermedio/avanzado/experto) con lógica de enrutamiento asociada (L1 vs. L2) | Sugerido explícitamente en conv. 25 tras una queja formal por repetición de pasos ya agotados por un usuario experto |
| Riesgo de Churn | **Mantenerse, pero conectarse automáticamente a `Plan empresa`** | Falla crítica documentada en audit conv. 5 (plan EXTRACCION visible, churn no detectado) |

**NO DISPONIBLE:** tasa de precisión porcentual agregada de atributos sobre el volumen total — la sección anterior documenta *fallas puntuales con evidencia*, no un porcentaje estadístico de acierto, que requeriría una muestra mayor y aleatoria.

---

## 6. ESCALAMIENTOS

> Se reportan dos fuentes de datos que **no deben combinarse**: (A) escalamientos de FIN hacia agentes humanos, documentados en las 29 conversaciones; (B) el desempeño posterior de agentes humanos gestionando esos escalamientos, documentado en la auditoría de Diana Zarate (54 casos, 1–25 junio). (B) mide a un humano, no a FIN.

### 6.1 Escalamientos de FIN — Datos reales (29 conversaciones)

- **25 de 25 conversaciones** del dataset principal fueron escaladas por FIN (100% — recordar que esta muestra fue seleccionada específicamente por tratarse de casos escalados, no es representativo de la tasa global de escalamiento de FIN).
- **2 de 5** conversaciones de la auditoría profunda no escalaron (resueltas por FIN sin intervención humana): audit convs. 2 y 3.
- **1 de 5** escaló con desenlace negativo documentado (audit conv. 5, RIOPARK, calificación 1/5).
- **2 de 5** cerraron por inactividad sin escalamiento ni confirmación de resolución ("assumed resolution", audit convs. 1 y 4).

### 6.2 Escalamientos correctos vs. evitables (con evidencia)

| Categoría | Casos | Evidencia |
|---|---|---|
| **Escalamiento correcto y oportuno** | Convs. 02, 06, 11, 17, 19, 21 — audit conv. 3 (no escaló, resolvió sola, correcto) | El analista concluyó explícitamente "que habría hecho un agente experto: idéntico a lo que hizo FIN" |
| **Escalamiento correcto pero tardío** | Convs. 01, 05, 07, 12 — audit conv. 5 | La decisión de escalar fue correcta; el *momento* de la decisión fue demasiado tarde (2–3 turnos de retraso documentados) |
| **Escalamiento potencialmente evitable con mejor diagnóstico previo** | Convs. 03, 04, 09, 16, 20, 24 | El error inicial de FIN (respuesta incorrecta, falta de pregunta de bifurcación) generó la necesidad de escalar; un diagnóstico correcto desde el primer turno pudo resolver sin intervención humana |
| **Escalamiento no ejecutado cuando debía** | Audit conv. 4 | El sistema marcó "Escalar sugerido" pero FIN no lo ejecutó — cerró por inactividad sin ofrecer conexión con asesor |

**Estimación con evidencia (no extrapolación estadística):** de las 25 conversaciones escaladas, **6 muestran evidencia textual de que el escalamiento pudo haberse evitado o acelerado con un diagnóstico inicial correcto** (convs. 03, 04, 09, 16, 20, 24) — 24% de la muestra.

### 6.3 Motivos principales de escalamiento (25 conversaciones)

| Motivo | Frecuencia |
|---|---|
| Solicitud explícita de agente humano por el usuario | 9 |
| Problema requiere acceso a backend/admin no disponible para FIN | 6 |
| Problema requiere área especializada (implementaciones, comercial) | 4 |
| Persistencia del problema tras diagnóstico agotado | 4 |
| Emergencia operativa (cierre de caja, sistema bloqueado) | 2 |

### 6.4 Productos afectados

Restobar concentra el 100% de los escalamientos documentados con evidencia (25/25 en el dataset principal; los 2 casos de Alojamientos en la auditoría de 5 no requirieron escalamiento a humano por parte de FIN, aunque uno de ellos —audit conv. 4— tenía un escalamiento sugerido y no ejecutado).

### 6.5 Oportunidades para reducir el escalamiento

1. Verificar variables de bifurcación obvias antes de la primera respuesta (¿pedido pagado o pendiente?, ¿tiene recetas configuradas?, ¿qué versión de comanda tiene?) — atacaría directamente el 24% de escalamientos potencialmente evitables identificado en 6.2.
2. Reducir el umbral de la pauta de escalamiento por persistencia de 3 a 2 intentos fallidos (sugerido en convs. 01, 12).
3. Ejecutar el escalamiento en el primer o segundo pedido explícito del usuario, sin contrapreguntas adicionales (falla crítica en audit conv. 5).
4. Adjuntar automáticamente artículo de KB relevante y resumen de diagnóstico en la nota de escalamiento al agente humano (ausente en convs. 02, 09, 14).

### 6.6 Referencia — Auditoría operacional de agente humano (Diana Zarate, 1–25 junio, no es desempeño de FIN)

Para contexto operativo, estos son los KPI reales del flujo posterior al escalamiento en el inbox "Diagnóstico Restobar":

| Métrica | Valor real |
|---|---|
| Casos totales gestionados | 54 |
| SLA de resolución ≤3 días | 100% cumplido |
| SLA de escalación interna <24h (asignación → primera gestión) | 78.4% — **meta de 90% NO cumplida** |
| Tiempo mediano de primera gestión | 5h 21m |
| Percentil 90 | ~47h 13m |
| Casos asignados sin ninguna gestión | 1 caso crítico (ID 215474812106310) |

Fuente: `reports/auditoria_diana_zarate_jun2026.md`. Esta auditoría **no debe leerse como desempeño de FIN** — mide el flujo de trabajo humano posterior al escalamiento en un inbox específico.

---

## 7. OPORTUNIDADES DE AUTOMATIZACIÓN

Identificadas directamente desde los campos reales `nueva_pauta_sugerida`, `articulo_conocimiento_faltante` y `prompt_susceptible_mejora` de las 29 conversaciones, priorizadas por impacto documentado (severidad y frecuencia).

| # | Oportunidad | Impacto esperado | Prioridad | Evidencia |
|---|---|---|---|---|
| 1 | Bifurcación automática por estado del sistema antes de responder (pedido pagado/pendiente, suscripción activa/vencida) | Reduce escalamientos evitables (~24% de la muestra) y respuestas incorrectas iniciales | **Alta** | Convs. 01, 13; audit convs. 1, 5 |
| 2 | Escalamiento inmediato sin contrapregunta cuando el usuario repite la solicitud de agente humano | Elimina la fricción documentada como "falla grave" en el caso de mayor severidad (churn amenazado) | **Alta** | Audit conv. 5, turnos 17–20 |
| 3 | Detección automática de plan "EXTRACCION" → activación de protocolo de retención en el primer turno | Convierte un riesgo de churn no detectado en una alerta proactiva | **Alta** | Audit conv. 5 |
| 4 | Reducir umbral de escalamiento por persistencia de 3 a 2 intentos fallidos | Reduce tiempo de resolución en casos con repetición de la misma respuesta (Media frecuencia) | **Alta** | Convs. 07, 12 (patrón "Repetición de misma respuesta sin escalar") |
| 5 | Verificación de versión/estado de componente antes de guiar instalación o configuración (comanda) | Evita diagnósticos largos (ttfa hasta 37 min) que terminan sin resolución | **Media** | Conv. 24 |
| 6 | Adjuntar automáticamente artículo KB + resumen de diagnóstico en la nota de escalamiento | Reduce tiempo de gestión del agente humano tras recibir el caso | **Media** | Convs. 02, 09, 14 |
| 7 | Cierre de brecha de 7 artículos de KB priorizados con evidencia de necesidad real | Reduce reincidencia de las mismas consultas sin respuesta directa | **Media** | Sección 10 |
| 8 | Auto-alerta interna si un caso permanece "Submitted"/sin gestión por más de 48h (aplica también al flujo humano post-escalamiento) | Reduce casos huérfanos como el detectado en la auditoría de Diana Zarate (1 caso crítico sin gestión) | **Media** | `reports/auditoria_diana_zarate_jun2026.md`, hallazgo #8 |
| 9 | Calibración del FIN Intelligence Score (FIS) con las 29 conversaciones ya auditadas manualmente como primer set de referencia | Habilita medición automática de calidad en vez de auditoría manual caso por caso | **Alta** (habilitador de todo lo demás) | `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` objetivo 1 (30 días) |
| 10 | Expandir el dataset de entrenamiento a Pymes y Nómina (0 casos actuales) | Condición de entrada a v2.0 según el propio proyecto | **Media** | `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` objetivo 2 (60 días) |

**Nota:** las oportunidades de automatización de mayor alcance —`fin_intelligence_review()`, el Continuous Learning Engine, y el CSAT Improvement Engine— ya están **diseñadas y documentadas en detalle** (`FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md`, `FIN_CONTINUOUS_LEARNING_ENGINE.md`), pero el propio proyecto decidió **no implementarlas hasta calibrar los módulos actuales** (congelamiento vigente desde el 27 de junio). No se listan aquí como "nuevas" porque ya existen como propuesta — la oportunidad real es ejecutarlas, no diseñarlas.

---

## 8. NUEVAS PAUTAS RECOMENDADAS

Generadas por el analista a partir de los patrones reales de fallo documentados en las Secciones 2, 4 y 6. Cada una cita el caso de origen.

### 8.1 Escalamiento inmediato ante solicitud repetida
- **Objetivo:** Escalar sin preguntas adicionales cuando el usuario pide agente humano por segunda vez en menos de 3 mensajes.
- **Justificación:** Documentado en 4 conversaciones (01, 05, 07, 12) como el patrón de error más frecuente ("Alta" frecuencia en la tabla de patrones globales); en audit conv. 5 generó la calificación más baja registrada (1/5) y una amenaza de churn explícita.
- **Problema que resuelve:** Fricción de escalamiento y frustración acumulada por contrapreguntas innecesarias.
- **Impacto esperado:** Reducción directa del patrón de error de mayor frecuencia detectado en la muestra.
- **Prioridad:** Alta.

### 8.2 Protocolo de interrupción de servicio activa
- **Objetivo:** Cuando el sistema está bloqueado (suscripción vencida, error crítico) y el usuario reporta clientes/operación en curso, escalar de inmediato sin intentar autoservicio.
- **Justificación:** Audit conv. 5 — FIN ofreció instrucciones de pago "para mañana" mientras el usuario explicaba que tenía clientes esperando en el restaurante en ese momento.
- **Problema que resuelve:** Desalineación entre la urgencia real del negocio del cliente y la respuesta de autoservicio de FIN.
- **Impacto esperado:** Reduce el riesgo de churn en el segmento de mayor impacto económico (interrupción operativa activa).
- **Prioridad:** Alta.

### 8.3 Protocolo de retención para cuentas en plan "EXTRACCION"
- **Objetivo:** Si el atributo de plan de la empresa indica proceso de baja/extracción, escalar automáticamente al equipo comercial/retención en el primer turno.
- **Justificación:** Audit conv. 5 — el dato ya estaba disponible en el sistema y no activó ninguna acción.
- **Problema que resuelve:** Churn silencioso no gestionado proactivamente.
- **Impacto esperado:** Convierte una señal ya capturada en una acción preventiva.
- **Prioridad:** Alta.

### 8.4 Verificación de variable de bifurcación antes de la primera respuesta
- **Objetivo:** Para categorías de consulta con dos rutas claramente distintas (pedido pagado/pendiente, con/sin recetas, versión de comanda), preguntar la variable de bifurcación en el primer turno.
- **Justificación:** Convs. 03, 16, 20, 24 y audit convs. 1, 2 — 6 de 29 casos (20.7%) muestran una primera respuesta incorrecta por esta causa exacta.
- **Problema que resuelve:** El patrón de error de mayor frecuencia después del escalamiento tardío.
- **Impacto esperado:** Reducción directa de re-trabajo y de escalamientos evitables (Sección 6.5).
- **Prioridad:** Alta.

### 8.5 Escalamiento L2 para usuarios expertos con pasos agotados
- **Objetivo:** Cuando el usuario declara haber realizado ya los pasos estándar, escalar directamente a soporte técnico de segundo nivel sin repetir el flujo básico.
- **Justificación:** Conv. 25 — terminó en queja formal escrita porque el agente humano (no solo FIN) repitió pasos ya realizados por un usuario identificado como "experto".
- **Problema que resuelve:** Pérdida de confianza en usuarios avanzados/técnicos.
- **Impacto esperado:** Previene el escalamiento máximo de severidad observado en la muestra (5/5).
- **Prioridad:** Media-Alta.

### 8.6 Declaración temprana de limitación del sistema
- **Objetivo:** Cuando se detecta que el usuario no cumple un prerrequisito técnico (ej. sin recetas configuradas) o que una función no existe, declarar la limitación en el turno inmediato siguiente, no seguir explicando el mecanismo que no aplica.
- **Justificación:** Audit conv. 2 (costo de productos, resolución alcanzada en 2 turnos más de lo necesario) y audit conv. 4 (plantilla de importación inexistente, oferta de ayuda vaga sin concretar alternativa).
- **Problema que resuelve:** Conversaciones innecesariamente largas y ofertas de ayuda genéricas sin acción concreta.
- **Impacto esperado:** Reducción de tiempo de resolución en consultas de información pura.
- **Prioridad:** Media.

### 8.7 Detección de loop de repetición
- **Objetivo:** Si FIN envía el mismo artículo o la misma instrucción 2 o más veces sin cambio en el resultado, escalar automáticamente.
- **Justificación:** Convs. 07 y 12 — ambas muestran repetición de 2–3 veces de la misma respuesta antes de escalar.
- **Problema que resuelve:** Patrón "Repetición de misma respuesta sin escalar" (frecuencia Media en la tabla de patrones globales).
- **Impacto esperado:** Reduce el número de turnos previos al escalamiento.
- **Prioridad:** Media.

---

## 9. NUEVOS ATRIBUTOS RECOMENDADOS

Compilados directamente del campo real `nuevo_atributo_sugerido` en las 29 conversaciones. Se seleccionan los 10 con mayor respaldo de evidencia o impacto documentado.

| # | Nombre | Descripción | Regla de clasificación | Caso de uso | Beneficio esperado |
|---|---|---|---|---|---|
| 1 | `nivel_usuario` | Nivel de experiencia técnica del cliente (básico/intermedio/avanzado/experto) | Detectar frases como "ya hice todo eso", "soy contador", "primera vez que uso esto" | Conv. 25 | Enrutamiento directo a L2 para usuarios expertos; evita repetir pasos básicos |
| 2 | `estado_bloqueo_sistema` | Tipo de bloqueo activo (suscripción vencida con operación activa / consulta administrativa / sin bloqueo) | Cruce de URL de la página + menciones de "clientes", "no puedo facturar", "sistema caído" | Audit conv. 5 | Dispara el protocolo de interrupción de servicio (Sección 8.2) |
| 3 | `hipotesis_agotada` | Marca cuando una hipótesis diagnóstica fue explícitamente negada por el usuario | El usuario contradice directamente una suposición previa de FIN | Conv. 05 | Evita que FIN vuelva a una hipótesis ya descartada |
| 4 | `usuario_primera_vez` | Señala que el cliente está en su primer día de uso del sistema | Frases como "es mi primer día", "no sé cómo funciona esto" | Conv. 08 | Deriva a capacitación en vez de soporte técnico estándar |
| 5 | `consulta_vs_accion` | Distingue si el usuario quiere información o ejecutar una acción | Enum: `consulta` / `accion`, se pregunta antes de dar pasos operativos | Conv. 16 | Evita enviar instrucciones de pago cuando el usuario solo preguntaba una fecha |
| 6 | `solicitud_funcionalidad_inexistente` | Registra que el usuario pidió una función que el sistema no tiene | Se activa cuando FIN confirma "esta función no existe" | Audit conv. 4 | Alimenta backlog de producto con evidencia real de demanda |
| 7 | `riesgo_churn_activo` (vínculo con plan de cuenta) | Cruza el campo de plan de la empresa (ej. "EXTRACCION") con el contenido de la conversación | Regla: si `plan == EXTRACCION` → forzar valor alto sin importar el tono del mensaje | Audit conv. 5 | Cierra la brecha de detección de churn documentada en 5.2 |
| 8 | `integracion_tercero_requerida` | Marca cuando la resolución depende de un proveedor externo (Siigo, DIAN, pasarela de pago) | Detectado por mención de nombre de proveedor externo o error de integración | Convs. 11, 17 | Permite fijar expectativas correctas de tiempo de resolución (fuera del control de FIN) |
| 9 | `opcion_no_encontrada` | El usuario reporta que no encuentra una opción que debería existir | Frase tipo "no veo esa opción", "no me aparece" tras instrucción de FIN | Conv. 12 | Señal temprana de posible cambio de permisos o de versión de plataforma |
| 10 | `version_componente` | Versión de la aplicación o componente instalado (ej. Comanda) declarada por el usuario | Campo de texto libre capturado en el primer turno de diagnóstico técnico | Conv. 24 | Evita reinstalaciones innecesarias cuando el problema es de versión, no de instalación |

**Atributos adicionales identificados con menor recurrencia** (para respaldo, no incluidos en la tabla principal): `error_visual_dian`, `app_comanda_activa`, `cuadre_caja_con_faltante`, `icono_nube_sincronizacion`, `mesa_abierta_post_factura`, `tipo_proveedor` (domicilio/inventario), `limite_documentos_fe`, `caja_anterior_abierta`, `requiere_backend_loggro`, `suscripcion_vencida_operativo_activo` (subsumido en `estado_bloqueo_sistema`, atributo #2).

---

## 10. OPTIMIZACIÓN DE BASE DE CONOCIMIENTO

Datos reales del inventario completo (`knowledge_inventory.json/csv`, `KNOWLEDGE_DIGITAL_TWIN.md`), snapshot tomado el 26 de junio de 2026.

### 10.1 Estado general

| Métrica | Valor real |
|---|---|
| Total de artículos | 1,036 |
| Publicados | 992 (95.8%) |
| Borradores | 44 (4.2%) |
| Sin descripción | 7 |
| Potencialmente obsoletos (sin actualizar >12 meses) | **0** |
| Grupos de artículos duplicados | 7 (14 artículos involucrados) |
| Artículos huérfanos (sin colección) | 5 |
| Artículos creados en junio 2026 | 16 |
| Artículos actualizados en junio 2026 | 33 |

### 10.2 Distribución por producto

| Producto | Total | Publicados | Borradores | % del total |
|---|---|---|---|---|
| Pymes | 443 | 433 | 10 | 42.8% |
| Restobar | 246 | 245 | 1 | 23.7% |
| Nómina | 165 | 150 | 15 | 15.9% |
| Desconocido (sin producto asignado) | 93 | 75 | 18 | 9.0% |
| Alojamientos | 89 | 89 | 0 | 8.6% |

**Hallazgo relevante:** 93 artículos (9%) no tienen producto asignado ("Desconocido") y concentran 18 de los 44 borradores del sistema — es el segmento con mayor proporción de contenido sin publicar (19.4%).

### 10.3 Artículos faltantes (identificados por casos reales sin cobertura)

Priorizados por la propia auditoría de las 25 conversaciones (`dataset_fin_25_conversaciones.md`, sección "Artículos KB Faltantes"):

1. "Mesa sigue abierta después de facturar: cómo cancelar pedido sin doble cobro" (conv. 14)
2. "Limitación de combos: zona de impresión única — alternativa con ítems separados" (conv. 15)
3. "Cómo cobrar desechables en pedidos para llevar sin impuesto INC" (conv. 10)
4. "Ícono de nube en Restobar: qué significa y cómo resolverlo" (conv. 09)
5. "Caja del día anterior sin cerrar: procedimiento de cierre" (conv. 23)
6. "Planes FE: límites de documentos por plan y cómo adquirir más" (conv. 18)
7. "Cómo verificar versión de comanda instalada" (conv. 24)

Adicionales identificados en la auditoría de 5 conversaciones:
8. "Qué hacer cuando necesitas anular un pedido ya pagado" (audit conv. 1)
9. "Cómo actualizar manualmente el costo de un producto sin recetas" (audit conv. 2)
10. "Protocolo de emergencia por suscripción vencida durante operación activa" (audit conv. 5)
11. "Alternativas de pago cuando PSE falla" (audit conv. 5)
12. "Cómo preparar y cargar servicios al sistema paso a paso (con plantilla descargable)" (audit conv. 4)

### 10.4 Artículos desactualizados

**NO DISPONIBLE en términos de antigüedad de contenido** — el inventario marca 0 artículos como "potencialmente obsoletos" bajo el criterio de "sin actualización mayor a 12 meses", porque el criterio automático evalúa solo `updated_at`, no la vigencia real del contenido frente a cambios de producto. Esto es una **limitación conocida del criterio de detección**, no una afirmación de que todo el contenido esté vigente: los 7 grupos de artículos faltantes (10.3) demuestran que existen huecos de contenido activos que el criterio de "obsolescencia por fecha" no captura.

### 10.5 Procesos repetitivos / contenido duplicado

7 grupos de artículos duplicados (mismo título, distinto producto o colección):

| Título | Productos involucrados |
|---|---|
| "Cómo contratar horas de acompañamiento, capacitación y soporte..." | Nómina / Pymes |
| "Cómo visualizar e imprimir el comprobante diario de caja" | Desconocido / Restobar |
| "Cómo consultar las deducciones no aplicadas en los pagos por control..." | Nómina / Desconocido |
| "Cómo consultar el Historial de Prórrogas de Contratos de los Empleados" | Nómina / Desconocido |
| "Cómo consultar el Informe de Compras de Inventario" | Restobar / Desconocido |
| "Cómo consultar el informe de ventas por documento" | Restobar / Desconocido |
| "Cómo eliminar gastos de forma masiva" | Restobar / Desconocido |

**Patrón identificado:** los 7 grupos de duplicados involucran consistentemente la categoría "Desconocido" como contraparte — sugiere que estos artículos deberían fusionarse y quedar asignados a un único producto en vez de existir en paralelo sin clasificación.

### 10.6 Información confusa / gaps de calidad estructural

- **5 artículos huérfanos** sin colección asignada, incluyendo contenido operativo real (ej. "Cómo consultar la central de facturas") mezclado con contenido de plantilla sin editar ("Your first public article").
- **7 artículos sin descripción**, 5 de ellos en estado borrador — reducen la capacidad de FIN de decidir si un artículo es relevante antes de citarlo.
- El uso real de KB en las 25 conversaciones muestra **52 artículos distintos citados para solo 25 casos** (más de 2 artículos distintos por conversación en promedio) — indica alta fragmentación temática: los problemas rara vez se resuelven con un solo artículo, lo que aumenta el riesgo de enviar contenido parcial o desalineado (documentado como error en 6 de 25 conversaciones).

### 10.7 Mejoras propuestas

1. Publicar o eliminar los 44 borradores — priorizando Nómina (15) y Desconocido (18), que concentran el 75% de los borradores.
2. Fusionar los 7 grupos de duplicados, asignando un producto único a cada artículo resultante.
3. Reasignar producto a los 93 artículos "Desconocido" (9% del total) — es la categoría con mayor tasa de borradores sin publicar.
4. Reclasificar los 5 artículos huérfanos dentro de una colección válida o retirarlos si son contenido de plantilla sin uso.
5. Crear los 12 artículos priorizados en 10.3, con seguimiento directo a la conversación real que evidenció la necesidad.
6. Añadir descripción a los 7 artículos que carecen de ella.
7. Revisar manualmente el criterio de "obsolescencia" — el criterio actual (antigüedad de actualización) no detecta ningún caso, pero la evidencia conversacional sí muestra huecos activos; se recomienda complementarlo con una señal de "artículo NO usado por FIN en los últimos N días pese a estar relacionado con consultas activas".

---

## 11. ANÁLISIS DE CALIDAD CONVERSACIONAL

### 11.1 Datos reales disponibles

| Fuente | Métrica | Valor |
|---|---|---|
| 25 conversaciones (dataset principal) | Calidad de diagnóstico promedio | 47.4/100 (mín. 20, máx. 70) |
| 5 conversaciones (auditoría profunda) | Calidad conversacional promedio (escala 0-100) | 68.6/100 (rango 38–95) |
| 5 conversaciones (auditoría profunda) | Nivel de frustración promedio (dataset 25) | 43.6/100 |
| 5 conversaciones (auditoría profunda) | Riesgo de churn promedio (dataset 25) | 20.6/100 (máx. 70, conv. 13) |
| 25 conversaciones | Tiempo promedio a primera respuesta | 682 segundos (11.4 min); máximo 2,614 seg (43.6 min) |

**Importante:** ambas muestras usan escalas y criterios definidos por el analista al momento de auditar (no hay un modelo de scoring automatizado y calibrado ejecutándose en producción — el FIS descrito en `FIN_ARCHITECT_ENTERPRISE.md` está diseñado pero "no calibrado con datos reales" según el propio FAT del proyecto). Los números anteriores son evaluaciones cualitativas documentadas caso por caso, no un score de sistema.

### 11.2 Claridad

- **Fortaleza documentada:** en el caso benchmark (audit conv. 3, 95/100), FIN respondió en un solo turno con 3 pasos numerados y artículos de KB vinculados por paso — "caso ejemplar que debe usarse como benchmark de calidad".
- **Debilidad documentada:** en 4 de 25 conversaciones (16%), la falta de una pregunta de clarificación inicial llevó a una respuesta inicial equivocada (convs. 03, 16, 20, 24).

### 11.3 Empatía

- Documentada como fortaleza consistente: en la mayoría de los 29 casos, el analista registra "tono empático y profesional mantenido durante toda la conversación" incluso en los casos de peor desenlace (audit conv. 5: "Entiendo, totalmente válido querer ahorrar tiempo").
- **Brecha:** empatía en el tono no se tradujo en acción — en audit conv. 5, el tono empático coexistió con la falla de escalamiento más grave de la muestra.

### 11.4 Precisión

- Un caso de información técnicamente incorrecta confirmado: conv. 15, donde FIN sugirió que era posible configurar zonas de impresión por componente de combo cuando es una limitación de la plataforma (los combos imprimen en una sola zona).
- Un caso de diagnóstico erróneo bajo presión: audit conv. 5, donde FIN diagnosticó "problema de permisos de usuario" cuando la causa real ya visible en el sistema era la suscripción vencida.

### 11.5 Tiempo de resolución

| Indicador | Valor real |
|---|---|
| Tiempo a primera respuesta promedio (25 convs.) | 11.4 minutos |
| Tiempo a primera respuesta máximo | 43.6 minutos (conv. 15) |
| Tiempo de resolución más rápido con calidad máxima | 5 minutos (audit conv. 3, 5/5 estrellas) |
| Tiempo de resolución más lento documentado | 65 minutos (audit conv. 5, terminó sin resolución) |

**Patrón:** existe una correlación observada (no un cálculo estadístico formal, dado el tamaño de muestra) entre menor tiempo de primera respuesta y mejor calificación final: el caso de 5 minutos obtuvo 5/5 estrellas; el caso de 65 minutos obtuvo 1/5.

### 11.6 Calidad técnica

Ver Sección 4 (rendimiento de pautas) y Sección 5 (rendimiento de atributos) — la calidad técnica de FIN depende directamente de qué tan bien se activan las pautas de diagnóstico, no de las pautas de comunicación (que funcionan de forma consistentemente sólida, Sección 4.3).

### 11.7 Calidad comunicativa

Consistentemente alta según la evidencia: las pautas de tono, personalidad, claridad progresiva y reducción de ruido se activan en 72–92% de los casos sin fallas de ejecución documentadas (Sección 4.1–4.3). El problema documentado en la muestra **no es de forma, es de fondo**: FIN comunica bien lo que decide decir, pero en ~20-24% de los casos decide decir algo incorrecto o tardío.

---

## 12. KPIs DEL MES

> **Aviso explícito:** El proyecto **no tiene un tablero de KPIs mensuales de FIN calibrado ni poblado con datos reales de junio.** El propio Final Acceptance Test del 27 de junio confirma: *"Madurez del scoring (FIS): Definido, no calibrado con datos reales"* y *"Madurez del scoring (PCS): Diseñado, no implementado"*. Los indicadores a continuación son **los únicos calculables** a partir de evidencia real, y se presentan con su fuente y limitación de alcance explícita.

| KPI | Valor | Fuente y limitación |
|---|---|---|
| % de resolución (dentro de la muestra de 25 conversaciones escaladas) | 36% resuelto, 16% parcial, 20% sin resolver, 16% derivado a área especializada, 4% abandono, 4% queja formal | Solo aplica a la muestra de 25 casos ya escalados — **no representa la tasa de resolución autónoma de FIN sobre el volumen total** |
| % de escalamiento (dentro de la muestra combinada de 29) | 26/29 conversaciones escalaron a humano (89.7%) | La muestra principal (25) fue seleccionada específicamente por estar escalada — **este porcentaje está sesgado hacia arriba por diseño de la muestra y NO debe usarse como tasa real de escalamiento de FIN** |
| % de consultas repetidas (mismo motivo, ≥2 ocurrencias, sobre 29) | Facturación electrónica: 6/29 (20.7%); comanda/impresión: 4/29 (13.8%) | Ver Sección 3.1 |
| % de atributos correctos | **NO DISPONIBLE** — no existe una medición estadística de precisión de atributos; solo hay fallas puntuales documentadas (Sección 5.2) | — |
| % de pautas cumplidas | **NO DISPONIBLE** como porcentaje agregado — 12 instancias de falla de timing documentadas sobre 25 casos (Sección 4.2), pero no constituye una tasa de cumplimiento total | — |
| Productos con mayor carga (dentro de la muestra) | Restobar: 27/29 (93.1%) | Ver Sección 2.2 — sesgo de muestra, no de volumen real |
| Categorías con mayor incidencia (dentro de la muestra) | Facturación electrónica (20.7%), configuración operativa (17.2%) | Ver Sección 3.1 |
| Calidad promedio de diagnóstico | 47.4/100 (25 convs. escaladas) / 68.6/100 (5 convs. no sesgadas por escalamiento) | Ver Sección 11.1 |
| Score de madurez del proyecto de software (FAT) | 64/100 — 🟠 Beta | Esto mide el software, no el desempeño de FIN con clientes — `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` |
| SLA de escalación interna <24h (agente humano Diana Zarate, no FIN) | 78.4% — meta de 90% no cumplida | `reports/auditoria_diana_zarate_jun2026.md` |
| SLA de resolución ≤3 días (agente humano Diana Zarate, no FIN) | 100% cumplido | Idem |
| Artículos KB publicados / totales | 992/1,036 (95.8%) | `knowledge_inventory.json` |
| Artículos KB actualizados en junio | 33 de 1,036 (3.2%) | Idem |

**KPIs que el proyecto define pero que NO tienen valor real calculado para junio:** FIN Intelligence Score (FIS) agregado, Predicted CSAT Score (PCS), Índice de Esfuerzo del Cliente (IEC), Score de Cobertura de Conocimiento (SCKB), Score de Cumplimiento de Workflows (SCW) — todos especificados en `FIN_ARCHITECT_ENTERPRISE.md` pero pendientes de calibración e implementación.

---

## 13. ROADMAP DE MEJORAS — JULIO 2026

Construido combinando (a) los objetivos que el propio proyecto ya se fijó al congelarse el 27 de junio (`FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` §9.2) y (b) las mejoras concretas derivadas del análisis de las 29 conversaciones reales (Secciones 6–10).

### Alta prioridad

| Iniciativa | Esfuerzo estimado | Impacto esperado | Beneficio operativo | Reducción esperada de escalamientos |
|---|---|---|---|---|
| Calibrar el FIS ejecutando `architect_review` sobre 50 conversaciones reales de Restobar y comparar contra evaluación humana (objetivo ya fijado por el proyecto, ventana 30 días) | Alto (requiere extracción de datos + validación humana) | Habilita medición automática de calidad en lugar de auditoría manual | Reemplaza el trabajo manual hecho para este mismo informe por un proceso repetible | No aplica directamente, pero es prerrequisito de todo lo demás |
| Implementar pauta de escalamiento inmediato ante solicitud repetida (Sección 8.1) y protocolo de interrupción de servicio activa (Sección 8.2) | Bajo (ajuste de pauta existente, no desarrollo nuevo) | Elimina el patrón de error de mayor frecuencia y el caso de peor desenlace documentado | Menos fricción en momentos de máxima tensión con el cliente | Directo — ataca 4+ casos de la muestra (convs. 01, 05, 07, 12, audit conv. 5) |
| Activar detección de plan "EXTRACCION" → protocolo de retención (Sección 8.3) | Bajo-Medio (requiere exponer el atributo de plan a FIN) | Convierte una señal ya disponible en acción preventiva | Reduce riesgo de churn silencioso | Indirecto (evita escalamientos por frustración acumulada) |
| Crear los 12 artículos de KB priorizados con evidencia real de necesidad (Sección 10.3) | Medio | Cierra huecos de contenido activos y documentados | Reduce reincidencia de consultas sin respuesta directa | Directo — cada artículo corresponde a un caso real sin resolución |
| Añadir verificación de variable de bifurcación antes de primera respuesta (Sección 8.4) | Medio (requiere ajuste de árboles de diagnóstico en 3+ flujos) | Reduce el segundo patrón de error más frecuente (20.7% de la muestra) | Menos re-trabajo por respuesta inicial incorrecta | Directo — convs. 03, 16, 20, 24 |

### Media prioridad

| Iniciativa | Esfuerzo estimado | Impacto esperado | Beneficio operativo | Reducción esperada de escalamientos |
|---|---|---|---|---|
| Expandir dataset de entrenamiento a Pymes y Nómina, mínimo 25 conversaciones por producto (objetivo ya fijado por el proyecto, ventana 60 días) | Alto | Condición de entrada a v2.0 según criterios propios del proyecto | Elimina el mayor gap de cobertura identificado en el FAT (25/100) | No aplica directamente |
| Fusionar los 7 grupos de artículos KB duplicados y reasignar los 93 artículos "Desconocido" | Medio | Reduce fragmentación y mejora precisión de selección de artículo por FIN | Menos riesgo de enviar contenido parcial/duplicado | Indirecto |
| Incorporar atributos `nivel_usuario`, `estado_bloqueo_sistema` y `consulta_vs_accion` al catálogo de clasificación (Sección 9) | Medio | Mejora la precisión de enrutamiento y de primera respuesta | Menos diagnósticos equivocados por falta de contexto | Indirecto |
| Adjuntar automáticamente artículo KB + resumen de diagnóstico en notas de escalamiento (Sección 6.5) | Bajo-Medio | Reduce tiempo de gestión del agente humano tras recibir el caso | Complementa (no reemplaza) la mejora de SLA de escalación humana (78.4% actual, meta 90%) | No reduce volumen, mejora tiempo de gestión posterior |
| Detección automática de loop de repetición (misma respuesta 2+ veces) → escalamiento automático (Sección 8.7) | Medio | Reduce turnos previos a escalamiento en casos de repetición | Menor frustración acumulada | Directo — convs. 07, 12 |

### Baja prioridad

| Iniciativa | Esfuerzo estimado | Impacto esperado | Beneficio operativo | Reducción esperada de escalamientos |
|---|---|---|---|---|
| Publicar o retirar los 44 artículos KB en borrador | Bajo | Limpieza de inventario, sin evidencia directa de impacto conversacional | Mejora la higiene del repositorio de conocimiento | Ninguna esperada de forma directa |
| Revisar criterio de "obsolescencia" de artículos (actualmente 0 detectados) para complementarlo con señal de uso real, no solo antigüedad (Sección 10.4) | Bajo | Mejora la detección de huecos de contenido no capturados hoy | Mantenimiento más preciso del KB a futuro | Ninguna esperada de forma directa |
| Documentar y usar el caso benchmark (audit conv. 3) como plantilla de entrenamiento para respuestas multi-paso | Bajo | Referencia de calidad reutilizable | Estandariza el patrón de mejor desempeño observado | Ninguna esperada de forma directa |
| Iniciar validación manual del PCS con 20 conversaciones con CSAT conocido (objetivo ya fijado por el proyecto, ventana 90 días) | Alto | Habilita a futuro un segundo modelo de calidad centrado en satisfacción | Complementa al FIS a mediano plazo | No aplica directamente en julio (objetivo a 90 días, más allá de julio) |

---

## 14. CONCLUSIÓN EJECUTIVA

**Para Dirección y Líderes de Producto:**

Junio de 2026 fue el mes en que Loggro construyó, por primera vez, un **lenguaje técnico compartido y una infraestructura de auditoría real** para entender cómo se desempeña FIN. Esto es un logro de fondo, no cosmético: antes de este mes no existía forma sistemática de responder "¿está FIN tomando las decisiones correctas?" con evidencia en vez de intuición. Hoy existen 15 herramientas operativas, un motor de decisión consolidado, un inventario completo de 1,036 artículos de conocimiento, y **29 conversaciones reales auditadas con un nivel de profundidad inusual** — causa raíz, pauta que faltó, atributo que faltó, artículo que faltó, prompt a mejorar, en cada caso.

**Principales hallazgos:** con la muestra disponible, el problema de FIN no es de tono ni de personalidad — las pautas de comunicación son sólidas y consistentes (Sección 4.3). El problema real está concentrado en dos puntos específicos y accionables: (1) FIN tarda en escalar cuando el usuario lo pide explícitamente, y en el caso de mayor severidad documentado esa demora coincidió con una amenaza de churn concreta; y (2) FIN responde antes de preguntar la variable que define el camino correcto (¿pagado o pendiente?, ¿con o sin recetas?, ¿qué versión tiene?) en aproximadamente uno de cada cinco casos analizados.

**Decisiones recomendadas:**
1. **Aceptar el congelamiento del framework** decidido por el propio proyecto el 27 de junio — no agregar más módulos hasta calibrar los que ya existen. Es la decisión técnicamente correcta dado que ningún modelo de scoring (FIS, PCS) tiene aún validación empírica.
2. **Priorizar la calibración del FIS sobre la expansión de producto.** Sin un modelo de calidad calibrado, cualquier decisión de negocio sobre FIN seguirá dependiendo de auditoría manual caso por caso, como la que sustenta este mismo informe.
3. **Tratar la muestra de 29 conversaciones como el primer lote de entrenamiento, no como el diagnóstico final.** El sesgo de la muestra (100% escalada en el dataset principal) es intencional y útil para encontrar patrones de fallo, pero no permite afirmar cuál es la tasa real de éxito de FIN sobre el volumen total — esa pregunta sigue abierta y requiere instrumentación adicional.

**Mejoras inmediatas (julio):** las cinco iniciativas de alta prioridad (Sección 13) no requieren nuevo desarrollo de producto — son ajustes a pautas ya existentes y contenido de conocimiento ya identificado como faltante, con evidencia directa de la conversación real que los originó. Son la forma más rápida de convertir este informe en resultado medible.

**Mejoras estratégicas:** la expansión de cobertura a Pymes y Nómina, y la calibración del PCS junto al FIS, son las dos condiciones que el propio proyecto definió como puerta de entrada a la versión 2.0. Ninguna de las dos es alcanzable dentro de julio según los plazos que el propio equipo se fijó (60 y 90 días respectivamente) — deben planificarse como objetivos de trimestre, no de mes.

**Impacto esperado para FIN:** si las mejoras de alta prioridad se ejecutan en julio, el impacto más medible no será un número de CSAT (ese modelo aún no existe), sino la reducción directa de los patrones de error ya identificados con nombre y evidencia: menos demora en escalamientos solicitados explícitamente, menos respuestas iniciales incorrectas por falta de una pregunta de bifurcación, y menos huecos de conocimiento activos. Estos tres cambios, por sí solos, atacan más del 40% de los casos problemáticos documentados en la muestra de junio.

---

## ANEXO — Índice de fuentes reales utilizadas

| Archivo | Rol en este informe |
|---|---|
| `dataset_fin_25_conversaciones.md` / `.csv` / `.json` | Fuente primaria de análisis de chats, pautas, atributos, escalamientos (Secciones 2–9) |
| `auditoria_fin_5_conversaciones.md` | Fuente primaria complementaria, incluye producto Alojamientos y transcripciones completas |
| `knowledge_inventory.json` / `.csv`, `KNOWLEDGE_DIGITAL_TWIN.md` | Fuente de la Sección 10 (Base de Conocimiento) |
| `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` | Fuente del estado del proyecto, FAT (64/100), objetivos de v1.1 (Secciones 1, 12, 13) |
| `FIN_ARCHITECT_ENTERPRISE.md` | Fuente del modelo de KPIs diseñado (FIS, PCS) — no calibrado (Sección 12) |
| `FIN_ARCHITECT_OPERATIONS_MANUAL.md` | Referencia de plantilla operativa (sin datos ejecutados) |
| `FIN_CONTINUOUS_LEARNING_ENGINE.md`, `FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md` | Referencia de automatizaciones diseñadas pendientes de implementación (Sección 7) |
| `CHANGELOG.md`, `docs/CHANGELOG.md`, historial de commits (`git log`) | Fuente del historial de mejoras y construcción del proyecto (Sección 1) |
| `reports/auditoria_diana_zarate_jun2026.md` | Fuente de referencia sobre el flujo humano posterior al escalamiento (Sección 6.6) — explícitamente no mezclada con el desempeño de FIN |
| `decision_engine.py`, `server.py` | Verificación del catálogo real de herramientas, categorías y constantes de clasificación implementadas |

*Fin del informe. Todas las cifras citadas provienen de los archivos listados arriba; donde el dato no existe en el proyecto, se declaró explícitamente como NO DISPONIBLE.*
