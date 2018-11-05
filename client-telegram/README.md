# Menstruation Telegram Bot

## Nächste Schritte

1. Benutzerfreundlichkeit
  - Ausführlichere Hilfetexte
  - Klarere Anleitung
2. Benutzereinstellungen
  - Mensawahl
  - Suchparameter
  - Persistenz via [`ConfigParser`](https://docs.python.org/3/library/configparser.html)

    ```ini
    [chat_id]
    preferred_mensa = 191
    default_max_price = 3 €
    default_colors = green,yellow
    default_tags = vegan
    ```
3. Support für alle Mensen des Studentenwerkes (s. `/codes`)
  - Dialog zur Mensawahl
