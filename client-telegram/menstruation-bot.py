from datetime import date
import emoji
import json
import locale
import os
import re
import requests
import sys
import telepot

ENDPOINT = "http://127.0.0.1:5000"

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

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


def menu_str(json_object, options):
    lines = []
    for group in json_object["groups"]:
        lines.append("*{}*".format(group["name"].upper()))
        for meal in group["meals"]:
            if "colors" not in options or meal["color"] in options["colors"]:
                if "tags" not in options or options["tags"] & set(meal["tags"]):
                    if meal["price"]["student"] <= options["max"]:
                        lines.append(r"{color} \[{price}] _{name}_ {tags}".format(
                            color=tag_emoji[meal["color"]],
                            price=locale.currency(meal["price"]["student"]),
                            name=meal["name"],
                            tags="".join(tag_emoji[tag] for tag in meal["tags"])
                        ))
        lines.append("")
    return "\n".join(lines)


def handle(msg):
    content_type, _, chat_id = telepot.glance(msg)
    if content_type == "text" and msg["text"].startswith("/menstruate"):
        text = emoji.demojize(msg["text"])

        options = {}
        maximum_price_result = re.search(r"(\d+)\s?€", text)
        options["max"] = float(maximum_price_result.group(1) if maximum_price_result else "inf")
        colors_result = re.search(r"(:green_heart:|:yellow_heart:|:red_heart:)", text)
        if colors_result:
            print(colors_result.groups())
            options["colors"] = set(emoji_tag[emoji] for emoji in colors_result.groups())
        tags_result = re.search(r"(:carrot:|:seedling:|:smiling_face_with_halo:|:fish:|:globe_showing_Americas:)", text)
        if tags_result:
            options["tags"] = set(emoji_tag[emoji] for emoji in tags_result.groups())

        json_object = json.loads(requests.get(ENDPOINT + "/{}/{}".format(191, date.today())).text)
        reply = emoji.emojize(menu_str(json_object, options))
        bot.sendMessage(chat_id, reply, parse_mode='Markdown')


if __name__ == "__main__":
    if "MENSTRUATION_TOKEN" not in os.environ:
        print("Please specify bot token in $MENSTRUATION_TOKEN.", file=sys.stderr)
        sys.exit(1)
    TOKEN = os.environ["MENSTRUATION_TOKEN"]
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle, run_forever=True)
