from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from src.golden_boot_model import (
    ModelConfig,
    model_players,
    rank_players,
    simulate_golden_boot,
)

st.set_page_config(page_title="Bota de Oro 2026", page_icon="⚽", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f17;
        --panel: #111722;
        --panel-2: #151c28;
        --stroke: rgba(255, 255, 255, 0.10);
        --muted: rgba(255, 255, 255, 0.64);
        --text: rgba(255, 255, 255, 0.95);
        --accent: #ff4b4b;
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2.4rem;
        max-width: 1680px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    [data-testid="stDeployButton"] {display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important;}

    .hero {
        border: 1px solid var(--stroke);
        background: radial-gradient(circle at 12% 20%, rgba(255, 75, 75, 0.15), transparent 30%),
                    linear-gradient(135deg, #121925 0%, #0b0f17 62%, #101722 100%);
        border-radius: 24px;
        padding: 2rem 2.1rem 1.65rem 2.1rem;
        margin-bottom: 1.35rem;
        box-shadow: 0 18px 48px rgba(0, 0, 0, 0.24);
    }
    .eyebrow {
        display: inline-flex;
        gap: 0.4rem;
        align-items: center;
        border: 1px solid rgba(255, 75, 75, 0.35);
        background: rgba(255, 75, 75, 0.10);
        color: #ffb2b2;
        border-radius: 999px;
        padding: 0.28rem 0.7rem;
        font-size: 0.84rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-bottom: 0.75rem;
    }
    .hero h1 {
        margin: 0 0 0.45rem 0;
        color: var(--text);
        font-size: clamp(2.05rem, 3vw, 3.25rem);
        line-height: 1.05;
        letter-spacing: -0.045em;
    }
    .hero p {
        margin: 0;
        color: var(--muted);
        max-width: 980px;
        font-size: 1.02rem;
        line-height: 1.55;
    }

    .kpi-card {
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, #171e2b 0%, #101722 100%);
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.22);
        padding: 1.08rem 1.15rem;
        border-radius: 18px;
        min-height: 112px;
    }
    .kpi-label {
        color: rgba(255, 255, 255, 0.64);
        font-size: 0.86rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        color: rgba(255, 255, 255, 0.97);
        font-size: 1.75rem;
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    .kpi-helper {
        color: rgba(255, 255, 255, 0.50);
        font-size: 0.82rem;
        margin-top: 0.45rem;
    }

    .insight-card {
        border: 1px solid var(--stroke);
        background: linear-gradient(180deg, #121925 0%, #0f1520 100%);
        border-radius: 20px;
        padding: 1.2rem 1.25rem;
        margin: 0.35rem 0 1.25rem 0;
    }
    .insight-title {
        color: rgba(255, 255, 255, 0.96);
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .insight-body {
        color: rgba(255, 255, 255, 0.68);
        font-size: 0.96rem;
        line-height: 1.55;
    }

    .source-pill a {
        color: #8ec5ff !important;
        text-decoration: none;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.55rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi(label: str, value: str, helper: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            <div class="kpi-helper">{html.escape(helper)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.header("Ajustes")
    simulations = st.slider("Simulaciones", 1_000, 100_000, 25_000, 1_000)
    random_seed = st.number_input("Semilla", value=26, step=1)

    with st.expander("Parámetros avanzados", expanded=False):
        shot_to_goal_rate = st.number_input(
            "Conversión tiro-gol",
            value=0.105,
            min_value=0.01,
            max_value=0.30,
            step=0.005,
            format="%.3f",
        )
        st.caption("Pesos usados para construir el rate goleador por 90 minutos.")
        w_npxg = st.number_input("npxG/90", value=0.55, step=0.05, format="%.2f")
        w_goals = st.number_input("Goles/90 recientes", value=0.25, step=0.05, format="%.2f")
        w_intl = st.number_input("Goles/90 selección", value=0.10, step=0.05, format="%.2f")
        w_shots = st.number_input("Tiros/90", value=0.10, step=0.05, format="%.2f")

    with st.expander("Actualizar base", expanded=False):
        uploaded = st.file_uploader("Cargar CSV", type=["csv"])

try:
    uploaded_file = uploaded
except NameError:
    uploaded_file = None

# Defaults are repeated here so older Streamlit reruns remain safe if the expander is not initialized.
shot_to_goal_rate = locals().get("shot_to_goal_rate", 0.105)
w_npxg = locals().get("w_npxg", 0.55)
w_goals = locals().get("w_goals", 0.25)
w_intl = locals().get("w_intl", 0.10)
w_shots = locals().get("w_shots", 0.10)

config = ModelConfig(
    weights={
        "npxg90": w_npxg,
        "verified_goals90": w_goals,
        "verified_intl_goals90": w_intl,
        "shots90": w_shots,
    },
    shot_to_goal_rate=shot_to_goal_rate,
)

players = pd.read_csv(uploaded_file) if uploaded_file else pd.read_csv("data/players_seed.csv")
players.columns = [c.replace("\ufeff", "") for c in players.columns]

try:
    players_model = model_players(players)
    ranked = rank_players(players, config=config)
    sim = simulate_golden_boot(
        players,
        simulations=int(simulations),
        random_seed=int(random_seed),
        config=config,
    )
except Exception as exc:
    st.error("No fue posible calcular el modelo con la base cargada.")
    st.caption(str(exc))
    st.stop()

ranked = ranked.copy()
sim = sim.copy()
ranked["rank_expected_goals"] = ranked["rank_expected_goals"].astype(int)

leader = sim.iloc[0]
leader_row = ranked.loc[ranked["player"].eq(leader["player"])].iloc[0]
leader_xg = float(leader_row["expected_goals_total"])
leader_prob = float(leader["golden_boot_probability_pct"])
quality_avg = pd.to_numeric(players_model.get("data_quality_score"), errors="coerce").mean()
quality_label = "—" if pd.isna(quality_avg) else f"{quality_avg:.2f}"

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">⚽ Modelo predictivo · Copa Mundial 2026</div>
        <h1>Predicción Bota de Oro — Mundial 2026</h1>
        <p>Estimación estadística del máximo goleador del torneo a partir de producción ofensiva reciente, minutos proyectados, penales y contexto competitivo de cada selección.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi("Favorito del modelo", str(leader["player"]), str(leader["team"]))
with c2:
    kpi("Probabilidad estimada", f"{leader_prob:.1f}%", f"{int(simulations):,} simulaciones")
with c3:
    kpi("Goles esperados", f"{leader_xg:.2f}", "media del modelo")
with c4:
    kpi("Candidatos evaluados", f"{len(players_model):,}", f"confianza promedio {quality_label}")

leader_source = str(leader_row.get("source_primary", "")).strip()
source_html = (
    f" <span class='source-pill'><a href='{html.escape(leader_source)}' target='_blank'>Ver fuente principal</a></span>"
    if leader_source
    else ""
)

st.markdown(
    f"""
    <div class="insight-card">
        <div class="insight-title">Conclusión del modelo</div>
        <div class="insight-body">
            Con los parámetros actuales, <strong>{html.escape(str(leader['player']))}</strong> aparece como el principal candidato a la Bota de Oro, con una probabilidad estimada de <strong>{leader_prob:.1f}%</strong> y una media de <strong>{leader_xg:.2f}</strong> goles esperados. El ranking debe leerse como una estimación probabilística, no como una certeza: los resultados cambian si se ajustan minutos, penales, forma reciente o proyección de partidos de cada selección.{source_html}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_result, tab_ranking, tab_data, tab_method = st.tabs([
    "Resultado",
    "Ranking completo",
    "Base de candidatos",
    "Metodología",
])

with tab_result:
    left, right = st.columns([1, 1])

    with left:
        st.subheader("Top 5 candidatos")
        top5 = sim.head(5).merge(
            ranked[["player", "individual_rate90", "expected_open_play_goals", "expected_penalty_goals"]],
            on="player",
            how="left",
        )
        top5_view = top5.rename(
            columns={
                "player": "Jugador",
                "team": "Selección",
                "expected_goals_total": "Goles esperados",
                "golden_boot_probability_pct": "Probabilidad (%)",
                "individual_rate90": "Rate/90",
                "expected_open_play_goals": "Jugada",
                "expected_penalty_goals": "Penal",
            }
        )
        st.dataframe(
            top5_view[["Jugador", "Selección", "Goles esperados", "Probabilidad (%)", "Rate/90", "Jugada", "Penal"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Goles esperados": st.column_config.NumberColumn(format="%.2f"),
                "Probabilidad (%)": st.column_config.NumberColumn(format="%.1f"),
                "Rate/90": st.column_config.NumberColumn(format="%.3f"),
                "Jugada": st.column_config.NumberColumn(format="%.2f"),
                "Penal": st.column_config.NumberColumn(format="%.2f"),
            },
        )

    with right:
        st.subheader("Probabilidad estimada")
        chart_data = sim.head(12).set_index("player")["golden_boot_probability_pct"]
        st.bar_chart(chart_data)

with tab_ranking:
    st.subheader("Ranking completo del modelo")
    ranking_view = ranked[[
        c for c in [
            "rank_expected_goals",
            "player",
            "team",
            "position",
            "individual_rate90",
            "expected_open_play_goals",
            "expected_penalty_goals",
            "expected_goals_total",
            "data_quality_score",
            "source_primary",
        ]
        if c in ranked.columns
    ]].copy()

    ranking_view = ranking_view.rename(
        columns={
            "rank_expected_goals": "Rank",
            "player": "Jugador",
            "team": "Selección",
            "position": "Posición",
            "individual_rate90": "Rate/90",
            "expected_open_play_goals": "Goles jugada",
            "expected_penalty_goals": "Goles penal",
            "expected_goals_total": "Goles esperados",
            "data_quality_score": "Confianza",
            "source_primary": "Fuente",
        }
    )
    st.dataframe(
        ranking_view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fuente": st.column_config.LinkColumn("Fuente", display_text="Ver fuente"),
            "Rate/90": st.column_config.NumberColumn(format="%.3f"),
            "Goles jugada": st.column_config.NumberColumn(format="%.2f"),
            "Goles penal": st.column_config.NumberColumn(format="%.2f"),
            "Goles esperados": st.column_config.NumberColumn(format="%.2f"),
            "Confianza": st.column_config.NumberColumn(format="%.2f"),
        },
    )

with tab_data:
    st.subheader("Candidatos incluidos en el cálculo")
    candidate_cols = [
        "player",
        "team",
        "club",
        "position",
        "verified_competition",
        "verified_goals",
        "verified_assists",
        "verified_minutes",
        "npxg90",
        "verified_goals90",
        "shots90",
        "expected_team_matches",
        "data_quality_score",
        "source_player_stats",
    ]
    candidate_view = players_model[[c for c in candidate_cols if c in players_model.columns]].copy()
    candidate_view = candidate_view.rename(
        columns={
            "player": "Jugador",
            "team": "Selección",
            "club": "Club",
            "position": "Posición",
            "verified_competition": "Competición base",
            "verified_goals": "Goles",
            "verified_assists": "Asistencias",
            "verified_minutes": "Minutos",
            "npxg90": "npxG/90",
            "verified_goals90": "Goles/90",
            "shots90": "Tiros/90",
            "expected_team_matches": "Partidos estimados",
            "data_quality_score": "Confianza",
            "source_player_stats": "Fuente",
        }
    )
    st.dataframe(
        candidate_view,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fuente": st.column_config.LinkColumn("Fuente", display_text="Ver fuente"),
            "npxG/90": st.column_config.NumberColumn(format="%.3f"),
            "Goles/90": st.column_config.NumberColumn(format="%.3f"),
            "Tiros/90": st.column_config.NumberColumn(format="%.2f"),
            "Partidos estimados": st.column_config.NumberColumn(format="%.1f"),
            "Confianza": st.column_config.NumberColumn(format="%.2f"),
        },
    )

    with st.expander("Ver base completa de jugadores", expanded=False):
        full_cols = [
            "player",
            "team",
            "team_code",
            "squad_number",
            "position",
            "club",
            "dob",
            "source_fifa_squad",
        ]
        full_view = players[[c for c in full_cols if c in players.columns]].copy()
        full_view = full_view.rename(
            columns={
                "player": "Jugador",
                "team": "Selección",
                "team_code": "Código",
                "squad_number": "Dorsal",
                "position": "Posición",
                "club": "Club",
                "dob": "Nacimiento",
                "source_fifa_squad": "Fuente plantilla",
            }
        )
        st.dataframe(
            full_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Fuente plantilla": st.column_config.LinkColumn("Fuente plantilla", display_text="FIFA"),
            },
        )

with tab_method:
    st.subheader("Metodología")
    st.markdown(
        """
        El modelo estima los goles esperados de cada jugador en dos componentes:

        **1. Goles de jugada**  
        Se calcula un rate goleador por 90 minutos usando npxG/90, goles recientes por 90, producción con selección y volumen de tiros. Luego se ajusta por minutos esperados, probabilidad de titularidad, fortaleza ofensiva de la selección y dificultad del grupo.

        **2. Goles por penales**  
        Se estima a partir de la probabilidad de que el jugador sea cobrador, la frecuencia esperada de penales de su selección y su conversión estimada.

        La probabilidad de Bota de Oro se obtiene con una simulación Monte Carlo. Cada simulación genera un posible torneo y asigna el primer lugar al jugador o jugadores con más goles simulados.
        """
    )

    method_cols = st.columns(3)
    with method_cols[0]:
        kpi("Simulaciones", f"{int(simulations):,}", "escenarios generados")
    with method_cols[1]:
        kpi("Confianza promedio", quality_label, "datos del ranking")
    with method_cols[2]:
        kpi("Base total", f"{len(players):,}", "jugadores en archivo")

    with st.expander("Parámetros actuales", expanded=False):
        params = pd.DataFrame(
            [
                {"Parámetro": "Peso npxG/90", "Valor": w_npxg},
                {"Parámetro": "Peso goles/90 recientes", "Valor": w_goals},
                {"Parámetro": "Peso goles/90 selección", "Valor": w_intl},
                {"Parámetro": "Peso tiros/90", "Valor": w_shots},
                {"Parámetro": "Conversión tiro-gol", "Valor": shot_to_goal_rate},
            ]
        )
        st.dataframe(params, use_container_width=True, hide_index=True)
