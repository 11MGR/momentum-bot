import os

# --- IG API CREDENTIALS --------------------------------------------------
IG_API_KEY    = os.getenv("IG_API_KEY")
IG_USERNAME   = os.getenv("IG_USERNAME")
IG_PASSWORD   = os.getenv("IG_PASSWORD")
IG_ACC_TYPE   = os.getenv("IG_ACC_TYPE", "DEMO")
IG_ACC_NUMBER = os.getenv("IG_ACC_NUMBER")
IG_BASE_URL   = "https://demo-api.ig.com/gateway/deal"

_required = {"IG_API_KEY": IG_API_KEY, "IG_USERNAME": IG_USERNAME,
             "IG_PASSWORD": IG_PASSWORD, "IG_ACC_NUMBER": IG_ACC_NUMBER}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Set them in Railway > Variables (never hardcode credentials)."
    )

# --- THEMATISCHES UNIVERSE -----------------------------------------------
# Werte nach persoenlichen Interessen: Halbleiter, Tech, EU-Sovereignty,
# Consumer Electronics (Xiaomi), Industrials/Energie.
UNIVERSE = [
    # Halbleiter & Chip-Equipment
    "ASML",     "NVDA",      "IFX.DE",   "STM",
    "BESI.AS",  "SOI.PA",   "AMAT",
    # Consumer Tech / Xiaomi
    "1810.HK",
    # Europaeische Verteidigung & Aerospace
    "RHM.DE",   "AIR.PA",   "LDO.MI",   "HO.PA",
    "SAF.PA",   "RR.L",     "HAG.DE",
    # Industrie & Energie
    "SIE.DE",   "ABBN.SW",  "SU.PA",    "ENR.DE",   "VWS.CO",
]

# --- YAHOO FINANCE TICKER MAP --------------------------------------------
# 1:1 Mapping epic -> Yahoo-Ticker (fuer Tickers die identisch sind, optional)
YAHOO_MAP = {
    "ASML":    "ASML",
    "NVDA":    "NVDA",
    "IFX.DE":  "IFX.DE",
    "STM":     "STM",
    "BESI.AS": "BESI.AS",
    "SOI.PA":  "SOI.PA",
    "AMAT":    "AMAT",
    "1810.HK": "1810.HK",
    "RHM.DE":  "RHM.DE",
    "AIR.PA":  "AIR.PA",
    "LDO.MI":  "LDO.MI",
    "HO.PA":   "HO.PA",
    "SAF.PA":  "SAF.PA",
    "RR.L":    "RR.L",
    "HAG.DE":  "HAG.DE",
    "SIE.DE":  "SIE.DE",
    "ABBN.SW": "ABBN.SW",
    "SU.PA":   "SU.PA",
    "ENR.DE":  "ENR.DE",
    "VWS.CO":  "VWS.CO",
}

# --- BROAD UNIVERSE (Score-Only) -----------------------------------------
# Globale Large-Caps - rein mechanisches Screening, unabhaengig von Praeferenzen.
BROAD_UNIVERSE = [
    # US Tech / Mega-Cap
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSM", "AVGO",
    # US Financials
    "JPM", "GS", "MS", "BLK",
    # US Industrie & Energie
    "CAT", "GE", "HON", "DE", "FCX", "XOM", "CVX",
    # US Healthcare
    "LLY", "UNH", "AMGN", "NEM",
    # US Consumer
    "COST", "WMT", "AMZN",
    # Europa Large-Cap
    "MC.PA", "OR.PA", "NESN.SW", "NOVO-B.CO", "SAP.DE", "ALV.DE",
    # Asien
    "005930.KS", "9988.HK", "BABA",
    # ETF-Proxies (Trends)
    "NOC",
]
# Deduplizieren
BROAD_UNIVERSE = list(dict.fromkeys(BROAD_UNIVERSE))

# --- REGIME FILTER -------------------------------------------------------
REGIME_EPIC      = "^NDX"   # Nasdaq 100 als Markt-Regime-Filter
REGIME_MA_PERIOD = 200      # 200-Tage-MA

# --- SCORING WEIGHTS -----------------------------------------------------
# Gewichte fuer die Scoring-Formel in scorer.py
# Summe der Momentum-Gewichte sollte ~1.0 ergeben (ohne Bonus/Penalty).
#
# Formel:
#   Score = mom_3m*W + mom_6m*W + mom_12m*W + hi52w*W + rel_strength*W
#           + consistency_bonus (wenn alle 3 Perioden positiv)
#           - volatility_penalty (bei Vola > vol_target)
WEIGHTS = {
    # Momentum-Gewichte (Summe = 1.0)
    "mom_3m":  0.20,   # Kurzfristiges Momentum (3 Monate)
    "mom_6m":  0.20,   # Mittelfristiges Momentum (6 Monate)
    "mom_12m": 0.25,   # Langfristiges Momentum (12 Monate)
    "hi52w":   0.15,   # Naehe zum 52W-Hoch
    "rel_strength": 0.20,  # Outperformance vs. Benchmark (^NDX, 6M)
    # Bonus / Penalty
    "consistency_bonus": 0.10,  # Bonus wenn 3M+6M+12M alle positiv
    "vol_target": 0.20,         # Ziel-Volatilitaet (20% ann.) - darunter kein Penalty
    "vol_scale":  0.30,         # Skalierung des Vola-Penalty
}

# --- RISK & POSITION SIZING ----------------------------------------------
MAX_POSITIONS        = 5      # Maximale gleichzeitige Positionen
RISK_PER_TRADE_PCT   = 1.0    # Risiko pro Trade in % des Kapitals
STOP_LOSS_PCT        = 5.0    # Stop-Loss in % vom Einstiegspreis
DAILY_LOSS_LIMIT_PCT = 3.0    # Kill-Switch: Tagesverlust-Limit in %

# --- REPORT & LOG PATHS --------------------------------------------------
TOP_N_SIGNALS = 7    # Top-N Buy-Signale im thematischen Universe
BROAD_TOP_N   = 10   # Top-N Signale im Score-Only Screening
REPORT_FILE   = "reports/daily_report.md"
LOG_FILE      = "logs/bot.log"
