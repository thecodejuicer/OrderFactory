import time

import streamlit as st
import pymongo
from pymongo import MongoClient
import pandas as pd

st.set_page_config(
    page_title="Customer View",
    layout="wide"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


# @st.cache_data(ttl=1)
def get_data():
    db = client.kafka
    query_params = st.experimental_get_query_params()
    items = db.all_orders.find({"CUSTOMER.ID":query_params['ID'][0]},{"_id":0})

    items = list(items)
    return items


st.sidebar.markdown("# Customers View")
st.title("Customers View")

placeholder = st.empty()

with placeholder.container():
    df = pd.DataFrame(get_data())

    st.dataframe(df,hide_index=True)
