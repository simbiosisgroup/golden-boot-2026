# Checklist antes de publicar

- [ ] Todas las filas tienen `source_primary` y `source_player_stats`.
- [ ] No hay filas demo en el top 20.
- [ ] `npxg90` viene de una sola fuente homogénea o está vacío.
- [ ] `verified_goals90` usa minutos reales, no apariciones, o la aproximación está declarada.
- [ ] `expected_team_matches` está documentado como supuesto.
- [ ] `starter_probability` está justificado por convocatoria/titularidad reciente.
- [ ] Penales: se verificó quién cobra en cada selección.
- [ ] Se corrió `pytest -q`.
- [ ] Se corrió `python scripts/validate_sources.py data/players_seed.csv`.
- [ ] El texto público diferencia claramente dato confirmado vs. supuesto del modelo.
