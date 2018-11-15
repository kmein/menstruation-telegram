FROM python:3.7-slim

ADD menstruation-bot requirements.txt /app/
WORKDIR /app
RUN set -ex \
    && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales \
    && sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen \
    && echo 'LANG="de_DE.UTF-8"'>/etc/default/locale \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG=de_DE.UTF-8 \
    && pip install -r requirements.txt \
    && rm requirements.txt

CMD [ "/usr/local/bin/python", "menstruation-bot" ]
