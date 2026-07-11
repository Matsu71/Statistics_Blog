#!/usr/bin/env python3
"""USD/JPY H1 mean-reversion backtest.

Rule
----
- Short USD/JPY (buy JPY) when an hourly bar first touches the highest USD/JPY
  level observed during the preceding 90 calendar days.
- The entry price is the prior 90-day high itself. If the market gaps above that
  level, the bar open is used because the lower level was not executable.
- Take-profit and stop-loss are symmetric: 2 JPY or 3 JPY.
- Only one position may be open at a time.
- Exit monitoring starts with the next hourly bar because OHLC data cannot reveal
  whether movements inside the entry hour happened before or after entry.
- If both TP and SL are touched in the same later bar, the primary result treats
  it as a loss (conservative stop-first assumption) and flags the trade.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "USDJPY_H1_5y.csv"
RESULTS_DIR = ROOT / "results"
LOOKBACK = pd.Timedelta(days=90)
TEST_YEARS = 3
BARRIERS = (2.0, 3.0)


@dataclass
class Trade:
    barrier_jpy: float
    entry_time_utc: str
    entry_price: float
    rolling_high: float
    gap_entry: bool
    target_price: float
    stop_price: float
    exit_time_utc: str | None
    exit_price: float | None
    result: str
    ambiguous_exit_bar: bool
    holding_hours: float | None
    pnl_jpy_per_usd: float | None


def wilson_interval(wins: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return center - half, center + half


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    required = {"time", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["time"] = pd.to_datetime(df["time"], utc=True, errors="raise")
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    df = (
        df.sort_values("time")
        .drop_duplicates(subset=["time"], keep="last")
        .reset_index(drop=True)
    )

    invalid = (
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        | (df["low"] > df[["open", "close", "high"]].min(axis=1))
    )
    if invalid.any():
        raise ValueError(f"Invalid OHLC rows: {int(invalid.sum())}")

    indexed = df.set_index("time")
    # Calendar-time window, excluding the current bar.
    df["prior_90d_high"] = (
        indexed["high"].rolling(LOOKBACK, closed="left").max().to_numpy()
    )
    return df


def simulate(df: pd.DataFrame, barrier: float, analysis_start: pd.Timestamp) -> list[Trade]:
    trades: list[Trade] = []
    n = len(df)
    i = int(df["time"].searchsorted(analysis_start, side="left"))

    while i < n:
        row = df.iloc[i]
        level = row["prior_90d_high"]
        if pd.isna(level) or row["high"] < level:
            i += 1
            continue

        # Exact touch at the old high unless the market opened above it.
        gap_entry = bool(row["open"] > level)
        entry = float(row["open"] if gap_entry else level)
        target = entry - barrier
        stop = entry + barrier

        exit_time = None
        exit_price = None
        result = "OPEN"
        ambiguous = False
        holding_hours = None
        pnl = None

        # Start at the next bar: within-entry-hour price order is unknowable.
        j = i + 1
        while j < n:
            future = df.iloc[j]
            hit_target = bool(future["low"] <= target)
            hit_stop = bool(future["high"] >= stop)

            if hit_target or hit_stop:
                exit_time = future["time"]
                ambiguous = hit_target and hit_stop
                if hit_stop:  # stop-first when both occur in the same bar
                    result = "LOSS"
                    exit_price = stop
                    pnl = -barrier
                else:
                    result = "WIN"
                    exit_price = target
                    pnl = barrier
                holding_hours = (
                    exit_time - row["time"]
                ).total_seconds() / 3600.0
                break
            j += 1

        trades.append(
            Trade(
                barrier_jpy=barrier,
                entry_time_utc=row["time"].isoformat(),
                entry_price=round(entry, 6),
                rolling_high=round(float(level), 6),
                gap_entry=gap_entry,
                target_price=round(target, 6),
                stop_price=round(stop, 6),
                exit_time_utc=exit_time.isoformat() if exit_time is not None else None,
                exit_price=round(float(exit_price), 6) if exit_price is not None else None,
                result=result,
                ambiguous_exit_bar=ambiguous,
                holding_hours=round(float(holding_hours), 3) if holding_hours is not None else None,
                pnl_jpy_per_usd=pnl,
            )
        )

        if result == "OPEN":
            break
        # No overlapping positions; do not open another trade in the exit bar.
        i = j + 1

    return trades


def summarize(trades: list[Trade], barrier: float, data_start: pd.Timestamp,
              analysis_start: pd.Timestamp, data_end: pd.Timestamp) -> dict[str, object]:
    closed = [t for t in trades if t.result in {"WIN", "LOSS"}]
    wins = sum(t.result == "WIN" for t in closed)
    losses = sum(t.result == "LOSS" for t in closed)
    open_count = sum(t.result == "OPEN" for t in trades)
    ambiguous = sum(t.ambiguous_exit_bar for t in closed)
    gap_entries = sum(t.gap_entry for t in trades)
    n = len(closed)
    win_rate = wins / n if n else math.nan
    ci_low, ci_high = wilson_interval(wins, n)
    holding = [t.holding_hours for t in closed if t.holding_hours is not None]

    # Best-case sensitivity: flip ambiguous stop-first losses to wins.
    best_case_wins = wins + ambiguous
    best_case_win_rate = best_case_wins / n if n else math.nan

    return {
        "barrier_jpy": barrier,
        "position": "USDJPY short (JPY long)",
        "lookback": "90 calendar days",
        "data_start_utc": data_start.isoformat(),
        "analysis_start_utc": analysis_start.isoformat(),
        "data_end_utc": data_end.isoformat(),
        "entries_total": len(trades),
        "closed_trades": n,
        "wins": wins,
        "losses": losses,
        "open_at_end": open_count,
        "win_rate": win_rate,
        "win_rate_pct": win_rate * 100 if n else math.nan,
        "wilson_95_low_pct": ci_low * 100 if n else math.nan,
        "wilson_95_high_pct": ci_high * 100 if n else math.nan,
        "ambiguous_exit_bars": ambiguous,
        "best_case_win_rate_pct_if_all_ambiguous_are_wins": best_case_win_rate * 100 if n else math.nan,
        "gap_entries": gap_entries,
        "gross_pnl_jpy_per_usd": sum(t.pnl_jpy_per_usd or 0 for t in closed),
        "average_holding_hours": sum(holding) / len(holding) if holding else math.nan,
        "median_holding_hours": pd.Series(holding).median() if holding else math.nan,
        "costs_included": False,
    }


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    data_start = df["time"].iloc[0]
    data_end = df["time"].iloc[-1]
    analysis_start = max(data_start + LOOKBACK, data_end - pd.DateOffset(years=TEST_YEARS))

    summaries: list[dict[str, object]] = []
    all_trades: dict[str, list[dict[str, object]]] = {}

    for barrier in BARRIERS:
        trades = simulate(df, barrier, analysis_start)
        summaries.append(summarize(trades, barrier, data_start, analysis_start, data_end))
        records = [asdict(t) for t in trades]
        all_trades[str(int(barrier))] = records
        pd.DataFrame(records).to_csv(
            RESULTS_DIR / f"trades_{int(barrier)}jpy.csv", index=False
        )

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(RESULTS_DIR / "summary.csv", index=False)

    metadata = {
        "strategy": "Sell USD/JPY at the prior 90-calendar-day high on first hourly touch",
        "entry_execution": "prior high; hourly open if gap above the level",
        "position_overlap": "prohibited",
        "entry_bar_exit_handling": "exit checks begin on next bar",
        "later_bar_both_hit_handling": "conservative stop-first; flagged as ambiguous",
        "barriers_jpy": list(BARRIERS),
        "test_years": TEST_YEARS,
        "data_rows": len(df),
        "data_source": "xavierchuan/quantmaster QuantResearch/data/raw/USDJPY_H1_5y.csv",
        "data_commit": "5daefb1c128b9254605edef8cdd93c78fb45d22a",
        "data_sha256_expected": "bda2a0a1d4676b8a04226bd9dc8a7cc4d02516d50aa6e70d44bb51676fe0344a",
        "costs": "spread, commission and swap excluded",
        "summaries": summaries,
    }
    (RESULTS_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
