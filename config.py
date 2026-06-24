import os

# — IG API CREDENTIALS ————————————————————————————————————————
# All credentials MUST be set via environment variables.
# Never put real values here – use Railway/GitHub Actions secrets.
IG_API_KEY     = os.getenv("IG_API_KEY")      # required
IG_USERNAME    = os.getenv("IG_USERNAME")     # required
IG_PASSWORD    = os.getenv("IG_PASSWORD")     # required
IG_ACC_TYPE    = os.getenv("IG_ACC_TYPE", "DEMO")  # DEMO | LIVE
IG_ACC_NUMBER  = os.getenv("IG_ACC_NUMBER")   # required
IG_BASE_URL    = "https://demo-api.ig.com/gateway/deal"

# Validate that required env vars are set
_required = {"IG_API_KEY": IG_API_KEY, "IG_USERNAME": IG_USERNAME,
             "IG_PASSWORD": IG_PASSWORD, "IG_ACC_NUMBER": IG_ACC_NUMBER}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Set them in Railway > Variables (never hardcode credentials)."
    )

# — UNIVERSE ——————————————————————————————————————————————————
# IG REST API provides historical prices for Indices, FX and Commodities.
# Equity shares require a different endpoint and are not available via
# the standard /prices endpoint in the demo environment.
UNIVERSE = [
    # Global Equity Indices (CFD)
    "IX.D.DAX.IFD.IP",          # Germany DAX 40
    "IX.D.NASDAQ.IFD.IP",       # US Tech 100
    "IX.D.SPTRD.IFD.IP",        # US 500
    "IX.D.DOW.IFD.IP",          # Wall Street 30
    "IX.D.FTSE.IFD.IP",         # UK 100
    "IX.D.ESXB.IFD.IP",         # Euro Stoxx 50
    "IX.D.NIKKEI.IFD.IP",       # Japan 225
    "IX.D.ASX.IFD.IP",          # Australia 200
    # FX Majors
    "CS.D.EURUSD.CFD.IP",       # EUR/USD
    "CS.D.GBPUSD.CFD.IP",       # GBP/USD
    "CS.D.USDJPY.CFD.IP",       # USD/JPY
    "CS.D.AUDUSD.CFD.IP",       # AUD/USD
    "CS.D.USDCHF.CFD.IP",       # USD/CHF
    # Commodities
    "CS.D.CFDGOLD.CFD.IP",      # Gold
    "CS.D.CFDSIVER.CFD.IP",     # Silver
    "CC.D.CL.UNC.IP",           # Crude Oil (WTI)
    "CC.D.NG.UNC.IP",           # Natural Gas
]

# Epic used for market-regime filter (S&P 500)
REGIME_EPIC      = "IX.D.SPTRD.IFD.IP"
REGIME_MA_PERIOD = 200      # days

# — SCORING WEIGHTS ———————————————————————————————————————————
WEIGHT_MOM_3M   = 0.30
WEIGHT_MOM_6M   = 0.25
WEIGHT_MOM_12M  = 0.20
WEIGHT_52W_HIGH = 0.15
WEIGHT_REL_STR  = 0.10

# — PORTFOLIO SETTINGS ————————————————————————————————————————
TOP_N_SIGNALS        = 5      # top N buy candidates shown in report
DAILY_LOSS_LIMIT_PCT = 0.02   # kill-switch: halt if daily loss > 2%
MAX_POSITIONS        = 5      # max concurrent open positions
RISK_PER_TRADE_PCT   = 0.01   # risk 1% of account per trade
STOP_LOSS_PCT        = 0.02   # stop loss at 2% below entry

# — OUTPUT ————————————————————————————————————————————————————
REPORT_FILE = "reports/daily_report.md"
LOG_FILE    = "logs/momentum_bot.log"
