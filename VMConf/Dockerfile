FROM alpine:3.6

RUN apk --update add python py-pip openssl ca-certificates bash git openssh-client && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install --upgrade pip cffi && pip install paramiko                && \
    apk del build-dependencies && rm -rf /var/cache/apk/*

ADD start.py /start.py
ADD main.py /main.py
RUN chmod +x /start.py
ENTRYPOINT ["python","/start.py"]