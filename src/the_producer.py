import json
import os
import random
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from money import Money

import protobuf.order_pb2 as order_pb2
from factory import Order, LineItem, Item, Customer, FactoryLocation, Cuisine
from schema import MenuItem, City

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


def mock_orders(exiting_event):
    # Separate menu items into their cuisine types.
    beverages = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Beverage.name]
    southern = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Southern.name]
    hispanic = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Hispanic.name]
    italian = [menu_item for menu_item in menu_items if menu_item.cuisine == Cuisine.Italian.name]

    # region Kafka config
    kafka_config = {
        'bootstrap.servers': '127.0.0.1:9092',
    }
    producer = Producer(kafka_config)
    schema_registry_conf = {'url': 'http://127.0.0.1:8081'}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    protobuf_serializer = ProtobufSerializer(order_pb2.Order, schema_registry_client,
                                             {'use.deprecated.format': False})
    string_serializer = StringSerializer()
    # endregion Kafka config

    factory_count = len(factories)
    customer_count = len(customers)

    # Begin data generation
    while not exiting_event.is_set():
        customer = customers[random.randint(0, customer_count - 1)]
        # Select a random "factory"
        factory_locations = factories[list(factories.keys())[random.randint(0, factory_count - 1)]]
        # Base the location on the customer's zip.
        factory_location: FactoryLocation = next(location for location in factory_locations
                                                 if location.zip_code == customer.zip_code)

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
        order = Order(customer)
        random_item = item_list[random.randint(0, items_count - 1)]
        random_beverage = beverages[random.randint(0, len(beverages) - 1)]

        order.add_line_item(LineItem(item=Item(name=random_item.name, price=random_item.price),
                                     quantity=random.randint(1, 4)))
        order.add_line_item(LineItem(item=Item(name=random_beverage.name, price=random_beverage.price),
                                     quantity=1))

        topic = f'{factory_location.name.replace(" ", "_").lower()}_orders'
        producer.produce(topic=topic,
                         key=string_serializer(str(order.id)),
                         value=protobuf_serializer(serialize_order(factory_location, order),
                                                   SerializationContext(topic, MessageField.VALUE))
                         )

        producer.flush()

        # Add a short pause, so it isn't a crazy bombardment
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
    order_buf.factory.city = factory.city
    order_buf.factory.state = factory.state
    order_buf.factory.zip_code = factory.zip_code

    return order_buf


def load_cities() -> list[City]:
    """
    Load all the cities.
    :return: A list of U.S. cities.
    """

    with open(script_directory + '/../resources/US_cities.json') as cities_file:
        cities_list = json.load(cities_file)

    return [City(city_name=city['city_name'], state=city['state'], zip_code=city['zip_code']) for city in cities_list]


def load_items() -> list[MenuItem]:
    """
    Load menu items from a JSON file.
    :return: A list of MenuItems.
    """
    with open(script_directory + '/../resources/menu_items.json') as menu_items_file:
        menu_item_list = json.load(menu_items_file)

    return [MenuItem(name=menu_item['name'],
                     price=Money(menu_item['price'], currency=menu_item['currency']),
                     cuisine=menu_item['cuisine'])
            for menu_item in menu_item_list]


def load_factories() -> dict[str, list[FactoryLocation]]:
    """
    Load factories and assign locations for all the cities.
    :return: dict[str, list[FactoryLocation]]
    """
    cities = load_cities()

    with open(script_directory + '/../resources/factories.json', mode='r') as factories_file:
        factory_list = json.load(factories_file)

        for factory in factory_list:
            factories[factory['name']] = list()

            for city in cities:
                factories[factory['name']].append(FactoryLocation(name=factory['name'],
                                                                  state=city.state,
                                                                  city=city.city_name,
                                                                  zip_code=city.zip_code,
                                                                  cuisine=factory['cuisine']))

    return factories


def load_customers() -> list[Customer]:
    with open(script_directory + '/../resources/customers_with_zip.json', mode='r') as f:
        customer_list = json.load(f)
        for customer in customer_list:
            customers.append(
                Customer(name=f"{customer['first_name']} {customer['last_name']}", email=customer['email'],
                         zip_code=customer['zip_code']))

    return customers


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Load the factories!
    factories = load_factories()
    customers = load_customers()
    menu_items = load_items()

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
