"""
features.py — Ingeniería de Características y Scoring de Riesgo Arquitectónico.

Genera variables derivadas mediante cruce de dimensiones y produce un
Risk Score compuesto normalizado [0, 1] para cada startup.
"""
import pandas as pd
import numpy as np
from .config import ORDINAL_MAPS, RISK_WEIGHTS, RISK_TIER_THRESHOLDS


def _ordinal_encode(series: pd.Series, dimension: str) -> pd.Series:
    """
    Codificación ordinal basada en keyword matching contra ORDINAL_MAPS.
    Retorna valores 1-3 (1=bajo riesgo, 3=alto riesgo).
    """
    keyword_map = ORDINAL_MAPS[dimension]

    def match(value):
        if pd.isna(value):
            return 2  # Default: riesgo medio si falta dato
        val_lower = str(value).lower()
        for keyword, score in keyword_map.items():
            if keyword in val_lower:
                return score
        return 2  # Default medio

    return series.apply(match)


def _assign_risk_tier(score: float) -> str:
    """Clasifica un risk_score [0,1] en un tier categórico."""
    for tier, threshold in RISK_TIER_THRESHOLDS.items():
        if score >= threshold:
            return tier
    return "Bajo"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade columnas de riesgo ordinal, flags de vulnerabilidad cruzada
    y un Risk Score compuesto normalizado.
    """
    df = df.copy()

    # ── Codificación ordinal por dimensión ─────────────────────────────────
    risk_dimensions = [
        "dedicated_devs",
        "code_management",
        "data_sensitivity",
        "qa_strategy",
        "cloud_budget",
        "api_dependency",
        "ai_usage",
    ]
    for dim in risk_dimensions:
        df[f"{dim}_risk"] = _ordinal_encode(df[dim], dim)

    # ── Normalización de complejidad a escala [0, 1] ───────────────────────
    df["complexity_normalized"] = df["complexity_score"] / 5.0

    # ── Risk Score compuesto (promedio ponderado normalizado) ───────────────
    risk_components = []
    for col, weight in RISK_WEIGHTS.items():
        if col == "complexity_normalized":
            component = df["complexity_normalized"] * weight
        else:
            # Normalizar de [1,3] a [0,1] antes de ponderar
            component = ((df[col] - 1) / 2.0) * weight
        risk_components.append(component)

    df["risk_score"] = sum(risk_components)
    # Renormalizar al rango real [0, 1]
    max_possible = sum(RISK_WEIGHTS.values())
    df["risk_score"] = df["risk_score"] / max_possible

    df["risk_tier"] = df["risk_score"].apply(_assign_risk_tier)

    # ── Flags de vulnerabilidad cruzada ────────────────────────────────────

    # FLAG 1: Vulnerabilidad de Seguridad
    # Alta sensibilidad de datos + gestión manual de código
    df["flag_security_vuln"] = (df["data_sensitivity_risk"] == 3) & (
        df["code_management_risk"] >= 2
    )

    # FLAG 2: Crisis de Presupuesto
    # No han explorado costos + complejidad alta (>=4)
    df["flag_budget_crisis"] = (df["cloud_budget_risk"] == 3) & (
        df["complexity_score"] >= 4
    )

    # FLAG 3: Tensión de Equipo
    # Sin devs dedicados + complejidad alta
    df["flag_team_strain"] = (df["dedicated_devs_risk"] >= 2) & (
        df["complexity_score"] >= 4
    )

    # FLAG 4: QA Insuficiente para Complejidad
    # QA ad-hoc + complejidad >= 4
    df["flag_qa_gap"] = (df["qa_strategy_risk"] >= 2) & (df["complexity_score"] >= 4)

    # FLAG 5: Dependencia Crítica de APIs
    # Depende fuertemente de APIs + alta sensibilidad
    df["flag_api_exposure"] = (df["api_dependency_risk"] == 3) & (
        df["data_sensitivity_risk"] >= 2
    )

    # ── Conteo total de flags por startup ──────────────────────────────────
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    df["total_flags"] = df[flag_cols].sum(axis=1)

    # ── Índice de Madurez Arquitectónica (inverso del riesgo) ──────────────
    df["maturity_index"] = (1 - df["risk_score"]).round(3)

    return df
