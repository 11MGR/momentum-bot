import os

# ─ IG API CREDENTIALS ────────────────────────────────────────────────
IG_API_KEY    = os.getenv("IG_API_KEY")          # required
IG_USERNAME   = os.getenv("IG_USERNAME")         # required
IG_PASSWORD   = os.getenv("IG_PASSWORD")         # required
IG_ACC_TYPE   = os.getenv("IG_ACC_TYPE", "DEMO") # DEMO | LIVE
IG_ACC_NUMBER = os.getenv("IG_ACC_NUMBER")       # required
IG_BASE_URL   = "https://demo-api.ig.com/gateway/deal"

_required = {"IG_API_KEY": IG_API_KEY, "IG_USERNAME": IG_USERNAME,
             "IG_PASSWORD": IG_PASSWORD, "IG_ACC_NUMBER": IG_ACC_NUMBER}
_missing = [k for k, v in _required.items() if not v]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        "Set them in Railway > Variables (never hardcode credentials)."
    )

# ─ UNIVERSE ───────────────────────────────────────────────────────────────────
#
# Thematisches Universe: Tech / Halbleiter / Europaeische Sovereignty-Plays
# Alle Eintraege sind direkte Yahoo-Finance-Ticker.
# YAHOO_MAP ist 1:1 (mit optionalen Korrekturen fuer Abweichungen).
#
UNIVERSE = [
    # ── Halbleiter & Chip-Equipment ─────────────────────────────────────────────
    "ASML",      # ASML Holding (NL) - EUV-Lithographie-Monopolist
    "NVDA",      # NVIDIA (US) - KI-Chips / GPU, unverzichtbar im Sektor
    "IFX.DE",    # Infineon Technologies (DE) - Automotive + Power Chips
    "STM",       # STMicroelectronics (EU/US) - Mixed-Signal / Automotive
    "BESI.AS",   # BE Semiconductor Industries (NL) - Packaging Equipment
    "SOI.PA",    # Soitec (FR) - Silicon-on-Insulator Wafer
    "AMAT",      # Applied Materials (US) - Kern-Zulieferer der ASML-Chain
    # ── Consumer Tech / Xiaomi ────────────────────────────────────────────────
    "1810.HK",   # Xiaomi Corp (HK) - Consumer Electronics + EV
    # ── Europaeische Verteidigung & Aerospace (Sovereignty) ───────────────
    "RHM.DE",    # Rheinmetall (DE) - Ruestung / Panzer / Munition
    "AIR.PA",    # Airbus (EU) - Aerospace / Defence / Raumfahrt
    "LDO.MI",    # Leonardo (IT) - Defence Electronics / Hubschrauber
    "HO.PA",     # Thales (FR) - Defence Electronics / Cyber / Space
    "SAF.PA",    # Safran (FR) - Triebwerke / Avionics
    "RR.L",      # Rolls-Royce Holdings (UK) - Triebwerke / SMR-Reaktoren
    "HAG.DE",    # Hensoldt AG (DE) - Radarsysteme / Sensors / EW
    # ── Industrials / Automation / Energie ─────────────────────────────
    "SIE.DE",    # Siemens AG (DE) - Automatisierung / Digital Industries
    "ABBN.SW",   # ABB Ltd (CH) - Robotics / Electrification
    "SU.PA",     # Schneider Electric (FR) - Energiemanagement / IoT
    "ENR.DE",    # Siemens Energy (DE) - Energiewende / Gasturbinen
    "VWS.CO",    # Vestas Wind Systems (DK) - Windenergie
]

# Yahoo Finance Ticker Map (1:1 fuer direkte YF-Ticker als Universe)
YAHOO_MAP = {ticker: ticker for ticker in UNIVERSE}

# Regime-Filter: NASDAQ 100 (tech-lastiger Index, passend zum Universe)
REGIME_EPIC      = "^NDX"
REGIME_MA_PERIOD = 200

# ─ SCORING WEIGHTS ───────────────────────────────────────────────────────────
WEIGHTS = {
    "mom_3m":  0.25,  # 3-Monats-Momentum
    "mom_6m":  0.25,  # 6-Monats-Momentum
    "mom_12m": 0.30,  # 12-Monats-Momentum (Trend-Staerke)
    "hi52w":   0.20,  # Naehe zum 52-Wochen-Hoch (Staerke-Signal)
}

# ─ BOT PARAMETERS ──────────────────────────────────────────────────────────────
TOP_N_SIGNALS       = 7     # Top 7 Buy-Signale + Top 7 Exit im Report
MAX_POSITIONS       = 5     # max. gleichzeitige Positionen
RISK_PER_TRADE_PCT  = 0.01  # 1% Account-Risiko pro Trade
STOP_LOSS_PCT       = 0.02  # 2% Stop-Loss
DAILY_LOSS_LIMIT_PCT= 0.05  # Kill-Switch bei 5% Tagesverlust

# ─ FILE PATHS ───────────────────────────────────────────────────────────────────
LOG_FILE    = "logs/momentum_bot.log"
REPORT_FILE = "reports/daily_report.md"
