import logging
from typing import Dict

import requests
from cachetools import cached, TTLCache

from menstruation.query import Color, Tag, Query


def render_cents(total_cents: int):
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


@cached(cache=TTLCache(maxsize=512, ttl=450))
def get_json_cached(url: str):
    response = requests.get(url=url)
    logging.debug(f"Requesting {response.url}, status_code: {response.status_code}")
    return response.json()


def get_json(endpoint: str, mensa_code: int, query: Query) -> dict:
    url = f"{endpoint}/menu"
    request = requests.Request(
        "GET", url, params=dict(mensa=str(mensa_code), **query.params())
    ).prepare()
    return get_json_cached(request.url or url)


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def get_allergens(endpoint: str) -> Dict[str, str]:
    response = requests.get(f"{endpoint}/allergens")
    logging.debug(f"Requesting {response.url}")
    number_name = dict()
    for allergen in response.json()["items"]:
        number = (
            f"{allergen['number']}"
            f"{allergen['index'] if allergen['index'] is not None else ''}"
        )
        number_name[number] = allergen["name"]
    return number_name


@cached(cache=TTLCache(maxsize=64, ttl=3600))
def get_mensas(endpoint: str, pattern: str = "") -> Dict[int, str]:
    response = requests.get(f"{endpoint}/codes", params={"pattern": pattern})
    logging.debug(f"Requesting {response.url}")
    code_name = dict()
    for uni in response.json():
        for mensa in uni["items"]:
            if "Coffeebar" not in mensa["name"]:
                code_name[mensa["code"]] = mensa["name"]
    return code_name
