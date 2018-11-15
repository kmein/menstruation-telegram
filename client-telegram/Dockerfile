FROM python:3.7-alpine3.8

ADD menstruation-bot requirements.txt /app/
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

CMD [ "/usr/local/bin/python", "menstruation-bot" ]
