import time

import streamlit as st
import pymongo
from pymongo import MongoClient
import pandas as pd

from queries import state_totals

st.set_page_config(
    page_title="Pizza Cabin Stats",
    layout="wide"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=5)
def get_data():
    db = client.kafka
    items = db.all_orders.aggregate(state_totals('Taco Shell'))
    items = list(items)
    return items


st.sidebar.markdown("# Taco Shell")
st.title("Taco Shell")

placeholder = st.empty()

while True:
    with placeholder.container():
        frame = pd.DataFrame(get_data())

        column_config = {
            "state": "State",
            "totalOrders": "Total Orders",
            "totalSalesAmount": st.column_config.NumberColumn("Total Sales", format="$ %.2f")
        }

        col1, = st.columns(1)
        with col1:
            st.dataframe(frame[['state', 'totalOrders', 'totalSalesAmount']], column_config=column_config, hide_index=True)

        time.sleep(5)
