#!/usr/bin/env python3
from datetime import datetime, time
from emoji import emojize, demojize
from telegram import Bot, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import Updater, JobQueue
from telegram.ext.filters import Filters
from typing import List
import configparser
import logging
import os
from functools import partial
import random
import sys

from client import Query
import client

NOTIFICATION_TIME: time = datetime.strptime(
    os.environ.get("MENSTRUATION_TIME", "09:00"), "%H:%M"
).time()

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

logging.basicConfig(
    level=logging.DEBUG if "MENSTRUATION_DEBUG" in os.environ else logging.INFO
)


def help_handler(bot: Bot, update: Update):
    def infos(mapping):
        return "\n".join(k + " – " + v for k, v in mapping.items())

    command_description = {
        "/menu :seedling: 3€": "Heutige Speiseangebote (vegan bis 3€).",
        "/menu tomorrow": "Morgige Speiseangebote.",
        "/menu 2018-10-22": "Speiseangebote für den 22.10.2018.",
        "/help": "Dieser Hilfetext.",
        "/mensa beuth": "Auswahlmenü für die Mensen der Beuth Hochschule.",
        "/subscribe": "Abonniere tägliche Benachrichtigungen der Speiseangebote.",
        "/unsubscribe": "Abonnement kündigen.",
        "/allergens": "Allergene auswählen.",
        "/resetallergens": "Allergene zurücksetzen",
        "/info": "Informationen über gewählte Mensa, Abonnement und Allergene.",
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


def send_menu(bot: Bot, chat_id: int, query: Query):
    query.allergens = set(
        allergen
        for allergen in config.get(str(chat_id), "allergens", fallback="").split(",")
        if allergen != ""
    )
    logging.info(query.params())
    mensa_code = config.getint(str(chat_id), "mensa")
    json_object = client.get_json(ENDPOINT, mensa_code, query)
    reply = "".join(client.render_group(group) for group in json_object)
    if reply:
        bot.send_message(chat_id, emojize(reply), parse_mode=ParseMode.MARKDOWN)
    else:
        bot.send_message(
            chat_id, emojize("Kein Essen gefunden. {}".format(error_emoji()))
        )


def menu_handler(bot: Bot, update: Update, args: List[str]):
    text = demojize("".join(args))
    try:
        send_menu(bot, update.message.chat_id, Query.from_text(text))
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.warning(e)
        bot.send_message(
            update.message.chat_id,
            emojize(
                "Wie es aussieht, hast Du noch keine Mensa ausgewählt. {}\nTu dies zum Beispiel mit „/mensa adlershof“ :information:".format(
                    error_emoji()
                )
            ),
        )
    except ValueError as e:
        logging.warning(e)
        bot.send_message(
            update.message.chat_id,
            emojize(
                "Entweder ist diese Mensa noch nicht unterstützt, {}\noder es gibt an diesem Tag dort kein Essen. {}".format(
                    error_emoji(), error_emoji()
                )
            ),
        )


def info_handler(bot: Bot, update: Update):
    number_name = client.get_allergens(ENDPOINT)
    code_name = client.get_mensas(ENDPOINT)
    section = str(update.message.chat_id)
    myallergens = set(
        allergen
        for allergen in config.get(section, "allergens", fallback="").split(",")
        if allergen != ""
    )
    mymensa = config.getint(section, "mensa", fallback="keine")
    subscribed = config.getboolean(section, "subscribed")
    subscription_filter = config.get(section, "menu_filter", fallback="kein Filter")
    bot.send_message(
        update.message.chat_id,
        "*MENSA*\n{mensa}\n\n*ABO*\n{subscription}\n\n*ALLERGENE*\n{allergens}".format(
            mensa=code_name[mymensa] if mymensa != "keine" else "keine",
            allergens="\n".join(number_name[number] for number in myallergens),
            subscription=emojize(
                (":thumbs_up:" if subscribed else ":thumbs_down:")
                + " ({})".format(subscription_filter)
            ),
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


def allergens_handler(bot: Bot, update: Update):
    number_name = client.get_allergens(ENDPOINT)
    allergens_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"A{number}")]
            for number, name in number_name.items()
        ]
    )
    bot.send_message(
        update.message.chat_id,
        emojize("Wähle Deine Allergene aus. :index_pointing_up:"),
        reply_markup=allergens_chooser,
    )


def resetallergens_handler(bot: Bot, update: Update):
    section = str(update.message.chat_id)
    config.remove_option(section, "allergens")
    bot.send_message(
        update.message.chat_id, emojize("Allergene zurückgesetzt. :heavy_check_mark:")
    )
    with open(CONFIGURATION_FILE, "w") as ini:
        config.write(ini)


def mensa_handler(bot: Bot, update: Update, args: List[str]):
    text = " ".join(args)
    pattern = text.strip()
    code_name = client.get_mensas(ENDPOINT, pattern)
    mensa_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=code)]
            for code, name in sorted(code_name.items(), key=lambda item: item[1])
        ]
    )
    bot.send_message(
        update.message.chat_id,
        emojize("Wähle Deine Mensa aus. :index_pointing_up:"),
        reply_markup=mensa_chooser,
    )


def callback_handler(bot: Bot, update: Update):
    query = update.callback_query
    print(query)
    if query:
        section = str(query.message.chat_id)
        if not config.has_section(section):
            config.add_section(section)
            logging.info("Created new config section: {}".format(section))
        if query.data.startswith("A"):
            allergen_number = query.data.lstrip("A")
            name = client.get_allergens(ENDPOINT)[allergen_number]
            bot.answer_callback_query(
                query.id, text=emojize(f"„{name}” ausgewählt. :heavy_check_mark:")
            )
            allergens = set(
                allergen
                for allergen in config.get(section, "allergens", fallback="").split(",")
                if allergen != ""
            )
            print(allergens)
            allergens.add(allergen_number)
            print(allergens)
            config.set(section, "allergens", ",".join(allergens))
            logging.info("Set {}.allergens to {}".format(section, allergens))
        else:
            name = client.get_mensas(ENDPOINT)[int(query.data)]
            bot.answer_callback_query(
                query.id,
                text=emojize("„{}“ ausgewählt. :heavy_check_mark:".format(name)),
            )
            config.set(section, "mensa", query.data)
            logging.info("Set {}.mensa to {}".format(section, query.data))
        with open(CONFIGURATION_FILE, "w") as ini:
            config.write(ini)


def subscribe_handler(bot: Bot, update: Update, args: List[str], job_queue: JobQueue):
    section = str(update.message.chat_id)
    filter_text = demojize("".join(args))
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
        config.set(section, "menu_filter", filter_text)
        logging.info(
            "Subscribed {} for notification at {} with filter '{}'".format(
                update.message.chat_id, NOTIFICATION_TIME, filter_text
            )
        )
        job_queue.run_daily(
            lambda updater, job: send_menu(
                updater.bot,
                job.context["chat_id"],
                Query.from_text(job.context["menu_filter"]),
            ),
            NOTIFICATION_TIME,
            days=(1, 2, 3, 4, 5),
            name=section,
            context={"chat_id": update.message.chat_id, "menu_filter": filter_text},
        )
        with open(CONFIGURATION_FILE, "w") as ini:
            config.write(ini)
        bot.send_message(
            update.message.chat_id,
            "Du bekommst ab jetzt täglich den Speiseplan zugeschickt.",
        )


def unsubscribe_handler(bot: Bot, update: Update, job_queue: JobQueue):
    section = str(update.message.chat_id)
    if not config.has_section(section):
        config.add_section(section)
        logging.info("Created new config section: {}".format(section))
    already_subscribed = config.getboolean(section, "subscribed", fallback=False)
    if already_subscribed:
        config.set(section, "subscribed", "no")
        for job in job_queue.get_jobs_by_name(section):
            job.schedule_removal()
        logging.info("Unsubscribed {}".format(update.message.chat_id))
        with open(CONFIGURATION_FILE, "w") as ini:
            config.write(ini)
        bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan erfolgreich abbestellt."
        )
    else:
        bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan gar nicht abonniert."
        )


def error_emoji() -> str:
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
    job_queue = JobQueue(bot)

    bot.dispatcher.add_handler(CommandHandler("help", help_handler))
    bot.dispatcher.add_handler(CommandHandler("start", help_handler))
    bot.dispatcher.add_handler(CommandHandler("menu", menu_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("mensa", mensa_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("allergens", allergens_handler))
    bot.dispatcher.add_handler(CommandHandler("info", info_handler))
    bot.dispatcher.add_handler(CommandHandler("resetallergens", resetallergens_handler))
    bot.dispatcher.add_handler(
        CommandHandler(
            "subscribe", partial(subscribe_handler, job_queue=job_queue), pass_args=True
        )
    )
    bot.dispatcher.add_handler(
        CommandHandler("unsubscribe", partial(unsubscribe_handler, job_queue=job_queue))
    )
    bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.command, help_handler))

    # config
    for section in config.sections():
        if config.getboolean(section, "subscribed", fallback=False):
            filter_text = config.get(section, "menu_filter", fallback="")
            logging.info(
                "Subscribed {} for notification at {} with filter '{}'".format(
                    section, NOTIFICATION_TIME, filter_text
                )
            )
            job_queue.run_daily(
                lambda updater, job: send_menu(
                    updater.bot,
                    job.context["chat_id"],
                    Query.from_text(job.context["menu_filter"]),
                ),
                NOTIFICATION_TIME,
                days=(1, 2, 3, 4, 5),
                name=section,
                context={"chat_id": int(section), "menu_filter": filter_text},
            )

    job_queue.start()
    bot.start_polling()
    bot.idle()
