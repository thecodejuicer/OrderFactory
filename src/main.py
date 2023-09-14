import random

from factory import Order, LineItem, Item, Customer, Factory
from money import Money
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
from time import sleep
from confluent_kafka import Producer
import socket

import os
import sys

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

factories = dict[str, list[Factory]]()
customers = list[Customer]()

def acked(err, msg):
    if err is not None:
        if err is not None:
            print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
        else:
            print("Message produced: %s" % (str(msg)))


def mock_orders(exiting):
    customer_count = len(customers)
    factory_count = len(factories)

    kafka_config = {
        'bootstrap.servers': '127.0.0.1:9092',
        'client.id': socket.gethostname()
    }

    producer = Producer(kafka_config)

    while not exiting.is_set():
        customer = customers[random.randint(0, customer_count-1)]
        factory = factories[list(factories.keys())[random.randint(0, factory_count-1)]]
        location = factory[random.randint(0, len(factory)-1)]

        order = Order(customer)
        item = Item(name="A thing",price=Money('11.22', 'USD'))
        order.add_line_item(LineItem(item=item, quantity=random.randint(1,10)))
        location.add_order(order)

        producer.produce('orders', key=order.id, value=json.dumps(order), callback=acked)
        print('produced')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Load the factories!
    with open(script_directory + '/../resources/factories.json', mode='r') as f:
        factory_list = json.load(f)

        for factory in factory_list:
            factories[factory['name']] = list()
            for location in factory['locations']:
                factories[factory['name']].append(Factory(name=factory['name'], location=location))

    # And now some customers...
    with open(script_directory + '/../resources/customers.json', mode='r') as f:
        customer_list = json.load(f)
        for customer in customer_list:
            customers.append(
                Customer(name=f"{customer['first_name']} {customer['last_name']}", email=customer['email']))

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
