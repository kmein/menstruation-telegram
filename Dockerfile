FROM python:3.7-alpine3.9

ADD bot.py client.py requirements.txt /app/

ENV TZ=Europe/Berlin \
    MENSTRUATION_TOKEN='TOKEN' \
    MENSTRUATION_ENDPOINT=http://127.0.0.1:8000 \
    MENSTRUATION_DIR=/data

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

VOLUME ["$MENSTRUATION_DIR"]

CMD [ "/usr/local/bin/python", "bot.py" ]
