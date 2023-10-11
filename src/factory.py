import uuid
from typing import Any
from uuid import uuid4, UUID
from money import Money
from enum import Enum
from json import JSONEncoder
import protobuf.order_pb2 as OrderPbuf
import json

class Cuisine(Enum):
    Italian = 1
    Hispanic = 2
    Southern = 3
    Beverage = 4


class Customer:
    def __init__(self, name: str, email: str, zip_code: str):
        self.id = uuid.uuid5(uuid.NAMESPACE_URL, email)
        self.name = name
        self.email = email
        self.zip_code = zip_code


class Item:
    def __init__(self, name: str, price: Money, description: str = None):
        self.id = uuid4()
        self.name = name
        self.price = price
        self.description = description


class LineItem:
    quantity: int

    def __init__(self, item: Item, quantity: int = 1):
        self.id = uuid4()
        self.item = item
        self.quantity = quantity

    @property
    def price(self) -> Money:
        return self.item.price * self.quantity

    @property
    def unit_price(self) -> Money:
        return self.item.price

    @property
    def currency(self) -> str:
        return self.item.price.currency

    @property
    def as_dict(self) -> dict:
        line_item = dict()
        line_item['id'] = str(self.item.id)
        line_item['name'] = self.item.name
        line_item['unit_price'] = str(self.unit_price)
        line_item['quantity'] = self.quantity
        line_item['price'] = str(self.price)
        return line_item


class OrderStatus(Enum):
    NEW = 1
    RECEIVED = 2
    PROCESSING = 3
    SHIPPING = 4
    DELIVERED = 5
    COMPLETED = 6
    LOST = 7
    UNKNOWN = 8


class Order:
    def __init__(self, customer: Customer):
        self.id = uuid4()
        self.line_items = list[LineItem]()
        self.customer = customer
        self._status: OrderStatus = OrderStatus.NEW

    @property
    def total(self) -> Money:
        sum_total = Money(currency='USD')
        prices = [total.price for total in self.line_items]
        for price in prices:
            sum_total = sum_total + price

        return sum_total

    def add_line_item(self, line_item: LineItem):
        self.line_items.append(line_item)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: OrderStatus):
        self._status = status

    @property
    def as_dict(self):
        order = dict()
        order['id'] = str(self.id)
        # order['line_items'] = [json.loads(json.dumps(li, cls=LineItemEncoder)) for li in self.line_items]
        order['line_items'] = [li.as_dict for li in self.line_items]
        order['customer'] = {'id': str(self.customer.id),
                             'name': self.customer.name,
                             'email': self.customer.email}
        order['status'] = self.status.name

        return order

    @property
    def as_protobuf(self):
        buf = OrderPbuf.Order()
        buf.id = str(self.id)

        for li in self.line_items:
            line_item = buf.line_items.add()
            line_item.id = str(li.id)
            line_item.name = li.item.name
            line_item.unit_price = str(li.unit_price.amount)
            line_item.quantity = li.quantity
            line_item.price = str(li.price.amount)
            line_item.currency = li.currency
        buf.customer.id = str(self.customer.id)
        buf.customer.name = self.customer.name
        buf.customer.email = self.customer.email

        buf.status = self.status.name

        return buf


class FactoryLocation:
    def __init__(self, name: str, state: str, city: str, zip_code: str, cuisine: str):
        self.id = uuid4()
        self.name = name
        self.state = state
        self.city = city
        self.zip_code = zip_code
        self.cuisine = cuisine