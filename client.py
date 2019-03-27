import json
import re
import requests
from typing import Tuple, Set, Dict
import logging
import sys
from datetime import date, datetime, timedelta

tag_emoji = {
    "vegetarian": ":carrot:",
    "vegan": ":seedling:",
    "organic": ":smiling_face_with_halo:",
    "sustainable fishing": ":fish:",
    "climate friendly": ":globe_showing_Americas:",
    "yellow": ":yellow_heart:",
    "green": ":green_heart:",
    "red": ":red_heart:",
}

emoji_tag = {emoji: tag for tag, emoji in tag_emoji.items()}


def render_cents(total_cents):
    euros = total_cents // 100
    cents = total_cents % 100
    return r"{},{:2} €".format(euros, cents)


def render_meal(meal):
    return "{color}{price} _{name}_ {tags}".format(
        color=tag_emoji[meal["color"]],
        price=r" \[{}]".format(render_cents(meal["price"]["student"]))
        if meal["price"]
        else "",
        name=meal["name"],
        tags="".join(tag_emoji[tag] for tag in meal["tags"]),
    )


def render_group(group):
    if group["items"]:
        return "*{name}*\n{meals}\n\n".format(
            name=group["name"].upper(),
            meals="\n".join(render_meal(meal) for meal in group["items"]),
        )
    else:
        return ""


def extract_query(text: str) -> Tuple[int, Set[str], Set[str]]:
    max_price_result = re.search(r"(\d+,?\d*)\s?€", text)
    max_price = (
        int(float(max_price_result.group(1).replace(",", ".")) * 100)
        if max_price_result
        else sys.maxsize
    )

    colors = set(
        emoji_tag[emoji]
        for emoji in re.findall(r"(:green_heart:|:yellow_heart:|:red_heart:)", text)
    )
    tags = set(
        emoji_tag[emoji]
        for emoji in re.findall(
            r"(:carrot:|:seedling:|:smiling_face_with_halo:|:fish:|:globe_showing_Americas:)",
            text,
        )
    )

    logging.info('Extracted {} from "{}"'.format((max_price, colors, tags), text))
    return max_price, colors, tags


def extract_date(text: str) -> date:
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
        logging.info("Malformed date in '{}', defaulting to today".format(text))
        return date.today()


def get_json(
    endpoint: str, mensa_code: int, date: date, query: Tuple[int, Set[str], Set[str]]
) -> dict:
    max_price, colors, tags = query
    request_url = "{}/menu".format(endpoint)
    response = requests.get(
        request_url,
        params={
            "mensa": str(mensa_code),
            "date": date.isoformat(),
            "max_price": str(max_price),
            "tag": tags,
            "color": colors,
        },
    )
    logging.info("Requesting {}".format(response.url))
    return response.json()


def get_mensas(endpoint: str) -> Dict[int, str]:
    request_url = "{}/codes".format(endpoint)
    logging.info("Requesting {}".format(request_url))
    json_object = requests.get(request_url).json()
    code_name = dict()
    for uni in json_object:
        for mensa in uni["items"]:
            if "Coffeebar" not in mensa["name"]:
                code_name[mensa["code"]] = mensa["name"]
    return code_name
