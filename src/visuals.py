"""
visuals.py — Generación de Visualizaciones Científicas de Alto Impacto.

Produce 6 gráficas profesionales con tema oscuro institucional exportadas
en alta resolución (300 DPI) para uso en informes y presentaciones.
"""
import matplotlib
matplotlib.use("Agg")  # Backend no-interactivo
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from .config import PALETTE, RISK_TIER_COLORS, DARK_RCPARAMS

# Intentar importar squarify para treemap
try:
    import squarify
    HAS_SQUARIFY = True
except ImportError:
    HAS_SQUARIFY = False


def _apply_dark_theme():
    """Aplica el tema oscuro institucional a matplotlib."""
    plt.rcParams.update(DARK_RCPARAMS)


def _save_figure(fig, path: Path, viz_id: str) -> dict:
    """Guarda figura y retorna entrada del manifiesto."""
    fig.savefig(path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return {"id": viz_id, "path": str(path)}


def viz_01_stack_heatmap(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 01: Matriz de Ecosistema Tecnológico (Frontend × Backend).
    Heatmap que muestra las combinaciones de stack elegidas por las startups.
    """
    _apply_dark_theme()
    ct = pd.crosstab(df["frontend_clean"], df["backend_clean"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        ct,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor=PALETTE["grid"],
        ax=ax,
        cbar_kws={"label": "Nº de Startups", "shrink": 0.8},
        square=False,
    )
    ax.set_title("Matriz de Ecosistema Tecnológico\nFrontend × Backend", pad=15)
    ax.set_xlabel("Backend Stack")
    ax.set_ylabel("Frontend Stack")
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()

    path = output_dir / "01_stack_heatmap.png"
    return _save_figure(fig, path, "stack_heatmap") | {
        "title": "Matriz de Ecosistema Tecnológico (Frontend × Backend)",
        "description": "Heatmap de combinaciones de stack tecnológico. Revela clustering de ecosistemas y dependencias tecnológicas dominantes.",
    }


def viz_02_risk_ranking(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 02: Ranking de Riesgo Arquitectónico por Startup.
    Barras horizontales ordenadas por risk_score, coloreadas por tier.
    """
    _apply_dark_theme()
    df_sorted = df.sort_values("risk_score", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = [RISK_TIER_COLORS[tier] for tier in df_sorted["risk_tier"]]

    bars = ax.barh(
        df_sorted["startup_name"],
        df_sorted["risk_score"],
        color=colors,
        edgecolor=PALETTE["bg_dark"],
        linewidth=0.5,
        height=0.7,
    )

    # Añadir valores y tier label
    for bar, score, tier in zip(
        bars, df_sorted["risk_score"], df_sorted["risk_tier"]
    ):
        ax.text(
            bar.get_width() + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f} [{tier}]",
            va="center",
            fontsize=9,
            color=PALETTE["text_light"],
        )

    # Líneas de umbral
    for tier, threshold in [("Crítico", 0.80), ("Alto", 0.60), ("Medio", 0.40)]:
        ax.axvline(
            x=threshold,
            color=RISK_TIER_COLORS[tier],
            linestyle="--",
            alpha=0.4,
            linewidth=1,
        )

    ax.set_xlim(0, 1.0)
    ax.set_title(
        "Ranking de Riesgo Arquitectónico por Startup", pad=15
    )
    ax.set_xlabel("Risk Score (0 = bajo riesgo → 1 = crítico)")
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    fig.tight_layout()

    path = output_dir / "02_risk_ranking.png"
    return _save_figure(fig, path, "risk_ranking") | {
        "title": "Ranking de Riesgo Arquitectónico por Startup",
        "description": "Clasificación de startups por score de riesgo compuesto. Identifica proyectos que requieren intervención prioritaria.",
    }


def viz_03_security_matrix(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 03: Matriz de Vulnerabilidad de Seguridad.
    Cruce de Sensibilidad de Datos × Gestión de Código.
    """
    _apply_dark_theme()

    # Crear etiquetas legibles para los ejes
    sensitivity_labels = {1: "Baja", 2: "Media", 3: "Alta"}
    code_mgmt_labels = {1: "Ramas\nestructuradas", 2: "Repo\núnico", 3: "Manual\n(Drive/USB)"}

    df_plot = df.copy()
    df_plot["sens_label"] = df_plot["data_sensitivity_risk"].map(sensitivity_labels)
    df_plot["code_label"] = df_plot["code_management_risk"].map(code_mgmt_labels)

    ct = pd.crosstab(df_plot["sens_label"], df_plot["code_label"])
    # Reindexar para orden lógico
    sens_order = ["Baja", "Media", "Alta"]
    code_order = ["Ramas\nestructuradas", "Repo\núnico", "Manual\n(Drive/USB)"]
    ct = ct.reindex(index=[s for s in sens_order if s in ct.index],
                    columns=[c for c in code_order if c in ct.columns],
                    fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        ct,
        annot=True,
        fmt="d",
        cmap=sns.color_palette(
            [PALETTE["success"], PALETTE["accent"], PALETTE["danger"]], as_cmap=True
        ),
        linewidths=1,
        linecolor=PALETTE["bg_dark"],
        ax=ax,
        cbar_kws={"label": "Nº de Startups"},
        square=True,
    )
    ax.set_title(
        "Matriz de Vulnerabilidad de Seguridad\nSensibilidad de Datos × Gestión de Código",
        pad=15,
    )
    ax.set_ylabel("Sensibilidad de Datos")
    ax.set_xlabel("Gestión de Código Fuente")
    fig.tight_layout()

    path = output_dir / "03_security_matrix.png"
    return _save_figure(fig, path, "security_matrix") | {
        "title": "Matriz de Vulnerabilidad de Seguridad",
        "description": "Cruce de sensibilidad de datos vs. prácticas de gestión de código. El cuadrante Alta+Manual indica vulnerabilidad crítica.",
    }


def viz_04_radar_profile(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 04: Perfil de Riesgo Promedio del Ecosistema (Radar).
    Spider chart con las dimensiones de riesgo promedio del cohort.
    """
    _apply_dark_theme()

    dimensions = [
        ("Equipo\nDedicado", "dedicated_devs_risk"),
        ("Gestión\nde Código", "code_management_risk"),
        ("Sensibilidad\nde Datos", "data_sensitivity_risk"),
        ("Estrategia\nQA", "qa_strategy_risk"),
        ("Presupuesto\nCloud", "cloud_budget_risk"),
        ("Dependencia\nAPIs", "api_dependency_risk"),
        ("Uso de IA", "ai_usage_risk"),
    ]

    labels = [d[0] for d in dimensions]
    # Normalizar promedios de [1,3] a [0,1]
    values = [((df[d[1]].mean() - 1) / 2.0) for d in dimensions]

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_closed = values + [values[0]]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_facecolor(PALETTE["bg_card"])
    fig.set_facecolor(PALETTE["bg_dark"])

    # Relleno y línea
    ax.fill(angles_closed, values_closed, color=PALETTE["danger"], alpha=0.15)
    ax.plot(
        angles_closed,
        values_closed,
        color=PALETTE["danger"],
        linewidth=2,
        marker="o",
        markersize=6,
    )

    # Zona ideal (todo bajo)
    ideal = [0.2] * N + [0.2]
    ax.fill(angles_closed, ideal, color=PALETTE["success"], alpha=0.08)
    ax.plot(
        angles_closed,
        ideal,
        color=PALETTE["success"],
        linewidth=1,
        linestyle="--",
        alpha=0.5,
    )

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=9, color=PALETTE["text_light"])
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=8, color=PALETTE["neutral"])
    ax.spines["polar"].set_color(PALETTE["grid"])
    ax.grid(color=PALETTE["grid"], alpha=0.3)

    ax.set_title(
        "Perfil de Riesgo del Ecosistema\n(Promedio de todas las startups)",
        pad=25,
        color=PALETTE["text_light"],
    )
    fig.tight_layout()

    path = output_dir / "04_radar_profile.png"
    return _save_figure(fig, path, "radar_profile") | {
        "title": "Perfil de Riesgo Promedio del Ecosistema (Radar)",
        "description": "Spider chart multidimensional del riesgo promedio del cohort. Revela las debilidades sistémicas del ecosistema.",
    }


def viz_05_mentorship_distribution(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 05: Distribución de Demanda de Mentoría (Treemap o Donut).
    """
    _apply_dark_theme()
    counts = df["mentorship_clean"].value_counts()

    color_cycle = [
        PALETTE["primary"],
        PALETTE["secondary"],
        PALETTE["accent"],
        PALETTE["danger"],
        PALETTE["success"],
        PALETTE["neutral"],
    ]

    if HAS_SQUARIFY and len(counts) >= 2:
        # Treemap
        fig, ax = plt.subplots(figsize=(10, 6))
        labels = [
            f"{name}\n({count} — {count/len(df)*100:.0f}%)"
            for name, count in zip(counts.index, counts.values)
        ]
        colors_list = color_cycle[: len(counts)]
        squarify.plot(
            sizes=counts.values,
            label=labels,
            color=colors_list,
            alpha=0.85,
            text_kwargs={"fontsize": 11, "color": "white", "fontweight": "bold"},
            ax=ax,
        )
        ax.axis("off")
        ax.set_title(
            "Distribución de Demanda de Mentoría Prioritaria", pad=15
        )
    else:
        # Fallback: donut chart
        fig, ax = plt.subplots(figsize=(8, 8))
        colors_list = color_cycle[: len(counts)]
        wedges, texts, autotexts = ax.pie(
            counts.values,
            labels=counts.index,
            colors=colors_list,
            autopct="%1.0f%%",
            startangle=90,
            pctdistance=0.75,
            textprops={"color": PALETTE["text_light"], "fontsize": 10},
        )
        centre_circle = plt.Circle((0, 0), 0.55, fc=PALETTE["bg_dark"])
        ax.add_artist(centre_circle)
        ax.set_title(
            "Distribución de Demanda de Mentoría Prioritaria", pad=15
        )

    fig.tight_layout()
    path = output_dir / "05_mentorship_distribution.png"
    return _save_figure(fig, path, "mentorship_distribution") | {
        "title": "Distribución de Demanda de Mentoría Prioritaria",
        "description": "Distribución de áreas de mentoría solicitadas. Informa la asignación estratégica de recursos de acompañamiento.",
    }


def viz_06_complexity_landscape(df: pd.DataFrame, output_dir: Path) -> dict:
    """
    VIZ 06: Paisaje de Complejidad vs Riesgo (Scatter con anotaciones).
    Ejes: Complejidad × Risk Score. Color por plataforma. Tamaño por flags.
    """
    _apply_dark_theme()

    platform_colors = {
        "Web": PALETTE["primary"],
        "Móvil Nativa": PALETTE["accent"],
        "Híbrida (Web + Móvil)": PALETTE["secondary"],
    }

    fig, ax = plt.subplots(figsize=(11, 7))

    for platform in df["platform_clean"].unique():
        mask = df["platform_clean"] == platform
        subset = df[mask]
        color = platform_colors.get(platform, PALETTE["neutral"])
        sizes = 80 + subset["total_flags"] * 60

        ax.scatter(
            subset["complexity_score"],
            subset["risk_score"],
            s=sizes,
            c=color,
            alpha=0.75,
            edgecolors="white",
            linewidth=0.5,
            label=platform,
            zorder=3,
        )

    # Anotaciones de nombres
    for _, row in df.iterrows():
        ax.annotate(
            row["startup_name"],
            (row["complexity_score"], row["risk_score"]),
            textcoords="offset points",
            xytext=(8, 5),
            fontsize=7.5,
            color=PALETTE["text_light"],
            alpha=0.85,
        )

    # Cuadrantes de riesgo
    ax.axhline(y=0.50, color=PALETTE["accent"], linestyle=":", alpha=0.4)
    ax.axvline(x=3.5, color=PALETTE["accent"], linestyle=":", alpha=0.4)
    ax.text(4.6, 0.88, "ZONA\nCRÍTICA", fontsize=10, color=PALETTE["danger"],
            ha="center", alpha=0.6, fontweight="bold")

    ax.set_xlabel("Complejidad Auto-Reportada (1-5)")
    ax.set_ylabel("Risk Score Compuesto")
    ax.set_title(
        "Paisaje de Complejidad vs Riesgo Arquitectónico",
        pad=15,
    )
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    ax.legend(title="Plataforma", loc="upper left", framealpha=0.3)
    fig.tight_layout()

    path = output_dir / "06_complexity_landscape.png"
    return _save_figure(fig, path, "complexity_landscape") | {
        "title": "Paisaje de Complejidad vs Riesgo Arquitectónico",
        "description": "Scatter bidimensional: complejidad auto-reportada vs. riesgo calculado. El tamaño del punto indica el número de flags de vulnerabilidad activos. Identifica startups en la 'zona crítica' (alta complejidad + alto riesgo).",
    }


def generate_all_visualizations(
    df: pd.DataFrame, output_dir: Path
) -> list[dict]:
    """Ejecuta todas las visualizaciones y retorna el manifiesto completo."""
    output_dir.mkdir(parents=True, exist_ok=True)

    generators = [
        viz_01_stack_heatmap,
        viz_02_risk_ranking,
        viz_03_security_matrix,
        viz_04_radar_profile,
        viz_05_mentorship_distribution,
        viz_06_complexity_landscape,
    ]

    manifest = []
    for gen in generators:
        entry = gen(df, output_dir)
        manifest.append(entry)
        print(f"      ✓ {entry['title']}")

    return manifest
