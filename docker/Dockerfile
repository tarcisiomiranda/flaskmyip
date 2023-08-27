FROM alpine:3.18

ENV AMB=prod

RUN apk add python3 \
    && apk add py3-pip

COPY ./requirements.txt /srv/app/requirements.txt
COPY ./telegram.py /srv/app/telegram.py
COPY ./app.py /srv/app/app.py
COPY ./html /srv/app/html
COPY ./.env /srv/app/.env


RUN pip install -r /srv/app/requirements.txt

RUN rm -rf /var/lib/apk/* /tmp/* /var/tmp/*

RUN chown -R 1000:1000 /srv/app

WORKDIR /srv/app
COPY ./.env /srv/app/
RUN touch home_ip.txt

ENTRYPOINT [ "python3", "app.py" ]

CMD [ "" ]
