from __future__ import annotations

import sys

import pandas as pd

REQUIRED_BASE_SOURCE_COLUMNS = ["source_primary", "source_fifa_squad"]
REQUIRED_SCORING_SOURCE_COLUMNS = ["source_player_stats"]
RATE_COLUMNS = ["npxg90", "verified_goals90", "verified_intl_goals90", "shots90"]


def truthy(series: pd.Series) -> pd.Series:
    return series.fillna(False).astype(str).str.strip().str.lower().isin(
        ["true", "1", "yes", "sí", "si", "y"]
    )


def scoring_ready_mask(df: pd.DataFrame) -> pd.Series:
    explicit = truthy(df["scoring_ready"]) if "scoring_ready" in df.columns else pd.Series(False, index=df.index)
    available = [c for c in RATE_COLUMNS if c in df.columns]
    if available:
        has_rate = df[available].apply(pd.to_numeric, errors="coerce").notna().any(axis=1)
    else:
        has_rate = pd.Series(False, index=df.index)
    return explicit | has_rate


def main(path: str = "data/players_seed.csv") -> int:
    df = pd.read_csv(path)
    df.columns = [c.replace("\ufeff", "") for c in df.columns]
    errors = []

    for col in REQUIRED_BASE_SOURCE_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
            continue
        blank = df[col].fillna("").astype(str).str.strip().eq("")
        if blank.any():
            errors.append(f"Blank {col} in {int(blank.sum())} row(s).")

    scoring = df.loc[scoring_ready_mask(df)].copy()
    if scoring.empty:
        errors.append("No scoring-ready rows found.")
    else:
        for col in REQUIRED_SCORING_SOURCE_COLUMNS:
            if col not in scoring.columns:
                errors.append(f"Missing column: {col}")
                continue
            blank = scoring[col].fillna("").astype(str).str.strip().eq("")
            if blank.any():
                players = scoring.loc[blank, "player"].fillna("<blank>").tolist()
                errors.append(f"Blank {col} for scoring-ready players: {players}")

    if errors:
        print("Source validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(
        f"OK: {len(df)} candidate row(s), {len(scoring)} scoring-ready row(s), required source columns present."
    )
    return 0


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/players_seed.csv"
    raise SystemExit(main(csv_path))
