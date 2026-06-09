# Tarea para Codex

Quiero convertir este repositorio en una app pública y confiable para predecir el máximo goleador del Mundial FIFA 2026.

Prioridades:

1. Mantén trazabilidad completa de datos: ninguna fila puede aparecer en el ranking si no tiene `source_primary` y `source_player_stats`.
2. No inventes datos faltantes. Si falta xG, minutos o titularidad, marca el campo como supuesto y baja `data_quality_score`.
3. Mejora la app Streamlit para que el usuario pueda:
   - subir un CSV propio;
   - editar supuestos del modelo;
   - ver ranking por goles esperados;
   - ver probabilidad de Bota de Oro por Monte Carlo;
   - exportar resultados a CSV.
4. Agrega filtros por selección, posición y calidad de dato.
5. Agrega una vista “fuentes” con enlaces por jugador.
6. Agrega validaciones fuertes:
   - columnas obligatorias;
   - URLs no vacías;
   - probabilidades entre 0 y 1;
   - ajustes positivos;
   - minutos por partido entre 0 y 120.
7. Corre antes de entregar:

```bash
pytest -q
python scripts/validate_sources.py data/players_seed.csv
```

Regla editorial: es preferible mostrar “dato no confirmado” antes que completar con una suposición silenciosa.
