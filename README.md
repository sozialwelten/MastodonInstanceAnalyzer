# Mastodon Instance Analyzer

Ein Python CLI-Tool zur Analyse von Mastodon-Instanzen. Erstellt detaillierte Statistiken über Accounts, Aktivitäten und Vernetzung.
Funktioniert am besten mit ADMIN-Token

## 📊 Features

- **Instanz-Informationen**: Name, Version, Nutzer-, Post- und Föderations-Statistiken
- **Aktivitätsanalyse**: Wöchentliche Statistiken über Logins, Posts und Registrierungen
- **Account-Statistiken**: 
  - Lokale vs. Remote Accounts
  - Aktivitätsanalyse (30/90 Tage)
  - Post-Verteilung pro Account
  - Top 10 aktivste Poster
- **Timeline-Analyse**: Medien, Content Warnings, Replies, Boosts (optional)
- **Export-Formate**: Text und JSON

## 🚀 Installation

### Voraussetzungen

- Python 3.7 oder höher
- pip (Python Package Manager)

### Abhängigkeiten installieren

```bash
pip install requests
```

### Tool herunterladen

```bash
# Repository klonen
git clone https://github.com/yourusername/mastodon-instance-analyzer.git
cd mastodon-instance-analyzer

# Script ausführbar machen (Linux/Mac)
chmod +x MastodonInstanceAnalyzer.py
```

## 📖 Verwendung

### Basis-Analyse (ohne Token)

Grundlegende Instanz-Informationen abrufen:

```bash
python MastodonInstanceAnalyzer.py https://ihre-instanz.de
```

### Vollständige Analyse (mit Admin-Token)

Für detaillierte Account-Statistiken benötigen Sie einen Admin-Token:

```bash
python MastodonInstanceAnalyzer.py https://ihre-instanz.de --token IHR_ADMIN_TOKEN
```

### Ausgabe in Datei speichern

```bash
python MastodonInstanceAnalyzer.py https://ihre-instanz.de --token IHR_TOKEN --output report.txt
```

### JSON-Export

```bash
python MastodonInstanceAnalyzer.py https://ihre-instanz.de --token IHR_TOKEN --format json > report.json
```

## 🔑 Admin-Token erstellen

Für vollständige Account-Statistiken benötigen Sie einen Admin-Token mit entsprechenden Berechtigungen:

1. In Ihrer Mastodon-Instanz einloggen
2. **Einstellungen** → **Entwicklung** → **Neue Anwendung**
3. Anwendungsname: z.B. "Instance Analyzer"
4. Erforderliche Berechtigungen auswählen:
   - `admin:read:accounts` (für Account-Statistiken)
   - `read:statuses` (optional, für Timeline-Analyse)
5. **Absenden** klicken
6. Token kopieren und sicher aufbewahren

⚠️ **Wichtig**: Behandeln Sie den Admin-Token wie ein Passwort und teilen Sie ihn niemals öffentlich!

## 📋 Beispiel-Ausgabe

```
======================================================================
MASTODON INSTANZ ANALYSE: https://ihre-instanz.de
======================================================================

📊 INSTANZ-INFORMATIONEN
----------------------------------------------------------------------
Name:        Ihre Mastodon Instanz
Version:     4.5.0
Beschreibung: Eine freundliche Community...
Nutzer:      49
Posts:       20,690
Domains:     27,612

📈 AKTIVITÄT (12 WOCHEN)
----------------------------------------------------------------------
2025-KW44 (04.11.): 4 Logins, 2 Posts, 0 Registrierungen
2025-KW43 (28.10.): 15 Logins, 77 Posts, 0 Registrierungen
2025-KW42 (21.10.): 15 Logins, 86 Posts, 0 Registrierungen

👥 ACCOUNT-STATISTIKEN
----------------------------------------------------------------------
Gesamt:           49
Lokal:            49
Remote:           0
Aktiv (30 Tage): 13
Aktiv (90 Tage): 18
Inaktiv:          31
Mit Posts:        37
Ohne Posts:       12

📝 POSTS PRO ACCOUNT
----------------------------------------------------------------------
         0 Posts: 12 Accounts
      1-10 Posts: 8 Accounts
     11-50 Posts: 9 Accounts
    51-100 Posts: 6 Accounts
   101-500 Posts: 9 Accounts
      500+ Posts: 5 Accounts

🏆 TOP 10 POSTER
----------------------------------------------------------------------
 1. @username1           1,234 Posts (zuletzt: 2025-11-05)
 2. @username2             987 Posts (zuletzt: 2025-11-03)
 ...
```

## 📚 Erklärung der Metriken

### Instanz-Informationen

- **Nutzer**: Gesamtzahl aller registrierten Accounts (lokal + remote)
- **Posts**: Gesamtzahl aller Posts auf der Instanz
- **Domains**: Anzahl föderierter Instanzen (zeigt Vernetzung im Fediverse)

### Aktivität

- **Logins**: Anzahl der Anmeldungen in der jeweiligen Woche
- **Posts**: Neu erstellte Posts in der Woche
- **Registrierungen**: Neue Account-Registrierungen

### Account-Statistiken

- **Lokal**: Auf Ihrer Instanz registrierte Accounts
- **Remote**: Von anderen Instanzen bekannte Accounts
- **Aktiv (30/90 Tage)**: Accounts mit mindestens einem Post im Zeitraum
- **Inaktiv**: Accounts ohne Posts im letzten Quartal

## 🛠️ Kommandozeilen-Optionen

```
usage: MastodonInstanceAnalyzer.py [-h] [--token TOKEN] [--format {text,json}] 
                                    [--output OUTPUT] instance

positional arguments:
  instance              URL der Mastodon-Instanz (z.B. https://mastodon.social)

optional arguments:
  -h, --help            Zeigt diese Hilfe an
  --token TOKEN, -t TOKEN
                        Access Token (optional, empfohlen für Admin-Features)
  --format {text,json}, -f {text,json}
                        Output-Format (default: text)
  --output OUTPUT, -o OUTPUT
                        Ausgabe-Datei (optional)
```

## 🔒 Datenschutz & Sicherheit

- Das Tool greift nur lesend auf die Mastodon-API zu
- Keine Daten werden an Dritte übermittelt
- Admin-Token werden nicht gespeichert
- Empfehlung: Token nach Verwendung widerrufen oder mit minimalen Berechtigungen erstellen

## 📄 Lizenz

GNU General Public License v3.0 

## 👤 Autor

**Michael Karbacher**