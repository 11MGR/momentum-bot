import os

# ─ IG API CREDENTIALS ────────────────────────────────────────────────
IG_API_KEY    = os.getenv("IG_API_KEY")          # required
IG_USERNAME   = os.getenv("IG_USERNAME")         # required
IG_PASSWORD   = os.getenv("IG_PASSWORD")         # required
IG_ACC_TYPE   = os.getenv("IG_ACC_TYPE", "DEMO") # DEMO | LIVE
IG_ACC_NUMBER = os.getenv("IG_ACC_NUMBER")       # required
IG_BASE_URL   = "https://demo-api.ig.com/gateway/deal"

# Validate that required env vars are set
_required = {"IG_API_KEY": IG_API_KEY, "IG_USERNAME": IG_USERNAME,
             "IG_PASSWORD": IG_PASSWORD, "IG_ACC_NUMBER": IG_ACC_NUMBER}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Set them in Railway > Variables (never hardcode credentials)."
    )

# ─ UNIVERSE ─────────────────────────────────────────────────────────────
# IG epics used for order placement on the demo account.
# Price history is fetched via Yahoo Finance (yfinance) - see YAHOO_MAP below.
UNIVERSE = [
    # Global Equity Indices
    "IX.D.DAX.IFD.IP",     # Germany DAX 40
    "IX.D.SPTRD.IFD.IP",   # US S&P 500
    "IX.D.NASDAQ.IFD.IP",  # US NASDAQ 100
    "IX.D.DOW.IFD.IP",     # US Dow Jones
    "IX.D.FTSE.IFD.IP",    # UK FTSE 100
    "IX.D.ESXB.IFD.IP",    # Euro Stoxx 50
    "IX.D.NIKKEI.IFD.IP",  # Japan Nikkei 225
    # FX Majors
    "CS.D.EURUSD.CFD.IP",  # EUR/USD
    "CS.D.GBPUSD.CFD.IP",  # GBP/USD
    "CS.D.USDJPY.CFD.IP",  # USD/JPY
    "CS.D.AUDUSD.CFD.IP",  # AUD/USD
    "CS.D.USDCHF.CFD.IP",  # USD/CHF
    # Commodities
    "CS.D.CFDGOLD.CFD.IP", # Gold
    "CS.D.CFDSIVER.CFD.IP",# Silver
    "CC.D.CL.UNC.IP",      # Crude Oil WTI
    "CC.D.NG.UNC.IP",      # Natural Gas
]

# Yahoo Finance ticker map: IG epic -> yfinance symbol
# Used for momentum scoring (price history). IG is used for order placement only.
YAHOO_MAP = {
    "IX.D.DAX.IFD.IP":     "^GDAXI",   # DAX 40
    "IX.D.SPTRD.IFD.IP":   "^GSPC",    # S&P 500
    "IX.D.NASDAQ.IFD.IP":  "^NDX",     # NASDAQ 100
    "IX.D.DOW.IFD.IP":     "^DJI",     # Dow Jones
    "IX.D.FTSE.IFD.IP":    "^FTSE",    # FTSE 100
    "IX.D.ESXB.IFD.IP":    "^STOXX50E",# Euro Stoxx 50
    "IX.D.NIKKEI.IFD.IP":  "^N225",    # Nikkei 225
    "CS.D.EURUSD.CFD.IP":  "EURUSD=X", # EUR/USD
    "CS.D.GBPUSD.CFD.IP":  "GBPUSD=X", # GBP/USD
    "CS.D.USDJPY.CFD.IP":  "USDJPY=X", # USD/JPY
    "CS.D.AUDUSD.CFD.IP":  "AUDUSD=X", # AUD/USD
    "CS.D.USDCHF.CFD.IP":  "USDCHF=X", # USD/CHF
    "CS.D.CFDGOLD.CFD.IP": "GC=F",     # Gold Futures
    "CS.D.CFDSIVER.CFD.IP":"SI=F",     # Silver Futures
    "CC.D.CL.UNC.IP":      "CL=F",     # WTI Crude Oil
    "CC.D.NG.UNC.IP":      "NG=F",     # Natural Gas
}

# Epic used for market-regime filter (S&P 500 200-day MA)
REGIME_EPIC      = "IX.D.SPTRD.IFD.IP"
REGIME_MA_PERIOD = 200

# ─ SCORING WEIGHTS ───────────────────────────────────────────────────────────
WEIGHTS = {
    "mom_3m":  0.25,  # 3-month momentum
    "mom_6m":  0.25,  # 6-month momentum
    "mom_12m": 0.30,  # 12-month momentum
    "hi52w":   0.20,  # proximity to 52-week high
}

# ─ BOT PARAMETERS ──────────────────────────────────────────────────────────────
TOP_N_SIGNALS       = 5     # how many top/bottom signals to show in report
MAX_POSITIONS       = 5     # max concurrent positions
RISK_PER_TRADE_PCT  = 0.01  # 1% account risk per trade
STOP_LOSS_PCT       = 0.02  # 2% stop loss per trade
DAILY_LOSS_LIMIT_PCT= 0.05  # halt if daily drawdown exceeds 5%

# ─ FILE PATHS ───────────────────────────────────────────────────────────────────
LOG_FILE    = "logs/momentum_bot.log"
REPORT_FILE = "reports/daily_report.md"
