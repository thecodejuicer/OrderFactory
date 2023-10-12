import traceback

from confluent_kafka import KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.admin import AdminClient, NewTopic, ClusterMetadata
import os
import sys

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
    # client = KSQLdbClient('http://localhost:8088')

    ksql_queries = [
        "CREATE STREAM IF NOT EXISTS taco_shell_orders_stream( order_id VARCHAR KEY ) WITH( kafka_topic='taco_shell_orders', value_format='PROTOBUF', key_format='KAFKA');",
        "CREATE STREAM IF NOT EXISTS  pizza_cabin_orders_stream ( order_id VARCHAR KEY ) WITH (kafka_topic='pizza_cabin_orders', value_format='PROTOBUF', key_format='KAFKA');",
        "CREATE STREAM IF NOT EXISTS tennessee_baked_chicken_orders_stream ( order_id VARCHAR KEY ) WITH (kafka_topic='tennessee_baked_chicken_orders', value_format='PROTOBUF', key_format='KAFKA');",
        "CREATE OR REPLACE STREAM all_orders_stream WITH ( KAFKA_TOPIC = 'all_orders_stream', VALUE_FORMAT = 'PROTOBUF', KEY_FORMAT = 'KAFKA' ) AS SELECT * FROM taco_shell_orders_stream emit changes;",
        "INSERT INTO all_orders_stream SELECT * FROM pizza_cabin_orders_stream emit changes;",
        "INSERT INTO all_orders_stream SELECT * FROM tennessee_baked_chicken_orders_stream emit changes;",
        "CREATE TABLE IF NOT EXISTS customer_order_status_tbl ( order_id VARCHAR PRIMARY KEY, status VARCHAR, customer STRUCT<id VARCHAR, name VARCHAR, email VARCHAR>, factory STRUCT<name VARCHAR> ) WITH ( KAFKA_TOPIC = 'all_orders_stream', VALUE_FORMAT = 'PROTOBUF', KEY_FORMAT = 'KAFKA' );",
        "CREATE OR REPLACE TABLE customer_order_statuses WITH ( KAFKA_TOPIC = 'customer_order_statuses', VALUE_FORMAT = 'PROTOBUF', KEY_FORMAT = 'KAFKA' ) AS SELECT order_id, status, customer->id AS customer_id, customer->name AS customer_name, customer->email AS customer_email, factory->name AS factory_name FROM customer_order_status_tbl;"
    ]

    # for query in ksql_queries:
    #     client.ksql(query)


if __name__ == '__main__':
    client = AdminClient({'bootstrap.servers': 'localhost:9092'})
    create_topics(client)
    # create_ksql_objects()
