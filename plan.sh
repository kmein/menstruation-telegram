#!/usr/bin/env nix-shell
#!nix-shell -i bash -p xpdf
TMP=/tmp
PDF=aktuelle_woche_de.pdf
URL="https://www.stw.berlin/assets/speiseplaene/191/$PDF"

wget --quiet --directory-prefix="$TMP" "$URL"
pdftotext "$TMP/$PDF" - | iconv --from-code=ISO-8859-1 --to-code=UTF-8
