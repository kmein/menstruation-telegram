from datetime import date, datetime, timedelta
from enum import Enum
from typing import Set, Dict, List, Union, Optional
import logging
import re
import requests
import sys


class Color(Enum):
    RED = ":red_heart:"
    GREEN = ":green_heart:"
    YELLOW = ":yellow_heart:"

    @staticmethod
    def from_text(text: str) -> "Color":
        if text == "green":
            return Color.GREEN
        elif text == "yellow":
            return Color.YELLOW
        elif text == "red":
            return Color.RED
        else:
            raise ValueError(f"{text} is no valid color")

    def __str__(self: "Color") -> str:
        if self == Color.GREEN:
            return "green"
        elif self == Color.YELLOW:
            return "yellow"
        elif self == Color.RED:
            return "red"
        else:
            raise ValueError("unreachable")


class Tag(Enum):
    VEGETARIAN = ":carrot:"
    VEGAN = ":seedling:"
    ORGANIC = ":smiling_face_with_halo:"
    SUSTAINABLE_FISHING = ":fish:"
    CLIMATE_FRIENDLY = ":globe_showing_Americas:"

    @staticmethod
    def from_text(text: str) -> "Tag":
        if text == "vegetarian":
            return Tag.VEGETARIAN
        elif text == "vegan":
            return Tag.VEGAN
        elif text == "organic":
            return Tag.ORGANIC
        elif text == "sustainable fishing":
            return Tag.SUSTAINABLE_FISHING
        elif text == "climate friendly":
            return Tag.CLIMATE_FRIENDLY
        else:
            raise ValueError(f"{text} is no valid tag")

    def __str__(self: "Tag") -> str:
        if self == Tag.VEGETARIAN:
            return "vegetarian"
        elif self == Tag.VEGAN:
            return "vegan"
        elif self == Tag.ORGANIC:
            return "organic"
        elif self == Tag.SUSTAINABLE_FISHING:
            return "sustainable fishing"
        elif self == Tag.CLIMATE_FRIENDLY:
            return "climate friendly"
        else:
            raise ValueError("unreachable")


class Query:
    def __init__(
        self: "Query",
        max_price: Optional[int],
        colors: Set[Color],
        tags: Set[Tag],
        date: Optional[date],
    ) -> None:
        self.max_price = max_price
        self.tags: Set[Tag] = tags
        self.colors: Set[Color] = colors
        self.date = date

    def params(self: "Query") -> Dict[str, Union[str, List[str]]]:
        params = dict()
        if self.date:
            params["date"] = self.date.isoformat()
        if self.max_price:
            params["max_price"] = str(self.max_price)
        if self.tags:
            params["tag"] = [str(tag) for tag in self.tags]
        if self.colors:
            params["color"] = [str(color) for color in self.colors]
        return params

    @staticmethod
    def from_text(text: str) -> "Query":
        def extract_date(text: str) -> Optional[date]:
            matches = re.search(r"(\d{4}-\d{2}-\d{2}|today|tomorrow)", text)
            if matches:
                if matches.group(1) == "today":
                    parsed_date = date.today()
                elif matches.group(1) == "tomorrow":
                    parsed_date = date.today() + timedelta(days=1)
                elif matches.group(1):
                    parsed_date = datetime.strptime(matches.group(1), "%Y-%m-%d").date()
                logging.info('Extracted {} from "{}"'.format(parsed_date, text))
                return parsed_date
            else:
                logging.info("Malformed date in '{}'".format(text))
                return None

        max_price_result = re.search(r"(\d+,?\d*)\s?€", text)
        # logging.info('Extracted {} from "{}"'.format((max_price, colors, tags), text))

        return Query(
            max_price=(
                int(float(max_price_result.group(1).replace(",", ".")) * 100)
                if max_price_result
                else None
            ),
            colors=set(
                Color(emoji)
                for emoji in re.findall(
                    r"(:green_heart:|:yellow_heart:|:red_heart:)", text
                )
            ),
            tags=set(
                Tag(emoji)
                for emoji in re.findall(
                    r"(:carrot:|:seedling:|:smiling_face_with_halo:|:fish:|:globe_showing_Americas:)",
                    text,
                )
            ),
            date=extract_date(text),
        )


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
    logging.info("Requesting {}".format(response.url))
    return response.json()


def get_mensas(endpoint: str, pattern: str = "") -> Dict[int, str]:
    response = requests.get(f"{endpoint}/codes", params={"pattern": pattern})
    logging.info("Requesting {}".format(response.url))
    code_name = dict()
    for uni in response.json():
        for mensa in uni["items"]:
            if "Coffeebar" not in mensa["name"]:
                code_name[mensa["code"]] = mensa["name"]
    return code_name
