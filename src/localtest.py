import random

from factory import Order, LineItem, Item, Customer, FactoryLocation, OrderEncoder
from money import Money
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
from time import sleep
from confluent_kafka import Producer
import socket

item = Item(name="A thing",price=Money('11.22', 'USD'))
order = Order(Customer('Test customer'))
order.add_line_item(LineItem(item, 10))

print(json.dumps(order, cls=OrderEncoder))
