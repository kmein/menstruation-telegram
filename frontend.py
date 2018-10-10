from termcolor import colored, cprint
import argparse
import json
import locale
import itertools
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
    parser.add_argument("-v", "--vegetarian", dest="restrictions", action="append_const", const=["vegetarian", "vegan"], help="Show vegetarian offers (implies vegan)")
    parser.add_argument("-V", "--vegan", dest="restrictions", action="append_const", const=["vegan"], help="Show vegan offers")
    parser.add_argument("-o", "--organic", dest="restrictions", action="append_const", const=["organic"], help="Show organic offers (BIO)")
    parser.add_argument("-c", "--climate", dest="restrictions", action="append_const", const=["climate"], help="Show climate-friendly offers")
    parser.add_argument("-g", "--green", dest="health", action="append_const", const="green", help="Show healthy offers")
    parser.add_argument("-y", "--yellow", dest="health", action="append_const", const="yellow", help="Show semi-healthy offers")
    parser.add_argument("-r", "--red", dest="health", action="append_const", const="red", help="Show unhealthy offers")
    parser.add_argument("--min", metavar="EUR", type=float, default=0, help="Only show offers above EUR euros")
    parser.add_argument("--max", metavar="EUR", type=float, default=float("inf"), help="Only show offers below EUR euros")
    args = parser.parse_args()

    restrictions = set(sum(args.restrictions, [])) if args.restrictions else set()

    json_source = sys.stdin.read()
    json_object = json.loads(json_source)
    for group in json_object["groups"]:
        cprint(9 * " " + group["name"].upper(), attrs=["bold"])
        for meal in group["meals"]:
            if not args.health or set(args.health) & set(meal["tags"]):
                if not restrictions or restrictions & set(meal["tags"]):
                    price = meal["price"][args.perspective]
                    if price >= args.min and price <= args.max:
                        display_meal(meal, args.perspective)
        print()

