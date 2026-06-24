"""scorer.py - Erweitertes Momentum-Scoring mit 5 Komponenten.

Formel:
  Score = W_MOM_3M  * mom_3m
        + W_MOM_6M  * mom_6m
        + W_MOM_12M * mom_12m
        + W_HI52W   * hi52w
        + W_RS      * rel_strength_6m   # Outperformance vs Benchmark
        + CONSISTENCY_BONUS             # wenn alle 3 Momentum-Perioden positiv
        - VOLATILITY_PENALTY            # bestraft hohe Vola (annualisiert)

Werte kommen aus config.WEIGHTS.
"""
import logging
import math
from typing import List, Dict
from config import WEIGHTS

logger = logging.getLogger(__name__)

# Gewichte aus config
W_MOM_3M  = WEIGHTS.get("mom_3m",  0.20)
W_MOM_6M  = WEIGHTS.get("mom_6m",  0.20)
W_MOM_12M = WEIGHTS.get("mom_12m", 0.25)
W_HI52W   = WEIGHTS.get("hi52w",   0.15)
W_RS      = WEIGHTS.get("rel_strength", 0.20)

# Bonus/Penalty-Parameter
CONSISTENCY_BONUS   = WEIGHTS.get("consistency_bonus", 0.10)
VOLATILITY_TARGET   = WEIGHTS.get("vol_target", 0.20)  # 20% ann. Ziel-Vola
VOLATILITY_SCALE    = WEIGHTS.get("vol_scale",  0.30)  # Skalierung des Penalty


def _extract_closes(prices: list) -> list:
    """Extrahiert Mid-Preise aus IG-kompatiblen Preis-Dicts."""
    closes = []
    for p in prices:
        bid = p.get("closePrice", {}).get("bid")
        ask = p.get("closePrice", {}).get("ask")
        if bid is not None and ask is not None:
            closes.append((bid + ask) / 2)
    return closes


def momentum_return(closes: list, lookback: int) -> float:
    """Prozentualer Return ueber die letzten `lookback` Bars."""
    if len(closes) < lookback + 1:
        return 0.0
    start = closes[-(lookback + 1)]
    end   = closes[-1]
    if start == 0:
        return 0.0
    return (end - start) / start


def proximity_to_52w_high(closes: list) -> float:
    """Wie nah ist der aktuelle Kurs am 52W-Hoch? 1.0 = neues Hoch, 0.0 = weit weg."""
    if len(closes) < 252:
        window = closes
    else:
        window = closes[-252:]
    if not window:
        return 0.0
    high_52w = max(window)
    current  = closes[-1]
    if high_52w == 0:
        return 0.0
    return current / high_52w


def annualized_volatility(closes: list, lookback: int = 63) -> float:
    """Annualisierte Volatilitaet (Standardabweichung der Daily Returns * sqrt(252))."""
    if len(closes) < lookback + 2:
        return VOLATILITY_TARGET  # Fallback: Zielvola annehmen
    window = closes[-lookback:]
    returns = []
    for i in range(1, len(window)):
        if window[i - 1] != 0:
            returns.append((window[i] - window[i - 1]) / window[i - 1])
    if len(returns) < 5:
        return VOLATILITY_TARGET
    n = len(returns)
    mean = sum(returns) / n
    variance = sum((r - mean) ** 2 for r in returns) / (n - 1)
    return math.sqrt(variance) * math.sqrt(252)


def relative_strength(closes: list, bench_closes: list, lookback: int = 126) -> float:
    """Outperformance des Instruments vs Benchmark ueber `lookback` Bars."""
    inst_ret  = momentum_return(closes, lookback)
    bench_ret = momentum_return(bench_closes, lookback) if len(bench_closes) >= lookback + 1 else 0.0
    return inst_ret - bench_ret


def score_instrument(
    prices: list,
    benchmark_prices: list,
) -> float:
    """
    Erweiterter Composite-Momentum-Score.

    Komponenten:
      1. Momentum 3M  (kurzfristig)
      2. Momentum 6M  (mittelfristig)
      3. Momentum 12M (langfristig, ohne letzten Monat = Skip-1-Month nicht impl.)
      4. 52W-High Proximity
      5. Relative Strength vs Benchmark (6M)
      6. Konsistenz-Bonus: alle 3 Perioden positiv
      7. Volatilitaets-Penalty: hohe Vola wird bestraft
    """
    closes       = _extract_closes(prices)
    bench_closes = _extract_closes(benchmark_prices) if benchmark_prices else []

    if len(closes) < 63:
        return 0.0

    # --- Momentum-Komponenten ---
    mom_3m  = momentum_return(closes, 63)
    mom_6m  = momentum_return(closes, 126)
    mom_12m = momentum_return(closes, 252)
    hi52w   = proximity_to_52w_high(closes)
    rs_6m   = relative_strength(closes, bench_closes, 126)

    # --- Basis-Score ---
    score = (
        W_MOM_3M  * mom_3m
        + W_MOM_6M  * mom_6m
        + W_MOM_12M * mom_12m
        + W_HI52W   * hi52w
        + W_RS      * rs_6m
    )

    # --- Konsistenz-Bonus: alle 3 Perioden positiv = starker Trend ---
    if mom_3m > 0 and mom_6m > 0 and mom_12m > 0:
        score += CONSISTENCY_BONUS
        logger.debug("Konsistenz-Bonus angewendet")

    # --- Volatilitaets-Penalty: hohe Vola relativ zur Ziel-Vola bestraft ---
    vola = annualized_volatility(closes, 63)
    if vola > 0:
        # Penalty = scale * (vola - target) / target, nur wenn vola > target
        excess_vola = max(0.0, vola - VOLATILITY_TARGET)
        penalty = VOLATILITY_SCALE * (excess_vola / VOLATILITY_TARGET)
        score -= penalty
        if excess_vola > 0:
            logger.debug("Vola-Penalty: vola=%.2f, penalty=%.4f", vola, penalty)

    return round(score, 6)


def rank_universe(
    universe: List[str],
    price_map: Dict[str, list],
    benchmark_prices: list,
) -> List[Dict]:
    """Score und Ranking aller Instrumente. Gibt Liste absteigend nach Score zurueck."""
    results = []
    for epic in universe:
        prices = price_map.get(epic, [])
        if not prices:
            logger.debug("Skipping %s - keine Preisdaten", epic)
            continue
        s = score_instrument(prices, benchmark_prices)
        results.append({"epic": epic, "score": s})
        logger.info(" Scored %s: %.4f", epic, s)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
