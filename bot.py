#!/usr/bin/env python3
from datetime import datetime, timedelta
from emoji import emojize, demojize
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import Updater
from telegram.ext.filters import Filters
import configparser
import logging
import os
import random
import schedule
import sys
import threading
import time

import client

try:
    ENDPOINT = os.environ["MENSTRUATION_ENDPOINT"]
    if not ENDPOINT:
        raise KeyError
except KeyError:
    ENDPOINT = "http://127.0.0.1:80"

if "MENSTRUATION_DIR" not in os.environ:
    print(
        "Please specify configuration directory in variable MENSTRUATION_DIR.",
        file=sys.stderr,
    )
    sys.exit(1)
CONFIGURATION_DIRECTORY = os.environ["MENSTRUATION_DIR"].strip()

CONFIGURATION_FILE = os.path.join(CONFIGURATION_DIRECTORY, "config.ini")

config = configparser.ConfigParser()
config.read(CONFIGURATION_FILE)

logging.basicConfig(level=logging.DEBUG)


def help_handler(bot, update):
    def infos(mapping):
        return "\n".join(k + " – " + v for k, v in mapping.items())

    command_description = {
        "/menu :seedling: 3€": "Heutige Speiseangebote (vegan bis 3€).",
        "/menu tomorrow": "Morgige Speiseangebote.",
        "/menu 2018-10-22": "Speiseangebote für den 22.10.2018.",
        "/help": "Dieser Hilfetext.",
        "/mensa beuth": "Auswahlmenü für die Mensen der Beuth Hochschule.",
    }
    emoji_description = {
        ":carrot:": "vegetarisch",
        ":seedling:": "vegan",
        ":smiling_face_with_halo:": "Bio",
        ":fish:": "nachhaltig gefischt",
        ":globe_showing_Americas:": "klimafreundlich",
        ":yellow_heart:": "Lebensmittelampel gelb",
        ":green_heart:": "Lebensmittelampel grün",
        ":red_heart:": "Lebensmittelampel rot",
    }
    bot.send_message(
        update.message.chat_id,
        emojize(
            "*BEFEHLE*\n{}\n\n*LEGENDE*\n{}".format(
                infos(command_description), infos(emoji_description)
            )
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


def menu_handler(bot, update, args):
    text = demojize("".join(args))
    max_price, colors, tags = client.extract_query(text)
    menstru_date = client.extract_date(text)

    try:
        json_object = client.get_json(
            ENDPOINT,
            config.get(str(update.message.from_user.id), "mensa"),
            menstru_date,
        )
    except configparser.NoSectionError as e:
        logging.warning(e)
        bot.send_message(
            update.message.chat_id,
            emojize(
                "Wie es aussieht, hast Du noch keine Mensa ausgewählt. {}\nTu dies zum Beispiel mit „/mensa adlershof“ :information:".format(
                    error_emoji()
                )
            ),
        )
        return
    except ValueError as e:
        logging.warning(e)
        bot.send_message(
            update.message.chat_id,
            emojize(
                "Entweder ist diese Mensa noch nicht unterstützt, {}\noder es gibt an diesem dort Tag kein Essen. {}".format(
                    error_emoji(), error_emoji()
                )
            ),
        )
        return

    reply = "".join(
        client.render_group(client.filter_meals(group, max_price, colors, tags))
        for group in json_object["groups"]
    )
    if reply:
        bot.send_message(
            update.message.chat_id, emojize(reply), parse_mode=ParseMode.MARKDOWN
        )
    else:
        bot.send_message(
            update.message.chat_id,
            emojize("Kein Essen gefunden. {}".format(error_emoji())),
        )


def mensa_handler(bot, update, args):
    text = " ".join(args)
    code_address = client.get_mensas(ENDPOINT)
    pattern = text.strip()
    mensa_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=address, callback_data=code)]
            for code, address in sorted(code_address.items(), key=lambda item: item[1])
            if pattern.lower() in address.lower()
        ]
    )
    bot.send_message(
        update.message.chat_id,
        emojize("Wähle Deine Mensa aus. :index_pointing_up:"),
        reply_markup=mensa_chooser,
    )


def mensa_callback_handler(bot, update):
    query = update.callback_query
    if query:
        section = str(query.from_user.id)
        if not config.has_section(section):
            config.add_section(section)
            logging.info("Created new config section: {}".format(section))
        address = client.get_mensas(ENDPOINT)[query.data]
        bot.answer_callback_query(
            query.id,
            text=emojize("„{}“ ausgewählt. :heavy_check_mark:".format(address)),
        )
        config.set(section, "mensa", query.data)
        with open(CONFIGURATION_FILE, "w") as ini:
            config.write(ini)
        logging.info("Set {}.mensa to {}".format(section, query.data))


def subscribe_handler(bot, update):
    section = str(update.message.from_user.id)
    if not config.has_section(section):
        config.add_section(section)
        logging.info("Created new config section: {}".format(section))
    already_subscribed = config.getboolean(section, "subscribed", fallback=False)
    if already_subscribed:
        bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan schon abonniert."
        )
    else:
        config.set(section, "subscribed", "yes")
        schedule.every().day.at("9:00").tag([update.message.from_user.id]).do(
            lambda: menu_handler(bot, update, [])
        )
        bot.send_message(
            update.message.chat_id,
            "Du bekommst ab jetzt täglich den Speiseplan zugeschickt.",
        )


def unsubscribe_handler(bot, update):
    section = str(update.message.from_user.id)
    if not config.has_section(section):
        config.add_section(section)
        logging.info("Created new config section: {}".format(section))
    already_subscribed = config.getboolean(section, "subscribed", fallback=False)
    if already_subscribed:
        config.set(section, "subscribed", False)
        schedule.clear(tag=update.message.from_user.id)
        bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan erfolgreich abbestellt."
        )
    else:
        bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan gar nicht abonniert."
        )


def error_emoji():
    return random.choice(
        [
            ":confused_face:",
            ":worried_face:",
            ":slightly_frowning_face:",
            ":frowning_face:",
            ":face_with_open_mouth:",
            ":hushed_face:",
            ":astonished_face:",
            ":flushed_face:",
            ":pleading_face:",
            ":frowning_face_with_open_mouth:",
            ":anguished_face:",
            ":fearful_face:",
            ":anxious_face_with_sweat:",
            ":sad_but_relieved_face:",
            ":crying_face:",
            ":loudly_crying_face:",
            ":face_screaming_in_fear:",
            ":confounded_face:",
            ":persevering_face:",
            ":disappointed_face:",
            ":downcast_face_with_sweat:",
            ":weary_face:",
            ":tired_face:",
        ]
    )


if __name__ == "__main__":
    if "MENSTRUATION_TOKEN" not in os.environ:
        print(
            "Please specify bot token in variable MENSTRUATION_TOKEN.", file=sys.stderr
        )
        sys.exit(1)
    TOKEN = os.environ["MENSTRUATION_TOKEN"].strip()

    bot = Updater(token=TOKEN)
    bot.dispatcher.add_handler(CommandHandler("help", help_handler))
    bot.dispatcher.add_handler(CommandHandler("start", help_handler))
    bot.dispatcher.add_handler(CommandHandler("menu", menu_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("mensa", mensa_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("subscribe", subscribe_handler))
    bot.dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
    bot.dispatcher.add_handler(CallbackQueryHandler(mensa_callback_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.command, help_handler))

    def run_subscriptions():
        while True:
            schedule.run_pending()
            time.sleep(1)

    cron = threading.Thread(target=run_subscriptions)
    telegram_bot = threading.Thread(target=bot.start_polling)

    cron.start()
    telegram_bot.start()