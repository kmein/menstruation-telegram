#!/usr/bin/env python3
import functools
import logging
import os
import random
from time import sleep

from emoji import emojize, demojize
from telegram import Bot, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized
from telegram.ext import CallbackContext

import menstruation.client as client
from menstruation.config import MenstruationConfig
from menstruation.query import Query

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

try:
    MODERATORS = list((os.environ["MENSTRUATION_MODERATORS"]).split(","))
except KeyError:
    MODERATORS = []

logging.basicConfig(
    level=logging.DEBUG if "MENSTRUATION_DEBUG" in os.environ else logging.INFO
)

user_db = MenstruationConfig(REDIS_HOST)


def debug_handler(func):
    @functools.wraps(func)
    def wrapper_decorator(*args):
        logging.debug(
            f"Entering: {func.__name__}, "
            f"chat_id: {args[0].message.chat_id}, "
            f"args: {args[1].args}"
        )
        func(*args)
        logging.debug(f"Exiting: {func.__name__}")
    return wrapper_decorator


@debug_handler
def help_handler(update: Update, context: CallbackContext):

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
    logging.debug(
        f"Entering: send_menu, chat_id: {chat_id}, allergens: {query.allergens}, mensa_code: {mensa_code}"
    )
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
    logging.debug(f"Exiting: send_menu")


@debug_handler
def menu_handler(update: Update, context: CallbackContext):
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


@debug_handler
def info_handler(update: Update, context: CallbackContext):
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


@debug_handler
def allergens_handler(update: Update, context: CallbackContext):
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


@debug_handler
def resetallergens_handler(update: Update, context: CallbackContext):
    user_db.reset_allergens_for(update.message.chat_id)
    context.bot.send_message(
        update.message.chat_id, emojize("Allergene zurückgesetzt. :heavy_check_mark:")
    )


@debug_handler
def mensa_handler(update: Update, context: CallbackContext):
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


@debug_handler
def subscribe_handler(update: Update, context: CallbackContext):
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
            "Subscribed {} for notification with filter '{}'".format(
                update.message.chat_id, filter_text
            )
        )
        if is_refreshed:
            logging.info("Subscription updated {}".format(update.message.chat_id))
        context.bot.send_message(
            update.message.chat_id,
            "Du bekommst ab jetzt täglich den Speiseplan zugeschickt."
            if not is_refreshed
            else "Du hast dein Abonnement erfolgreich aktualisiert.",
        )


@debug_handler
def unsubscribe_handler(update: Update, context: CallbackContext):
    logging.debug(f"is_subscriber: {user_db.is_subscriber(update.message.chat_id)}")
    if user_db.is_subscriber(update.message.chat_id):
        user_db.set_subscription(update.message.chat_id, False)
        logging.info(f"Unsubscribed {update.message.chat_id}")
        context.bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan erfolgreich abbestellt."
        )
    else:
        context.bot.send_message(
            update.message.chat_id, "Du hast den Speiseplan gar nicht abonniert."
        )


@debug_handler
def status_handler(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.message.chat_id,
        f"Registered: {len(user_db.users())}\n"
        f"Subscribed: {len(list(user for user in user_db.users() if user_db.is_subscriber(user)))}",
    )


@debug_handler
def broadcast_handler(update: Update, context: CallbackContext):
    """"For moderators only"""
    logging.debug(f"MODERATORS: {MODERATORS}")
    if str(update.message.chat_id) not in MODERATORS:
        logging.warning(
            f"{update.message.chat_id} tried to send a broadcast message, but is no moderator"
        )
        context.bot.send_message(
            update.message.chat_id,
            emojize(
                f"Du hast nicht die Berechtigung einen Broadcast zu versenden. {error_emoji()}"
            ),
        )
        return None
    text = demojize(" ".join(context.args))
    if not text:
        context.bot.send_message(
            update.message.chat_id,
            emojize(f"Broadcast-Text darf nicht leer sein. {error_emoji()}"),
        )
        return None
    emojized_text = emojize(text)
    for user_id in user_db.users():
        if user_id == update.message.chat_id:
            logging.debug(f"Skipped {user_id}, text: {text}")
            continue
        logging.debug(f"Send to {user_id}, text: {text}")
        try:
            context.bot.send_message(user_id, emojized_text)
        except Unauthorized:
            logging.exception(
                f"Skipped and removed {user_id}, because he blocked the bot"
            )
            user_db.remove_user(user_id)
            continue
    context.bot.send_message(
        update.message.chat_id, emojize("Broadcast erfolgreich versendet. :thumbs_up:")
    )


def notify_subscribers(context: CallbackContext):
    logging.debug("Entering: notify_subscribers")
    for user_id in user_db.users():
        if user_db.is_subscriber(user_id):
            logging.debug(f"Notify: {user_id}")
            filter_text = user_db.menu_filter_of(user_id) or ""
            try:
                send_menu(context.bot, user_id, Query.from_text(filter_text))
            except Unauthorized:
                logging.exception(
                    f"{user_id} has blocked the bot. Removed Subscription."
                )
                user_db.set_subscription(user_id, False)
                continue
            except Exception as err:
                logging.exception(f"Exception: {err}, skip user: {user_id}")
                continue
            sleep(1.0)
    logging.debug("Exiting: notify_subscribers")


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
