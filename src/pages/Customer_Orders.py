import math
import time
import uuid
from datetime import datetime
from decimal import Decimal

import streamlit as st
import pymongo
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import StringSerializer, MessageField, SerializationContext
from money import Money
from pymongo import MongoClient
from pymongo.database import Database
import pandas as pd

import json
from confluent_kafka import Producer

import protobuf.order_pb2 as order_pb2

from factory import LineItem, Item, Order, Customer, FactoryLocation, OrderStatus

st.set_page_config(
    page_title="Customer View",
    layout="centered"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


def get_orders():
    db: Database = client.kafka

    query_params = st.experimental_get_query_params()

    items = (db.customer_order_status
             .find({"CUSTOMER_ID": query_params['ID'][0]})
             .sort("ORDER_DATE", -1))

    items = list(items)
    return items


def get_customer():
    db: Database = client.kafka

    query_params = st.experimental_get_query_params()
    return db.customers.find_one({"id": query_params['ID'][0]})


def kafka_status(err, msg):
    if err is not None:
        st.error("Producer failed: {}".format(err))
    else:
        st.toast("Order status update sent.")


def update_status(order_id, status):
    db: Database = client.kafka
    orders = db.all_orders.aggregate([{'$match': {'ID': order_id}}, {'$project': {'_id': 0}}])
    full_order = list(orders)[0]

    company_topic = str(full_order['FACTORY']['NAME']).lower().replace(' ', '_') + '_orders'
    full_order['STATUS'] = status

    customer = Customer(name=full_order['CUSTOMER']['NAME'],
                        email=full_order['CUSTOMER']['EMAIL'],
                        zip_code=full_order['FACTORY'][
                            'ZIP_CODE'])  # by design for the demo, factory and customer zip are the same. This is not a bug. Not the "correct" way to do it, but not a bug.

    line_items = list[LineItem]()
    for line_item in full_order['LINE_ITEMS']:
        item = Item(name=line_item['NAME'],
                    price=Money(line_item['UNIT_PRICE'], line_item['CURRENCY']),
                    id=uuid.UUID(line_item['ID']))
        line_items.append(LineItem(item, line_item['QUANTITY']))

    order = Order(customer=customer,
                  status=OrderStatus[full_order['STATUS']],
                  id=uuid.UUID(full_order['ID']),
                  line_items=line_items)

    factory = FactoryLocation(name=full_order['FACTORY']['NAME'],
                              state=full_order['FACTORY']['STATE'],
                              city=full_order['FACTORY']['CITY'],
                              zip_code=full_order['FACTORY']['ZIP_CODE'],
                              cuisine='fix later maybe')
    order_serialized = order.as_protobuf
    order_serialized.factory.id = str(factory.id)
    order_serialized.factory.name = factory.name
    order_serialized.factory.city = factory.city
    order_serialized.factory.state = factory.state
    order_serialized.factory.zip_code = factory.zip_code
    order_serialized.order_date = math.floor(time.time_ns() / 1000000)

    schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
    order_serializer = ProtobufSerializer(order_pb2.Order, schema_registry_client, {'use.deprecated.format': False})
    string_serializer = StringSerializer()

    producer = Producer(**st.secrets['kafka'])
    producer.produce(topic=company_topic,
                     key=string_serializer(full_order['ID']),
                     value=order_serializer(order_serialized,
                                            SerializationContext(company_topic, MessageField.VALUE)),
                     callback=kafka_status)
    producer.flush()

    return True


with st.sidebar:
    st.markdown("# Customer View")

    st.markdown("### Set Order Status")

    customer_orders = get_orders()
    if st.button("Processing"):
        for order in customer_orders:
            update_status(order['ID'], 'PROCESSING')

    if st.button("Delivered"):
        for order in customer_orders:
            update_status(order['ID'], 'DELIVERED')

placeholder = st.empty()
while True:
    with placeholder.container():
        customer_orders = get_orders()
        df = pd.DataFrame(customer_orders)
        customer = get_customer()
        st.title(f"Orders for {customer['name']}")

        for index, record in enumerate(df.to_dict('records')):
            with st.container():
                st.subheader(f"{record['FACTORY_NAME']} ", divider='blue')
                st.markdown(
                    f"**Date** {datetime.fromtimestamp(record['ORDER_DATE'] / 1000).strftime('%m-%d-%Y @ %I:%M %p')}")

                col1, col2 = st.columns(2)

                with col1:
                    heading = '''
                    **Items Ordered**  
                    '''

                    items_ordered = [f"{item['QUANTITY']} x {item['NAME']} @ \${item['PRICE']}" for item in
                                     record['ITEMS']]

                    st.markdown(heading + '  \n'.join(items_ordered))

                    total = sum([Decimal(item['PRICE']) for item in record['ITEMS']])

                with col2:
                    st.metric(
                        "Order Status",
                        str.title(record.get('STATUS', 'Unknown'))
                    )

                st.markdown(f"#### Total: {'${:10.2f}'.format(total)}")

        # st.dataframe(df,hide_index=True)
    time.sleep(.1)
