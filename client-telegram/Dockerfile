FROM python:3.7-slim

ENV MENSTRUATION_ENDPOINT=""

ADD menstruation-bot requirements.txt /app/
WORKDIR /app

RUN set -ex \
    && pip install -r requirements.txt \
    && rm requirements.txt \

CMD [ "python", "menstruation-bot" ]

