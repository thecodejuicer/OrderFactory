import time

import streamlit as st
import pymongo
from pymongo import MongoClient
import pandas as pd

st.set_page_config(
    page_title="Customers",
    layout="wide"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=1)
def get_data():
    db = client.kafka
    items = db.customers.find({},{"_id":0}).limit(10)
    items = list(items)
    return items

st.sidebar.markdown("# Customers")
st.title("Customers")

placeholder = st.empty()

while True:
    with placeholder.container():
        st.dataframe(pd.DataFrame(get_data()))
        time.sleep(1)