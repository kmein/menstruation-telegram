import json
import re
import requests
from typing import Tuple, Set, Dict
import logging
from datetime import date, datetime, timedelta

tag_emoji = {
    "vegetarian": ":carrot:",
    "vegan": ":seedling:",
    "organic": ":smiling_face_with_halo:",
    "sustainable fishing": ":fish:",
    "climate": ":globe_showing_Americas:",
    "yellow": ":yellow_heart:",
    "green": ":green_heart:",
    "red": ":red_heart:",
}

emoji_tag = {emoji: tag for tag, emoji in tag_emoji.items()}


def render_meal(meal):
    return "{color}{price} _{name}_ {tags}".format(
        color=tag_emoji[meal["color"]],
        price=r" \[{:.2f} €]".format(meal["price"]["student"]).replace(".", ",")
        if "student" in meal["price"]
        else "",
        name=meal["name"],
        tags="".join(tag_emoji[tag] for tag in meal["tags"]),
    )


def filter_meals(group, max_price, colors, tags):
    group["meals"] = [
        meal
        for meal in group["meals"]
        if (not colors or meal["color"] in colors)
        and (not tags or set(meal["tags"]) & tags)
        and ("student" not in meal["price"] or meal["price"]["student"] <= max_price)
    ]
    return group


def render_group(group):
    if group["meals"]:
        return "*{name}*\n{meals}\n\n".format(
            name=group["name"].upper(),
            meals="\n".join(render_meal(meal) for meal in group["meals"])
        )
    else:
        return ""


def extract_query(text: str) -> Tuple[float, Set[str], Set[str]]:
    max_price_result = re.search(r"(\d+)\s?€", text)
    max_price = float(max_price_result.group(1) if max_price_result else "inf")

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


def get_json(endpoint: str, mensa_code: int, date: date) -> dict:
    request_url = "{}/{}/{}".format(endpoint, mensa_code, date)
    logging.info("Requesting {}".format(request_url))
    return json.loads(requests.get(request_url).text)


def get_mensas(endpoint: str) -> Dict[str, str]:
    request_url = "{}/codes".format(endpoint)
    logging.info("Requesting {}".format(request_url))
    json_object = json.loads(requests.get(request_url).text)
    code_address = dict()
    for uni in json_object["unis"]:
        for mensa in uni["mensas"]:
            if "Coffeebar" not in mensa["address"]:
                code_address[mensa["code"]] = mensa["address"].split(" / ")[0]
    return code_address
