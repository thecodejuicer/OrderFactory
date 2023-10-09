import argparse
import random
from typing import Any

from factory import Order, LineItem, Item, Customer, FactoryLocation
from money import Money
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
from time import sleep
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
import socket

import protobuf.order_pb2 as order_pb2

import os
import sys

from schema import MenuItem

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

def main(args):
    topic = args.topic
    protobuf_deserializer = ProtobufDeserializer(order_pb2.Order, {'use.deprecated.format': False})
    consumer_conf = {'bootstrap.servers': '127.0.0.1:9092',
                     'group.id': 'py_order_consumer_v0',
                     'auto.offset.reset': 'earliest'}

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            order = protobuf_deserializer(msg.value(), SerializationContext(topic, MessageField.VALUE))

            if order is not None:
                print("User record {}:\n"
                      "\tOrder ID: {}\n"
                      "\tCustomer name: {}\n"
                      "\tFactory: {}\n"
                      "\tLocation: {}\n"
                      "\tItems: {}\n"
                      .format(msg.key(),
                              order.id,
                              order.customer.name,
                              order.factory.name,
                              order.factory.location,
                              order.line_items))
        except KeyboardInterrupt:
            break

    consumer.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Order Consumer")
    parser.add_argument('-t', dest="topic",help="Topic name")
    main(parser.parse_args())