from bs4 import BeautifulSoup
from datetime import date, datetime
from enum import Enum
from itertools import tee, filterfalse
from typing import *
import json
import re
import requests

DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}

A = TypeVar("A")
def partition(pred: Callable[[A], bool], iterable: Iterable[A]) -> Tuple[Iterator[A], Iterator[A]]:
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)

def meals_html_for_day(mensa_code: int, date: date) -> str:
    return requests.post(
        "https://www.stw.berlin/xhr/speiseplan-wochentag.html",
        headers=DEFAULT_HEADERS,
        data={
            "week": "now",
            "date": date.isoformat(),
            "resources_id": mensa_code,
        }).text

def icon_to_tag(icon: str) -> str:
    return {
        "/vendor/infomax/mensen/icons/1.png": "vegetarian",
        "/vendor/infomax/mensen/icons/15.png": "vegan",
        "/vendor/infomax/mensen/icons/18.png": "organic",
        "/vendor/infomax/mensen/icons/38.png": "sustainable fishing",
        "/vendor/infomax/mensen/icons/43.png": "climate",
        "/vendor/infomax/mensen/icons/ampel_gelb_70x65.png": "yellow",
        "/vendor/infomax/mensen/icons/ampel_gruen_70x65.png": "green",
        "/vendor/infomax/mensen/icons/ampel_rot_70x65.png": "red",
    }[icon]

def extract_meals(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    groups = []
    for group in soup.find_all(class_="splGroupWrapper"):
        group_name = group.find(class_="splGroup").text.strip()
        meals = []
        for meal in group.find_all(class_="splMeal"):
            icons = [img["src"] for img in meal.find_all("img", class_="splIcon")]
            tag_icons, color_icons = partition(lambda x: "ampel" in x, icons)
            meal_name = meal.find("span", class_="bold").text.strip()
            student, employee, guest = (
                float(price)
                for price
                in meal.find("div", class_="text-right").text.replace("€ ", "").replace(",", ".").split("/")
            )
            allergen_matches = re.search("\((.*)\)", meal.find(class_="toolt").text)
            if allergen_matches:
                allergens = allergen_matches.group(1).split(", ")
            else:
                allergens = []
            meals.append({
                "name": meal_name,
                "color": icon_to_tag(next(color_icons)),
                "tags": [icon_to_tag(tag_icon) for tag_icon in tag_icons],
                "price": {
                    "student": student,
                    "employee": employee,
                    "guest": guest,
                },
                "allergens": allergens,
            })
        groups.append({
            "name": group_name,
            "meals": meals,
        })
    return {"groups": groups}

def meals(mensa_code: int, date: date) -> Dict[str, Any]:
    return extract_meals(meals_html_for_day(mensa_code, date))

###

from flask import Flask, jsonify
app = Flask(__name__)

app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

@app.route("/codes")
def list_codes():
    html = requests.get("https://www.stw.berlin/mensen.html", headers=DEFAULT_HEADERS).text
    soup = BeautifulSoup(html, "html.parser")
    unis = []
    for uni in soup.find(id="itemsHochschulen").find_all(class_="container-fluid"):
        name = uni.find("h4").text.strip()
        mensas = []
        for mensa in uni.find_all(class_=["row", "row-top-percent-1", "ptr"], onclick=True):
            code = mensa["onclick"][9:12]
            address = re.sub("\s+", " ", mensa.find(class_="addrcard").text.strip().replace("\n", " /"))
            mensas.append({"code": code, "address": address})
        unis.append({"name": name, "mensas": mensas})
    return jsonify({"unis": unis})

@app.route("/<mensa_code>", defaults={"isodate": date.today().isoformat()})
@app.route("/<mensa_code>/<isodate>")
def get_date(mensa_code, isodate):
    date = datetime.strptime(isodate, "%Y-%m-%d")
    return jsonify(meals(mensa_code, date))
