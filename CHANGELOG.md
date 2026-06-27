# Changelog

Todas las versiones significativas de FIN Architect Enterprise se documentan aquí.

---

## v1.0 Beta — 2026-06-27

**Cierre de la fase de construcción. Inicio de la fase operacional.**

Esta versión representa el baseline oficial de FIN Architect Enterprise. El sistema sale del modo de construcción de framework y entra en modo de operación y mejora continua basada en evidencia.

### Incluido en esta versión

**Herramientas MCP implementadas (9):**
- `audit_guideline` — Auditoría de pautas por conversación
- `optimize_guideline` — Propuestas de optimización de pautas
- `classify_guideline` — Taxonomía de pautas por tipo y producto
- `detect_conflicts` — Detección de conflictos entre pautas
- `score_guideline` — FIN Intelligence Score (FIS) por conversación
- `simulate_fin` — Simulación de comportamiento óptimo de Lia
- `generate_guideline` — Generación de nuevas pautas desde patrones
- `extract_guidelines` — Extracción de pautas implícitas de conversaciones
- `architect_review` — Orquestador del pipeline completo

**Artefactos de datos:**
- `KNOWLEDGE_DIGITAL_TWIN.md` — Inventario completo de 1,036 artículos KB
- `knowledge_inventory.json` / `.csv` — Datos estructurados del inventario
- `dataset_fin_25_conversaciones.json` / `.md` / `.csv` — 25 conversaciones Restobar con 36 campos anotados

**Documentación arquitectónica:**
- `FIN_ARCHITECT_ENTERPRISE.md` v1.1 — Blueprint completo del producto con CSAT Improvement Engine
- `FIN_INTELLIGENCE_REVIEW_ARCHITECTURE.md` — Diseño de `fin_intelligence_review()`
- `FIN_CONTINUOUS_LEARNING_ENGINE.md` — Diseño del motor de aprendizaje continuo
- `FIN_ARCHITECT_ENTERPRISE_v1.0_BETA.md` — Documento de cierre oficial

**Resultado del Final Acceptance Test:**
- Score de madurez: 64/100
- Veredicto: 🟠 Beta
- Cobertura operacional: Restobar (completo), Pymes/Nómina/Alojamientos (pendientes)

### Módulos diseñados (pendientes de implementación en v2.0)
- `fin_intelligence_review()` — Revisión inteligente con análisis temporal
- FIN Continuous Learning Engine — Ciclo OBSERVE→LEARN
- CSAT Improvement Engine — Predicted CSAT Score (PCS)

### Estado de la baseline
- Arquitectura: Congelada
- Interfaces MCP: Estables
- Modelos de scoring: Definidos, pendientes de calibración empírica

---

*Las versiones anteriores a v1.0 Beta corresponden a fases de desarrollo interno sin releases formales.*
