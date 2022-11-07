import logging
import re
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional, Set, Dict, Union, List


class Color(Enum):
    RED = ":red_heart:"
    GREEN = ":green_heart:"
    YELLOW = ":yellow_heart:"

    @staticmethod
    def from_text(text: str) -> "Color":
        if text == "green":
            return Color.GREEN
        elif text == "yellow":
            return Color.YELLOW
        elif text == "red":
            return Color.RED
        else:
            raise ValueError(f"{text} is no valid color")

    def __str__(self: "Color") -> str:
        if self == Color.GREEN:
            return "green"
        elif self == Color.YELLOW:
            return "yellow"
        elif self == Color.RED:
            return "red"
        else:
            raise ValueError("unreachable")


class Tag(Enum):
    VEGETARIAN = ":carrot:"
    VEGAN = ":seedling:"
    ORGANIC = ":smiling_face_with_halo:"
    SUSTAINABLE_FISHING = ":fish:"
    CLIMATE_FRIENDLY = ":globe_showing_Americas:"

    H2O_A = ""
    H2O_B = ""
    H2O_C = ""
    H2O_D = ""
    H2O_E = ""

    CO2_A = ""
    CO2_B = ""
    CO2_C = ""
    CO2_D = ""
    CO2_E = ""

    @staticmethod
    def from_text(text: str) -> "Tag":
        if text == "vegetarian":
            return Tag.VEGETARIAN
        elif text == "vegan":
            return Tag.VEGAN
        elif text == "organic":
            return Tag.ORGANIC
        elif text == "sustainable fishing":
            return Tag.SUSTAINABLE_FISHING
        elif text == "climate friendly":
            return Tag.CLIMATE_FRIENDLY
        elif text == "H2O A":
            return Tag.H2O_A
        elif text == "H2O B":
            return Tag.H2O_B
        elif text == "H2O C":
            return Tag.H2O_C
        elif text == "H2O D":
            return Tag.H2O_D
        elif text == "H2O E":
            return Tag.H2O_E
        elif text == "CO2 A":
            return Tag.CO2_A
        elif text == "CO2 B":
            return Tag.CO2_B
        elif text == "CO2 C":
            return Tag.CO2_C
        elif text == "CO2 D":
            return Tag.CO2_D
        elif text == "CO2 E":
            return Tag.CO2_E
        else:
            raise ValueError(f"{text} is no valid tag")

    def __str__(self: "Tag") -> str:
        if self == Tag.VEGETARIAN:
            return "vegetarian"
        elif self == Tag.VEGAN:
            return "vegan"
        elif self == Tag.ORGANIC:
            return "organic"
        elif self == Tag.SUSTAINABLE_FISHING:
            return "sustainable fishing"
        elif self == Tag.CLIMATE_FRIENDLY:
            return "climate friendly"
        elif self == Tag.H2O_A:
            return "H2O A"
        elif self == Tag.H2O_B:
            return "H2O B"
        elif self == Tag.H2O_C:
            return "H2O C"
        elif self == Tag.H2O_D:
            return "H2O D"
        elif self == Tag.H2O_E:
            return "H2O E"
        elif self == Tag.CO2_A:
            return "CO2 A"
        elif self == Tag.CO2_B:
            return "CO2 B"
        elif self == Tag.CO2_C:
            return "CO2 C"
        elif self == Tag.CO2_D:
            return "CO2 D"
        elif self == Tag.CO2_E:
            return "CO2 E"
        else:
            raise ValueError("unreachable")


class Query:
    def __init__(
        self: "Query",
        max_price: Optional[int],
        colors: Set[Color],
        tags: Set[Tag],
        date: Optional[date],
        allergens: Set[str],
    ) -> None:
        self.max_price = max_price
        self.tags: Set[Tag] = tags
        self.colors: Set[Color] = colors
        self.date = date
        self.allergens = allergens

    def params(self: "Query") -> Dict[str, Union[str, List[str]]]:
        params: Dict[str, Union[str, List[str]]] = dict()
        if self.date:
            params["date"] = self.date.isoformat()
        if self.max_price:
            params["max_price"] = str(self.max_price)
        if self.tags:
            params["tag"] = [str(tag) for tag in self.tags]
        if self.colors:
            params["color"] = [str(color) for color in self.colors]
        if self.allergens:
            params["allergen"] = [allergen for allergen in self.allergens]
        return params

    @staticmethod
    def from_text(text: str) -> "Query":
        def extract_date(text: str) -> Optional[date]:
            matches = re.search(r"(\d{4}-\d{2}-\d{2}|today|tomorrow)", text)
            if matches:
                if matches.group(1) == "today":
                    parsed_date = date.today()
                elif matches.group(1) == "tomorrow":
                    parsed_date = date.today() + timedelta(days=1)
                elif matches.group(1):
                    parsed_date = datetime.strptime(matches.group(1), "%Y-%m-%d").date()
                logging.debug(f'Extracted {parsed_date} from "{text}"')
                return parsed_date
            else:
                logging.debug(f"No date found in '{text}'")
                return None

        max_price_result = re.search(r"(\d+,?\d*)\s?€", text)
        # logging.info('Extracted {} from "{}"'.format((max_price, colors, tags), text))

        return Query(
            max_price=(
                int(float(max_price_result.group(1).replace(",", ".")) * 100)
                if max_price_result
                else None
            ),
            colors=set(
                Color(emoji)
                for emoji in re.findall(
                    r"(:green_heart:|:yellow_heart:|:red_heart:)", text
                )
            ),
            tags=set(
                Tag(emoji)
                for emoji in re.findall(
                    r"(:carrot:|:seedling:|:smiling_face_with_halo:|:fish:|:globe_showing_Americas:)",
                    text,
                )
            ),
            date=extract_date(text),
            allergens=set(),
        )
