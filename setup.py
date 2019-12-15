from setuptools import setup

setup(
    name="menstruation",
    version="0.1.0",
    description="Berlin Uni-Mensa Telegram Bot",
    author="Kierán Meinhardt",
    author_email="kieran.meinhardt@gmail.com",
    packages=["menstruation"],
    scripts=["bin/menstruation-telegram"],
    install_requires=["requests", "emoji", "python-telegram-bot", "redis"],
)
