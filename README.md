# menstruation
Schluss mit Frustration, _regel_ dein Essen mit `menstruation`!

## Beispiel

Stell dir vor, du möchtest wissen, was es heute in der Mensa gibt. Du möchtest
aber weder

* die Wochenplan-PDF herunterladen müssen, noch
* die miserabel designte Webseite des Studentenwerks aufrufen, noch
* Fleisch essen, noch
* mehr als 3 € bezahlen.

Was lange als unmöglich galt, ist nun bloß einen Befehl entfernt!

```bash
$ ./menstruate student --vegetarian --max 3
         VORSPEISEN
2,95 EUR Wraps Variationen (vegetarian)

         SALATE
1,75 EUR Große Salatschale (vegan)
1,05 EUR Kleiner Rohkostsalat (vegan)
0,65 EUR Kleine Salatschale (vegan)

         SUPPEN
0,60 EUR Vegane Cremesuppe mit Gartengemüse (vegan)

         AKTIONEN
2,45 EUR Tomatensauce mit Artischocken an Nudelauswahl (vegan)
0,70 EUR Ein Eierpfannkuchen mit Apfelmus (vegetarian)

         ESSEN
2,10 EUR Sonnenweizen mit frischer Zucchini, Paprika, und Karotten (vegan, climate)
1,55 EUR Zwei Schwarzwurzelmedaillons an Curry-Mango-Sauce (vegetarian)
1,55 EUR Ein Kürbis-Chiasamen-Bratling an Curry-Mango-Sauce (vegan)

         BEILAGEN
0,60 EUR Romanesco (vegan)
0,65 EUR Spiralnudeln (organic, vegan)
0,65 EUR Grüne Bohnen (organic, vegan)
0,60 EUR Salzkartoffeln (vegan)
0,60 EUR Parboiledreis (vegan)
0,30 EUR Joghurt-Limonen-Dip (vegetarian)
0,30 EUR Curry-Mango-Sauce (vegan)

         DESSERTS
0,65 EUR Aprikosenjoghurt (vegetarian)
0,65 EUR Johannisbeerquark (vegetarian)
0,65 EUR Pistazienpudding (vegetarian)
0,60 EUR Obstkompott (vegan)
```

Im Terminal sind die Angebote darüber hinaus gemäß der Lebensmittelampel eingefärbt.

## Voraussetzungen
* [GDOM](https://github.com/syrusakbary/gdom)
* [termcolor](https://pypi.org/pypi/termcolor)
* [`jq`](https://stedolan.github.io/jq/)
