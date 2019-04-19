[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b40b44056d1947708ae636f5fcfe750a)](https://app.codacy.com/app/kmein/menstruation-telegram?utm_source=github.com&utm_medium=referral&utm_content=kmein/menstruation-telegram&utm_campaign=Badge_Grade_Dashboard)
# ![Menstruation. Regel dein Essen.](https://img.shields.io/badge/menstruation-Regel%20dein%20Essen.-red.svg?style=for-the-badge) [![Bot](https://img.shields.io/badge/telegram-chat-blue.svg?logo=telegram&logoColor=white&colorB=2CA5E0&style=flat-square)](https://t.me/menstruate_bot)

## Nächste Schritte

- [x] Benutzerfreundlichkeit
  - [x] Ausführlichere Hilfetexte
  - [x] Klarere Anleitung
- [ ] Benutzereinstellungen
  - [x] Mensawahl
  - [ ] Suchparameter
  - [ ] Persistenz via [`ConfigParser`](https://docs.python.org/3/library/configparser.html)

    ```ini
    [chat_id]
    mensa = 191
    max_price = 3 €
    colors = green,yellow
    tags = vegan
    ```
- [x] Support für alle Mensen des Studentenwerkes (s. `/codes`)
  - [x] Dialog zur Mensawahl
