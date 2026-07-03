# 📦 Entregables — Ejercicio Propuesto 2 (Pruebas de Integración)

**Práctica 08 · Pruebas de Software · NRC VII**
**Proyecto Final:** NovaChef — Sistema SaaS de Restaurante + Delivery
**Herramienta elegida:** `pytest` + `FastAPI TestClient` (equivalente Python de Supertest/Requests, versionable en el mismo repositorio del proyecto)
**Resultado:** ✅ **24 / 24 pruebas PASSED** — 24 casos de inyección de fallas sobre 5 fronteras

---

## Ejercicio 2 y cómo se cumplió (y superó)

| Requisito de la guía                                       | Mínimo exigido |                         Entregado                          | Dónde                                                  |
| ---------------------------------------------------------- | :------------: | :--------------------------------------------------------: | ------------------------------------------------------ |
| **1. Mapeo de la Frontera** (dónde A entrega datos a B)    |   1 frontera   |           **5 fronteras** mapeadas con diagrama            | `01_mapeo_fronteras.md`                                |
| **2. Inyección de Fallas de Interfaz**                     |    3 casos     | **24 casos** (8 Sintácticos, 13 Semánticos, 3 Resiliencia) | `tests/test_fronteras_integracion.py`                  |
| &nbsp;&nbsp;• Caso 1 Sintáctico (campos/tipos erróneos)    |       1        |                           **8**                            | IDs `SIN-01…SIN-08`                                    |
| &nbsp;&nbsp;• Caso 2 Semántico (valores ilógicos)          |       1        |                           **13**                           | IDs `SEM-01…SEM-13`                                    |
| &nbsp;&nbsp;• Caso 3 Resiliencia (latencia/timeout)        |       1        |                           **3**                            | IDs `RES-01…RES-03`                                    |
| **3. Reporte de Incidente** (Esperado vs Real)             | por cada falla |     24 en matriz + 4 en formato IEEE-829 + 2 hallazgos     | `02_reportes_incidentes.md`                            |
| **Evidencia de ejecución** (salida de terminal, como Ej.1) |       —        |      Terminal + reporte pytest-html + 3 capturas PNG       | `03_salida_terminal.txt`, `reporte_html/`, `capturas/` |

---

## 📂 Estructura de la carpeta

```
entregables_ejercicio2/
├── Informe_Ejercicio2_NovaChef_v4.docx  ← 📄 INFORME WORD DEFINITIVO (diseño senior + 24 fichas IEEE-829)
├── diagramas_mermaid.md                 ← código Mermaid de las figuras (generar en mermaid.live)
├── 04_log_detallado.txt                 ← log completo por prueba (trazas HTTP, fuente del Anexo C)
├── 00_LEEME.md                        ← este índice
├── 01_mapeo_fronteras.md              ← TAREA 1: mapeo de las 5 fronteras + diagrama
├── 02_reportes_incidentes.md          ← TAREA 3: reportes IEEE-829, matriz 24 casos, hallazgos
├── 03_salida_terminal.txt             ← evidencia: salida real de `pytest -v`
├── reporte_html/
│   ├── reporte_integracion.html       ← reporte OFICIAL de pytest-html (abrir en navegador)
│   └── dashboard_evidencia.html       ← dashboard visual resumen
└── capturas/
    ├── 01_dashboard_evidencia.png     ← captura del dashboard (matriz completa + hallazgos)
    ├── 02_matriz_resultados.png       ← recorte de la matriz Esperado vs Real
    └── 03_reporte_pytest_html.png     ← captura del reporte pytest-html (24 Passed)

tests/test_fronteras_integracion.py    ← TAREA 2: la suite (código fuente de las pruebas)
```

> El archivo de la suite vive en `tests/` (junto al resto de pruebas del proyecto) para
> respetar la convención del repositorio y ejecutarse con el `conftest.py` compartido.

---

## ▶️ Cómo reproducir la ejecución

```bash
# Desde la raíz del proyecto "GUERRA DE TESTERS"
.venv/Scripts/python.exe -m pytest tests/test_fronteras_integracion.py -v

# Regenerar reporte HTML:
.venv/Scripts/python.exe -m pytest tests/test_fronteras_integracion.py \
    --html=entregables_ejercicio2/reporte_html/reporte_integracion.html --self-contained-html

# Regenerar capturas PNG (requiere: pip install playwright && playwright install chromium):
.venv/Scripts/python.exe entregables_ejercicio2/_tomar_capturas.py
```

**Dependencias añadidas para el ejercicio:** `pytest-html` (reporte) y `playwright` (capturas).

---

## 🔎 Resumen de hallazgos

- **H-01 (Severidad MEDIA):** no hay _timeout_/circuit-breaker en la capa HTTP. Bajo
  latencia sostenida, los workers pueden agotarse. Recomendación: middleware de timeout
  (504) + `pool_timeout` en SQLAlchemy. → evidencia en `RES-01`.
- **H-02 (Informativo):** validación de stock duplicada (Carrito y Pedido) = buena
  práctica de defensa en profundidad. → evidencia en `SEM-03`.

El resto de las 22 fronteras respondieron **exactamente** como su contrato exige.

---
