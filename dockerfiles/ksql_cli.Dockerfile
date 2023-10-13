FROM confluentinc/cp-ksqldb-cli:7.5.0

ADD "../resources/create_initial_streams.ksql" /var/scripts/create_initial_streams.ksql