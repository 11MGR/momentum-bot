import logging
from typing import List, Dict
from config import WEIGHTS

logger = logging.getLogger(__name__)

# Extract weights from config dict for readability
W_MOM_3M  = WEIGHTS.get("mom_3m",  0.25)
W_MOM_6M  = WEIGHTS.get("mom_6m",  0.25)
W_MOM_12M = WEIGHTS.get("mom_12m", 0.30)
W_HI52W   = WEIGHTS.get("hi52w",   0.20)


def _extract_closes(prices: list) -> list:
    """Extract closing mid prices from price history list."""
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
    if len(closes) < 2:
        return 0.0
    window = closes[-252:] if len(closes) >= 252 else closes
    high = max(window)
    current = closes[-1]
    if high == 0:
        return 0.0
    return current / high


def relative_strength(closes: list, benchmark_closes: list, lookback: int = 252) -> float:
    """Return momentum of instrument minus benchmark over `lookback` bars."""
    instr_ret = momentum_return(closes, lookback)
    bench_ret = momentum_return(benchmark_closes, lookback) if benchmark_closes else 0.0
    return instr_ret - bench_ret


def score_instrument(
    prices: list,
    benchmark_prices: list,
) -> float:
    """
    Composite momentum score for a single instrument.
    Higher = stronger momentum = higher rank.
    """
    closes = _extract_closes(prices)
    bench_closes = _extract_closes(benchmark_prices) if benchmark_prices else []

    if len(closes) < 63:  # need at least 3 months of data
        return 0.0

    # Momentum signals (trading days: 63~3m, 126~6m, 252~12m)
    mom_3m  = momentum_return(closes, 63)
    mom_6m  = momentum_return(closes, 126)
    mom_12m = momentum_return(closes, 252)
    hi52w   = proximity_to_52w_high(closes)

    score = (
        W_MOM_3M  * mom_3m
        + W_MOM_6M  * mom_6m
        + W_MOM_12M * mom_12m
        + W_HI52W   * hi52w
    )
    return round(score, 6)


def rank_universe(
    universe: List[str],
    price_map: Dict[str, list],
    benchmark_prices: list,
) -> List[Dict]:
    """Score and rank all instruments. Returns list sorted descending by score."""
    results = []
    for epic in universe:
        prices = price_map.get(epic, [])
        if not prices:
            logger.debug("Skipping %s - no price data", epic)
            continue
        s = score_instrument(prices, benchmark_prices)
        results.append({"epic": epic, "score": s})
        logger.info("  Scored %s: %.4f", epic, s)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
