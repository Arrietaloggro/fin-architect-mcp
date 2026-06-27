# fin-architect-mcp
MCP para auditoría y optimización de pautas de Intercom Fin

---

# Project Status

🟢 **Status:** Beta Operacional

| Campo            | Valor                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| Versión          | 1.0 Beta                                                                    |
| Estado           | Baseline congelada                                                          |
| Arquitectura     | Congelada                                                                   |
| Implementación   | Parcial                                                                     |
| Uso interno      | Aprobado                                                                    |
| Producción       | Asistida                                                                    |
| Modo actual      | Operación y mejora continua                                                 |
| Próximo objetivo | Validar impacto en producción sobre CSAT, resolución y eficiencia operativa |

FIN Architect Enterprise entra oficialmente en su fase de operación y mejora continua basada en evidencia. La baseline v1.0 Beta está congelada: la arquitectura de 12 módulos, las 9 herramientas MCP implementadas, y los modelos de scoring FIS y PCS son la referencia estable desde la cual se inicia la validación operacional. El foco a partir de esta versión es ejecutar el sistema sobre conversaciones reales, medir su impacto, y acumular evidencia para informar la evolución hacia v2.0.

---

## Descripción

FIN Architect Enterprise es una plataforma de inteligencia operacional para equipos de CX que supervisan agentes de IA. Proporciona herramientas para auditar, evaluar, simular y mejorar el comportamiento del agente Lia de Loggro, operado sobre Intercom.

## Arquitectura

El sistema está compuesto por 12 módulos en 3 capas:

**Capa 1 — Ejecución (9 herramientas MCP activas):**
- `audit_guideline` — Audita si una pauta se aplicó correctamente
- `optimize_guideline` — Propone mejoras a pautas existentes
- `classify_guideline` — Clasifica pautas por tipo, complejidad y producto
- `detect_conflicts` — Detecta pautas contradictorias o redundantes
- `score_guideline` — Calcula el FIN Intelligence Score (FIS) por conversación
- `simulate_fin` — Simula el comportamiento óptimo de Lia
- `generate_guideline` — Genera nuevas pautas desde patrones detectados
- `extract_guidelines` — Extrae pautas implícitas de conversaciones históricas
- `architect_review` — Orquestador principal del pipeline completo

**Capa 2 — Orquestación:**
- `architect_review` integra todas las herramientas en un pipeline de revisión end-to-end

**Capa 3 — Inteligencia (diseñados, pendientes de implementación):**
- `fin_intelligence_review()` — Revisión inteligente con análisis temporal y clustering
- FIN Continuous Learning Engine — Ciclo OBSERVE→LEARN automatizado
- CSAT Improvement Engine — Predicción y mejora del Predicted CSAT Score (PCS)

## Documentación

| Documento | Descripción |
|-----------|-------------|
| `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` | **Documento de cierre oficial** — referencia canónica de v1.0 Beta |
| `FIN_ARCHITECT_ENTERPRISE.md` | Blueprint completo del producto (v1.1) |
| `FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md` | Arquitectura de `fin_intelligence_review()` |
| `FIN_CONTINUOUS_LEARNING_ENGINE.md` | Diseño del motor de aprendizaje continuo |
| `KNOWLEDGE_DIGITAL_TWIN.md` | Inventario completo de 1,036 artículos KB |
| `CHANGELOG.md` | Historial de versiones |

## Datos

| Archivo | Descripción |
|---------|-------------|
| `dataset_fin_25_conversaciones.json` | 25 conversaciones Restobar anotadas (36 campos) |
| `knowledge_inventory.json` | 1,036 artículos KB con metadatos completos |

## Uso

```bash
# Iniciar servidor MCP
python server.py

# El servidor expone las 9 herramientas MCP via SSE en el puerto configurado
# Conectar desde Claude con el MCP configurado en settings
```

## Roadmap

| Versión | Objetivo | Criterio de entrada |
|---------|----------|---------------------|
| v1.0 Beta (actual) | Baseline congelada, inicio de operación | — |
| v1.1 | Calibración FIS + datasets Pymes y Nómina | Correlación FIS-humano ≥ 0.75 |
| v2.0 | Implementación CLE + CIE | 3/4 productos con dataset; 8 semanas de uso activo |
| Enterprise | Plataforma multi-producto completa | PCS validado; primer ciclo de mejora completado |
