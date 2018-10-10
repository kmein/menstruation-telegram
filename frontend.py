from termcolor import colored, cprint
import argparse
import json
import locale
import sys

locale.setlocale(locale.LC_ALL, 'de_DE')

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
    parser.add_argument("perspective", choices=["student", "employee", "guest"], help="Select the price category")
    parser.add_argument("--vegetarian", help="Show vegetarian offers", dest='flags', action='append_const', const="vegetarian")
    parser.add_argument("--vegan", help="Show vegan offers", dest='flags', action='append_const', const="vegan")
    parser.add_argument("--organic", help="Show organic offers (BIO)", dest='flags', action='append_const', const="organic")
    parser.add_argument("--green", help="Show healthy offers", dest='flags', action='append_const', const="green")
    parser.add_argument("--yellow", help="Show semi-healthy offers", dest='flags', action='append_const', const="yellow")
    parser.add_argument("--red", help="Show unhealthy offers", dest='flags', action='append_const', const="red")
    parser.add_argument("--climate", help="Show climate-friendly offers", dest='flags', action='append_const', const="climate")
    parser.add_argument("--min", metavar="EUR", type=float, help="Only show offers above EUR euros", default=0)
    parser.add_argument("--max", metavar="EUR", type=float, help="Only show offers below EUR euros", default=float("inf"))
    args = parser.parse_args()

    # all vegan offers are automatically vegetarian
    if "vegetarian" in args.flags:
        args.flags.append("vegan")

    json_source = sys.stdin.read()
    json_object = json.loads(json_source)
    for group in json_object["groups"]:
        cprint(9 * " " + group["name"].upper(), attrs=["bold"])
        for meal in group["meals"]:
            if not args.flags or set(args.flags) & set(meal["tags"]):
                price = meal["price"][args.perspective]
                if price >= args.min and price <= args.max:
                    display_meal(meal, args.perspective)
        print()

