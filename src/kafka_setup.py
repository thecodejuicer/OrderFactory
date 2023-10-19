import json
import os
import sys
import traceback

import docker
import requests
from confluent_kafka import KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic, ClusterMetadata
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

import protobuf.customer_pb2 as customer_pb2
from factory import Customer

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

kafka_config = {
    'bootstrap.servers': '127.0.0.1:9092',
}

def delivery_report(err, msg):
    """
    Reports the failure of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return


def create_topics(admin_client):
    with open(script_directory + '\protobuf\order.proto') as schema_file:
        orders_schema = Schema(schema_file.read(), 'PROTOBUF')

    with open(script_directory + '\protobuf\customer.proto') as schema_file:
        customer_schema = Schema(schema_file.read(), 'PROTOBUF')

    topics_to_create = [
        {'name': 'customers', 'config': NewTopic('customers', num_partitions=10,
                                                 config={'cleanup.policy': 'compact'}),
         'schema': customer_schema},
        {'name': 'pizza_cabin_orders', 'config': NewTopic('pizza_cabin_orders', num_partitions=10),
         'schema': orders_schema},
        {'name': 'taco_shell_orders', 'config': NewTopic('taco_shell_orders', num_partitions=10),
         'schema': orders_schema},
        {'name': 'tennessee_baked_chicken_orders',
         'config': NewTopic('tennessee_baked_chicken_orders', num_partitions=10),
         'schema': orders_schema}
    ]

    exiting_topics: ClusterMetadata = admin_client.list_topics(timeout=10)

    topic_list = []
    schema_list = []
    for topic in topics_to_create:
        if exiting_topics.topics.get(topic['name'], None) is None:
            topic_list.append(topic['config'])

            if topic.get('schema', None):
                schema_list.append({'subject_name': topic['name'] + '-value', 'schema': topic['schema']})

    if len(topic_list) > 0:
        futures = admin_client.create_topics(topic_list)

        try:
            for k, future in futures.items():
                print(f"type(k): {type(k)}")
                print(f"type(v): {type(future)}")
                print(future.result())

            if len(schema_list) > 0:
                schema_registry_conf = {'url': 'http://127.0.0.1:8081'}
                schema_registry_client = SchemaRegistryClient(schema_registry_conf)
                for schema in schema_list:
                    schema_registry_client.register_schema(schema['subject_name'], schema['schema'])

        except KafkaError:
            print(traceback.format_exc())

    else:
        print("No topics added.")


def create_ksql_objects():
    """
    Since the ksql libraries for Python are outdated, this runs the ksqldb cli with a script.
    :return:
    """
    client = docker.from_env()
    ksql_container = client.containers.get('ksqldb-cli')
    result = ksql_container.exec_run("ksql --file /var/scripts/create_initial_streams.ksql http://ksqldb-server:8088")

    print(result.output)


def create_connectors():
    """
    Creates all the connectors. It uses PUT on purpose, just in case the connector already exists.
    """
    endpoint = 'http://localhost:8083/connectors'

    with open(script_directory + '\..\kafka_connect\mongo_all_orders_stream.json') as cfile:
        connect_config = cfile.read()
        response = requests.put(url=endpoint + '/mongodb_sink/config', data=connect_config,
                                headers={'Content-Type': 'application/json'})

        print(response.text)

    with open(script_directory + '\..\kafka_connect\customer_stream.json') as cfile:
        connect_config = cfile.read()
        response = requests.put(url=endpoint + '/mongodb_customer_sink/config', data=connect_config,
                                headers={'Content-Type': 'application/json'})

        print(response.text)

    with open(script_directory + '\..\kafka_connect\customer_order_sink.json') as cfile:
        connect_config = cfile.read()
        response = requests.put(url=endpoint + '/mongodb_customer_order_sink/config', data=connect_config,
                                headers={'Content-Type': 'application/json'})

        print(response.text)

    with open(script_directory + '\..\kafka_connect\mongo_anonymized_orders_sink.json') as cfile:
        connect_config = cfile.read()
        response = requests.put(url=endpoint + '/mongodb_anonymized_order_sink/config', data=connect_config,
                                headers={'Content-Type': 'application/json'})

        print(response.text)


def get_protobuf_serializer(protobuf_schema) -> ProtobufSerializer:
    schema_registry_conf = {'url': 'http://127.0.0.1:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    return ProtobufSerializer(protobuf_schema, schema_registry_client, {'use.deprecated.format': False})


def seed_data():
    with open(script_directory + '/../resources/customers_with_zip.json', mode='r') as f:
        customer_list = json.load(f)

        producer = Producer(kafka_config)

        protobuf_serializer = get_protobuf_serializer(customer_pb2.Customer)
        string_serializer = StringSerializer()
        topic = 'customers'
        for customer in customer_list:
            customer_obj = Customer(name=f"{customer['first_name']} {customer['last_name']}", email=customer['email'],
                                    zip_code=customer['zip_code'])

            producer.produce(topic=topic, key=string_serializer(str(customer_obj.id)),
                             value=protobuf_serializer(customer_obj.as_protobuf(),
                                                       SerializationContext(topic, MessageField.VALUE)),
                             callback=delivery_report)

        producer.flush()


if __name__ == '__main__':
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
    create_topics(admin_client)
    create_ksql_objects()
    create_connectors()
    seed_data()
