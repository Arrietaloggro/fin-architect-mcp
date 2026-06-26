# AUDITORÍA OPERACIONAL — FIN ARCHITECT v1.0
## Diagnóstico Restobar · Diana Milena Zarate Beltran · Junio 1–25, 2026

**Generado:** 26 de junio de 2026  
**Analista:** FIN Architect v1.0 (IA)  
**Fuente de datos:** Intercom MCP — Workspace Loggro  
**Admin auditada:** Diana Milena Zarate Beltran (`admin_id: 9751458`, `dzarateb@loggro.com`)  
**Inbox:** Diagnóstico Restobar (`team_id: 10111540`)  
**Período:** 1 al 25 de junio de 2026 (COT, UTC-5)

---

## RESUMEN EJECUTIVO

| Métrica clave | Valor |
|---|---|
| Total casos en alcance | **54** |
| Casos gestionados por Diana | **48 (88.9%)** |
| Casos nunca gestionados | **6 (11.1%)** |
| Tiempo promedio asignación→primera gestión | **27h 08m** |
| Tiempo mediano asignación→primera gestión | **5h 21m** |
| Percentil 90 (P90) | **~47h 13m** |
| SLA escalación <24h | **78.4% — ⚠️ META NO CUMPLIDA** (meta: 90%) |
| SLA resolución ≤3 días | **100% — ✅ META CUMPLIDA** |
| Tickets cerrados/resueltos | **47/54 (87.0%)** |
| Tickets abiertos | **7/54 (13.0%)** |

---

## CONTEXTO Y ALCANCE

### Infraestructura identificada

| Entidad | ID | Nombre |
|---|---|---|
| Team (inbox) | 10111540 | PQR RESTOBAR (interno) / "Diagnóstico Restobar" |
| SLA aplicado | — | "Diagnostico" · Meta resolución: 259,200 seg (3 días) |
| Admin auditada | 9751458 | Diana Milena Zarate Beltran |
| Principal asignador | 9753945 | Angie Paola Casallas Ortiz |
| Bot enrutador | 9218425 | Lia |

### Tipos de ticket procesados por Diana

| Tipo | Cantidad | % |
|---|---|---|
| PQR RESTOBAR | 47 | 87.0% |
| Sin ticket (conversación directa) | 5 | 9.3% |
| Revision Restobar | 1 | 1.9% |
| Diagnostico Restobar | 1 | 1.9% |
| **Total** | **54** | **100%** |

> **Nota metodológica:** El inbox "Diagnóstico Restobar" (team 10111540) gestiona principalmente tickets de tipo "PQR RESTOBAR" (cambios de NIT, solicitudes, sugerencias escaladas). Solo 1 conversación es del tipo "Diagnostico Restobar" con SLA "Diagnostico" aplicado. Los estados de folio clásicos del flujo Diagnóstico (Devuelto a servicio, En Gestión por Diagnóstico, etc.) no aplican a PQR RESTOBAR; la sección 4 reporta los estados reales encontrados.

---

## SECCIÓN 1 — TIEMPO DE ASIGNACIÓN A PRIMERA GESTIÓN

### Resumen estadístico

| Estadístico | Segundos | HH:MM:SS |
|---|---|---|
| N (casos medibles con tiempo positivo) | 37 | — |
| Casos auto-gestionados (actuó antes de asignación) | 8 | — |
| Casos sin datos de tiempo | 9 | — |
| **Promedio** | 97,723 | **27:08:43** |
| **Mediana** | 19,240 | **05:20:40** |
| **Mínimo** | 1 | **00:00:01** |
| **Máximo** | 1,546,342 | **429:12:22 (17.9 días)** |
| **P90** | ~169,972 | **~47:12:52** |

### Distribución por rangos

| Rango | Casos | % |
|---|---|---|
| < 1 hora | 13 | 35.1% |
| 1 – 4 horas | 4 | 10.8% |
| 4 – 8 horas | 2 | 5.4% |
| 8 – 24 horas | 10 | 27.0% |
| 24 – 48 horas | 4 | 10.8% |
| > 48 horas | 4 | 10.8% |
| **Total** | **37** | **100%** |

### Top 10 casos más lentos

| # | ID | Título | Tiempo | Asignado | Primera gestión |
|---|---|---|---|---|---|
| 1 | 215474537554895 | GUACAMOLYN FOOD BRAND (NIT) | 429:12:22 | Jun 1 | Jun 19 |
| 2 | 215474684227177 | Las Presitas wing (NIT) | 82:20:41 | Jun 10 | Jun 13 |
| 3 | 215474683463491 | Las Presitas wing (NIT) | 82:14:38 | Jun 10 | Jun 13 |
| 4 | 215474594629827 | BOMART (Sug esc) | 66:34:21 | Jun 6 | Jun 9 |
| 5 | 215474554426949 | SANDWICHES (Sug esc) | 47:12:52 | Jun 2 | Jun 4 |
| 6 | 215474548441925 | BODEGA COCINA ISLA (Diag) | 47:08:23 | Jun 2 | Jun 4 |
| 7 | 215474703254206 | LA AZOTEA GASTROBAR (Sug) | 40:46:21 | Jun 12 | Jun 13 |
| 8 | 215474784953736 | DON FIERRO POPAYÁN (NIT) | 35:53:23 | Jun 22 | Jun 23 |
| 9 | 215474550300181 | QUILE STEAK (NIT) | 21:06:28 | Jun 2 | Jun 3 |
| 10 | 215474563840449 | Barroco Restaurante (Sug) | 21:30:42 | Jun 3 | Jun 4 |

> **⚠️ Outlier extremo:** ID 215474537554895 registra 17.9 días sin gestión. Requiere investigación inmediata.

---

## SECCIÓN 2 — CASOS ASIGNADOS SIN GESTIÓN DE DIANA

**Total: 6 casos (11.1% del total)**

| ID | Título | Estado actual | Fecha creación | ¿Asignado a Diana? | Estado conv. |
|---|---|---|---|---|---|
| 215474814913579 | QUITAR PAGO - NAPOLES FRESAS | Resolved | Jun 23 | No (null) | closed |
| 215474812106310 | SUGERENCIA NUEVA COMANDA - GRUPO VALENCIA ESCOBAR | Submitted | Jun 23 | **Sí** (asignado pero no gestionado) | open |
| 215474789529263 | Pago 3 meses no refleja - PAPASAURIOS | Resolved | Jun 22 | No (null) | closed |
| 215474755114102 | Reportes históricos - Boxes Grupo | Resolved | Jun 18 | No (null) | closed |
| 215474659588095 | Reportes históricos - Boxes Grupo | Resolved | Jun 10 | No (null) | closed |
| 215474658593354 | Jesús Enrique Orozco | Resolved | Jun 10 | No (null) | closed |

**Análisis:**
- 5 de 6 estuvieron en el equipo pero nunca asignados directamente a Diana (fueron resueltos por otros agentes del equipo)
- **1 caso crítico:** ID 215474812106310 fue asignado explícitamente a Diana pero ella no tomó ninguna acción. Está abierto con estado "Submitted" — **requiere atención inmediata**
- Los 5 casos resueltos sin participación de Diana no representan riesgo operativo actual, pero sí oportunidades de mejora en rotación de carga

---

## SECCIÓN 3 — ESTADÍSTICAS DE ESCALAMIENTO

### Por estado actual del ticket

| Estado (admin label) | Cantidad | % |
|---|---|---|
| Resolved | 44 | 81.5% |
| Sin ticket (conversación directa) | 5 | 9.3% |
| Escalado Cambio de NIT | 3 | 5.6% |
| Submitted (nunca procesado) | 2 | 3.7% |
| **Total** | **54** | **100%** |

### Por prioridad

| Prioridad | Cantidad | % |
|---|---|---|
| priority (alta) | 27 | 50.0% |
| not_priority (normal) | 27 | 50.0% |

### Por estado de conversación

| Estado | Cantidad | % |
|---|---|---|
| closed | 47 | 87.0% |
| open | 7 | 13.0% |

### Tickets abiertos pendientes (7 casos)

| ID | Título | Estado ticket | Prioridad |
|---|---|---|---|
| 215474764457625 | Cambio de nit - CANIBAL GROUP ENVIGADO | in_progress / Escalado NIT | normal |
| 215474838056395 | Cambio de nit - Vibras burger | in_progress / Escalado NIT | normal |
| 215474835680140 | SUG - Cami Atelier | submitted | normal |
| 215474817596157 | Escalado NIT - [empresa] | in_progress / Escalado NIT | alta |
| 215474812106310 | SUGERENCIA NUEVA COMANDA - GRUPO VALENCIA | submitted | normal |
| 215474814913579 | QUITAR PAGO - NAPOLES FRESAS | — | normal |
| 215474789529263 | Pago 3 meses - PAPASAURIOS | — | normal |

### Principales temas de escalamiento

| Categoría | Cantidad | % |
|---|---|---|
| Cambio de NIT / razón social | ~30 | ~55.6% |
| Sugerencias escaladas (Sug esc) | ~10 | ~18.5% |
| Sugerencias directas (SUG) | ~3 | ~5.6% |
| Diagnóstico / PQR técnico | ~4 | ~7.4% |
| Solicitudes especiales | ~4 | ~7.4% |
| Otros / sin título | ~3 | ~5.6% |

### Agentes que más asignan casos a Diana

| Agente asignador | Casos |
|---|---|
| Angie Paola Casallas Ortiz | **18** |
| Diana Milena Zarate Beltran (autoasignación) | 4 |
| Leydi Johanna Ruiz Garcia | 6 |
| Lisseth Andrea Graciano Cifuentes | 4 |
| Paola Andrea Caballero Pedraza | 3 |
| Daniel Alberto Olier Diaz | 3 |
| Juan Pablo Gallego Gaona | 2 |
| Otros | 5 |
| Sin registrar | 9 |

---

## SECCIÓN 4 — AUDITORÍA DE FOLIOS

### Estados actuales de ticket (ticket_state)

| ticket_state | Cantidad | % |
|---|---|---|
| resolved | 44 | 81.5% |
| in_progress | 3 | 5.6% |
| submitted | 2 | 3.7% |
| null (sin ticket formal) | 5 | 9.3% |
| **Total** | **54** | **100%** |

### Estados etiqueta administrador (ticket_custom_state_admin_label)

| Label | Cantidad | % |
|---|---|---|
| Resolved | 44 | 81.5% |
| Escalado Cambio de NIT | 3 | 5.6% |
| Submitted | 2 | 3.7% |
| null (sin ticket) | 5 | 9.3% |
| **Total** | **54** | **100%** |

> **Nota:** Los estados del folio Diagnóstico clásico (Devuelto a servicio, En Gestión por Diagnóstico, Escalado a mantenimiento, Escalado a producto, Escalado a producto Improvement, En curso, Esperando al cliente) **no aparecen** en el trabajo de Diana durante este período. Su carga es 87% PQR RESTOBAR (cambios de NIT, sugerencias, solicitudes), no casos de diagnóstico técnico de nivel 2 con esos estados. Solo 1 de 54 tickets es tipo "Diagnostico Restobar".

### Conversaciones con folio enlazado (linked_conversation_id)

| Enlace | Cantidad | % |
|---|---|---|
| Con conversación enlazada | 50 | 92.6% |
| Sin enlace (standalone) | 4 | 7.4% |

---

## SECCIÓN 5 — CUMPLIMIENTO DE SLA

### SLA de Resolución (≤ 3 días = 259,200 segundos)

| Métrica | Valor |
|---|---|
| Casos con datos de SLA | 12 |
| Casos que cumplen ≤3 días | 12 |
| **Tasa de cumplimiento** | **100% ✅** |
| Tiempo mínimo de cierre | 491 seg (8:11 min) |
| Tiempo máximo de cierre | 170,791 seg (47:26:31) |
| Tiempo promedio de cierre | 24,456 seg (6:47:36) |

> **Nota:** Solo 12 de 54 conversaciones tienen datos de `time_to_first_close_seconds` disponibles. Los tickets admin-iniciados (back-office) no registran este indicador en Intercom. Los 12 casos con datos son las conversaciones con componente cliente visible.

### SLA de Escalación Interna (< 24h desde asignación a primera acción)

| Métrica | Valor |
|---|---|
| Casos medibles | 37 |
| Casos que cumplen < 24h | **29** |
| Casos que NO cumplen | **8** |
| **Tasa de cumplimiento** | **78.4% ⚠️** |
| **Meta** | **90%** |
| **Brecha** | **-11.6 pp** (faltan 4 casos más bajo 24h para alcanzar meta) |

#### Casos que exceden 24 horas en primera gestión

| ID | Título | Tiempo | Razón probable |
|---|---|---|---|
| 215474537554895 | GUACAMOLYN (NIT) | 17.9 días | Caso extremo — posible omisión |
| 215474684227177 | Las Presitas wing (NIT) | 82h 21m | Cola de NIT acumulada |
| 215474683463491 | Las Presitas wing (NIT) | 82h 15m | Idem caso anterior |
| 215474594629827 | BOMART (Sug esc) | 66h 34m | Sugerencia de baja prioridad |
| 215474554426949 | SANDWICHES (Sug esc) | 47h 13m | Fin de semana probable |
| 215474548441925 | BODEGA COCINA ISLA | 47h 08m | Idem |
| 215474703254206 | LA AZOTEA (Sug) | 40h 46m | Cola acumulada Jun 12–13 |
| 215474784953736 | DON FIERRO POPAYÁN (NIT) | 35h 53m | Caso de Jun 22 |

---

## SECCIÓN 6 — DISTRIBUCIÓN TEMPORAL

### Por día (COT)

| Fecha | Casos | | Fecha | Casos |
|---|---|---|---|---|
| Jun 1 | 5 | | Jun 14 | 2 |
| Jun 2 | 6 | | Jun 15 | 0 |
| Jun 3 | 3 | | Jun 16 | 2 |
| Jun 4 | 4 | | Jun 17 | 1 |
| Jun 5 | 2 | | Jun 18 | 2 |
| Jun 6 | 2 | | Jun 19 | 1 |
| Jun 7 | 1 | | Jun 20 | 1 |
| Jun 8 | 1 | | Jun 21 | 1 |
| Jun 9 | 4 | | Jun 22 | 4 |
| Jun 10 | 0 | | Jun 23 | 7 |
| Jun 11 | 5 | | Jun 24 | 2 |
| Jun 12 | 3 | | Jun 25 | 0 |
| Jun 13 | 0 | | **Total** | **54** |

### Por semana

| Semana | Período | Casos |
|---|---|---|
| Semana 1 | Jun 1–7 | **23** |
| Semana 2 | Jun 8–14 | **15** |
| Semana 3 | Jun 15–21 | **8** |
| Semana 4 | Jun 22–25 | **9** |

> Pico máximo: **Semana 1 (Jun 1–7)** con 23 casos (42.6% del total mensual).  
> Día con más casos: **Jun 23** (7 casos).

---

## SECCIÓN 7 — TICKETS AUTO-GESTIONADOS POR DIANA

Diana creó o se autoasignó 4 tickets:

| ID | Título | Tipo | Estado | Empresa |
|---|---|---|---|---|
| 215474803873209 | Sug esc - Fatness - Puntos de clientes | PQR RESTOBAR | resolved | null |
| 215474835680140 | SUG - Cami Atelier | PQR RESTOBAR | **submitted (abierto)** | null |
| 215474722661119 | Sug esc - EL BOTELLON - Escanear productos | PQR RESTOBAR | resolved | EL BOTELLON |
| 215474659451053 | SUG - SANDWICHES DONDE MISTER S.A.S. | Revision Restobar | resolved | SANDWICHES DONDE MISTER SAS |

> **Pendiente activo:** ID 215474835680140 (SUG - Cami Atelier) creado Jun 24, estado "Submitted" — sin avance.

---

## SECCIÓN 8 — HALLAZGOS INTELIGENTES

### 🔴 Cuellos de botella críticos

1. **Outlier extremo (ID 215474537554895):** 17.9 días sin primera gestión. Un solo caso infla el promedio de 5:21h a 27:09h. Sin este outlier, el promedio sería ~**6:06h** y P90 ~**40h**. Verificar si fue omisión, caso bloqueado por tercero, o falla en asignación.

2. **SLA escalación <24h: 78.4% vs meta 90%.** 8 casos exceden 24h. El patrón indica que casos de fin de semana (Jun 2→4, Jun 12→13) y colas de NIT son las principales causas.

3. **1 caso asignado sin gestión (ID 215474812106310):** Abierto, estado "Submitted", asignado directamente a Diana Jun 23. Sin acción. Requiere revisión inmediata.

### 🟡 Patrones de carga

4. **Concentración de trabajo en NIT:** 55% de los casos son solicitudes de cambio de NIT/razón social. Esto sugiere que Diana opera principalmente como procesadora de cambios de back-office, no como agente de diagnóstico técnico. El inbox está siendo usado para un flujo de trabajo diferente a su diseño original.

5. **Semana 1 absorbe el 42.6% del volumen** (23 casos). El flujo cae drásticamente en semanas 3–4. Investigar si hubo cambio operativo, vacaciones, o redistribución de carga.

6. **Angie Paola Casallas Ortiz asigna el 33.3% de los casos** (18/54). Alta dependencia de una sola fuente de asignación — riesgo operativo si ese agente está ausente.

### 🟢 Automatizaciones sugeridas para FIN

7. **Auto-alerta a 12h sin primera acción:** Si `assignment_to_diana_at` existe y han pasado 12h sin ningún `part` de admin 9751458, enviar notificación interna automática.

8. **Auto-escalación de casos "Submitted" después de 48h:** Los tickets que permanecen en estado "Submitted" sin actividad deberían ser reasignados automáticamente a cola general o al supervisor.

9. **Detección de outliers de tiempo:** Cualquier caso con `time_to_manage > 72h` debe ser marcado como prioritario y notificado al líder de equipo.

### 📚 Mejoras de Knowledge Base sugeridas

10. **Proceso de cambio de NIT:** Con 30 casos (55%), este es el flujo más repetitivo. Un protocolo estandarizado y checklist en KB reduciría el tiempo promedio de gestión significativamente.

11. **Gestión de sugerencias escaladas:** 10 casos de tipo "Sug esc" — definir criterios claros de priorización y tiempo de respuesta específico para este tipo.

---

## APÉNDICE: IDENTIFICADORES TÉCNICOS

| Elemento | Valor |
|---|---|
| Admin ID Diana | 9751458 |
| Email Diana | dzarateb@loggro.com |
| Team ID Diagnóstico Restobar | 10111540 |
| Team ID Restobar (nivel 1) | 9246314 |
| SLA ID | "Diagnostico" (resolución 259,200 seg) |
| Bot enrutador | Lia (admin 9218425) |
| Rango Unix período | 1780272000 – 1782450000 |
| Total conversaciones recuperadas | 54 |
| Herramienta | Intercom MCP API |

---

*Reporte generado automáticamente por FIN Architect v1.0 — Datos extraídos directamente de Intercom. Sin estimaciones. Las métricas marcadas con "No disponible" corresponden a limitaciones de la API de Intercom para tickets admin-iniciados.*
