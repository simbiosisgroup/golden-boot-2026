"""Golden Boot 2026 prediction model.

This module is intentionally conservative: it separates verified inputs
from editorial assumptions, keeps source URLs, and ranks only rows that are
explicitly scoring-ready or have at least one usable scoring-rate input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "player",
    "team",
    "position",
    "expected_team_matches",
    "expected_minutes_per_match",
    "starter_probability",
    "team_attack_adjustment",
    "group_difficulty_adjustment",
    "penalty_taker_probability",
    "expected_team_penalties_per_match",
    "penalty_conversion_probability",
]

RATE_COLUMNS = [
    "npxg90",
    "verified_goals90",
    "verified_intl_goals90",
    "shots90",
]

DEFAULT_WEIGHTS = {
    "npxg90": 0.55,
    "verified_goals90": 0.25,
    "verified_intl_goals90": 0.10,
    # shots90 is converted to expected goals using a conservative conversion factor.
    "shots90": 0.10,
}

DEFAULT_SHOT_TO_GOAL_RATE = 0.105


@dataclass(frozen=True)
class ModelConfig:
    weights: dict[str, float]
    shot_to_goal_rate: float = DEFAULT_SHOT_TO_GOAL_RATE
    minimum_data_quality: float = 0.0

    @classmethod
    def default(cls) -> "ModelConfig":
        return cls(weights=DEFAULT_WEIGHTS.copy())


def _to_float(value, default: float = np.nan) -> float:
    if value is None:
        return default
    if isinstance(value, str) and value.strip() == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.strip().str.lower().isin(
        ["true", "1", "yes", "sí", "si", "y"]
    )


def score_ready_mask(df: pd.DataFrame) -> pd.Series:
    """Return rows safe to feed into the scoring model.

    A row is scoring-ready when either:
    1) scoring_ready is explicitly true, or
    2) at least one scoring-rate input is present.

    This lets the CSV contain the full official FIFA FW/MF candidate universe
    without pretending rows with no player-stat inputs are model-ready.
    """
    if "scoring_ready" in df.columns:
        explicit = _truthy(df["scoring_ready"])
    else:
        explicit = pd.Series(False, index=df.index)

    available_rate_cols = [c for c in RATE_COLUMNS if c in df.columns]
    if available_rate_cols:
        numeric_rates = df[available_rate_cols].apply(pd.to_numeric, errors="coerce")
        has_rate = numeric_rates.notna().any(axis=1)
    else:
        has_rate = pd.Series(False, index=df.index)

    return explicit | has_rate


def model_players(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows that have enough data to score."""
    return df.loc[score_ready_mask(df)].copy().reset_index(drop=True)


def validate_players(df: pd.DataFrame) -> list[str]:
    """Return data-quality warnings instead of raising immediately."""
    warnings: list[str] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        warnings.append(f"Missing required columns: {', '.join(missing)}")

    for col in ["player", "team"]:
        if col in df.columns and df[col].isna().any():
            warnings.append(f"Column '{col}' has blank values.")

    scoring = model_players(df) if not missing else df.iloc[0:0]
    if len(scoring) == 0:
        warnings.append("No scoring-ready rows found. Add at least one rate input: npxG/90, goals/90, intl goals/90 or shots/90.")

    for col in ["source_primary", "source_player_stats"]:
        if col in df.columns:
            if len(scoring) > 0:
                blank = scoring[col].fillna("").astype(str).str.strip().eq("")
                if blank.any():
                    warnings.append(
                        f"{blank.sum()} scoring-ready row(s) have no URL in '{col}'. Do not publish rankings without sources."
                    )
            else:
                blank = df[col].fillna("").astype(str).str.strip().eq("")
                if blank.any():
                    warnings.append(f"{blank.sum()} row(s) have no URL in '{col}'.")
        else:
            warnings.append(f"Column '{col}' is missing; source traceability is weaker.")

    if "data_quality_score" in df.columns and len(scoring) > 0:
        quality = pd.to_numeric(scoring["data_quality_score"], errors="coerce")
        bad = quality.lt(0.7)
        if bad.any():
            warnings.append(
                f"{bad.sum()} scoring-ready row(s) have data_quality_score below 0.70; mark as provisional."
            )
    return warnings


def individual_rate90(row: pd.Series, config: Optional[ModelConfig] = None) -> float:
    """Estimate a player's non-penalty scoring rate per 90 minutes.

    Missing values are ignored and remaining weights are re-normalized.
    shots90 is converted to expected goals using shot_to_goal_rate.
    """
    config = config or ModelConfig.default()
    components: list[tuple[float, float]] = []

    for metric, weight in config.weights.items():
        value = _to_float(row.get(metric))
        if np.isnan(value):
            continue
        if metric == "shots90":
            value *= config.shot_to_goal_rate
        components.append((value, weight))

    if not components:
        return np.nan

    total_weight = sum(weight for _, weight in components)
    if total_weight <= 0:
        return np.nan
    return sum(value * weight for value, weight in components) / total_weight


def score_player(row: pd.Series, config: Optional[ModelConfig] = None) -> pd.Series:
    """Return expected goals components for one player."""
    config = config or ModelConfig.default()

    rate90 = individual_rate90(row, config)
    expected_matches = _to_float(row.get("expected_team_matches"), 0.0)
    minutes_per_match = _to_float(row.get("expected_minutes_per_match"), 0.0)
    starter_probability = _to_float(row.get("starter_probability"), 0.0)
    team_attack = _to_float(row.get("team_attack_adjustment"), 1.0)
    group_adjustment = _to_float(row.get("group_difficulty_adjustment"), 1.0)

    if np.isnan(rate90):
        open_play_goals = np.nan
    else:
        open_play_goals = (
            rate90
            * (expected_matches * minutes_per_match / 90.0)
            * starter_probability
            * team_attack
            * group_adjustment
        )

    expected_penalties_per_match = _to_float(row.get("expected_team_penalties_per_match"), 0.0)
    penalty_taker_probability = _to_float(row.get("penalty_taker_probability"), 0.0)
    penalty_conversion = _to_float(row.get("penalty_conversion_probability"), 0.78)
    penalty_goals = (
        expected_penalties_per_match
        * expected_matches
        * penalty_taker_probability
        * penalty_conversion
    )

    total = open_play_goals + penalty_goals if not np.isnan(open_play_goals) else np.nan

    return pd.Series(
        {
            "individual_rate90": rate90,
            "expected_open_play_goals": open_play_goals,
            "expected_penalty_goals": penalty_goals,
            "expected_goals_total": total,
        }
    )


def rank_players(players: pd.DataFrame, config: Optional[ModelConfig] = None) -> pd.DataFrame:
    """Calculate expected goals and return ranked scoring-ready players."""
    config = config or ModelConfig.default()
    warnings = validate_players(players)
    if any(w.startswith("Missing required columns") for w in warnings):
        raise ValueError("; ".join(warnings))

    scored = model_players(players)
    if scored.empty:
        raise ValueError("No scoring-ready rows found.")

    score_cols = scored.apply(lambda row: score_player(row, config), axis=1)
    scored = pd.concat([scored, score_cols], axis=1)
    scored = scored[scored["expected_goals_total"].notna()].copy()
    if scored.empty:
        raise ValueError("Scoring-ready rows exist, but none have a usable individual scoring rate.")

    scored["rank_expected_goals"] = scored["expected_goals_total"].rank(
        ascending=False, method="min"
    )
    return scored.sort_values(
        ["expected_goals_total", "expected_penalty_goals", "player"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def simulate_golden_boot(
    players: pd.DataFrame,
    simulations: int = 50_000,
    random_seed: int = 26,
    config: Optional[ModelConfig] = None,
) -> pd.DataFrame:
    """Monte Carlo simulation using each player's expected_goals_total as Poisson lambda.

    If multiple players tie for top goals in a simulation, the win credit is split equally.
    This avoids pretending we know the exact tie-breaker before assists/minutes are simulated.
    """
    ranked = rank_players(players, config)
    lambdas = ranked["expected_goals_total"].fillna(0).clip(lower=0).to_numpy()
    rng = np.random.default_rng(random_seed)
    draws = rng.poisson(lam=lambdas, size=(simulations, len(ranked)))
    max_goals = draws.max(axis=1)
    winners = draws == max_goals[:, None]
    split_credit = winners / winners.sum(axis=1)[:, None]
    probabilities = split_credit.mean(axis=0)

    out = ranked[["player", "team", "expected_goals_total"]].copy()
    out["golden_boot_probability"] = probabilities
    out["golden_boot_probability_pct"] = probabilities * 100
    return out.sort_values(
        ["golden_boot_probability", "expected_goals_total"], ascending=[False, False]
    ).reset_index(drop=True)


def load_players(path: str = "data/players_seed.csv") -> pd.DataFrame:
    return pd.read_csv(path)
