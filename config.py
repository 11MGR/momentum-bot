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
#
# Fokus:
#   - Halbleiter & Chip-Equipment (ASML, Infineon, STMicro, BE Semi, Soitec)
#   - Consumer Tech / Xiaomi (HK-listed)
#   - Europaeische Verteidigung & Aerospace (Rheinmetall, Airbus, Leonardo,
#     Thales, Safran, Rolls-Royce) -- Abloese US/CN-Abhaengigkeit
#   - Industrials / Automation (Siemens, ABB, Schneider Electric, Siemens Energy)
#   - Regime-Filter bleibt NASDAQ 100 (technologie-lastig)
#
# WICHTIG: Diese Werte sind KEINE IG-Epics fuer echte Orders --
#   sie dienen ausschliesslich der Momentum-Berechnung via Yahoo Finance.
#   Fuer echte IG-Orders muessen die passenden IG-Epics separat gepflegt werden.
#   Das UNIVERSE-Feld enthaelt hier die Yahoo-Finance-Ticker direkt.

UNIVERSE = [
    # ── Halbleiter & Chip-Equipment ─────────────────────────────────────────────
    "ASML",          # ASML Holding - weltweiter EUV-Monopolist
    "IFX.DE",        # Infineon Technologies - DE, Automotive + Power Chips
    "STM",           # STMicroelectronics - EU, Mixed-Signal / Automotive
    "BESI.AS",       # BE Semiconductor Industries - NL, Packaging Equipment
    "SOI.PA",        # Soitec - FR, Silicon-on-Insulator Wafer
    "AMAT",          # Applied Materials - US, aber Kern-Zulieferer ASML-Chain
    # ── Consumer Tech / Xiaomi ────────────────────────────────────────────────
    "1810.HK",       # Xiaomi Corp - HK-listed, EV + Consumer Electronics
    # ── Europaeische Verteidigung & Aerospace (Sovereignty) ───────────────
    "RHM.DE",        # Rheinmetall - DE, Ruestung / Fahrzeuge
    "AIR.PA",        # Airbus - EU, Aerospace / Defence
    "LDO.MI",        # Leonardo - IT, Defence Electronics & Helicopters
    "HO.PA",         # Thales - FR, Defence Electronics / Cyber / Space
    "SAF.PA",        # Safran - FR, Triebwerke / Avionics
    "RR.L",          # Rolls-Royce Holdings - UK, Triebwerke / Micro-Reaktoren
    "BAYN.DE",       # Hensoldt - nein, lieber: DHER.DE (Diehl) -- nicht verfuegbar
    "HENSOLDT.DE",   # Hensoldt AG - DE, Radarsysteme
    # ── Industrials / Automation / Energie ─────────────────────────────
    "SIE.DE",        # Siemens AG - DE, Automatisierung / Digital Industries
    "ABBN.SW",       # ABB Ltd - CH, Robotics / Electrification
    "SU.PA",         # Schneider Electric - FR, Energiemanagement / IoT
    "ENR.DE",        # Siemens Energy - DE, Energiewende
    "VWS.CO",        # Vestas Wind - DK, Windenergie
]

# Yahoo Finance Ticker Map
# Da wir hier direkt YF-Ticker als UNIVERSE verwenden, ist die Map 1:1
YAHOO_MAP = {ticker: ticker for ticker in UNIVERSE}
# Korrekturen fuer Sonderzeichen / Abweichungen:
YAHOO_MAP["HENSOLDT.DE"] = "HAG.DE"  # Hensoldt AG an der XETRA

# Epic fuer Regime-Filter: NASDAQ 100 (tech-lastig, passt zum Universe)
REGIME_EPIC      = "^NDX"
REGIME_MA_PERIOD = 200

# ─ SCORING WEIGHTS ───────────────────────────────────────────────────────────
WEIGHTS = {
    "mom_3m":  0.25,  # 3-Monats-Momentum
    "mom_6m":  0.25,  # 6-Monats-Momentum
    "mom_12m": 0.30,  # 12-Monats-Momentum
    "hi52w":   0.20,  # Naehe zum 52-Wochen-Hoch
}

# ─ BOT PARAMETERS ──────────────────────────────────────────────────────────────
TOP_N_SIGNALS       = 7     # Top 7 Buy + Top 7 Exit im Report
MAX_POSITIONS       = 5     # max. gleichzeitige Positionen
RISK_PER_TRADE_PCT  = 0.01  # 1% Account-Risiko pro Trade
STOP_LOSS_PCT       = 0.02  # 2% Stop-Loss
DAILY_LOSS_LIMIT_PCT= 0.05  # Kill-Switch bei 5% Tagesverlust

# ─ FILE PATHS ───────────────────────────────────────────────────────────────────
LOG_FILE    = "logs/momentum_bot.log"
REPORT_FILE = "reports/daily_report.md"
