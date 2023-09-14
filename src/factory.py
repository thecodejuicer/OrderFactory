from typing import Any
from uuid import uuid4, UUID
from money import Money
from enum import Enum
from json import JSONEncoder


class Customer:
    def __init__(self, name: str, email: str = None):
        self.id = uuid4()
        self.name = name
        self.email = email


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


class Factory:
    def __init__(self, name: str, location: str):
        self.id = uuid4()
        self.name = name
        self.location = location
        self.orders = dict[UUID, Order]()

    def add_order(self, order: Order):
        """
        Add a new order.
        :type order: object
        """
        self.orders[order.id] = order


class OrderEncoder(JSONEncoder):
    def default(self, o: Order) -> Any:
        order_dict = {
            'id': str(o.id),
            'line_items': o.line_items.__dict__
        }
        return o.__dict__