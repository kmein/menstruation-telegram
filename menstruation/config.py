import logging
import os
from typing import Set, Optional, List
import redis


class MenstruationConfig(object):

    def __init__(self) -> None:
        args = self.get_environment_args()
        self.__endpoint = args['ENDPOINT']
        self.__redis_host = args['REDIS_HOST']
        self.__moderators = args['MODERATORS']
        self.__debug = args['DEBUG']
        self.user_db = UserDatabase(self.redis_host)
        self.set_logging_level()

    def get_endpoint(self) -> str:
        return self.__endpoint

    def get_redis_host(self) -> str:
        return self.__redis_host

    def get_moderators(self) -> list:
        return self.__moderators

    def set_moderators(self, moderators: List) -> None:
        self.__moderators = moderators

    def get_debug(self) -> bool:
        return self.__debug

    def set_debug(self, debug: bool) -> None:
        self.__debug = debug
        self.set_logging_level()

    endpoint = property(get_endpoint)
    redis_host = property(get_redis_host)
    moderators = property(get_moderators, set_moderators)
    debug = property(get_debug, set_debug)

    def set_logging_level(self):
        logging.basicConfig(
            level=logging.DEBUG if self.__debug else logging.INFO
        )

    @staticmethod
    def get_environment_args() -> dict:

        args = dict()

        try:
            args['ENDPOINT'] = os.environ["MENSTRUATION_ENDPOINT"]
            if not args['ENDPOINT']:
                raise KeyError
        except KeyError:
            args['ENDPOINT'] = "http://127.0.0.1:80"

        try:
            args['REDIS_HOST'] = os.environ["MENSTRUATION_REDIS"]
        except KeyError:
            args['REDIS_HOST'] = "localhost"

        try:
            args['MODERATORS'] = list((os.environ["MENSTRUATION_MODERATORS"]).split(","))
        except KeyError:
            args['MODERATORS'] = []

        args['DEBUG'] = True if "MENSTRUATION_DEBUG" in os.environ else False

        return args


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
