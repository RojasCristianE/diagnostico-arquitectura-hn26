"""
cleaning.py — Ingesta de datos y normalización del CSV de respuestas.

Responsabilidades:
  1. Lectura del CSV con encoding correcto.
  2. Renombramiento posicional de columnas a shortnames.
  3. Normalización de respuestas de texto libre (platform, frontend, mentorship).
  4. Limpieza de strings (strip, títulos).
"""
import pandas as pd
from pathlib import Path
from .config import (
    COLUMN_SHORTNAMES,
    PLATFORM_NORMALIZATION,
    PLATFORM_KEYWORDS,
    FRONTEND_NORMALIZATION,
    FRONTEND_KEYWORDS,
    BACKEND_NORMALIZATION,
    MENTORSHIP_NORMALIZATION,
    MENTORSHIP_KEYWORDS,
)


def _normalize_field(value: str, exact_map: dict, keyword_map: dict) -> str:
    """Normaliza un campo: primero busca coincidencia exacta, luego keywords."""
    if pd.isna(value):
        return "Sin respuesta"
    value_stripped = value.strip()
    # Exact match
    if value_stripped in exact_map:
        return exact_map[value_stripped]
    # Keyword match (case-insensitive)
    value_lower = value_stripped.lower()
    for keyword, canonical in keyword_map.items():
        if keyword in value_lower:
            return canonical
    return value_stripped  # Fallback: return cleaned original


def _normalize_backend(value: str) -> str:
    """Normalización específica para backend (sin keyword fallback complejo)."""
    if pd.isna(value):
        return "Sin respuesta"
    value_stripped = value.strip()
    if value_stripped in BACKEND_NORMALIZATION:
        return BACKEND_NORMALIZATION[value_stripped]
    return value_stripped


def ingest_and_clean(csv_path: Path) -> pd.DataFrame:
    """
    Lee el CSV de respuestas del diagnóstico y devuelve un DataFrame limpio
    con columnas renombradas y valores normalizados.
    """
    df = pd.read_csv(csv_path, encoding="utf-8")

    # ── Renombrar columnas por posición ────────────────────────────────────
    if len(df.columns) != len(COLUMN_SHORTNAMES):
        raise ValueError(
            f"CSV tiene {len(df.columns)} columnas, se esperaban {len(COLUMN_SHORTNAMES)}"
        )
    df.columns = COLUMN_SHORTNAMES

    # ── Limpieza básica de strings ─────────────────────────────────────────
    df["startup_name"] = df["startup_name"].str.strip()
    df["tech_lead"] = df["tech_lead"].str.strip().str.title()

    # ── Parseo del timestamp ───────────────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d/%m/%Y %H:%M:%S")

    # ── Parseo de complexity_score como entero ─────────────────────────────
    df["complexity_score"] = pd.to_numeric(df["complexity_score"], errors="coerce").astype(int)

    # ── Normalización de campos categóricos con texto libre ────────────────
    df["platform_clean"] = df["platform"].apply(
        lambda x: _normalize_field(x, PLATFORM_NORMALIZATION, PLATFORM_KEYWORDS)
    )
    df["frontend_clean"] = df["frontend_stack"].apply(
        lambda x: _normalize_field(x, FRONTEND_NORMALIZATION, FRONTEND_KEYWORDS)
    )
    df["backend_clean"] = df["backend_stack"].apply(_normalize_backend)
    df["mentorship_clean"] = df["mentorship_priority"].apply(
        lambda x: _normalize_field(x, MENTORSHIP_NORMALIZATION, MENTORSHIP_KEYWORDS)
    )

    return df
