import time

import streamlit as st
import pymongo
from pymongo import MongoClient
import pandas as pd

st.set_page_config(
    page_title="Customers with Orders",
    layout="wide"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


# @st.cache_data(ttl=1)
def get_data():
    db = client.kafka
    # items = db.customers.find({},{"_id":0}).limit(10)
    items = db.all_orders.aggregate([
        {
            '$limit': 10
        }, {
            '$group': {
                '_id': None,
                'uniqueValues': {
                    '$addToSet': '$CUSTOMER'
                }
            }
        }, {
            '$unwind': {
                'path': '$uniqueValues'
            }
        }, {
            '$replaceRoot': {
                'newRoot': '$uniqueValues'
            }
        }
    ])
    items = list(items)
    return items


st.sidebar.markdown("# Customers w/ Orders")
st.title("Customers with Orders")

placeholder = st.empty()

with placeholder.container():
    df = pd.DataFrame(get_data())
    df['ID'] = df['ID'].apply(lambda x: f'customer_view?ID={x}')

    column_config = {
        "ID": st.column_config.LinkColumn("ID")
    }

    st.dataframe(df, column_config=column_config, hide_index=True)
