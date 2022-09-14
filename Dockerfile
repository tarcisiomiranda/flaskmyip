FROM alpine:3.15.0

RUN apk add python3 \
    && apk add py3-pip

COPY ./requirements.txt /src/app/requirements.txt

COPY ./app.py /src/app/app.py

RUN pip install -r /src/app/requirements.txt

RUN rm -rf /var/lib/apk/* /tmp/* /var/tmp/*

RUN chown -R 1000:1000 /src/app

WORKDIR /src/app

ENTRYPOINT [ "python3", "app.py" ]

CMD [ "" ]
