from money import Money
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer


class City(object):
    def __init__(self, city_name: str, state: str, zip_code: str):
        self.city_name = city_name
        self.state = state
        self.zip_code = zip_code


class MenuItem(object):
    def __init__(self, name: str, price: Money, cuisine: str):
        self.name = name
        self.price = Money(price)
        self.cuisine = cuisine