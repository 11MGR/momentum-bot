# momentum-bot

Automatisierter Momentum-Trading-Bot für das IG Demo-Konto. Tägliches Stock-Screening mit Scoring-Engine, Marktregime-Filter und Risikomanagement.

[![Live Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://11mgr.github.io/momentum-bot/)

## Live Dashboard

**https://11mgr.github.io/momentum-bot/**

Das öffentliche Dashboard zeigt täglich aktualisierte Momentum-Signale:
- Top Buy-Signale (Thematisches Universe)
- Broad Universe Screening
- Exit / Avoid Signale

Die Daten werden automatisch täglich Mo–Fr nach Börsenschluss aktualisiert.

## Funktionsweise

Der Bot läuft täglich Mo–Fr um 18:00 Uhr CEST (nach EU-Börsenschluss) und:

1. Loggt sich in die IG REST API ein
2. Prüft den Marktregime-Filter (S&P 500 vs. 50-Tage-MA)
3. Lädt 260 Tage Kurshistorie für 40+ Aktien
4. Berechnet Momentum-Score (3M/6M/12M-Momentum, 52W-Hoch, relative Stärke)
5. Erstellt einen täglichen Markdown-Report mit Top-5 Kauf- und Exit-Signalen
6. Aktualisiert das öffentliche Dashboard unter GitHub Pages

## Projektstruktur

```
momentum-bot/
├── config.py           # Konfiguration & Scoring-Parameter
├── ig_client.py        # IG REST API Wrapper
├── scorer.py           # Momentum-Scoring-Engine
├── main.py             # Hauptablauf (täglich ausführen)
├── requirements.txt    # Python-Abhängigkeiten
├── .env.example        # Vorlage für Umgebungsvariablen
├── docs/
│   └── index.html      # GitHub Pages Dashboard
├── logs/               # Log-Dateien (auto-erstellt)
└── reports/            # Tägliche Reports (auto-erstellt)
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

| Variable | Beschreibung |
|---|---|
| `IG_API_KEY` | IG REST API Key |
| `IG_USERNAME` | IG Benutzername / E-Mail |
| `IG_PASSWORD` | IG Passwort |
| `IG_ACC_TYPE` | `DEMO` oder `LIVE` |
| `IG_ACC_NUMBER` | IG Kontonummer |

> **Wichtig:** Niemals echte Credentials in den Code oder ins Repository committen. Alle Werte werden über Umgebungsvariablen gesetzt (Railway > Variables).

## Hosting

| Komponente | Plattform | Details |
|---|---|---|
| Bot (Ausführung) | Railway.app | Cron: `0 16 * * 1-5` (18:00 CEST) |
| Dashboard | GitHub Pages | https://11mgr.github.io/momentum-bot/ |

## Sicherheit

- Keine Credentials im Code – ausschließlich `os.getenv()`
- `.env` ist in `.gitignore` eingetragen und wird nie committet
- Secret Protection (GitHub Secret Scanning) aktiv
- Dependabot alerts & security updates aktiv
- Repository ist öffentlich – der Code enthält keine sensiblen Daten

## Risikomanagement

- Max. 5 gleichzeitige Positionen
- 1% Risiko pro Trade
- 3% Stop-Loss
- 5% Daily-Loss-Limit mit automatischem Kill-Switch
- Marktregime-Filter gegen bearishe Märkte

---

> **Hinweis:** Dieser Bot läuft auf einem IG Demo-Konto mit virtuellem Kapital. Keine Anlageberatung.
