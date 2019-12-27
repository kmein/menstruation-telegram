import logging
import os
import sys
from datetime import time, datetime
from typing import Set, Optional, List

import redis


class UserDatabase(object):

    def __init__(self, host: str) -> None:
        self.redis = redis.Redis(host, decode_responses=True)

    def allergens_of(self, user_id: int) -> Set[str]:
        value = self.redis.hget(str(user_id), "allergens")
        if value is not None:
            return set(value.split(","))
        else:
            return set()

    def set_allergens_for(self, user_id: int, allergens: Set[str]) -> None:
        self.redis.hset(str(user_id), "allergens", ",".join(allergens))

    def reset_allergens_for(self, user_id: int) -> None:
        self.redis.hdel(str(user_id), "allergens")

    def mensa_of(self, user_id: int) -> Optional[int]:
        value = self.redis.hget(str(user_id), "mensa")
        if value is not None:
            return int(value)
        else:
            return None

    def set_mensa_for(self, user_id: int, mensa_str: str) -> None:
        self.redis.hset(str(user_id), "mensa", mensa_str)

    def is_subscriber(self, user_id: int) -> bool:
        return self.redis.hget(str(user_id), "subscribed") == "yes"

    def set_subscription(self, user_id: int, subscribed: bool) -> None:
        self.redis.hset(str(user_id), "subscribed", "yes" if subscribed else "no")

    def menu_filter_of(self, user_id: int) -> Optional[str]:
        return self.redis.hget(str(user_id), "menu_filter")

    def set_menu_filter(self, user_id: int, menu_filter: str) -> None:
        self.redis.hset(str(user_id), "menu_filter", menu_filter)

    def users(self) -> List[int]:
        return [int(user_id_str) for user_id_str in self.redis.keys()]

    def remove_user(self, user_id: int) -> int:
        return self.redis.hdel(str(user_id), 'mensa', 'subscribed', 'menu_filter')


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
    os.environ.get("MENSTRUATION_TIME", "09:00"), "%H:%M"
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

user_db = UserDatabase(redis_host)

logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO
    )
