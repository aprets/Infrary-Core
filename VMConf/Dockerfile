FROM alpine:3.6

RUN apk --update add python py-pip openssl ca-certificates bash git openssh-client && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install --upgrade pip cffi && pip install paramiko requests&& \
    apk del build-dependencies && rm -rf /var/cache/apk/*

COPY constants.py /
ADD VMConf/start.py /start.py
RUN chmod +x /start.py
ENTRYPOINT ["python","/start.py"]