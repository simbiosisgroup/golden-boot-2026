import pandas as pd

from src.golden_boot_model import model_players, rank_players, simulate_golden_boot, validate_players


def test_model_filters_full_candidate_universe_to_scoring_ready_rows():
    players = pd.read_csv("data/players_seed.csv")
    scoring = model_players(players)
    assert len(players) > len(scoring)
    assert len(scoring) >= 10


def test_rank_players_outputs_expected_columns_and_no_nan_goals():
    players = pd.read_csv("data/players_seed.csv")
    ranked = rank_players(players)
    assert "expected_goals_total" in ranked.columns
    assert ranked["expected_goals_total"].notna().all()
    assert ranked.iloc[0]["expected_goals_total"] >= ranked.iloc[-1]["expected_goals_total"]


def test_simulation_probabilities_sum_to_one():
    players = pd.read_csv("data/players_seed.csv")
    sim = simulate_golden_boot(players, simulations=2_000, random_seed=1)
    assert abs(sim["golden_boot_probability"].sum() - 1.0) < 1e-9


def test_validate_players_allows_candidate_pool_with_warning_not_crash():
    players = pd.read_csv("data/players_seed.csv")
    warnings = validate_players(players)
    assert isinstance(warnings, list)
