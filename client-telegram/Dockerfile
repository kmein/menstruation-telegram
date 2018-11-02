FROM python:3.7-slim

ENV MENSTRUATION_ENDPOINT=""

ADD menstruation-bot requirements.txt /app/
WORKDIR /app
RUN set -ex \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales \
    && pip install -r requirements.txt \
    && rm requirements.txt \
    && locale -a

CMD [ "python", "menstruation-bot" ]

