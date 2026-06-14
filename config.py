import os

# ── IG API CREDENTIALS (via environment variables) ──────────────────────────
IG_API_KEY      = os.getenv("IG_API_KEY", "1d203bee248c56e41739a6c4722fcfe9c8e7b15c")
IG_USERNAME     = os.getenv("IG_USERNAME", "sotirios.l@live.de")
IG_PASSWORD     = os.getenv("IG_PASSWORD", "")   # Set via env var – never hardcode!
IG_ACC_TYPE     = os.getenv("IG_ACC_TYPE", "DEMO")   # DEMO | LIVE
IG_ACC_NUMBER   = os.getenv("IG_ACC_NUMBER", "Z6B6N5")
IG_BASE_URL     = "https://demo-api.ig.com/gateway/deal"

# ── UNIVERSE ────────────────────────────────────────────────────────────────
# EPIC codes for liquid instruments on IG (CFD)
# Mix of US large caps, EU indices and top ETFs
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
WEIGHT_MOM_3M   = 0.30   # 3-month momentum
WEIGHT_MOM_6M   = 0.25   # 6-month momentum
WEIGHT_MOM_12M  = 0.20   # 12-month momentum
WEIGHT_52W_HIGH = 0.15   # proximity to 52-week high
WEIGHT_REL_STR  = 0.10   # relative strength vs benchmark

# ── RISK PARAMETERS ─────────────────────────────────────────────────────────
MAX_POSITIONS        = 5       # max concurrent open positions
RISK_PER_TRADE_PCT   = 0.01   # 1% of account per trade
STOP_LOSS_PCT        = 0.03   # 3% stop loss per position
DAILY_LOSS_LIMIT_PCT = 0.05   # halt if daily P&L < -5%

# ── REGIME FILTER ───────────────────────────────────────────────────────────
REGIME_EPIC      = "IX.D.SPTRD.IFD.IP"   # S&P 500 CFD as regime proxy
REGIME_MA_PERIOD = 50                     # 50-day MA

# ── OUTPUT ──────────────────────────────────────────────────────────────────
TOP_N_SIGNALS    = 5    # show top N buy signals in daily report
LOG_FILE         = "logs/momentum_bot.log"
REPORT_FILE      = "reports/daily_report.md"
