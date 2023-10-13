import os
import sys
import traceback

import docker
import requests
from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient, NewTopic, ClusterMetadata
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

def create_topics(admin_client):
    with open(script_directory + '\protobuf\order.proto') as schema_file:
        orders_schema = Schema(schema_file.read(), 'PROTOBUF')

    with open(script_directory + '\protobuf\customer.proto') as schema_file:
        customer_schema = Schema(schema_file.read(), 'PROTOBUF')

    topics_to_create = [
        {'name': 'customers', 'config': NewTopic('customers', num_partitions=10,
                                                 config={'cleanup.policy': 'compact', 'delete.retention.ms': '60000'}),
         'schema': customer_schema},
        {'name': 'pizza_cabin_orders', 'config': NewTopic('pizza_cabin_orders', num_partitions=10),
         'schema': orders_schema},
        {'name': 'taco_shell_orders', 'config': NewTopic('taco_shell_orders', num_partitions=10),
         'schema': orders_schema},
        {'name': 'tennessee_baked_chicken_orders',
         'config': NewTopic('tennessee_baked_chicken_orders', num_partitions=10),
         'schema': orders_schema}
    ]

    exiting_topics: ClusterMetadata = client.list_topics(timeout=10)

    topic_list = []
    schema_list = []
    for topic in topics_to_create:
        if exiting_topics.topics.get(topic['name'], None) is None:
            topic_list.append(topic['config'])

            if topic.get('schema', None):
                schema_list.append({'subject_name': topic['name'] + '-value', 'schema': topic['schema']})

    if len(topic_list) > 0:
        futures = client.create_topics(topic_list)

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
    endpoint = 'http://localhost:8083/connectors'

    with open(script_directory + '\..\kafka_connect\mongodb.json') as cfile:
        connect_config = cfile.read()
        response = requests.put(url=endpoint + '/mongodb_sink/config', data=connect_config,
                                headers={'Content-Type': 'application/json'})

        print(response.text)


if __name__ == '__main__':
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
    create_topics(admin_client)
    create_ksql_objects()
    create_connectors()