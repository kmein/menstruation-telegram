FROM python:3.7-alpine3.8

ENV MENSTRUATION_ENDPOINT=""

ADD menstruation-bot requirements.txt /app/
WORKDIR /app

RUN set -ex \
    && apk add --no-cache tzdata \
    && pip install -r requirements.txt \
    && rm requirements.txt \
    \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

CMD [ "python", "menstruation-bot" ]

