# Metodología

## 1. Qué predice el modelo

El modelo no predice “quién es mejor futbolista”. Predice cuántos goles puede anotar un jugador durante el Mundial 2026.

La Bota de Oro depende de tres bloques:

1. tasa goleadora individual;
2. minutos esperados;
3. número esperado de partidos de su selección.

## 2. Fórmula

```text
expected_goals_total = expected_open_play_goals + expected_penalty_goals
```

```text
expected_open_play_goals = individual_rate90
                           × expected_team_matches
                           × expected_minutes_per_match / 90
                           × starter_probability
                           × team_attack_adjustment
                           × group_difficulty_adjustment
```

```text
expected_penalty_goals = expected_team_penalties_per_match
                         × expected_team_matches
                         × penalty_taker_probability
                         × penalty_conversion_probability
```

## 3. Cálculo del `individual_rate90`

Se combinan métricas por 90 minutos:

| Métrica | Peso inicial | Comentario |
|---|---:|---|
| `npxg90` | 55% | Idealmente viene de una fuente homogénea tipo Opta/StatsBomb/FBref/Wyscout. |
| `verified_goals90` | 25% | Goles recientes, preferiblemente con minutos reales. |
| `verified_intl_goals90` | 10% | Producción reciente con selección. |
| `shots90` | 10% | Se convierte a goles esperados con un coeficiente conservador. |

Si falta una métrica, se ignora y los pesos restantes se re-normalizan. Esto evita inventar datos.

## 4. Simulación Monte Carlo

La simulación usa una distribución de Poisson con lambda igual a `expected_goals_total`. En empates, el crédito de victoria se divide entre jugadores empatados. Esto es conservador porque no simula asistencias/minutos como desempate.

## 5. Límites del modelo

- Lesiones, rotaciones, expulsiones y cambios tácticos pueden alterar totalmente los minutos.
- xG de distintas fuentes no debe mezclarse sin normalización.
- Datos de clubes y datos de selección no tienen el mismo contexto competitivo.
- Las filas con `data_quality_score < 0.70` deben tratarse como provisionales.
