from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
class City(object):
    def __init__(self, city_name: str, state: str, zip_code: str):
        self.city_name = city_name
        self.state = state
        self.zip_code = zip_code

