import os

# ─ IG API CREDENTIALS ────────────────────────────────────────────────
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

# ─ THEMATISCHES UNIVERSE ─────────────────────────────────────────────────────
# Werte nach persoenlichen Interessen: Halbleiter, Tech, EU-Sovereignty,
# Consumer Electronics (Xiaomi), Industrials/Energie.
UNIVERSE = [
    # Halbleiter & Chip-Equipment
    "ASML",     "NVDA",     "IFX.DE",   "STM",
    "BESI.AS",  "SOI.PA",   "AMAT",
    # Consumer Tech / Xiaomi
    "1810.HK",
    # Europaeische Verteidigung & Aerospace
    "RHM.DE",   "AIR.PA",   "LDO.MI",   "HO.PA",
    "SAF.PA",   "RR.L",     "HAG.DE",
    # Industrials / Automation / Energie
    "SIE.DE",   "ABBN.SW",  "SU.PA",    "ENR.DE",   "VWS.CO",
]

# ─ BREITES SCORE-ONLY UNIVERSE ─────────────────────────────────────────────────
# Kein thematischer Filter -- rein mechanisches Momentum-Screening.
# Breite Auswahl globaler Large-/Mid-Caps aus verschiedenen Sektoren.
# Der Bot rankt diese taeglich ausschliesslich nach Score.
# Werte die hier oben auftauchen sind unabhaengig von Praeferenzen
# objektiv die staerksten Momentum-Kandidaten weltweit.
BROAD_UNIVERSE = [
    # ── US Mega-Cap Tech
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet
    "META",   # Meta Platforms
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "NVDA",   # NVIDIA (auch im thematischen, aber hier nochmal)
    "ORCL",   # Oracle (Cloud/AI)
    "CRM",    # Salesforce
    "PLTR",   # Palantir (AI/Data)
    # ── US Financials
    "BRK-B",  # Berkshire Hathaway
    "JPM",    # JPMorgan Chase
    "GS",     # Goldman Sachs
    "V",      # Visa
    "MA",     # Mastercard
    # ── US Healthcare / Pharma
    "LLY",    # Eli Lilly (GLP-1 / Adipositas)
    "NVO",    # Novo Nordisk (Ozempic)
    "UNH",    # UnitedHealth
    "ABBV",   # AbbVie
    # ── US Industrials / Defence
    "CAT",    # Caterpillar
    "RTX",    # Raytheon Technologies
    "LMT",    # Lockheed Martin
    "NOC",    # Northrop Grumman
    "GE",     # GE Aerospace
    # ── US Energy / Commodities
    "XOM",    # ExxonMobil
    "CVX",    # Chevron
    "FCX",    # Freeport-McMoRan (Kupfer)
    "NEM",    # Newmont (Gold)
    # ── US Consumer
    "COST",   # Costco
    "WMT",    # Walmart
    "AMGN",   # Amgen
    # ── Europaeische Blue Chips
    "MC.PA",  # LVMH (Luxus)
    "OR.PA",  # L'Oreal
    "NESN.SW",# Nestle (defensiv)
    "NOVO-B.CO", # Novo Nordisk DK (Doppelticker)
    "SAP.DE", # SAP (Enterprise Software)
    "ALV.DE", # Allianz (Versicherung)
    # ── Asien / EM
    "TSM",    # Taiwan Semiconductor (TSMC)
    "BABA",   # Alibaba (US-listed ADR)
    "005930.KS", # Samsung Electronics (KRW)
    "9988.HK",   # Alibaba HK
    "700.HK",    # Tencent
]

# Fuer Ticker-Auflosung: beide Universes zusammenfassen
# YAHOO_MAP bleibt 1:1
YAHOO_MAP = {ticker: ticker for ticker in UNIVERSE + BROAD_UNIVERSE}

# Regime-Filter: NASDAQ 100
REGIME_EPIC      = "^NDX"
REGIME_MA_PERIOD = 200

# ─ SCORING WEIGHTS ───────────────────────────────────────────────────────────
WEIGHTS = {
    "mom_3m":  0.25,
    "mom_6m":  0.25,
    "mom_12m": 0.30,
    "hi52w":   0.20,
}

# ─ BOT PARAMETERS ──────────────────────────────────────────────────────────────
TOP_N_SIGNALS       = 7
BROAD_TOP_N         = 10   # Top 10 aus dem Score-Only Screening
MAX_POSITIONS       = 5
RISK_PER_TRADE_PCT  = 0.01
STOP_LOSS_PCT       = 0.02
DAILY_LOSS_LIMIT_PCT= 0.05

# ─ FILE PATHS ───────────────────────────────────────────────────────────────────
LOG_FILE    = "logs/momentum_bot.log"
REPORT_FILE = "reports/daily_report.md"
