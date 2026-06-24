"""main.py - Daily entry point for the Momentum Bot.

Drei Report-Sektionen:
1. THEMATISCHES UNIVERSE  -- persoenliche Interessensgebiete (Halbleiter etc.)
2. SCORE-ONLY SCREENING   -- rein mechanisch, 40+ globale Large-Caps
   => zeigt objektiv die staerksten Momentum-Werte, unabhaengig von Praeferenzen
3. Exit / Avoid           -- schwache Werte aus dem thematischen Universe
"""
import os
import logging
import datetime
from pathlib import Path

from config import (
    UNIVERSE, BROAD_UNIVERSE, REGIME_EPIC, REGIME_MA_PERIOD,
    TOP_N_SIGNALS, BROAD_TOP_N, LOG_FILE, REPORT_FILE,
    MAX_POSITIONS, RISK_PER_TRADE_PCT, STOP_LOSS_PCT,
    DAILY_LOSS_LIMIT_PCT,
)
from ig_client import IGClient
from price_fetcher import fetch_all_prices_yf, check_regime_yf, get_prices_yf
from scorer import rank_universe

Path("logs").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("main")


def build_table(ranked: list) -> str:
    """Build a markdown table from a ranked list of (epic, score) tuples."""
    lines = [
        "| Rank | EPIC | Score |",
        "|------|------|-------|",
    ]
    for i, (epic, score) in enumerate(ranked, 1):
        lines.append(f"| {i} | {epic} | {score:.4f} |")
    return "\n".join(lines)


def main():
    logger.info("=== Momentum Bot starting ===")

    # --- IG Login ---
    ig = IGClient()
    ig.login()
    balance = ig.get_account_balance()
    logger.info(f"Account balance: EUR {balance:,.2f}")

    # --- Market Regime Check ---
    logger.info("Checking market regime via Yahoo Finance...")
    bullish = check_regime_yf(REGIME_EPIC, REGIME_MA_PERIOD)
    regime_label = "BULLISH" if bullish else "BEARISH"
    logger.info(f"Market regime: {regime_label}")

    # --- Fetch prices for THEMATIC UNIVERSE ---
    logger.info("Fetching price data for universe via Yahoo Finance...")
    prices = fetch_all_prices_yf(UNIVERSE)
    logger.info(f"Price data fetched for {len(prices)}/{len(UNIVERSE)} instruments.")

    # --- Score THEMATIC UNIVERSE ---
    logger.info("Scoring universe...")
    ranked_all = rank_universe(prices)

    # Top buy signals (positive score, up to TOP_N_SIGNALS)
    top_signals = [(e, s) for e, s in ranked_all if s > 0][:TOP_N_SIGNALS]
    # Exit / Avoid signals (negative score)
    exit_signals = [(e, s) for e, s in ranked_all if s < 0]

    # --- Fetch prices for BROAD_UNIVERSE (Score-Only) ---
    logger.info("Fetching price data for BROAD_UNIVERSE via Yahoo Finance...")
    broad_prices = fetch_all_prices_yf(BROAD_UNIVERSE)
    logger.info(f"Broad price data fetched for {len(broad_prices)}/{len(BROAD_UNIVERSE)} instruments.")

    # --- Score BROAD_UNIVERSE ---
    logger.info("Scoring BROAD_UNIVERSE...")
    broad_ranked_all = rank_universe(broad_prices)
    # Take top BROAD_TOP_N with positive score
    broad_top = [(e, s) for e, s in broad_ranked_all if s > 0][:BROAD_TOP_N]

    # --- Build Report ---
    today = datetime.date.today().isoformat()
    report_lines = [
        "# Momentum Bot Daily Report",
        f"**Date:** {today}",
        f"**Market Regime:** {regime_label}",
        f"**Account Balance:** EUR {balance:,.2f}",
        "**Price Source:** Yahoo Finance (yfinance)",
        "",
        "---",
        "",
        "## 1. Thematisches Universe - Top Buy Signals",
        "",
    ]
    if top_signals:
        report_lines.append(build_table(top_signals))
    else:
        report_lines.append("_Keine Buy-Signale (Regime BEARISH oder alle Scores negativ)_")

    report_lines += [
        "",
        "---",
        "",
        "## 2. Score-Only Screening (Breites Universe - unabhaengig von Praeferenzen)",
        "",
        f"_Top {BROAD_TOP_N} globale Large-Caps nach reinem Momentum-Score:_",
        "",
    ]
    if broad_top:
        report_lines.append(build_table(broad_top))
    else:
        report_lines.append("_Keine Score-Only-Signale verfuegbar._")

    report_lines += [
        "",
        "---",
        "",
        "## 3. Exit / Avoid Signals (Thematisches Universe)",
        "",
    ]
    if exit_signals:
        report_lines.append(build_table(exit_signals))
    else:
        report_lines.append("_Keine Exit-Signale._")

    report_lines += [
        "",
        "---",
        "*This report is generated automatically. Always verify before trading.*",
    ]

    report = "\n".join(report_lines)

    # --- Save Report ---
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    logger.info(f"Report saved to {REPORT_FILE}")

    # --- Print Report to Logs ---
    print(report)

    logger.info("=== Momentum Bot finished ===")


if __name__ == "__main__":
    main()
