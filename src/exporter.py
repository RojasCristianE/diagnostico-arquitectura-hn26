"""
exporter.py — Exportador de Telemetría Optimizada para LLMs.

Genera un archivo JSON estructurado con todos los hallazgos estadísticos,
perfiles de riesgo y metadatos de visualización en un formato diseñado
para inyección directa en prompts de generación de informes.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from .config import PIPELINE_VERSION, RISK_WEIGHTS


def _distribution(series: pd.Series) -> dict:
    """Genera distribución de frecuencias como dict."""
    counts = series.value_counts()
    total = len(series)
    return {
        str(k): {"count": int(v), "pct": round(v / total * 100, 1)}
        for k, v in counts.items()
    }


def _descriptive_stats(series: pd.Series) -> dict:
    """Estadísticas descriptivas para una serie numérica."""
    return {
        "mean": round(float(series.mean()), 3),
        "median": round(float(series.median()), 3),
        "std": round(float(series.std()), 3),
        "min": round(float(series.min()), 3),
        "max": round(float(series.max()), 3),
        "q1": round(float(series.quantile(0.25)), 3),
        "q3": round(float(series.quantile(0.75)), 3),
    }


def _build_startup_profiles(df: pd.DataFrame) -> list[dict]:
    """Construye perfil de riesgo detallado por startup."""
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    risk_dims = [c for c in df.columns if c.endswith("_risk") and c != "risk_score"]

    profiles = []
    for _, row in df.iterrows():
        active_flags = [
            col.replace("flag_", "")
            for col in flag_cols
            if row[col]
        ]
        dimensions = {
            col.replace("_risk", ""): int(row[col])
            for col in risk_dims
        }
        profiles.append({
            "startup": row["startup_name"],
            "tech_lead": row["tech_lead"],
            "platform": row["platform_clean"],
            "frontend": row["frontend_clean"],
            "backend": row["backend_clean"],
            "complexity_score": int(row["complexity_score"]),
            "risk_score": round(float(row["risk_score"]), 3),
            "risk_tier": row["risk_tier"],
            "maturity_index": round(float(row["maturity_index"]), 3),
            "active_flags": active_flags,
            "total_flags": int(row["total_flags"]),
            "risk_dimensions": dimensions,
            "mentorship_requested": row["mentorship_clean"],
            "ai_usage": row["ai_usage"],
            "cloud_budget": row["cloud_budget"],
        })

    return sorted(profiles, key=lambda x: x["risk_score"], reverse=True)


def _build_cross_tabulations(df: pd.DataFrame) -> dict:
    """Construye tabulaciones cruzadas clave."""
    crosstabs = {}

    # Sensibilidad × Gestión de código
    ct1 = pd.crosstab(
        df["data_sensitivity_risk"].map({1: "Baja", 2: "Media", 3: "Alta"}),
        df["code_management_risk"].map({1: "Ramas", 2: "Repo único", 3: "Manual"}),
    )
    crosstabs["sensitivity_vs_code_management"] = {
        "description": "Cruce de sensibilidad de datos vs gestión de código. "
        "Celdas Alta+Manual indican vulnerabilidad de seguridad crítica.",
        "data": ct1.to_dict(),
    }

    # Complejidad × QA
    ct2 = pd.crosstab(
        df["complexity_score"],
        df["qa_strategy_risk"].map({1: "Automatizada", 2: "Manual checklist", 3: "Ad-hoc"}),
    )
    crosstabs["complexity_vs_qa"] = {
        "description": "Cruce de complejidad vs estrategia QA. "
        "Complejidad alta + QA ad-hoc = alto riesgo de bugs en producción.",
        "data": {str(k): v for k, v in ct2.to_dict().items()},
    }

    # Frontend × Backend
    ct3 = pd.crosstab(df["frontend_clean"], df["backend_clean"])
    crosstabs["frontend_vs_backend"] = {
        "description": "Combinaciones de stacks tecnológicos. "
        "Revela clustering de ecosistemas y preferencias del cohort.",
        "data": ct3.to_dict(),
    }

    return crosstabs


def _build_flag_summary(df: pd.DataFrame) -> dict:
    """Resumen de flags de vulnerabilidad activos."""
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    flag_descriptions = {
        "flag_security_vuln": "Vulnerabilidad de Seguridad (Alta sensibilidad + gestión débil de código)",
        "flag_budget_crisis": "Crisis de Presupuesto (Sin presupuesto + complejidad ≥ 4)",
        "flag_team_strain": "Tensión de Equipo (Sin devs dedicados + complejidad ≥ 4)",
        "flag_qa_gap": "Brecha de QA (QA inadecuada + complejidad ≥ 4)",
        "flag_api_exposure": "Exposición por APIs (Dependencia fuerte + datos sensibles)",
    }
    summary = {}
    for col in flag_cols:
        affected = df[df[col]]["startup_name"].tolist()
        summary[col.replace("flag_", "")] = {
            "description": flag_descriptions.get(col, col),
            "affected_count": len(affected),
            "affected_startups": affected,
        }
    return summary


def export_llm_telemetry(
    df: pd.DataFrame, viz_manifest: list[dict], output_dir: Path
) -> Path:
    """
    Exporta telemetría completa en JSON optimizado para inyección en prompts LLM.

    Estructura del output:
    - metadata: Versión, timestamp, dimensiones
    - executive_summary: Distribuciones clave y alertas
    - dimensional_analysis: Estadísticas por dimensión
    - cross_tabulations: Cruces de variables críticas
    - risk_profiles: Perfil detallado por startup (ordenado por riesgo)
    - vulnerability_flags: Resumen de alertas cruzadas
    - visualization_manifest: Metadatos de gráficas generadas
    - mentorship_allocation: Distribución de demanda
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    telemetry = {
        "$schema": "observatorio-telemetria-arquitectura-v1",
        "metadata": {
            "pipeline_version": PIPELINE_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "Diagnóstico de Arquitectura y Plan de Desarrollo",
            "n_startups": len(df),
            "n_features": len(df.columns),
            "risk_scoring_weights": RISK_WEIGHTS,
            "response_period": {
                "first": df["timestamp"].min().isoformat(),
                "last": df["timestamp"].max().isoformat(),
            },
        },
        "executive_summary": {
            "total_startups": len(df),
            "risk_distribution": _distribution(df["risk_tier"]),
            "risk_score_stats": _descriptive_stats(df["risk_score"]),
            "complexity_stats": _descriptive_stats(df["complexity_score"]),
            "dominant_platform": df["platform_clean"].mode().iloc[0],
            "dominant_frontend": df["frontend_clean"].mode().iloc[0],
            "dominant_backend": df["backend_clean"].mode().iloc[0],
            "startups_with_flags": int((df["total_flags"] > 0).sum()),
            "startups_zero_flags": int((df["total_flags"] == 0).sum()),
        },
        "dimensional_analysis": {
            "team_structure": _distribution(df["dedicated_devs"]),
            "code_management": _distribution(df["code_management"]),
            "platform": _distribution(df["platform_clean"]),
            "frontend_stack": _distribution(df["frontend_clean"]),
            "backend_stack": _distribution(df["backend_clean"]),
            "api_dependency": _distribution(df["api_dependency"]),
            "cloud_budget": _distribution(df["cloud_budget"]),
            "data_sensitivity": _distribution(df["data_sensitivity"]),
            "qa_strategy": _distribution(df["qa_strategy"]),
            "ai_usage": _distribution(df["ai_usage"]),
        },
        "cross_tabulations": _build_cross_tabulations(df),
        "vulnerability_flags": _build_flag_summary(df),
        "risk_profiles": _build_startup_profiles(df),
        "mentorship_allocation": _distribution(df["mentorship_clean"]),
        "visualization_manifest": viz_manifest,
    }

    output_path = output_dir / "telemetria_arquitectura.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(telemetry, f, ensure_ascii=False, indent=2, default=str)

    return output_path
