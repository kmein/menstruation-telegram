#!/usr/bin/env python3
import logging
import pytz

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Updater,
    Defaults,
)
from telegram.ext.filters import Filters

from menstruation import config, jobs
from menstruation.handlers import (
    help_handler,
    menu_handler,
    mensa_handler,
    allergens_handler,
    info_handler,
    resetallergens_handler,
    subscribe_handler,
    unsubscribe_handler,
    status_handler,
    broadcast_handler,
    callback_handler,
    chat_id_handler,
    debug_handler,
)


def run():
    bot = Updater(
        token=config.token,
        workers=config.workers,
        defaults=Defaults(tzinfo=pytz.timezone("Europe/Berlin")),
    )

    bot.dispatcher.add_handler(CommandHandler("help", help_handler, run_async=True))
    bot.dispatcher.add_handler(CommandHandler("start", help_handler, run_async=True))
    bot.dispatcher.add_handler(
        CommandHandler("menu", menu_handler, pass_args=True, run_async=True)
    )
    bot.dispatcher.add_handler(
        CommandHandler("mensa", mensa_handler, pass_args=True, run_async=True)
    )
    bot.dispatcher.add_handler(
        CommandHandler("allergens", allergens_handler, run_async=True)
    )
    bot.dispatcher.add_handler(CommandHandler("info", info_handler, run_async=True))
    bot.dispatcher.add_handler(
        CommandHandler("resetallergens", resetallergens_handler, run_async=True)
    )
    bot.dispatcher.add_handler(
        CommandHandler("subscribe", subscribe_handler, pass_args=True, run_async=True)
    )
    bot.dispatcher.add_handler(
        CommandHandler("unsubscribe", unsubscribe_handler, run_async=True)
    )
    bot.dispatcher.add_handler(
        CommandHandler("chatid", chat_id_handler, run_async=True)
    )
    bot.dispatcher.add_handler(CommandHandler("status", status_handler, run_async=True))
    bot.dispatcher.add_handler(
        CommandHandler("broadcast", broadcast_handler, pass_args=True, run_async=True)
    )
    bot.dispatcher.add_handler(CommandHandler("debug", debug_handler, run_async=True))
    bot.dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    bot.dispatcher.add_handler(MessageHandler(Filters.command, help_handler))

    job_queue = bot.job_queue
    jobs.setup_job_queue(job_queue)

    logging.info("Bot is ready")

    bot.start_polling()
    bot.idle()
