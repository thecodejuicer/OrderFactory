import decimal
import time
from datetime import datetime
from decimal import Decimal

import streamlit as st
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import pandas as pd

st.set_page_config(
    page_title="Customer View",
    layout="centered",
    initial_sidebar_state='collapsed'
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=5)
def get_orders():
    db: Database = client.kafka

    query_params = st.experimental_get_query_params()
    items = (db.customer_order_status
             .find({"CUSTOMER_ID": query_params['ID'][0]})
             .sort("ORDER_DATE", -1))

    items = list(items)
    return items


@st.cache_data(ttl=5)
def get_customer():
    db: Database = client.kafka

    query_params = st.experimental_get_query_params()
    return db.customers.find_one({"id": query_params['ID'][0]})


st.sidebar.markdown("# Customer View")

placeholder = st.empty()

while True:
    with placeholder.container():
        df = pd.DataFrame(get_orders())
        customer = get_customer()
        st.title(f"Orders for {customer['name']}")

        for index, record in enumerate(df.to_dict('records')):
            with st.container():
                st.subheader(f"{record['FACTORY_NAME']} ", divider='blue')
                st.markdown(
                    f"**Date** {datetime.fromtimestamp(record['ORDER_DATE'] / 1000).strftime('%m-%d-%Y @ %I:%M %p')}")

                col1, col2 = st.columns(2)

                # with col2:
                #     # location_string = f"**Location**  \n{record['FACTORY']['NAME']}"
                #     location_string = f'''
                #         **Location**
                #         {record['FACTORY']['NAME']}
                #         {record['FACTORY']['CITY']} {record['FACTORY']['STATE']}, {record['FACTORY']['ZIP_CODE']}
                #     '''
                #
                #     st.markdown(location_string)

                with col1:
                    heading = '''
                    **Items Ordered**  
                    '''

                    items_ordered = [f"{item['QUANTITY']} x {item['NAME']} @ \${item['PRICE']}" for item in
                                     record['ITEMS']]
                    # for item in record['LINE_ITEMS']:
                    #     items_ordered = f'''{items_ordered}
                    # | {item['NAME']} | {item['QUANTITY']} | {item['PRICE']} |
                    #     '''
                    st.markdown(heading + '  \n'.join(items_ordered))

                    total = sum([Decimal(item['PRICE']) for item in record['ITEMS']])

                with col2:
                    st.metric(
                        "Order Status",
                        str.title(record.get('STATUS', 'Unknown'))
                    )

                st.markdown(f"#### Total: {'${:10.2f}'.format(total)}")

        # st.dataframe(df,hide_index=True)
    time.sleep(5)
