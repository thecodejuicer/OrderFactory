FROM cnfldemos/kafka-connect-datagen:0.6.2-7.5.0

ENV CONNECT_PLUGIN_PATH: "/usr/share/java,/usr/share/confluent-hub-components"
USER root

#RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:1.11.0
ADD --chmod=644 "certs/caadmin-netskope.crt" /tmp/caadmin-netskope.crt
ADD --chmod=644 "certs/*.pem" /tmp/

RUN cat /tmp/cacert.pem /tmp/caadmin-netskope.crt > /etc/pki/ca-trust/source/anchors/cacert-with-netskope.pem \
    && update-ca-trust \
    && mkdir -p /var/private/ssl \
#    # Add Netskope cert to java keystore
    && keytool -importcert -file /tmp/caadmin-netskope.crt -cacerts -keypass changeit -storepass changeit -noprompt -alias netskope \
    && confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:1.11.0 \
    && rm /tmp/*.crt \