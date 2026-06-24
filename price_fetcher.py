"""price_fetcher.py

Fetches historical OHLCV price data via Yahoo Finance (yfinance).
Returns data in a format compatible with the scorer module:
  List of dicts: [{"closePrice": {"bid": float, "ask": float}}, ...]

Why yfinance instead of IG /prices endpoint?
IG Demo API does not provide historical price data via /prices for most
epics (returns HTTP 404). IG is still used for login, account info, and
order placement. Price history for momentum scoring comes from yfinance.
"""
import logging
import datetime
from typing import Optional

import yfinance as yf
import pandas as pd

from config import YAHOO_MAP, REGIME_EPIC

logger = logging.getLogger(__name__)


def _to_ig_format(closes: list) -> list:
    """Convert a list of close prices to the IG prices-list format."""
    result = []
    for price in closes:
        result.append({
            "closePrice": {
                "bid": float(price),
                "ask": float(price),
            }
        })
    return result


def get_prices_yf(
    epic: str,
    num_points: int = 260,
) -> Optional[list]:
    """
    Fetch up to `num_points` daily close prices for an IG epic via yfinance.
    Returns a list of IG-compatible price dicts, or None on failure.
    """
    ticker = YAHOO_MAP.get(epic)
    if not ticker:
        logger.warning("No Yahoo Finance ticker mapped for epic: %s", epic)
        return None

    # Download slightly more days to account for weekends/holidays
    days_needed = int(num_points * 1.5)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_needed)

    try:
        df = yf.download(
            ticker,
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            progress=False,
            auto_adjust=True,
        )
    except Exception as exc:
        logger.warning("yfinance download failed for %s (%s): %s", epic, ticker, exc)
        return None

    if df is None or df.empty:
        logger.warning("yfinance returned no data for %s (%s)", epic, ticker)
        return None

    # Handle MultiIndex columns (yfinance >= 0.2.x returns MultiIndex when
    # downloading a single ticker sometimes)
    close_col = df["Close"]
    if isinstance(close_col, pd.DataFrame):
        # MultiIndex: take the first column
        close_col = close_col.iloc[:, 0]

    closes = close_col.dropna().tolist()
    if len(closes) < 20:
        logger.warning("Too few data points for %s (%s): %d", epic, ticker, len(closes))
        return None

    # Trim to requested number of points
    closes = closes[-num_points:]
    logger.info("yfinance %s (%s): %d bars fetched", epic, ticker, len(closes))
    return _to_ig_format(closes)


def fetch_all_prices_yf(universe: list, num_points: int = 260) -> dict:
    """
    Fetch price history for every epic in `universe` via Yahoo Finance.
    Returns a dict mapping epic -> list of IG-format price dicts.
    """
    price_map = {}
    for epic in universe:
        prices = get_prices_yf(epic, num_points=num_points)
        if prices:
            price_map[epic] = prices
        else:
            logger.warning("  %s: no data from yfinance", epic)
    return price_map


def check_regime_yf(regime_epic: str = REGIME_EPIC, ma_period: int = 200) -> bool:
    """
    Market-regime filter: returns True (bullish) if the current close
    of the S&P 500 is above its `ma_period`-day moving average.
    """
    prices = get_prices_yf(regime_epic, num_points=ma_period + 10)
    if not prices:
        logger.warning("Regime check failed - assuming bearish.")
        return False

    closes = [p["closePrice"]["bid"] for p in prices]
    if len(closes) < ma_period:
        logger.warning("Not enough data for regime MA - assuming bearish.")
        return False

    ma = sum(closes[-ma_period:]) / ma_period
    current = closes[-1]
    bullish = current > ma
    logger.info(
        "Regime (yfinance): price=%.2f, MA%d=%.2f, bullish=%s",
        current, ma_period, ma, bullish,
    )
    return bullish
