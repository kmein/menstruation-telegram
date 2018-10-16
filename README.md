# menstruation
Schluss mit Frustration! _Regel_ dein Essen mit `menstruation`!

Stell dir vor, du möchtest wissen, was es heute in deiner HU-Mensa gibt. Du möchtest
aber

* weder die Wochenplan-PDF herunterladen müssen,
* noch die miserabel designte Webseite des Studentenwerks aufrufen,
* noch Fleisch essen,
* noch mehr als 3 € bezahlen.

Unmöglich? Denkste!
All das ist nun bloß _einen_ Befehl entfernt! (Und im Terminal sogar bunt!)

```bash
$ menstruate --vegetarian --max 3
       VORSPEISEN
2,95 € Wraps Variationen (vegetarian)

       SALATE
1,75 € Große Salatschale (vegan)
1,05 € Kleiner Rohkostsalat (vegan)
0,65 € Kleine Salatschale (vegan)

       SUPPEN
0,60 € Champignoncremesuppe (vegetarian)

       AKTIONEN
2,45 € Ein Germknödel mit Pflaumenmusfüllung, Mohnzucker und Vanillesauce (vegetarian)

       ESSEN
1,90 € Buchweizenpfanne mit Porree, Karotten, Rosinen und Erdnusssauce (vegan, climate)
1,45 € Tiroler Kaiserschmarrn mit Rosinen und Apfelkompott (vegetarian)

       BEILAGEN
0,60 € Paprika-Mais-Gemüse (vegan)
0,60 € Mangold in Rahm (vegetarian)
0,60 € Salzkartoffeln (vegan)
0,60 € Olivenreis (vegan)
0,30 € Knoblauchmayonnaise (vegetarian)

       DESSERTS
0,65 € Joghurt mit Früchten (vegetarian)
0,65 € Quarkspeise (vegetarian)
0,65 € Pudding (vegetarian)
0,60 € Obstkompott (vegan)
```

## server

```bash
pip install -r server/requirements.txt
FLASK_APP=server/backend.py flask run
```

### API-Beschreibung

* `/code` Listet alle Codes der Mensen des Studentenwerks Berlin auf.

```json
{
  "unis": [
    {
      "mensas": [
        {
          "address": "<Adresse>",
          "code": "<Code>"
        }
      ],
      "name": "<Uni-Name>"
    }
  ]
}
```

* `/<Mensa-Code>/<YYYY-MM-DD>` Gibt den Speiseplan der Mensa `<Mensa-Code>` am Tag `<YYYY-MM-DD>` zurück. Dabei ist das Datum optional, und es wird der aktuelle Speiseplan zurückgegeben.

```json
{
  "groups": [
    {
      "meals": [
        {
          "allergens": ["<Allergene>"],
          "name": "<Essensname>",
          "price": {
            "student": <Studentenpreis>,
            "employee": <Angestelltenpreis>,
            "guest": <Gästepreis>
          },
          "tags": ["<Kennzeichen>"]
        }
      ],
      "name": "<Gruppenname>"
    }
  ]
}
```

## client-cli

TODO

## To-Do
* [ ] Allergien herausfiltern
