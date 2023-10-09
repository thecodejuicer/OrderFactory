import random

from factory import Order, LineItem, Item, Customer, FactoryLocation, Cuisine
from money import Money
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
from time import sleep
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
import socket

import protobuf.order_pb2 as order_pb2

import os
import sys

from schema import MenuItem

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

factories = dict[str, list[FactoryLocation]]()
customers = list[Customer]()
menu_items = list[MenuItem]()


def acked(err, msg):
    if err is not None:
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: %s" % (str(msg)))

def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

def mock_orders(exiting):
    customer_count = len(customers)
    factory_count = len(factories)

    beverages = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Beverage.name]
    southern = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Southern.name]
    hispanic = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Hispanic.name]
    italian = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Italian.name]

    kafka_config = {
        'bootstrap.servers': '127.0.0.1:9092',
    }
    producer = Producer(kafka_config)

    schema_registry_conf = {'url': 'http://127.0.0.1:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    protobuf_serializer = ProtobufSerializer(order_pb2.Order, schema_registry_client,
                                             {'use.deprecated.format': False})
    string_serializer = StringSerializer()

    while not exiting.is_set():
        factory = factories[list(factories.keys())[random.randint(0, factory_count - 1)]]
        factory_location: FactoryLocation = factory[random.randint(0, len(factory) - 1)]

        # Figure out which menu items are available based on the "factory's" cuisine.
        match factory_location.cuisine:
            case Cuisine.Italian.name:
                item_list = italian
            case Cuisine.Southern.name:
                item_list = southern
            case Cuisine.Hispanic.name:
                item_list = hispanic
            case _:
                item_list = beverages

        items_count = len(item_list)


        # Create a new order for a random customer.
        order = Order(customers[random.randint(0, customer_count-1)])
        random_item = item_list[random.randint(0, items_count-1)]

        order.add_line_item(LineItem(item=Item(name=random_item.name, price=random_item.price),
                                     quantity=random.randint(1,4)))

        topic = f'{factory_location.name.replace(" ","_").lower()}_orders'
        producer.produce(topic=topic,
                         key=string_serializer(str(order.id)),
                         value=protobuf_serializer(serialize_order(factory_location, order),
                                                   SerializationContext(topic, MessageField.VALUE))
                         )

        producer.flush()

        # Add a short pause so it isn't a crazy bombardment
        sleep(random.uniform(0.03, 0.5))


def serialize_order(factory: FactoryLocation, order: Order) -> order_pb2.Order:
    """
    Creates a protobuf serialized object from an order and a factory.
    :param factory: The factory the order belongs to.
    :param order: The order.
    :return: order_pb2.Order object.
    """
    order_buf = order.as_protobuf
    order_buf.factory.id = str(factory.id)
    order_buf.factory.name = factory.name
    order_buf.factory.location = factory.location

    return order_buf


def load_items():
    """
    Load menu items from a JSON file.
    :return: A list of MenuItems.
    """
    with open(script_directory + '/../resources/menu_items.json') as itemlist:
        menu_item_list = json.load(itemlist)

    return [MenuItem(name = menu_item['name'],
                     price=Money(menu_item['price'], currency=menu_item['currency']),
                     cuisine=menu_item['cuisine'])
            for menu_item in menu_item_list]


def load_factories():
    with open(script_directory + '/../resources/factories.json', mode='r') as f:
        factory_list = json.load(f)

        for factory in factory_list:
            factories[factory['name']] = list()
            for location in factory['locations']:
                factories[factory['name']].append(FactoryLocation(name=factory['name'],
                                                                  location=location,
                                                                  cuisine=factory['cuisine']))

    return factories


def load_customers():
    with open(script_directory + '/../resources/customers.json', mode='r') as f:
        customer_list = json.load(f)
        for customer in customer_list:
            customers.append(
                Customer(name=f"{customer['first_name']} {customer['last_name']}", email=customer['email']))

    return customers


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Load the factories!
    factories = load_factories()
    customers = load_customers()
    menu_items = load_items()

    # schema_registry_conf = {'url': 'http://127.0.0.1:8081'}
    # schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    # protobuf_serializer = ProtobufSerializer(order_pb2.Order, schema_registry_client,
    #                                          {'use.deprecated.format': False})
    # string_serializer = StringSerializer()

    # cust = customers[random.randint(0, 10)]
    # fctr = factories[list(factories.keys())[random.randint(0, 2)]]
    # loc = fctr[random.randint(0, len(fctr) - 1)]

    # order = Order(cust)
    # item = Item(name="A thing",price=Money('11.22', 'USD'))
    # order.add_line_item(LineItem(item=item, quantity=random.randint(1,10)))
    # order.add_line_item(LineItem(item=item, quantity=random.randint(1,10)))
    #
    # kafka_config = {
    #     'bootstrap.servers': '127.0.0.1:9092',
    # }
    #
    # producer = Producer(kafka_config)

    # topic = 'orders'
    # producer.produce(topic=topic,
    #                  key=string_serializer(str(order.id)),
    #                  value=protobuf_serializer(serialize_order(loc, order), SerializationContext(topic, MessageField.VALUE))
    #                  )
    #
    # producer.flush()

    exiting = threading.Event()

    def signal_handler(signum, frame):
        exiting.set()

    signal.signal(signal.SIGTERM, signal_handler)

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(mock_orders, exiting)

        try:
            while not exiting.is_set():
                pass
        except KeyboardInterrupt:
            exiting.set()
