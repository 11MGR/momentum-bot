import os

# ── IG API CREDENTIALS ───────────────────────────────────────────────────────────────
# All credentials MUST be set via environment variables.
# Never put real values here – use Railway/Docker env vars.
IG_API_KEY      = os.getenv("IG_API_KEY")       # required
IG_USERNAME     = os.getenv("IG_USERNAME")      # required
IG_PASSWORD     = os.getenv("IG_PASSWORD")      # required
IG_ACC_TYPE     = os.getenv("IG_ACC_TYPE", "DEMO")   # DEMO | LIVE
IG_ACC_NUMBER   = os.getenv("IG_ACC_NUMBER")    # required
IG_BASE_URL     = "https://demo-api.ig.com/gateway/deal"

# Validate that required env vars are set
_required = {"IG_API_KEY": IG_API_KEY, "IG_USERNAME": IG_USERNAME,
             "IG_PASSWORD": IG_PASSWORD, "IG_ACC_NUMBER": IG_ACC_NUMBER}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Set them in Railway > Variables (never hardcode credentials)."
    )

# ── UNIVERSE ────────────────────────────────────────────────────────────────
UNIVERSE = [
    # US Large Caps
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "UNH",
    "XOM", "LLY", "JNJ", "PG", "MA", "HD", "MRK", "ABBV", "CVX", "PEP",
    # EU / DAX
    "SAP", "SIE", "ALV", "MBG", "BMW", "BAS", "MUV2", "ADS", "DTE", "VOW3",
    # Indices (CFD)
    "IX.D.DAX.IFD.IP", "IX.D.SPTRD.IFD.IP", "IX.D.NASDAQ.IFD.IP",
]

# ── SCORING WEIGHTS ─────────────────────────────────────────────────────────
WEIGHT_MOM_3M   = 0.30
WEIGHT_MOM_6M   = 0.25
WEIGHT_MOM_12M  = 0.20
WEIGHT_52W_HIGH = 0.15
WEIGHT_REL_STR  = 0.10

# ── RISK PARAMETERS ─────────────────────────────────────────────────────────
MAX_POSITIONS        = 5
RISK_PER_TRADE_PCT   = 0.01
STOP_LOSS_PCT        = 0.03
DAILY_LOSS_LIMIT_PCT = 0.05

# ── REGIME FILTER ───────────────────────────────────────────────────────────
REGIME_EPIC      = "IX.D.SPTRD.IFD.IP"
REGIME_MA_PERIOD = 50

# ── OUTPUT ──────────────────────────────────────────────────────────────────
TOP_N_SIGNALS    = 5
LOG_FILE         = "logs/momentum_bot.log"
REPORT_FILE      = "reports/daily_report.md"
