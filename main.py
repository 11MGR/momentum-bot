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


def get_account_balance(client: IGClient) -> float:
    try:
        info = client.get_account_info()
        for acc in info.get("accounts", []):
            if acc.get("preferred"):
                return float(acc["balance"]["available"])
    except Exception as e:
        logger.warning(f"Balance nicht abrufbar: {e}")
    return 0.0


def check_daily_loss_limit(client: IGClient) -> bool:
    try:
        info = client.get_account_info()
        for acc in info.get("accounts", []):
            if acc.get("preferred"):
                balance = float(acc["balance"]["balance"])
                deposit = float(acc["balance"]["deposit"])
                pnl_pct = (balance - deposit) / deposit if deposit else 0
                if pnl_pct < -DAILY_LOSS_LIMIT_PCT:
                    logger.error(f"KILL SWITCH: Tagesverlust {pnl_pct:.1%} > Limit {DAILY_LOSS_LIMIT_PCT:.1%}")
                    return False
    except Exception as e:
        logger.warning(f"Loss-Limit-Check fehlgeschlagen: {e}")
    return True


def generate_report(
    ranked_theme: list,
    ranked_broad: list,
    regime_bullish: bool,
    balance: float,
    date_str: str,
) -> str:
    """Erstellt den dreiteiligen Markdown-Report und schreibt ihn auf Disk."""

    # --- Thematische Signale ---
    top_buys_theme = [r for r in ranked_theme if r["score"] > 0][:TOP_N_SIGNALS]
    top_exits_theme = [r for r in reversed(ranked_theme) if r["score"] < 0][:TOP_N_SIGNALS]

    # --- Score-Only Picks (dedupliziert gegen thematisches Universe) ---
    theme_tickers = {r["epic"] for r in ranked_theme}
    # Nur Werte zeigen, die NICHT schon im thematischen Universe sind
    broad_unique = [r for r in ranked_broad if r["epic"] not in theme_tickers]
    top_broad = [r for r in broad_unique if r["score"] > 0][:BROAD_TOP_N]

    regime_str = "BULLISH" if regime_bullish else "BEARISH"
    lines = [
        "# Momentum Bot Daily Report",
        f"**Datum:** {date_str}  ",
        f"**Markt-Regime:** {regime_str} (NASDAQ 100 vs. MA{REGIME_MA_PERIOD})  ",
        f"**Account Balance:** EUR {balance:,.2f}  ",
        f"**Preisquelle:** Yahoo Finance (yfinance)  ",
        "",
        "---",
        "",
        "## Thematische Buy-Signale",
        "> *Dein persoenliches Universe: Halbleiter, EU-Sovereignty, Industrials*",
        "",
        "| Rang | Ticker | Score |",
        "|------|--------|-------|",
    ]
    if top_buys_theme:
        for i, r in enumerate(top_buys_theme, 1):
            lines.append(f"| {i} | `{r['epic']}` | {r['score']:.4f} |")
    else:
        lines.append("| - | Keine Buy-Signale heute | - |")

    lines += [
        "",
        "## Score-Only Picks",
        "> *Rein mechanisches Momentum-Screening aus 40+ globalen Large-Caps --*",
        "> *kein thematischer Filter, nur der Score entscheidet.*",
        "> *Werte aus dem thematischen Universe werden hier nicht doppelt gezeigt.*",
        "",
        "| Rang | Ticker | Score |",
        "|------|--------|-------|",
    ]
    if top_broad:
        for i, r in enumerate(top_broad, 1):
            lines.append(f"| {i} | `{r['epic']}` | {r['score']:.4f} |")
    else:
        lines.append("| - | Keine Score-Only-Kandidaten heute | - |")

    lines += [
        "",
        "## Exit / Vermeiden",
        "> *Schwache Werte aus dem thematischen Universe (negativer Score)*",
        "",
        "| Rang | Ticker | Score |",
        "|------|--------|-------|",
    ]
    if top_exits_theme:
        for i, r in enumerate(top_exits_theme, 1):
            lines.append(f"| {i} | `{r['epic']}` | {r['score']:.4f} |")
    else:
        lines.append("| - | Keine Exit-Signale heute | - |")

    lines += [
        "",
        "---",
        "*Automatisch generiert. Immer vor dem Trading verifizieren.*",
    ]

    report = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"Report gespeichert: {REPORT_FILE}")
    return report


def main():
    logger.info("=== Momentum Bot startet ===")
    date_str = datetime.date.today().isoformat()

    # 1. IG-Login (Account-Info + Kill-Switch)
    client = IGClient()

    # 2. Kill-Switch
    if not check_daily_loss_limit(client):
        logger.error("Tagesverlust-Limit erreicht. Abbruch.")
        return

    balance = get_account_balance(client)
    logger.info(f"Account Balance: EUR {balance:,.2f}")

    # 3. Markt-Regime via Yahoo Finance
    logger.info("Pruefe Markt-Regime via Yahoo Finance...")
    regime_bullish = check_regime_yf(regime_epic=REGIME_EPIC, ma_period=REGIME_MA_PERIOD)
    logger.info(f"Markt-Regime: {'BULLISH' if regime_bullish else 'BEARISH'}")

    # 4a. Thematisches Universe fetchen & scoren
    logger.info(f"Lade Preise fuer thematisches Universe ({len(UNIVERSE)} Werte)...")
    price_map_theme = fetch_all_prices_yf(UNIVERSE, num_points=260)
    logger.info(f"Thematisch: {len(price_map_theme)}/{len(UNIVERSE)} Werte mit Daten")

    # 4b. Breites Score-Only Universe fetchen & scoren
    logger.info(f"Lade Preise fuer Score-Only Universe ({len(BROAD_UNIVERSE)} Werte)...")
    price_map_broad = fetch_all_prices_yf(BROAD_UNIVERSE, num_points=260)
    logger.info(f"Score-Only: {len(price_map_broad)}/{len(BROAD_UNIVERSE)} Werte mit Daten")

    # Benchmark (S&P 500 / NASDAQ) fuer Relative-Strength
    benchmark_prices = get_prices_yf(REGIME_EPIC, num_points=260)

    # 5. Ranken
    logger.info("Scoren & Ranken...")
    ranked_theme = rank_universe(UNIVERSE, price_map_theme, benchmark_prices)
    ranked_broad = rank_universe(BROAD_UNIVERSE, price_map_broad, benchmark_prices)

    # 6. Report
    report = generate_report(ranked_theme, ranked_broad, regime_bullish, balance, date_str)
    print("\n" + report)
    logger.info("=== Momentum Bot abgeschlossen ===")


if __name__ == "__main__":
    main()
