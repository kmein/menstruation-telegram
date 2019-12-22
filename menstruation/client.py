import logging

import requests
from typing import Dict

from menstruation.query import Color, Tag, Query


def render_cents(total_cents):
    euros = total_cents // 100
    cents = total_cents % 100
    return r"{},{:2} €".format(euros, cents)


def render_meal(meal):
    return "{color}{price} _{name}_ {tags}".format(
        color=Color.from_text(meal["color"]).value,
        price=r" \[{}]".format(render_cents(meal["price"]["student"]))
        if meal["price"]
        else "",
        name=meal["name"],
        tags="".join(Tag.from_text(tag).value for tag in meal["tags"]),
    )


def render_group(group):
    if group["items"]:
        return "*{name}*\n{meals}\n\n".format(
            name=group["name"].upper(),
            meals="\n".join(render_meal(meal) for meal in group["items"]),
        )
    else:
        return ""


def get_json(endpoint: str, mensa_code: int, query: Query) -> dict:
    response = requests.get(
        f"{endpoint}/menu", params=dict(mensa=str(mensa_code), **query.params())
    )
    logging.info(f"Requesting {response.url}, status_code: {response.status_code}")
    return response.json()


def get_allergens(endpoint: str) -> Dict[str, str]:
    response = requests.get(f"{endpoint}/allergens")
    logging.info("Requesting {}".format(response.url))
    number_name = dict()
    for allergen in response.json()["items"]:
        number = "{}{}".format(
            allergen["number"],
            allergen["index"] if allergen["index"] is not None else "",
        )
        number_name[number] = allergen["name"]
    return number_name


def get_mensas(endpoint: str, pattern: str = "") -> Dict[int, str]:
    response = requests.get(f"{endpoint}/codes", params={"pattern": pattern})
    logging.info("Requesting {}".format(response.url))
    code_name = dict()
    for uni in response.json():
        for mensa in uni["items"]:
            if "Coffeebar" not in mensa["name"]:
                code_name[mensa["code"]] = mensa["name"]
    return code_name
