from setuptools import setup

setup(
    name="menstruation",
    version="0.1.0",
    description="Berlin Uni-Mensa Telegram Bot",
    author="Kierán Meinhardt",
    author_email="kieran.meinhardt@gmail.com",
    packages=["menstruation"],
    scripts=["bin/menstruation-telegram"],
    install_requires=["requests==2.22.0",
                      "emoji==0.5.3",
                      "python-telegram-bot==12.2",
                      "redis==3.3.8"],
)
