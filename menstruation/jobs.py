import logging
from json import JSONDecodeError
from random import randint
from time import sleep

from emoji import emojize
from telegram.error import Unauthorized

from menstruation import config
from telegram.ext import CallbackContext, JobQueue, Job

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


def add_subscriber(user_id: str):
    logging.debug(f"Added subscriber: {user_id}")
    job_queue.run_daily(
        notify_subscriber,
        config.notification_time,
        days=(0, 1, 2, 3, 4),
        name=user_id,
    )


def remove_subscriber(user_id: str):
    logging.debug(f"Removed subscriber: {user_id}")
    for job in job_queue.get_jobs_by_name(user_id):
        logging.debug(f"Job: {job.name}, {job.enabled}, {job.removed}")
        job.schedule_removal()


def notify_subscriber(context: CallbackContext):
    user_id = context.job.name
    if not user_db.is_subscriber(user_id):
        logging.error(f"{user_id} is no subscriber, but had an subscription job")
        remove_subscriber(user_id)
        return
    logging.debug(f"Notify: {user_id}")
    filter_text = user_db.menu_filter_of(user_id) or ""
    for retries in range(5):
        try:
            send_menu(context.bot, user_id, Query.from_text(filter_text))
        except TypeError:
            logging.exception(f"{user_id} has no mensa selected")
        except JSONDecodeError:
            logging.exception(
                f"JSONDecodeError: Try number {retries + 1} trying again, response"
            )
            sleep(randint(100, 500)/100)
            continue
        except Unauthorized:
            logging.exception(
                f"{user_id} has blocked the bot. Removed Subscription"
            )
            user_db.set_subscription(user_id, False)
        except Exception as err:
            logging.exception(f"Exception: {err}, skip user: {user_id}")
        break


def setup_job_queue(jq: JobQueue):
    global job_queue
    job_queue = jq
    job_queue.run_once(startup_message, 0)

    for user_id in user_db.users():
        if user_db.is_subscriber(user_id):
            add_subscriber(str(user_id))
    job_queue.start()


def show_job_queue() -> str:
    text = ""
    for job in job_queue.jobs():
        text += f"{job.name}: enabled: {job.enabled}, removed: {job.removed}\n"
    return text
