"""main.py - Daily entry point for the Momentum Bot.

Run once per day after market close:
    python main.py

The script:
1. Logs into IG demo account (account info + kill-switch via IG API)
2. Checks market regime via Yahoo Finance (S&P 500 200-day MA)
3. Fetches 260 days of daily price history via Yahoo Finance
4. Scores and ranks all instruments by momentum
5. Generates a daily Markdown report with top buy signals and exit warnings
6. (Optional) Places paper orders on IG demo for the top N signals

Note: IG Demo API does not serve historical prices via /prices endpoint.
All price history is fetched from Yahoo Finance (yfinance) instead.
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
from price_fetcher import fetch_all_prices_yf, check_regime_yf
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


def get_account_balance(client: IGClient) -> float:
    """Return available cash balance from IG demo account."""
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
                balance = float(acc["balance"]["balance"])
                deposit = float(acc["balance"]["deposit"])
                pnl_pct = (balance - deposit) / deposit if deposit else 0
                if pnl_pct < -DAILY_LOSS_LIMIT_PCT:
                    logger.error(
                        f"KILL SWITCH: daily loss {pnl_pct:.1%} exceeds "
                        f"limit {DAILY_LOSS_LIMIT_PCT:.1%}"
                    )
                    return False
    except Exception as e:
        logger.warning(f"Loss-limit check failed: {e}")
    return True


def generate_report(
    ranked: list, regime_bullish: bool, balance: float, date_str: str
) -> str:
    """Build a Markdown report and write it to disk."""
    top_buys = [r for r in ranked if r["score"] > 0][:TOP_N_SIGNALS]
    top_exits = [r for r in reversed(ranked) if r["score"] < 0][:TOP_N_SIGNALS]

    lines = [
        "# Momentum Bot Daily Report",
        f"**Date:** {date_str}  ",
        f"**Market Regime:** {'BULLISH' if regime_bullish else 'BEARISH'}  ",
        f"**Account Balance:** EUR {balance:,.2f}  ",
        f"**Price Source:** Yahoo Finance (yfinance)  ",
        "",
        "## Top Buy Signals",
        "| Rank | EPIC | Score |",
        "|------|------|-------|",
    ]
    if top_buys:
        for i, r in enumerate(top_buys, 1):
            lines.append(f"| {i} | {r['epic']} | {r['score']:.4f} |")
    else:
        lines.append("| - | No buy signals today | - |")

    lines += [
        "",
        "## Exit / Avoid Signals",
        "| Rank | EPIC | Score |",
        "|------|------|-------|",
    ]
    if top_exits:
        for i, r in enumerate(top_exits, 1):
            lines.append(f"| {i} | {r['epic']} | {r['score']:.4f} |")
    else:
        lines.append("| - | No exit signals today | - |")

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

    # 1. Connect to IG (for account info + kill-switch + future order placement)
    client = IGClient()

    # 2. Kill switch check
    if not check_daily_loss_limit(client):
        logger.error("Daily loss limit reached. Halting.")
        return

    balance = get_account_balance(client)
    logger.info(f"Account balance: EUR {balance:,.2f}")

    # 3. Market regime filter via Yahoo Finance
    logger.info("Checking market regime via Yahoo Finance...")
    regime_bullish = check_regime_yf(
        regime_epic=REGIME_EPIC, ma_period=REGIME_MA_PERIOD
    )
    logger.info(f"Market regime: {'BULLISH' if regime_bullish else 'BEARISH'}")

    # 4. Fetch price history via Yahoo Finance
    logger.info("Fetching price data for universe via Yahoo Finance...")
    price_map = fetch_all_prices_yf(UNIVERSE, num_points=260)
    logger.info(f"Price data fetched for {len(price_map)}/{len(UNIVERSE)} instruments.")

    # Also fetch benchmark for scorer (S&P 500)
    from price_fetcher import get_prices_yf
    benchmark_prices = get_prices_yf(REGIME_EPIC, num_points=260)

    # 5. Score & rank
    logger.info("Scoring universe...")
    ranked = rank_universe(UNIVERSE, price_map, benchmark_prices)

    # 6. Report
    report = generate_report(ranked, regime_bullish, balance, date_str)
    print("\n" + report)
    logger.info("=== Momentum Bot finished ===")


if __name__ == "__main__":
    main()
