#!/usr/bin/env python3
import logging
import os
import random
import sys
from datetime import datetime, time
from functools import partial

from emoji import emojize, demojize
from telegram import Bot, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from telegram.ext import Updater, JobQueue
from telegram.ext.filters import Filters

import client
from config import MenstruationConfig
from query import Query
from time import sleep

NOTIFICATION_TIME: time = datetime.strptime(
    os.environ.get("MENSTRUATION_TIME", "09:00"), "%H:%M"
).time()

try:
    ENDPOINT = os.environ["MENSTRUATION_ENDPOINT"]
    if not ENDPOINT:
        raise KeyError
except KeyError:
    ENDPOINT = "http://127.0.0.1:80"

try:
    REDIS_HOST = os.environ["MENSTRUATION_REDIS"]
except KeyError:
    REDIS_HOST = "localhost"


logging.basicConfig(
    level=logging.DEBUG if "MENSTRUATION_DEBUG" in os.environ else logging.INFO
)

user_db = MenstruationConfig(REDIS_HOST)


def help_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: help_handler" +
                  f", chat_id: {update.message.chat_id}")

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
        "/status": "Status des Bots",
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
    context.bot.send_message(
        update.message.chat_id,
        emojize(
            "*BEFEHLE*\n{}\n\n*LEGENDE*\n{}".format(
                infos(command_description), infos(emoji_description)
            )
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


def send_menu(bot: Bot, chat_id: int, query: Query):
    query.allergens = user_db.allergens_of(chat_id)
    mensa_code = user_db.mensa_of(chat_id)
    logging.debug(f"Entering: send_menu, chat_id: {chat_id}, allergens: {query.allergens}, mensa_code: {mensa_code}")
    if mensa_code is None:
        raise TypeError("No mensa selected")
    json_object = client.get_json(ENDPOINT, mensa_code, query)
    reply = "".join(client.render_group(group) for group in json_object)
    if reply:
        bot.send_message(chat_id, emojize(reply), parse_mode=ParseMode.MARKDOWN)
    else:
        bot.send_message(
            chat_id, emojize("Kein Essen gefunden. {}".format(error_emoji()))
        )


def menu_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: menu_handler" +
                  f", chat_id: {update.message.chat_id}")
    text = demojize("".join(context.args))
    try:
        send_menu(context.bot, update.message.chat_id, Query.from_text(text))
    except TypeError as e:
        logging.warning(e)
        context.bot.send_message(
            update.message.chat_id,
            emojize(
                "Wie es aussieht, hast Du noch keine Mensa ausgewählt. {}\nTu dies zum Beispiel mit „/mensa adlershof“ :information:".format(
                    error_emoji()
                )
            ),
        )
    except ValueError as e:
        logging.warning(e)
        context.bot.send_message(
            update.message.chat_id,
            emojize(
                "Entweder ist diese Mensa noch nicht unterstützt, {}\noder es gibt an diesem Tag dort kein Essen. {}".format(
                    error_emoji(), error_emoji()
                )
            ),
        )


def info_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: info_handler" +
                  f", chat_id: {update.message.chat_id}")
    number_name = client.get_allergens(ENDPOINT)
    code_name = client.get_mensas(ENDPOINT)
    myallergens = user_db.allergens_of(update.message.chat_id)
    mymensa = user_db.mensa_of(update.message.chat_id)
    subscribed = user_db.is_subscriber(update.message.chat_id)
    subscription_filter = (
        user_db.menu_filter_of(update.message.chat_id) or "kein Filter"
    )
    context.bot.send_message(
        update.message.chat_id,
        "*MENSA*\n{mensa}\n\n*ABO*\n{subscription}\n\n*ALLERGENE*\n{allergens}".format(
            mensa=code_name[mymensa] if mymensa is not None else "keine",
            allergens="\n".join(number_name[number] for number in myallergens),
            subscription=emojize(
                (":thumbs_up:" if subscribed else ":thumbs_down:")
                + " ({})".format(subscription_filter)
            ),
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


def allergens_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: allergens_handler" +
                  f", chat_id: {update.message.chat_id}")
    number_name = client.get_allergens(ENDPOINT)
    allergens_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"A{number}")]
            for number, name in number_name.items()
        ]
    )
    context.bot.send_message(
        update.message.chat_id,
        emojize("Wähle Deine Allergene aus. :index_pointing_up:"),
        reply_markup=allergens_chooser,
    )


def resetallergens_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: resetallergens_handler" +
                  f", chat_id: {update.message.chat_id}")
    user_db.reset_allergens_for(update.message.chat_id)
    context.bot.send_message(
        update.message.chat_id, emojize("Allergene zurückgesetzt. :heavy_check_mark:")
    )


def mensa_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: mensa_handler" +
                  f", chat_id: {update.message.chat_id}")
    text = " ".join(context.args)
    pattern = text.strip()
    code_name = client.get_mensas(ENDPOINT, pattern)
    mensa_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=code)]
            for code, name in sorted(code_name.items(), key=lambda item: item[1])
        ]
    )
    context.bot.send_message(
        update.message.chat_id,
        emojize("Wähle Deine Mensa aus. :index_pointing_up:"),
        reply_markup=mensa_chooser,
    )


def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        if query.data.startswith("A"):
            allergen_number = query.data.lstrip("A")
            name = client.get_allergens(ENDPOINT)[allergen_number]
            context.bot.answer_callback_query(
                query.id, text=emojize(f"„{name}” ausgewählt. :heavy_check_mark:")
            )
            allergens = user_db.allergens_of(query.message.chat_id)
            allergens.add(allergen_number)
            user_db.set_allergens_for(query.message.chat_id, allergens)
            logging.info(
                "Set {}.allergens to {}".format(query.message.chat_id, allergens)
            )
        else:
            name = client.get_mensas(ENDPOINT)[int(query.data)]
            context.bot.answer_callback_query(
                query.id,
                text=emojize("„{}“ ausgewählt. :heavy_check_mark:".format(name)),
            )
            user_db.set_mensa_for(query.message.chat_id, query.data)
            logging.info("Set {}.mensa to {}".format(query.message.chat_id, query.data))


def subscribe_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: subscribe_handler" +
                  f", chat_id: {update.message.chat_id}")
    filter_text = demojize("".join(context.args))
    is_refreshed = user_db.menu_filter_of(update.message.chat_id) not in [
        filter_text,
        None,
    ]
    if not is_refreshed and user_db.is_subscriber(update.message.chat_id):
        context.bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan schon abonniert."
        )
    else:
        user_db.set_subscription(update.message.chat_id, True)
        user_db.set_menu_filter(update.message.chat_id, filter_text)
        logging.info(
            "Subscribed {} for notification at {} with filter '{}'".format(
                update.message.chat_id, NOTIFICATION_TIME, filter_text
            )
        )
        if is_refreshed:
            section = str(update.message.chat_id)
            logging.info("Subscription updated {}".format(update.message.chat_id))
        context.bot.send_message(
            update.message.chat_id,
            "Du bekommst ab jetzt täglich den Speiseplan zugeschickt."
            if not is_refreshed
            else "Du hast dein Abonnement erfolgreich aktualisiert.",
        )


def unsubscribe_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: status_handler" +
                  f", chat_id: {update.message.chat_id}"
                  f", is_subscriber: {user_db.is_subscriber(update.message.chat_id)}")
    if user_db.is_subscriber(update.message.chat_id):
        user_db.set_subscription(update.message.chat_id, False)
        logging.info("Unsubscribed {}".format(update.message.chat_id))
        context.bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan erfolgreich abbestellt."
        )
    else:
        context.bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan gar nicht abonniert."
        )


def status_handler(update: Update, context: CallbackContext):
    logging.debug(f"Entering: status_handler" +
                  f", chat_id: {update.message.chat_id}" +
                  f", user_db.users(): {user_db.users()}" +
                  f", user is_subscriber: {list(user for user in user_db.users() if user_db.is_subscriber(user))}")
    context.bot.send_message(
        update.message.chat_id,
        f"Registered: {len(user_db.users())}\n"
        f"Subscribed: {len(list(user for user in user_db.users() if user_db.is_subscriber(user)))}",
    )


def notify_subscribers(context: CallbackContext):
    logging.debug(f"Entering: notify_subscribers")
    for user_id in user_db.users():
        if user_db.is_subscriber(user_id):
            logging.debug(f"Notify: {user_id}")
            filter_text = user_db.menu_filter_of(user_id) or ""
            try:
                send_menu(context.bot, user_id, Query.from_text(filter_text))
            except Unauthorized:
                logging.exception(f"{user_id} has blocked the bot. Removed Subscription.")
                user_db.set_subscription(user_id, False)
                continue
            sleep(1.0)
    logging.debug(f"Leaving: notify_subscribers")

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

    bot = Updater(token=TOKEN, use_context=True)
    job_queue = bot.job_queue

    bot.dispatcher.add_handler(CommandHandler("help", help_handler))
    bot.dispatcher.add_handler(CommandHandler("start", help_handler))
    bot.dispatcher.add_handler(CommandHandler("menu", menu_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("mensa", mensa_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("allergens", allergens_handler))
    bot.dispatcher.add_handler(CommandHandler("info", info_handler))
    bot.dispatcher.add_handler(CommandHandler("resetallergens", resetallergens_handler))
    bot.dispatcher.add_handler(CommandHandler("subscribe", subscribe_handler, pass_args=True))
    bot.dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_handler))
    bot.dispatcher.add_handler(CommandHandler("status", status_handler))
    bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.command, help_handler))

    logging.debug(f"NOTIFICATION_TIME: {NOTIFICATION_TIME}")

    job_queue.run_daily(
        notify_subscribers,
        NOTIFICATION_TIME,
        days=(0, 1, 2, 3, 4),
        name='notify_subscribers',
    )

    job_queue.start()
    bot.start_polling()
    bot.idle()
