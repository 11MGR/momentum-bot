import logging
from typing import List, Dict
from config import (
    WEIGHT_MOM_3M, WEIGHT_MOM_6M, WEIGHT_MOM_12M,
    WEIGHT_52W_HIGH, WEIGHT_REL_STR,
)

logger = logging.getLogger(__name__)


def _extract_closes(prices: list) -> list:
    """Extract closing mid prices from IG price history."""
    closes = []
    for p in prices:
        bid = p.get("closePrice", {}).get("bid")
        ask = p.get("closePrice", {}).get("ask")
        if bid is not None and ask is not None:
            closes.append((bid + ask) / 2)
    return closes


def momentum_return(closes: list, lookback: int) -> float:
    """Percentage return over the last `lookback` bars."""
    if len(closes) < lookback + 1:
        return 0.0
    start = closes[-(lookback + 1)]
    end   = closes[-1]
    if start == 0:
        return 0.0
    return (end - start) / start


def proximity_to_52w_high(closes: list) -> float:
    """How close current price is to 52-week high. 1.0 = at high."""
    window = closes[-252:] if len(closes) >= 252 else closes
    if not window:
        return 0.0
    high = max(window)
    current = closes[-1]
    if high == 0:
        return 0.0
    return current / high


def relative_strength(closes: list, benchmark_closes: list, lookback: int = 63) -> float:
    """Return of instrument minus return of benchmark over lookback."""
    r_instrument = momentum_return(closes, lookback)
    r_benchmark  = momentum_return(benchmark_closes, lookback)
    return r_instrument - r_benchmark


def score_instrument(prices: list, benchmark_prices: list) -> float:
    """Compute composite momentum score for one instrument."""
    closes = _extract_closes(prices)
    bench  = _extract_closes(benchmark_prices)

    if len(closes) < 63:
        return 0.0

    mom_3m  = momentum_return(closes, 63)
    mom_6m  = momentum_return(closes, 126)
    mom_12m = momentum_return(closes, 252)
    w52     = proximity_to_52w_high(closes)
    rel_str = relative_strength(closes, bench, 63)

    score = (
        WEIGHT_MOM_3M   * mom_3m
        + WEIGHT_MOM_6M   * mom_6m
        + WEIGHT_MOM_12M  * mom_12m
        + WEIGHT_52W_HIGH * w52
        + WEIGHT_REL_STR  * rel_str
    )

    logger.debug(
        f"  mom3m={mom_3m:.3f} mom6m={mom_6m:.3f} mom12m={mom_12m:.3f} "
        f"52w={w52:.3f} rel={rel_str:.3f} -> score={score:.4f}"
    )
    return score


def rank_universe(
    universe: List[str],
    price_map: Dict[str, list],
    benchmark_prices: list,
) -> List[Dict]:
    """Score and rank all instruments. Returns sorted list descending."""
    results = []
    for epic in universe:
        prices = price_map.get(epic, [])
        if not prices:
            continue
        s = score_instrument(prices, benchmark_prices)
        results.append({"epic": epic, "score": s})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
