import logging
from json import JSONDecodeError
from time import sleep

from emoji import emojize
from telegram.error import Unauthorized

from menstruation import config
from telegram.ext import CallbackContext, JobQueue

from menstruation.handlers import send_menu
from menstruation.query import Query

user_db = config.user_db
job_queue = None


def startup_message(context: CallbackContext):
    for moderator in config.moderators:
        try:
            context.bot.send_message(moderator, emojize("Server wurde gestartet :thumbs_up:"))
        except Unauthorized:
            logging.exception(f"Moderator: {moderator}, has blocked the Bot.")
        except Exception as err:
            logging.exception(f"Error in startup_message: {err}")


def notify_subscribers(context: CallbackContext):
    for user_id in user_db.users():
        if user_db.is_subscriber(user_id):
            logging.debug(f"Notify: {user_id}")
            filter_text = user_db.menu_filter_of(user_id) or ""
            for retries in range(5):
                try:
                    send_menu(context.bot, user_id, Query.from_text(filter_text))
                except JSONDecodeError:
                    logging.exception(
                        f"JSONDecodeError: Try number {retries + 1} trying again, response"
                    )
                    continue
                except Unauthorized:
                    logging.exception(
                        f"{user_id} has blocked the bot. Removed Subscription."
                    )
                    user_db.set_subscription(user_id, False)
                except Exception as err:
                    logging.exception(f"Exception: {err}, skip user: {user_id}")
                break
            sleep(1.0)


def setup_job_queue(jq: JobQueue):
    global job_queue
    job_queue = jq
    job_queue.run_once(startup_message, 0)

    job_queue.run_daily(
        notify_subscribers,
        config.notification_time,
        days=(0, 1, 2, 3, 4),
        name="notify_subscribers"
    )

    job_queue.start()
