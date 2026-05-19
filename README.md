# 📊 Diagnóstico de Arquitectura — Hackathon Nicaragua 2026

Pipeline automatizado de análisis y diagnóstico técnico para los 17 equipos participantes en la fase de incubación del Hackathon Nicaragua 2026.

> **Centro de Innovación — INATEC Nicaragua**

## ¿Qué hace este repositorio?

1. **Ingesta y limpieza** del CSV de respuestas del diagnóstico de arquitectura.
2. **Feature engineering** — calcula un score de riesgo compuesto y detecta vulnerabilidades cruzadas.
3. **Genera 6 visualizaciones** científicas en alta resolución (300 DPI).
4. **Exporta telemetría JSON** optimizada para consumo por LLMs.
5. **Publica el informe** automáticamente en GitHub Pages.

## Estructura del Repositorio

```
diagnostico-arquitectura-hn26/
├── .github/workflows/pipeline.yml  ← GitHub Actions (CI/CD)
├── data/
│   └── respuestas.csv              ← Datos del diagnóstico (Google Forms)
├── src/
│   ├── config.py                   ← Configuración centralizada
│   ├── cleaning.py                 ← Ingesta y normalización
│   ├── features.py                 ← Scoring de riesgo y flags
│   ├── visuals.py                  ← 6 gráficas con tema oscuro
│   └── exporter.py                 ← Exportador JSON para LLMs
├── run_pipeline.py                 ← Orquestador principal
├── docs/
│   └── index.html                  ← Informe (GitHub Pages)
├── outputs/                        ← Generado por el pipeline
│   ├── plots/                      ← Gráficas PNG (300 DPI)
│   └── llm_context/                ← telemetria_arquitectura.json
└── requirements.txt
```

## Ejecución Local

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el pipeline completo
python run_pipeline.py
```

## Ejecución Automática (GitHub Actions)

El pipeline se ejecuta automáticamente al hacer push a `main` si se modifican:
- `data/**` (datos actualizados)
- `src/**` (cambios en la lógica)
- `run_pipeline.py`
- `docs/**`

También se puede disparar manualmente desde la pestaña **Actions** del repositorio.

El workflow:
1. Ejecuta el pipeline completo.
2. Copia las gráficas generadas a `docs/assets/`.
3. Hace commit de los outputs.
4. Despliega el informe en **GitHub Pages**.

## Informe en Línea

Una vez configurado GitHub Pages (Settings → Pages → Source: GitHub Actions), el informe estará disponible en:

```
https://<usuario>.github.io/diagnostico-arquitectura-hn26/
```

---

*Pipeline v1.0.0 · Mayo 2026*
