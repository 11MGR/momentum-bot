"""main.py - Daily entry point for the Momentum Bot.

Run once per day after market close:
    python main.py

The script:
1. Logs into IG demo account
2. Checks market regime (S&P 500 trend)
3. Fetches daily price history for the full universe
4. Scores and ranks all instruments
5. Generates a daily Markdown report with top buy signals and exit warnings
6. (Optional) Places paper orders on IG demo for the top N signals
"""

import os
import logging
import datetime
from pathlib import Path

from config import (
    UNIVERSE, REGIME_EPIC, REGIME_MA_PERIOD,
    TOP_N_SIGNALS, LOG_FILE, REPORT_FILE,
    MAX_POSITIONS, RISK_PER_TRADE_PCT, STOP_LOSS_PCT,
    DAILY_LOSS_LIMIT_PCT,
)
from ig_client import IGClient
from scorer import rank_universe

# ── Logging setup ────────────────────────────────────────────────────────────
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


def check_regime(client: IGClient) -> bool:
    """Return True if market regime is bullish (price > MA)."""
    prices = client.get_prices(REGIME_EPIC, resolution="DAY", num_points=REGIME_MA_PERIOD + 10)
    if not prices:
        logger.warning("Could not fetch regime data. Assuming bearish.")
        return False
    closes = [(p["closePrice"]["bid"] + p["closePrice"]["ask"]) / 2 for p in prices
              if p.get("closePrice")]
    if len(closes) < REGIME_MA_PERIOD:
        return False
    ma = sum(closes[-REGIME_MA_PERIOD:]) / REGIME_MA_PERIOD
    current = closes[-1]
    bullish = current > ma
    logger.info(f"Regime check: price={current:.2f}, MA{REGIME_MA_PERIOD}={ma:.2f}, bullish={bullish}")
    return bullish


def fetch_all_prices(client: IGClient) -> dict:
    """Fetch 260 days of daily prices for every epic in universe."""
    price_map = {}
    for epic in UNIVERSE:
        prices = client.get_prices(epic, resolution="DAY", num_points=260)
        if prices:
            price_map[epic] = prices
            logger.info(f"  {epic}: {len(prices)} bars")
        else:
            logger.warning(f"  {epic}: no data")
    return price_map


def get_account_balance(client: IGClient) -> float:
    """Return available cash balance."""
    try:
        info = client.get_account_info()
        for acc in info.get("accounts", []):
            if acc.get("preferred"):
                return float(acc["balance"]["available"])
    except Exception as e:
        logger.warning(f"Could not fetch balance: {e}")
    return 0.0


def check_daily_loss_limit(client: IGClient) -> bool:
    """Return True if daily loss limit NOT breached (safe to trade)."""
    try:
        info = client.get_account_info()
        for acc in info.get("accounts", []):
            if acc.get("preferred"):
                balance    = float(acc["balance"]["balance"])
                deposit    = float(acc["balance"]["deposit"])
                pnl_pct    = (balance - deposit) / deposit if deposit else 0
                if pnl_pct < -DAILY_LOSS_LIMIT_PCT:
                    logger.error(f"KILL SWITCH: daily loss {pnl_pct:.1%} exceeds limit {DAILY_LOSS_LIMIT_PCT:.1%}")
                    return False
    except Exception as e:
        logger.warning(f"Loss-limit check failed: {e}")
    return True


def generate_report(ranked: list, regime_bullish: bool, balance: float, date_str: str) -> str:
    """Build a Markdown report and write it to disk."""
    top_buys  = [r for r in ranked if r["score"] > 0][:TOP_N_SIGNALS]
    top_exits = [r for r in reversed(ranked) if r["score"] < 0][:TOP_N_SIGNALS]

    lines = [
        f"# Momentum Bot Daily Report",
        f"**Date:** {date_str}  ",
        f"**Market Regime:** {'BULLISH' if regime_bullish else 'BEARISH'}  ",
        f"**Account Balance:** EUR {balance:,.2f}  ",
        "",
        "## Top Buy Signals",
        "| Rank | EPIC | Score |",
        "|------|------|-------|",
    ]
    for i, r in enumerate(top_buys, 1):
        lines.append(f"| {i} | {r['epic']} | {r['score']:.4f} |")

    lines += [
        "",
        "## Exit / Avoid Signals",
        "| Rank | EPIC | Score |",
        "|------|------|-------|",
    ]
    for i, r in enumerate(top_exits, 1):
        lines.append(f"| {i} | {r['epic']} | {r['score']:.4f} |")

    lines += [
        "",
        "---",
        "*This report is generated automatically. Always verify before trading.*",
    ]

    report = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Report saved to {REPORT_FILE}")
    return report


def main():
    logger.info("=== Momentum Bot starting ===")
    date_str = datetime.date.today().isoformat()

    # 1. Connect
    client = IGClient()

    # 2. Kill switch check
    if not check_daily_loss_limit(client):
        logger.error("Daily loss limit reached. Halting.")
        return

    balance = get_account_balance(client)
    logger.info(f"Account balance: EUR {balance:,.2f}")

    # 3. Regime filter
    regime_bullish = check_regime(client)

    # 4. Fetch prices
    logger.info("Fetching price data for universe...")
    benchmark_prices = client.get_prices(REGIME_EPIC, resolution="DAY", num_points=260)
    price_map = fetch_all_prices(client)

    # 5. Score & rank
    logger.info("Scoring universe...")
    ranked = rank_universe(UNIVERSE, price_map, benchmark_prices)

    # 6. Report
    report = generate_report(ranked, regime_bullish, balance, date_str)
    print("\n" + report)

    logger.info("=== Momentum Bot finished ===")


if __name__ == "__main__":
    main()
