FROM python:2-alpine


RUN apk --update add python py-pip openssl ca-certificates bash git openssh-client && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install --upgrade pip cryptography && \
    apk del build-dependencies && rm -rf /var/cache/apk/*

WORKDIR /usr/src/app

COPY main.py .
COPY do.py .
COPY vt.py .
COPY start.py .

ENTRYPOINT [ "python", "./start.py" ]