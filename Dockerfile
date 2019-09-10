FROM python:3.7-alpine3.10

ADD *.py requirements.txt /app/

ENV TZ=Europe/Berlin \
    MENSTRUATION_TOKEN='TOKEN' \
    MENSTRUATION_ENDPOINT=http://127.0.0.1:8000

WORKDIR /app

RUN set -ex \
    && apk add --no-cache tzdata \
                          openssl-dev \
    && apk add --no-cache --virtual .build-deps \
                                    build-base \
                                    python3-dev \
                                    libffi-dev \
    && pip install -r requirements.txt \
    && rm requirements.txt \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apk del .build-deps

LABEL author="Kierán Meinhardt <kieran.meinhardt@gmail.com>" \
      maintainer="QttyLog <qttylog@gmail.com>" \
      github="https://github.com/kmein/menstruation-telegram"

CMD [ "/usr/local/bin/python", "bot.py" ]
