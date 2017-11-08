FROM alpine:3.6

ENV REQUIREMENTS "YES"
ENV KEY """"""


RUN apk --update add python py-pip openssl ca-certificates bash git && \
    apk --update add --virtual build-dependencies python-dev libffi-dev openssl-dev build-base && \
    pip install --upgrade pip cffi && pip install ansible                && \
    apk del build-dependencies && rm -rf /var/cache/apk/*               && \
    mkdir -p /etc/ansible

ADD requirements.yml /requirements.yml

ADD infraryAnsibleLauncher.sh /usr/local/bin/infraryAnsibleLauncher
RUN chmod +x /usr/local/bin/infraryAnsibleLauncher
CMD ["/bin/bash","/usr/local/bin/infraryAnsibleLauncher"]