FROM alpine

RUN apk --update add python py-pip openssl ca-certificates bash git openssh-client go libc-dev make docker && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install --upgrade pip flask PyJWT docker gunicorn cryptography&& \
    apk del build-dependencies && rm -rf /var/cache/apk/*

ENV GOPATH /root/go

RUN go get github.com/GoogleCloudPlatform/docker-credential-gcr && \
    cd $GOPATH/src/github.com/GoogleCloudPlatform/docker-credential-gcr && \
    make && mv ./bin/docker-credential-gcr /usr/bin/docker-credential-gcr

WORKDIR /usr/src/app

COPY constants.py .
COPY ContMan.py .

EXPOSE 8080
ENTRYPOINT ["/usr/bin/gunicorn", "-b", ":8080", "ContMan:app"]