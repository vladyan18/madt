FROM madt/client

ADD ./lib/router.py router.py
ADD ./lib/entrypoint.sh entrypoint.sh

RUN apk --no-cache add quagga iptables && \
	mkdir /var/log/zebra && \
    chown -R quagga:quagga /var/log/zebra && \
    chown -R quagga:quagga /var/run/quagga

RUN apk update && apk add bash
RUN apk add tshark 
RUN apk add nano

ENTRYPOINT sh entrypoint.sh