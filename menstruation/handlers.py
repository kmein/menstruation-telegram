#!/usr/bin/env python3
import functools
import logging
import random
import re
from datetime import datetime
from json import JSONDecodeError
from time import sleep

from emoji import emojize, demojize
from telegram import Bot, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized
from telegram.ext import CallbackContext, run_async

import menstruation.client as client
from menstruation import config
from menstruation import jobs
from menstruation.query import Query

user_db = config.user_db
TIME_PATTERN = r"([01][0-9]|2[0-3]|[0-9]):[0-5][0-9]"


def debug_logging(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        try:
            logging.debug(
                f"Entering: {func.__name__}, "
                f"chat_id: {args[0].message.chat_id}, "
                f"args: {args[1].args}"
            )
        except AttributeError:
            logging.debug(f"Entering: {func.__name__}")
        func(*args, **kwargs)
        logging.debug(f"Exiting: {func.__name__}")

    return wrapper_decorator


@debug_logging
@run_async
def help_handler(update: Update, context: CallbackContext):
    def infos(mapping):
        return "\n".join(k + " – " + v for k, v in mapping.items())

    command_description = {
        "/menu :seedling: 3€": "Heutige Speiseangebote (vegan bis 3€).",
        "/menu tomorrow": "Morgige Speiseangebote.",
        "/menu 2018-10-22": "Speiseangebote für den 22.10.2018.",
        "/help": "Dieser Hilfetext.",
        "/mensa beuth": "Auswahlmenü für die Mensen der Beuth Hochschule.",
        "/subscribe :carrot: 2€ 9:30": "Abonniere tägliche Benachrichtigungen der Speiseangebote "
                                       "(vegetarisch bis 2€ um 9:30 Uhr).",
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
        update.effective_message.chat_id,
        emojize(
            f"*BEFEHLE*\n{infos(command_description)}\n\n*LEGENDE*\n{infos(emoji_description)}"
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@debug_logging
def send_menu(bot: Bot, chat_id: int, query: Query):
    query.allergens = user_db.allergens_of(chat_id)
    mensa_code = user_db.mensa_of(chat_id)
    logging.debug(f"allergens: {query.allergens}, mensa_code: {mensa_code}")
    if mensa_code is None:
        raise TypeError("No mensa selected")
    json_object = client.get_json(config.endpoint, mensa_code, query)
    reply = "".join(client.render_group(group) for group in json_object)
    if reply:
        bot.send_message(chat_id, emojize(reply), parse_mode=ParseMode.MARKDOWN)
    else:
        bot.send_message(
            chat_id, emojize(f"Kein Essen gefunden. {error_emoji()}")
        )


@debug_logging
@run_async
def menu_handler(update: Update, context: CallbackContext):
    logging.info(f"{update.effective_message.chat_id} asks for a menu")
    text = demojize("".join(context.args))
    try:
        send_menu(context.bot, update.effective_message.chat_id, Query.from_text(text))
    except TypeError as e:
        logging.debug(e)
        context.bot.send_message(
            update.effective_message.chat_id,
            emojize(
                f"Wie es aussieht, hast Du noch keine Mensa ausgewählt. {error_emoji()}\n"
                f"Tu dies zum Beispiel mit „/mensa adlershof“ :information:"
            )
        )
    except (ValueError, JSONDecodeError) as e:
        logging.debug(e)
        context.bot.send_message(
            update.effective_message.chat_id,
            emojize(
                f"Entweder ist diese Mensa noch nicht unterstützt, {error_emoji()}\n"
                f"oder es gibt an diesem Tag dort kein Essen. {error_emoji()}"
            )
        )


@debug_logging
@run_async
def info_handler(update: Update, context: CallbackContext):
    number_name = client.get_allergens(config.endpoint)
    code_name = client.get_mensas(config.endpoint)
    myallergens = user_db.allergens_of(update.effective_message.chat_id)
    mymensa = user_db.mensa_of(update.effective_message.chat_id)
    subscribed = user_db.is_subscriber(update.effective_message.chat_id)
    subscription_time = jobs.show_job_time(update.effective_message.chat_id)
    subscription_filter = (
        user_db.menu_filter_of(update.effective_message.chat_id) or "kein Filter"
    )
    context.bot.send_message(
        update.effective_message.chat_id,
        "*MENSA*\n{mensa}\n\n*ABO*\n{subscription}\n\n*ALLERGENE*\n{allergens}".format(
            mensa=code_name[mymensa] if mymensa is not None else "keine",
            allergens="\n".join(number_name[number] for number in myallergens),
            subscription=emojize(
                (":thumbs_up:" if subscribed else ":thumbs_down:")
                + f" ({subscription_filter}) {subscription_time}"
            ),
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@debug_logging
@run_async
def allergens_handler(update: Update, context: CallbackContext):
    number_name = client.get_allergens(config.endpoint)
    allergens_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"A{number}")]
            for number, name in number_name.items()
        ]
    )
    context.bot.send_message(
        update.effective_message.chat_id,
        emojize("Wähle Deine Allergene aus. :index_pointing_up:"),
        reply_markup=allergens_chooser,
    )


@debug_logging
@run_async
def resetallergens_handler(update: Update, context: CallbackContext):
    logging.info(f"Allergens reset for {update.effective_message.chat_id}")
    user_db.reset_allergens_for(update.effective_message.chat_id)
    context.bot.send_message(
        update.effective_message.chat_id, emojize("Allergene zurückgesetzt. :heavy_check_mark:")
    )


@debug_logging
@run_async
def mensa_handler(update: Update, context: CallbackContext):
    text = " ".join(context.args)
    pattern = text.strip()
    code_name = None
    for retries in range(config.retries_api_failure):
        try:
            code_name = client.get_mensas(config.endpoint, pattern)
            break
        except JSONDecodeError:
            logging.debug(f"JSONDecodeError: Try number {retries + 1} / {config.retries_api_failure}")
            sleep(1)
            continue
    if code_name is None:
        logging.exception(f"Failed to load code_names")
        return
    mensa_chooser = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=code)]
            for code, name in sorted(code_name.items(), key=lambda item: item[1])
        ]
    )
    context.bot.send_message(
        update.effective_message.chat_id,
        emojize("Wähle Deine Mensa aus. :index_pointing_up:"),
        reply_markup=mensa_chooser,
    )


@debug_logging
@run_async
def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        if query.data.startswith("A"):
            allergen_number = query.data.lstrip("A")
            name = client.get_allergens(config.endpoint)[allergen_number]
            context.bot.answer_callback_query(
                query.id, text=emojize(f"„{name}” ausgewählt. :heavy_check_mark:")
            )
            allergens = user_db.allergens_of(query.message.chat_id)
            allergens.add(allergen_number)
            user_db.set_allergens_for(query.message.chat_id, allergens)
            logging.info(
                f"Set {query.message.chat_id} allergens to {allergens}"
            )
        else:
            name = client.get_mensas(config.endpoint)[int(query.data)]
            context.bot.answer_callback_query(
                query.id,
                text=emojize(f"„{name}“ ausgewählt. :heavy_check_mark:"),
            )
            user_db.set_mensa_for(query.message.chat_id, query.data)
            logging.info(f"Set {query.message.chat_id} mensa to {query.data}")


@debug_logging
@run_async
def subscribe_handler(update: Update, context: CallbackContext):
    filter_text = demojize("".join(context.args))
    is_refreshed = user_db.menu_filter_of(update.effective_message.chat_id) not in [
        filter_text,
        None,
    ]
    if not is_refreshed and user_db.is_subscriber(update.effective_message.chat_id):
        context.bot.send_message(
            update.effective_message.chat_id, "Du hast den Speiseplan schon abonniert."
        )
    else:
        time_match = re.search(TIME_PATTERN, filter_text)
        if time_match:
            time_match = time_match.group(0)
            user_db.set_subscription_time(
                update.effective_message.chat_id,
                datetime.strptime(time_match, '%H:%M').time()
            )
            filter_text = filter_text.replace(time_match, '')
        user_db.set_subscription(update.effective_message.chat_id, True)
        user_db.set_menu_filter(update.effective_message.chat_id, filter_text)
        jobs.remove_subscriber(str(update.effective_message.chat_id))
        jobs.add_subscriber(str(update.effective_message.chat_id))
        logging.info(
            f"Subscribed {update.effective_message.chat_id} for notification with filter '{filter_text}'"
        )
        if is_refreshed:
            logging.debug(f"Subscription updated {update.effective_message.chat_id}")
        context.bot.send_message(
            update.effective_message.chat_id,
            "Du bekommst ab jetzt täglich den Speiseplan zugeschickt."
            if not is_refreshed
            else "Du hast dein Abonnement erfolgreich aktualisiert.",
        )


@debug_logging
@run_async
def unsubscribe_handler(update: Update, context: CallbackContext):
    logging.debug(f"{update.effective_message.chat_id} "
                  f"is_subscriber: {user_db.is_subscriber(update.effective_message.chat_id)}")
    if user_db.is_subscriber(update.effective_message.chat_id):
        user_db.set_subscription(update.effective_message.chat_id, False)
        jobs.remove_subscriber(str(update.effective_message.chat_id))
        logging.info(f"Unsubscribed {update.effective_message.chat_id}")
        context.bot.send_message(
            update.effective_message.chat_id, "Du hast den Speiseplan erfolgreich abbestellt."
        )
    else:
        context.bot.send_message(
            update.effective_message.chat_id, "Du hast den Speiseplan gar nicht abonniert."
        )


@debug_logging
@run_async
def chat_id_handler(update: Update, context: CallbackContext):
    context.bot.send_message(
        update.effective_message.chat_id,
        f"Deine Chat_ID ist die {update.effective_message.chat_id}"
    )


@debug_logging
@run_async
def reset_handler(update: Update, context: CallbackContext):
    user_db.remove_user(update.effective_message.chat_id)
    context.bot.send_message(
        update.effective_message.chat_id,
        emojize(f"Deine Daten wurden gelöscht. :white_heavy_check_mark: {error_emoji()}")
    )


@debug_logging
@run_async
def status_handler(update: Update, context: CallbackContext):
    if str(update.effective_message.chat_id) in config.moderators:
        context.bot.send_message(
            update.effective_message.chat_id,
            f"*User DB*\n"
            f"Registered: {len(user_db.users())}\n"
            f"Subscribed: {len(list(user for user in user_db.users() if user_db.is_subscriber(user)))}\n\n"
            f"*Config*\n"
            f"Workers: {config.workers}\n"
            f"Moderators: {', '.join(config.moderators)}\n"
            f"Notification time: {config.notification_time.strftime('%H:%M')}\n"
            f"Retries on api failure: {config.retries_api_failure}\n"
            f"Debug: {config.debug}\n"
            f"Logging level: {logging.getLogger().getEffectiveLevel()}\n\n"
            f"*Job Queue*\n"
            f"{jobs.show_job_queue()}",
            parse_mode="Markdown"
        )
    else:
        help_handler(update, context)


@debug_logging
@run_async
def broadcast_handler(update: Update, context: CallbackContext):
    logging.debug(f"MODERATORS: {config.moderators}")
    if str(update.effective_message.chat_id) not in config.moderators:
        logging.warning(
            f"{update.effective_message.chat_id} tried to send a broadcast message, but is no moderator"
        )
        context.bot.send_message(
            update.effective_message.chat_id,
            emojize(
                f"Du hast nicht die Berechtigung einen Broadcast zu versenden. {error_emoji()}"
            ),
        )
        return None
    text = demojize(" ".join(context.args))
    if not text:
        context.bot.send_message(
            update.effective_message.chat_id,
            emojize(f"Broadcast-Text darf nicht leer sein. {error_emoji()}"),
        )
        return None
    emojized_text = emojize(text)
    logging.info(f"Sending the following broadcast: {emojized_text}")
    for user_id in user_db.users():
        if user_id == update.effective_message.chat_id:
            logging.debug(f"Skipped {user_id}")
            continue
        logging.debug(f"Send to {user_id}, text: {text}")
        try:
            context.bot.send_message(user_id, emojized_text)
            logging.info(f"Broadcast successfully sent to {user_id}")
        except Unauthorized:
            logging.exception(
                f"Skipped and removed {user_id}, because he blocked the bot"
            )
            user_db.remove_user(user_id)
            jobs.remove_subscriber(user_id)
            continue
    context.bot.send_message(
        update.effective_message.chat_id, emojize("Broadcast erfolgreich versendet. :thumbs_up:")
    )


@debug_logging
@run_async
def debug_handler(update: Update, context: CallbackContext):
    if str(update.effective_message.chat_id) in config.moderators:
        if config.debug:
            config.debug = False
            config.set_logging_level()
            context.bot.send_message(
                update.effective_message.chat_id, emojize("Debug deaktiviert. :zipper-mouth_face:")
            )
        else:
            config.debug = True
            config.set_logging_level()
            context.bot.send_message(
                update.effective_message.chat_id, emojize("Debug aktiviert. :wrench:")
            )
        logging.info(f"Log level is now {logging.getLogger().getEffectiveLevel()}")
    else:
        help_handler(update, context)


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
