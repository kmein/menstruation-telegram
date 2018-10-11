from jq import jq
from termcolor import colored, cprint
from itertools import chain
import argparse
import itertools
import locale
import sys

locale.setlocale(locale.LC_ALL, 'de_DE')

JQ_QUERY = """
.data.page | {
  groups: .groups | map({
    name: .name,
    meals: .meals | map({
      name: .name,
      price: .price | ltrimstr("€ ") | gsub(","; ".") | split("/") | map(tonumber) | {
        student: .[0],
        employee: .[1],
        guest: .[2]
      },
      tags: .icons | map(
        if .src == "/vendor/infomax/mensen/icons/1.png" then "vegetarian"
        elif .src == "/vendor/infomax/mensen/icons/15.png" then "vegan"
        elif .src == "/vendor/infomax/mensen/icons/18.png" then "organic"
        elif .src == "/vendor/infomax/mensen/icons/38.png" then "sustainable fishing"
        elif .src == "/vendor/infomax/mensen/icons/43.png" then "climate"
        elif .src == "/vendor/infomax/mensen/icons/ampel_gelb_70x65.png" then "yellow"
        elif .src == "/vendor/infomax/mensen/icons/ampel_gruen_70x65.png" then "green"
        elif .src == "/vendor/infomax/mensen/icons/ampel_rot_70x65.png" then "red"
        else .src
        end),
      allergens: .allergens | map({
        allergen: {
          code: .allergen | .[0].value,
          name: .allergen | .[1].value
        }
      })
    })
  })
}
"""

def display_meal(meal, perspective):
    assert perspective in ("student", "employee", "guest")
    print(locale.currency(meal["price"][perspective]), end=" ")

    if "green" in meal["tags"]:
        cprint(meal["name"], "green", end=" ")
    elif "yellow" in meal["tags"]:
        cprint(meal["name"], "yellow", end=" ")
    elif "red" in meal["tags"]:
        cprint(meal["name"], "red", end=" ")
    else:
        print(meal["name"], end=" ")

    relevant_tags = set(meal["tags"]) - {"red", "green", "yellow"}
    if relevant_tags:
        print(f"({', '.join(relevant_tags)})")
    else:
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="menstruate")
    parser.add_argument("perspective", choices=["student", "employee", "guest"], nargs="?", default="student", help="Select the price category (default student)")
    parser.add_argument("--vegetarian", "-v", dest="restrictions", action="append_const", const=["vegetarian", "vegan"], help="Show vegetarian offers (implies vegan)")
    parser.add_argument("--vegan", "-V", dest="restrictions", action="append_const", const=["vegan"], help="Show vegan offers")
    parser.add_argument("--organic", "-o", dest="restrictions", action="append_const", const=["organic"], help="Show organic offers (BIO)")
    parser.add_argument("--climate", "-c", dest="restrictions", action="append_const", const=["climate"], help="Show climate-friendly offers")
    parser.add_argument("--green", "-g", dest="health", action="append_const", const="green", help="Show healthy offers")
    parser.add_argument("--yellow", "-y", dest="health", action="append_const", const="yellow", help="Show semi-healthy offers")
    parser.add_argument("--red", "-r", dest="health", action="append_const", const="red", help="Show unhealthy offers")
    parser.add_argument("--min", metavar="EUR", type=float, default=0, help="Only show offers above EUR euros")
    parser.add_argument("--max", metavar="EUR", type=float, default=float("inf"), help="Only show offers below EUR euros")
    args = parser.parse_args()

    # flatten multiple restrictions
    restrictions = set(chain.from_iterable(args.restrictions)) if args.restrictions else set()

    json_source = sys.stdin.read()
    json_object = jq(JQ_QUERY).transform(text=json_source)
    for group in json_object["groups"]:
        cprint(9 * " " + group["name"].upper(), attrs=["bold"])
        for meal in group["meals"]:
            if not args.health or set(args.health) & set(meal["tags"]):
                if not restrictions or restrictions & set(meal["tags"]):
                    price = meal["price"][args.perspective]
                    if price >= args.min and price <= args.max:
                        display_meal(meal, args.perspective)
        print()

