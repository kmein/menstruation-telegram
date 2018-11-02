FROM python:3.7-slim

ENV MENSTRUATION_ENDPOINT=""

ADD menstruation-bot requirements.txt /app/
WORKDIR /app
RUN set -ex \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales \
    && locale-gen de_DE.UTF-8 \
    && pip install -r requirements.txt \
    && rm requirements.txt

CMD [ "python", "menstruation-bot" ]

