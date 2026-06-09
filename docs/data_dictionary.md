# Diccionario de variables

| Campo | Tipo | Descripción |
|---|---|---|
| `player` | texto | Nombre del jugador. |
| `team` | texto | Selección nacional. |
| `club` | texto | Club al momento de la fuente. |
| `position` | texto | Posición principal. |
| `verified_competition` | texto | Competición de la estadística reciente. |
| `verified_goals` | número | Goles confirmados por fuente. |
| `verified_assists` | número | Asistencias confirmadas por fuente. |
| `verified_minutes` | número | Minutos confirmados por fuente. |
| `verified_attempts` | número | Tiros/intentos confirmados por fuente. |
| `verified_penalties_scored` | número | Penales anotados confirmados. |
| `npxg90` | número | Expected goals sin penales por 90. Idealmente homogéneo. |
| `verified_goals90` | número | Goles por 90 o aproximación documentada. |
| `verified_intl_goals90` | número | Goles por 90 con selección. |
| `shots90` | número | Tiros por 90. |
| `expected_team_matches` | número | Partidos esperados de la selección. Es supuesto del modelo. |
| `expected_minutes_per_match` | número | Minutos esperados por partido. Es supuesto del modelo. |
| `starter_probability` | 0-1 | Probabilidad de titularidad/uso relevante. |
| `team_attack_adjustment` | número | Ajuste de fuerza ofensiva del equipo. 1.00 = neutral. |
| `group_difficulty_adjustment` | número | Ajuste por dificultad de rivales. 1.00 = neutral. |
| `penalty_taker_probability` | 0-1 | Probabilidad de que el jugador cobre penales. |
| `expected_team_penalties_per_match` | número | Penales esperados por partido para esa selección. |
| `penalty_conversion_probability` | 0-1 | Probabilidad de convertir penal. |
| `data_quality_score` | 0-1 | Calidad de datos. Debe bajar si hay aproximaciones. |
| `source_primary` | URL | Fuente principal de la fila. |
| `source_player_stats` | URL | Fuente estadística del jugador. |
| `source_team_context` | URL | Fuente de contexto de selección/torneo. |
| `notes` | texto | Advertencias, aproximaciones y supuestos. |
