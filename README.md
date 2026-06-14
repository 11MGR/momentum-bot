# momentum-bot

Automatisierter Momentum-Trading-Bot für das IG Demo-Konto. Tägliches Stock-Screening mit Scoring-Engine, Marktregime-Filter und Risikomanagement.

## Funktionsweise

Der Bot läuft täglich Mo–Fr um 18:00 Uhr CEST (nach EU-Börsenschluss) und:
1. Loggt sich in die IG REST API ein
2. Prüft den Marktregime-Filter (S&P 500 vs. 50-Tage-MA)
3. Lädt 260 Tage Kurshistorie für 40+ Aktien
4. Berechnet Momentum-Score (3M/6M/12M-Momentum, 52W-Hoch, relative Stärke)
5. Erstellt einen täglichen Markdown-Report mit Top-5 Kauf- und Exit-Signalen

## Projektstruktur

```
momentum-bot/
├── config.py          # Konfiguration & Scoring-Parameter
├── ig_client.py       # IG REST API Wrapper
├── scorer.py          # Momentum-Scoring-Engine
├── main.py            # Hauptablauf (täglich ausführen)
├── requirements.txt   # Python-Abhängigkeiten
├── .env.example       # Vorlage für Umgebungsvariablen
├── logs/              # Log-Dateien (auto-erstellt)
└── reports/           # Tägliche Reports (auto-erstellt)
```

## Setup (lokal)

```bash
# 1. Repository klonen
git clone https://github.com/11MGR/momentum-bot.git
cd momentum-bot

# 2. Umgebungsvariablen setzen
cp .env.example .env
# .env mit echten Werten füllen

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Bot starten
python main.py
```

## Umgebungsvariablen

Alle Credentials werden über Umgebungsvariablen gesetzt. **Niemals echte Werte committen!**

| Variable | Beschreibung |
|---|---|
| `IG_API_KEY` | IG Web API Schlüssel (Demo-Konto) |
| `IG_USERNAME` | IG Benutzername (E-Mail) |
| `IG_PASSWORD` | IG Passwort |
| `IG_ACC_TYPE` | Kontotyp: `DEMO` oder `LIVE` |
| `IG_ACC_NUMBER` | IG Kontonummer |

## Hosting

Der Bot läuft auf **Railway.app** mit Cron-Schedule `0 16 * * 1-5`.
Alle Credentials sind als Railway Service Variables hinterlegt.

## Sicherheit

- Keine Credentials im Code
- `.env` ist in `.gitignore` und wird nie committet
- Alter API Key ist deaktiviert, neuer Key nur in Railway Variables
- Repository ist **Private**

## Risikomanagement

- Max. 5 gleichzeitige Positionen
- 1% Risikobudget pro Trade
- 3% Stop-Loss pro Position
- 5% Daily-Loss-Limit mit automatischem Kill-Switch
- Regime-Filter: kein Kaufsignal bei bearishem Markt

> **Hinweis:** Dieser Bot läuft auf einem IG Demo-Konto mit virtuellem Kapital. Keine Anlageberatung.
