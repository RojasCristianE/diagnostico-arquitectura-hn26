#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  OBSERVATORIO DE INTELIGENCIA DE DATOS
  Pipeline de Telemetría Arquitectónica
  Centro de Innovación — INATEC Nicaragua
═══════════════════════════════════════════════════════════════════════════════

  Procesa el CSV del Diagnóstico de Arquitectura y Plan de Desarrollo,
  ejecuta limpieza, feature engineering, genera visualizaciones científicas
  y exporta telemetría optimizada para inyección en prompts LLM.

  Uso:
    python run_pipeline.py
"""
import sys
from src.config import PATHS, PIPELINE_VERSION
from src.cleaning import ingest_and_clean
from src.features import engineer_features
from src.visuals import generate_all_visualizations
from src.exporter import export_llm_telemetry


def main() -> int:
    print(f"\n{'═' * 60}")
    print(f"  OBSERVATORIO DE INTELIGENCIA DE DATOS")
    print(f"  Pipeline de Telemetría Arquitectónica v{PIPELINE_VERSION}")
    print(f"{'═' * 60}\n")

    # ── Phase 1: Data Ingestion & Cleaning ─────────────────────────────────
    print("[1/4] Ingesta y limpieza de datos...")
    try:
        df_clean = ingest_and_clean(PATHS["raw_csv"])
    except Exception as e:
        print(f"  ✗ ERROR en ingesta: {e}")
        return 1
    print(f"  ✓ {len(df_clean)} startups procesadas.\n")

    # ── Phase 2: Feature Engineering ───────────────────────────────────────
    print("[2/4] Ingeniería de características y scoring de riesgo...")
    df_enriched = engineer_features(df_clean)
    n_flags = (df_enriched["total_flags"] > 0).sum()
    print(f"  ✓ {len(df_enriched.columns)} features generadas.")
    print(f"  ⚠ {n_flags} startups con flags de vulnerabilidad activos.\n")

    # ── Phase 3: Visualization Generation ──────────────────────────────────
    print("[3/4] Generando visualizaciones científicas...")
    viz_manifest = generate_all_visualizations(df_enriched, PATHS["plots_dir"])
    print(f"  ✓ {len(viz_manifest)} gráficas exportadas a {PATHS['plots_dir']}\n")

    # ── Phase 4: LLM Telemetry Export ──────────────────────────────────────
    print("[4/4] Exportando telemetría optimizada para LLMs...")
    output_path = export_llm_telemetry(
        df_enriched, viz_manifest, PATHS["llm_context_dir"]
    )
    print(f"  ✓ Telemetría exportada: {output_path}\n")

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"{'═' * 60}")
    print(f"  PIPELINE COMPLETADO EXITOSAMENTE")
    print(f"{'═' * 60}")
    print(f"  Outputs:")
    print(f"    📊 Gráficas: {PATHS['plots_dir']}/")
    print(f"    📦 Telemetría: {output_path}")
    print(f"{'═' * 60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
