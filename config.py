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
# IG Demo API uses its own Epic format: CS.D.<TICKER>.CASH.IP for shares
# and IX.D.<INDEX>.IFD.IP for indices.
UNIVERSE = [
    # US Large Caps (IG Cash format)
    "CS.D.AAPL.CASH.IP",
    "CS.D.MSFT.CASH.IP",
    "CS.D.NVDA.CASH.IP",
    "CS.D.GOOGL.CASH.IP",
    "CS.D.AMZN.CASH.IP",
    "CS.D.META.CASH.IP",
    "CS.D.TSLA.CASH.IP",
    "CS.D.JPM.CASH.IP",
    "CS.D.V.CASH.IP",
    "CS.D.UNH.CASH.IP",
    "CS.D.XOM.CASH.IP",
    "CS.D.NFLX.CASH.IP",
    # EU / DAX Large Caps
    "CS.D.SAP.CASH.IP",
    "CS.D.SIE.CASH.IP",
    "CS.D.ALV.CASH.IP",
    "CS.D.MBG.CASH.IP",
    "CS.D.BMW.CASH.IP",
    "CS.D.BAYN.CASH.IP",
    "CS.D.DTE.CASH.IP",
    # Indices
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
TOP_N_SIGNALS       = 5      # top N buy candidates shown in report
DAILY_LOSS_LIMIT_PCT = 0.02  # kill-switch: halt if daily loss > 2 %

# — OUTPUT ————————————————————————————————————————————————————
REPORT_FILE = "reports/daily_report.md"
LOG_FILE    = "logs/momentum_bot.log"
