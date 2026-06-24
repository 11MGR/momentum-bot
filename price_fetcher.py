"""price_fetcher.py

Fetcht historische OHLCV-Preisdaten via Yahoo Finance (yfinance).
Gibt Daten im Format zurueck, das mit dem Scorer kompatibel ist:
  List of dicts: [{"closePrice": {"bid": float, "ask": float}}, ...]

Ab Version 2 (thematisches Universe):
- UNIVERSE enthaelt direkt Yahoo-Finance-Ticker
- YAHOO_MAP ist 1:1 (ticker -> ticker) mit optionalen Korrekturen
- REGIME_EPIC ist ebenfalls ein YF-Ticker (z.B. ^NDX)
- Ticker die nicht in YAHOO_MAP stehen werden direkt als YF-Ticker probiert
"""
import logging
import datetime
from typing import Optional

import yfinance as yf
import pandas as pd

from config import YAHOO_MAP, REGIME_EPIC

logger = logging.getLogger(__name__)


def _to_ig_format(closes: list) -> list:
    """Konvertiert eine Liste von Close-Preisen in das IG-kompatible Format."""
    result = []
    for price in closes:
        result.append({
            "closePrice": {
                "bid": float(price),
                "ask": float(price),
            }
        })
    return result


def _resolve_ticker(epic: str) -> str:
    """
    Gibt den Yahoo-Finance-Ticker fuer ein Epic zurueck.
    Sucht zuerst in YAHOO_MAP, faellt sonst direkt auf den epic-String zurueck.
    Das erlaubt es, YF-Ticker direkt als Universe-Eintraege zu nutzen.
    """
    return YAHOO_MAP.get(epic, epic)


def get_prices_yf(
    epic: str,
    num_points: int = 260,
) -> Optional[list]:
    """
    Holt bis zu `num_points` Tages-Closes fuer ein Epic / YF-Ticker.
    Gibt eine Liste von IG-kompatiblen Preis-Dicts zurueck, oder None.
    """
    ticker = _resolve_ticker(epic)

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
        logger.warning("yfinance Download fehlgeschlagen fuer %s (%s): %s", epic, ticker, exc)
        return None

    if df is None or df.empty:
        logger.warning("yfinance: keine Daten fuer %s (%s)", epic, ticker)
        return None

    # Sicherheitscheck: MultiIndex (kommt bei manchen yfinance-Versionen)
    close_col = df["Close"]
    if isinstance(close_col, pd.DataFrame):
        close_col = close_col.iloc[:, 0]

    closes = close_col.dropna().tolist()
    if len(closes) < 20:
        logger.warning("Zu wenig Datenpunkte fuer %s (%s): %d", epic, ticker, len(closes))
        return None

    closes = closes[-num_points:]
    logger.info("yfinance %s (%s): %d Bars geladen", epic, ticker, len(closes))
    return _to_ig_format(closes)


def fetch_all_prices_yf(universe: list, num_points: int = 260) -> dict:
    """
    Holt Preishistorie fuer alle Epics / Ticker im Universe.
    Gibt dict epic -> [Preis-Dicts] zurueck.
    """
    price_map = {}
    for epic in universe:
        prices = get_prices_yf(epic, num_points=num_points)
        if prices:
            price_map[epic] = prices
        else:
            logger.warning("  %s: keine Daten von yfinance", epic)
    return price_map


def check_regime_yf(regime_epic: str = REGIME_EPIC, ma_period: int = 200) -> bool:
    """
    Markt-Regime-Filter: True (bullish) wenn aktueller Kurs > MA(ma_period).
    Nutzt REGIME_EPIC (Standard: ^NDX = NASDAQ 100).
    """
    prices = get_prices_yf(regime_epic, num_points=ma_period + 10)
    if not prices:
        logger.warning("Regime-Check fehlgeschlagen - nehme bearish an.")
        return False

    closes = [p["closePrice"]["bid"] for p in prices]
    if len(closes) < ma_period:
        logger.warning("Zu wenig Daten fuer Regime-MA - nehme bearish an.")
        return False

    ma = sum(closes[-ma_period:]) / ma_period
    current = closes[-1]
    bullish = current > ma
    logger.info(
        "Regime (%s): Kurs=%.2f, MA%d=%.2f, bullish=%s",
        regime_epic, current, ma_period, ma, bullish,
    )
    return bullish
