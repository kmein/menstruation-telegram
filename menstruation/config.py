import logging
import os
import sys
from collections import namedtuple
from datetime import time, datetime
from typing import Set, List

import redis

USER_KEYS = [
    "mensa",
    "subscribed",
    "menu_filter",
    "subscription_time",
    "allergens",
    "mode",
]

User = namedtuple("User", USER_KEYS)


def set_logging_level():
    # reset root logging
    for handler in logging.root.handlers.copy():
        logging.root.removeHandler(handler)

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)


class UserDatabase(object):
    def __init__(self, host: str) -> None:
        self.redis = redis.Redis(host, decode_responses=True)

    def user_settings_of(self, user_id: int) -> User:
        mensa_str, subscribed_str, menu_filter_str, subscription_time_str, allergens_str, mode_str = self.redis.hmget(
            str(user_id), USER_KEYS
        )
        return User(
            subscribed=(subscribed_str == "yes"),
            menu_filter=menu_filter_str,
            allergens=set(allergens_str.split(","))
            if allergens_str is not None
            else set(),
            mensa=int(mensa_str) if mensa_str is not None else None,
            subscription_time=(
                datetime.strptime(subscription_time_str, "%H:%M").time()
                if subscription_time_str
                else None
            ),
            mode=mode_str or "student",
        )

    def set_allergens_for(self, user_id: int, allergens: Set[str]) -> None:
        self.redis.hset(str(user_id), "allergens", ",".join(allergens))

    def reset_allergens_for(self, user_id: int) -> None:
        self.redis.hdel(str(user_id), "allergens")

    def set_mode_for(self, user_id: int, mode: str) -> None:
        self.redis.hset(str(user_id), "mode", mode)

    def set_mensa_for(self, user_id: int, mensa_str: str) -> None:
        self.redis.hset(str(user_id), "mensa", mensa_str)

    def set_subscription(self, user_id: int, subscribed: bool) -> None:
        self.redis.hset(str(user_id), "subscribed", "yes" if subscribed else "no")

    def set_subscription_time(self, user_id: int, t: datetime.time) -> None:
        self.redis.hset(str(user_id), "subscription_time", t.strftime("%H:%M"))

    def set_menu_filter(self, user_id: int, menu_filter: str) -> None:
        self.redis.hset(str(user_id), "menu_filter", menu_filter)

    def users(self) -> List[int]:
        return [int(user_id_str) for user_id_str in self.redis.keys()]

    def remove_user(self, user_id: int) -> int:
        return self.redis.hdel(str(user_id), *USER_KEYS)


try:
    token = os.environ["MENSTRUATION_TOKEN"].strip()
except KeyError:
    print("Please specify bot token in variable MENSTRUATION_TOKEN.", file=sys.stderr)
    sys.exit(1)

try:
    endpoint = os.environ["MENSTRUATION_ENDPOINT"]
    if not endpoint:
        raise KeyError
except KeyError:
    endpoint = "http://127.0.0.1:80"

try:
    redis_host = os.environ["MENSTRUATION_REDIS"]
except KeyError:
    redis_host = "localhost"

notification_time: time = datetime.strptime(
    os.environ.get("MENSTRUATION_TIME", "11:00"), "%H:%M"
).time()

try:
    moderators = list((os.environ["MENSTRUATION_MODERATORS"]).split(","))
except KeyError:
    moderators = []

try:
    workers = int(os.environ["MENSTRUATION_WORKERS"])
    if not workers:
        raise KeyError
except (KeyError, ValueError):
    workers = 8

try:
    retries_api_failure = int(os.environ["MENSTRUATION_RETRIES"])
    if not retries_api_failure:
        raise KeyError
except (KeyError, ValueError):
    retries_api_failure = 5

debug = "MENSTRUATION_DEBUG" in os.environ

set_logging_level()

user_db = UserDatabase(redis_host)
