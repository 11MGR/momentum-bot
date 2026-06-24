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
# IG Epic format for German accounts:
#   UC.D.<TICKER>.CASH.IP  = US shares (Germany trading hours)
#   ED.D.<TICKER>.CASH.IP  = EU/DAX shares (Germany)
#   IX.D.<INDEX>.IFD.IP    = CFD Indices
UNIVERSE = [
    # US Large Caps (UC prefix = US shares, German account)
    "UC.D.AAPL.CASH.IP",
    "UC.D.MSFT.CASH.IP",
    "UC.D.NVDA.CASH.IP",
    "UC.D.GOOGL.CASH.IP",
    "UC.D.AMZN.CASH.IP",
    "UC.D.META.CASH.IP",
    "UC.D.TSLA.CASH.IP",
    "UC.D.JPM.CASH.IP",
    "UC.D.V.CASH.IP",
    "UC.D.UNH.CASH.IP",
    "UC.D.XOM.CASH.IP",
    "UC.D.NFLX.CASH.IP",
    # EU / DAX Large Caps (ED prefix = European shares)
    "ED.D.SAP.CASH.IP",
    "ED.D.SIE.CASH.IP",
    "ED.D.ALV.CASH.IP",
    "ED.D.MBG.CASH.IP",
    "ED.D.BMW.CASH.IP",
    "ED.D.BAYN.CASH.IP",
    "ED.D.DTE.CASH.IP",
    # Indices (CFD)
    "IX.D.DAX.IFD.IP",
    "IX.D.SPTRD.IFD.IP",
    "IX.D.NASDAQ.IFD.IP",
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
