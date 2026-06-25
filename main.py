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
    """Build a markdown table from a ranked list of dicts with 'epic' and 'score'."""
    lines = [
                "| Rank | EPIC | Price | Score |",
                "|------|------|-------|-------|"
    ]
    for i, item in enumerate(ranked, 1):
        epic = item.get("epic", "?")
        score = item.get("score", 0.0)
                price = item.get("price", 0.0)
        lines.append(f"| {i} | {epic} | {price:.2f} | {score:.4f} |")
    return "\n".join(lines)


def get_balance(ig: IGClient) -> float:
    """Extract available balance from account info."""
    try:
        info = ig.get_account_info()
        accounts = info.get("accounts", [])
        if accounts:
            return float(accounts[0].get("balance", {}).get("available", 0))
        return 0.0
    except Exception as e:
        logger.warning(f"Could not fetch balance: {e}")
        return 0.0


def main():
    logger.info("=== Momentum Bot starting ===")

    # --- IG Login (auto-login happens in IGClient.__init__) ---
    ig = IGClient()
    balance = get_balance(ig)
    logger.info(f"Account balance: EUR {balance:,.2f}")

    # --- Market Regime Check ---
    logger.info("Checking market regime via Yahoo Finance...")
    bullish = check_regime_yf(REGIME_EPIC, REGIME_MA_PERIOD)
    regime_label = "BULLISH" if bullish else "BEARISH"
    logger.info(f"Market regime: {regime_label}")

    # --- Fetch benchmark prices (used as relative-strength reference) ---
    logger.info(f"Fetching benchmark prices for {REGIME_EPIC}...")
    benchmark_prices = get_prices_yf(REGIME_EPIC) or []

    # --- Fetch prices for THEMATIC UNIVERSE ---
    logger.info("Fetching price data for universe via Yahoo Finance...")
    price_map = fetch_all_prices_yf(UNIVERSE)
    logger.info(f"Price data fetched for {len(price_map)}/{len(UNIVERSE)} instruments.")

    # --- Score THEMATIC UNIVERSE ---
    logger.info("Scoring universe...")
    ranked_all = rank_universe(UNIVERSE, price_map, benchmark_prices)

    # Top buy signals (positive score, up to TOP_N_SIGNALS)
    top_signals = [r for r in ranked_all if r.get("score", 0) > 0][:TOP_N_SIGNALS]
    # Exit / Avoid signals (negative score)
    exit_signals = [r for r in ranked_all if r.get("score", 0) < 0]

    # --- Fetch prices for BROAD_UNIVERSE (Score-Only) ---
    logger.info("Fetching price data for BROAD_UNIVERSE via Yahoo Finance...")
    broad_price_map = fetch_all_prices_yf(BROAD_UNIVERSE)
    logger.info(f"Broad price data fetched for {len(broad_price_map)}/{len(BROAD_UNIVERSE)} instruments.")

    # --- Score BROAD_UNIVERSE ---
    logger.info("Scoring BROAD_UNIVERSE...")
    broad_ranked_all = rank_universe(BROAD_UNIVERSE, broad_price_map, benchmark_prices)
    broad_top = [r for r in broad_ranked_all if r.get("score", 0) > 0][:BROAD_TOP_N]

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

        # --- Sektion 4: Unter-5-Euro-Aktien ---
        penny_signals = [r for r in ranked_all + broad_ranked_all if r.get("price", 999) < 5.0 and r.get("score", 0) > 0]
        penny_signals = sorted(penny_signals, key=lambda x: x["score"], reverse=True)
        # Deduplizieren
        seen = set()
        penny_unique = []
        for r in penny_signals:
            if r["epic"] not in seen:
                seen.add(r["epic"])
                penny_unique.append(r)
        report_lines += [
            "",
            "---",
            "",
            "## 4. Penny Stocks (Preis < 5 EUR) - Positive Momentum",
            "",
        ]
        if penny_unique:
            report_lines.append(build_table(penny_unique))
        else:
            report_lines.append("_Keine Penny-Stock-Signale._") 

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
       # --- Dashboard Report (docs/report.md fuer GitHub Pages) ---
    Path("docs").mkdir(exist_ok=True)
    with open("docs/report.md", "w") as f:
        f.write(report)
    logger.info("Dashboard report saved to docs/report.md")

    # --- Print Report to Logs ---
    print(report)

    logger.info("=== Momentum Bot finished ===")


if __name__ == "__main__":
    main()
