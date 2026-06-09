# Golden Boot 2026 — modelo predictivo compartible

Proyecto listo para abrir en Codex, GitHub Codespaces o localmente. Convierte una matriz tipo scouting en un modelo transparente para estimar:

1. goles esperados por jugador;
2. goles esperados por penales;
3. ranking de candidatos;
4. probabilidad de Bota de Oro vía simulación Monte Carlo.

> Principio editorial: ningún ranking serio debe publicarse sin fuentes verificables por fila. El CSV incluye columnas `source_*` y un `data_quality_score` para separar datos confirmados de supuestos del modelo.

## Estructura

```text
.
├── app.py                         # App Streamlit para compartir el modelo
├── data/
│   ├── players_seed.csv           # Datos iniciales y campos editables
│   └── sources_registry.csv       # Registro de fuentes recomendadas
├── docs/
│   ├── methodology.md             # Método explicado paso a paso
│   ├── data_dictionary.md         # Diccionario de variables
│   └── publication_checklist.md   # Checklist antes de publicar
├── scripts/
│   └── validate_sources.py        # Valida URLs obligatorias
├── src/
│   └── golden_boot_model.py       # Fórmulas y simulación
└── tests/
    └── test_model.py              # Tests básicos
```

## Cómo correrlo localmente

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
python scripts/validate_sources.py data/players_seed.csv
pytest -q
streamlit run app.py
```

## Cómo usarlo en Codex

1. Sube esta carpeta a un repo de GitHub.
2. Abre el repo en Codex.
3. Pega el contenido de `CODEX_TASK_PROMPT.md` como tarea inicial.
4. Pídele a Codex que corra `pytest -q` y `python scripts/validate_sources.py` antes de cualquier PR.

## Fórmula base

El modelo estima goles esperados por jugador:

```text
Expected Goals = open_play_goals + penalty_goals
```

Donde:

```text
open_play_goals = individual_rate90
                  × expected_team_matches
                  × expected_minutes_per_match / 90
                  × starter_probability
                  × team_attack_adjustment
                  × group_difficulty_adjustment
```

Y:

```text
penalty_goals = expected_team_penalties_per_match
                × expected_team_matches
                × penalty_taker_probability
                × penalty_conversion_probability
```

## Advertencia importante

El archivo `players_seed.csv` es una base inicial. Algunas filas están marcadas como demo o aproximadas cuando la fuente pública no entrega minutos/xG homogéneos. Para una predicción publicable, completa las plantillas oficiales, minutos, xG/npxG y penales con fuentes consistentes.
