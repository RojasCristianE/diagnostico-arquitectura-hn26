"""
config.py — Constantes, mapeos de columnas y esquemas de codificación ordinal.

Toda la configuración centralizada del pipeline reside aquí para facilitar
la reproducibilidad y el mantenimiento.
"""
from pathlib import Path

PIPELINE_VERSION = "1.0.0"

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
PATHS = {
    "raw_csv": BASE_DIR / "data" / "respuestas.csv",
    "plots_dir": BASE_DIR / "outputs" / "plots",
    "llm_context_dir": BASE_DIR / "outputs" / "llm_context",
}

# ── Nombres cortos de columnas (orden fijo del Google Form) ────────────────────
COLUMN_SHORTNAMES = [
    "timestamp",
    "startup_name",
    "tech_lead",
    "dedicated_devs",
    "code_management",
    "platform",
    "frontend_stack",
    "backend_stack",
    "api_dependency",
    "cloud_budget",
    "data_sensitivity",
    "qa_strategy",
    "ai_usage",
    "complexity_score",
    "mentorship_priority",
]

# ── Normalización de respuestas de texto libre ─────────────────────────────────
PLATFORM_NORMALIZATION = {
    "Aplicación Web (Accesible desde el navegador).": "Web",
    "Aplicación Móvil Nativa (Android/iOS).": "Móvil Nativa",
    "Software de Escritorio (Windows/Mac/Linux).": "Escritorio",
    "Hardware / IoT / Dispositivo Físico.": "IoT/Hardware",
}
PLATFORM_KEYWORDS = {
    "flutter": "Híbrida (Web + Móvil)",
    "pagina web": "Web",
    "página web": "Web",
    "web": "Web",
}

FRONTEND_NORMALIZATION = {
    "HTML/CSS/JS puro.": "HTML/CSS/JS",
    "React / Next.js / Vue / Angular.": "React/Vue/Angular",
    "Flutter / React Native (Móvil).": "Flutter/RN",
    "Constructores No-Code (Glide, Bubble, WordPress).": "No-Code",
}
FRONTEND_KEYWORDS = {
    "react": "React/Vue/Angular",
    "vue": "React/Vue/Angular",
    "angular": "React/Vue/Angular",
    "next": "React/Vue/Angular",
    "vite": "React/Vue/Angular",
    "tailwind": "React/Vue/Angular",
    "typescript": "React/Vue/Angular",
    "flutter": "Flutter/RN",
    "react native": "Flutter/RN",
    "bootstrap": "HTML/CSS/JS",
    "boostrap": "HTML/CSS/JS",  # Typo in data
    "html": "HTML/CSS/JS",
    "python": "HTML/CSS/JS",  # "Html y posiblemente Python"
}

BACKEND_NORMALIZATION = {
    "El proyecto no requiere base de datos.": "Sin BD",
    "PHP (Laravel)": "PHP/Laravel",
    "JS (Node.js)": "Node.js",
    "Python (Django / FastAPI / Flask).": "Python",
    "Firebase / Supabase / PocketBase (BaaS).": "BaaS",
    "Bases de Datos Edge / Serverless Modernas (Turso, Cloudflare KV/D1).": "Edge/Serverless",
    "Otras.": "Otros",
}

MENTORSHIP_NORMALIZATION = {
    "Estructuración, despliegue y alojamiento de la Base de Datos (Backend).": "Backend/BD",
    "Conexión entre el diseño y la lógica (Integración de APIs / Frontend).": "Integración APIs",
    "Diseño de interfaces, experiencia de usuario y accesibilidad (UX/UI).": "UX/UI",
    "Configuración de servidores y despliegue en la nube.": "Cloud/Deploy",
    "Planes de Negocios/marketing.": "Negocios/Marketing",
}
MENTORSHIP_KEYWORDS = {
    "ui": "UX/UI",
    "ux": "UX/UI",
    "interfaz": "UX/UI",
    "pasarela": "Integración APIs",
    "pago": "Integración APIs",
    "api": "Integración APIs",
    "offline": "UX/UI",
    "base de datos": "Backend/BD",
    "backend": "Backend/BD",
    "servidor": "Cloud/Deploy",
    "nube": "Cloud/Deploy",
    "negocio": "Negocios/Marketing",
    "marketing": "Negocios/Marketing",
}

# ── Codificación ordinal para scoring de riesgo ────────────────────────────────
# Valores más altos = más riesgo (escala 1-3)
ORDINAL_MAPS = {
    "dedicated_devs": {
        "dedicados": 1,
        "multidisciplinario": 2,
        "no tenemos": 3,
    },
    "code_management": {
        "ramas estructuradas": 1,
        "solo repositorio": 2,
        "manuales": 3,
    },
    "data_sensitivity": {
        "baja": 1,
        "media": 2,
        "alta": 3,
    },
    "qa_strategy": {
        "automatizadas": 1,
        "manuales": 2,
        "a medida": 3,
    },
    "cloud_budget": {
        "calculado": 1,
        "gratuitas": 2,
        "no hemos": 3,
    },
    "api_dependency": {
        "desarrollo propio": 1,
        "secundarias": 2,
        "fuertemente": 3,
    },
    "ai_usage": {
        "no utilizaremos": 1,
        "funcionalidad extra": 2,
        "núcleo": 3,
    },
}

# ── Pesos para el Risk Score compuesto ─────────────────────────────────────────
RISK_WEIGHTS = {
    "dedicated_devs_risk": 0.15,
    "code_management_risk": 0.20,
    "data_sensitivity_risk": 0.10,
    "qa_strategy_risk": 0.15,
    "cloud_budget_risk": 0.10,
    "api_dependency_risk": 0.10,
    "complexity_normalized": 0.20,
}

# ── Paleta visual (Tema Oscuro Institucional) ──────────────────────────────────
PALETTE = {
    "primary": "#3b82f6",
    "secondary": "#06b6d4",
    "accent": "#f59e0b",
    "danger": "#ef4444",
    "success": "#10b981",
    "neutral": "#6b7280",
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "text_light": "#e2e8f0",
    "grid": "#334155",
}

RISK_TIER_COLORS = {
    "Crítico": "#dc2626",
    "Alto": "#f97316",
    "Medio": "#eab308",
    "Bajo": "#22c55e",
}

RISK_TIER_THRESHOLDS = {
    "Crítico": 0.80,
    "Alto": 0.60,
    "Medio": 0.40,
    # Everything below 0.40 is "Bajo"
}

DARK_RCPARAMS = {
    "figure.facecolor": "#0f172a",
    "axes.facecolor": "#1e293b",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#e2e8f0",
    "text.color": "#e2e8f0",
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "grid.color": "#334155",
    "grid.alpha": 0.3,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "#0f172a",
    "savefig.pad_inches": 0.3,
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
}
