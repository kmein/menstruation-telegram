import logging
from json import JSONDecodeError
from random import randint
from time import sleep
from typing import Union

from emoji import emojize
from telegram.error import Unauthorized, NetworkError
from telegram.ext import CallbackContext, JobQueue

from menstruation import config
from menstruation.handlers import send_menu, error_emoji
from menstruation.query import Query

user_db = config.user_db
job_queue = None


def startup_message(context: CallbackContext):
    for moderator in config.moderators:
        try:
            context.bot.send_message(
                moderator, emojize("Server wurde gestartet :robot:")
            )
        except Unauthorized:
            logging.exception(f"Moderator: {moderator}, has blocked the Bot.")
        except Exception as err:
            logging.exception(f"Error in startup_message: {err}")


def add_subscriber(user_id: Union[str, int]):
    if job_queue:
        user_id = int(user_id)
        user_time = user_db.subscription_time_of(user_id)
        notification_time = user_time or config.notification_time
        logging.debug(f"Added subscriber: {user_id}, time: {notification_time}")
        job_queue.run_daily(
            notify_subscriber,
            notification_time,
            days=tuple(range(5)),
            name=str(user_id),
        )
    else:
        logging.error("Cannot add subscriber: job queue uninitialized")


def remove_subscriber(user_id: Union[str, int]):
    if job_queue:
        logging.debug(f"Removed subscriber: {user_id}")
        for job in job_queue.get_jobs_by_name(str(user_id)):
            job.schedule_removal()
    else:
        logging.error("Cannot remove subscriber: job queue uninitialized")


def notify_subscriber(context: CallbackContext):
    user_id = context.job.name
    if not user_db.is_subscriber(user_id):
        logging.error(f"{user_id} is no subscriber, but had a subscription job")
        remove_subscriber(user_id)
        return
    logging.debug(f"Notify: {user_id}")
    filter_text = user_db.menu_filter_of(user_id) or ""
    users_sum = len(user_db.users())
    for retries in range(config.retries_api_failure):
        try:
            send_menu(context.bot, user_id, Query.from_text(filter_text))
            logging.info("Successfully notified %s" % user_id)
            break
        except TypeError:
            logging.exception(f"{user_id} has no mensa selected")
        except (JSONDecodeError, NetworkError):
            logging.debug(
                f"JSONDecodeError: Try number {retries + 1} / {config.retries_api_failure}"
            )
            # Wait a random time and try again
            max_time = 200 + (200 * users_sum)
            sleep(randint(100, max_time) / 100)
            continue
        except Unauthorized:
            logging.exception(f"{user_id} has blocked the bot. Removed Subscription")
            user_db.set_subscription(user_id, False)
            remove_subscriber(user_id)
        except Exception as err:
            logging.exception(f"Exception: {err}")
        logging.exception(f"Menu for {user_id} could not be delivered")
        break


def setup_job_queue(jq: JobQueue):
    global job_queue
    job_queue = jq
    job_queue.run_once(startup_message, 0)

    for user_id in user_db.users():
        if user_db.is_subscriber(user_id):
            add_subscriber(str(user_id))
    job_queue.start()


def show_job_time(user_id: Union[str, int]):
    user_id = int(user_id)
    user_time = user_db.subscription_time_of(user_id)
    job_time = user_time if user_time else config.notification_time
    return job_time.strftime("%H:%M")


def show_job_queue() -> str:
    if job_queue:
        text = "\n".join(
            f"{job.name}: "
            f"Enabled: {':thumbs_up:' if job.enabled else ':thumbs_down:'}, "
            f"Removed: {':thumbs_up:' if job.removed else ':thumbs_down:'}, "
            f"Time: {show_job_time(job.name)}"
            for job in job_queue.jobs()
        )
        return emojize(text)
    else:
        return emojize(f"Job queue uninitialized! {error_emoji()}")
