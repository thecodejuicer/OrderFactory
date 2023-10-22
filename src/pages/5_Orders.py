import time
import uuid
from datetime import datetime
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
    items = db.all_orders.find({},{"_id":0}).limit(100)
    items = list(items)
    return items

st.sidebar.markdown("# Orders")
st.title("Orders")

placeholder = st.empty()

column_config = {
    "ORDER_DATE": "Order Date",
    "LINE_ITEMS": "Items Ordered",
    "CUSTOMER": "Customer"
}

with placeholder.container():
    df = pd.DataFrame(get_data())
    df['LINE_ITEMS'] = df['LINE_ITEMS'].apply(lambda x: [f"{li['NAME']}: {li['QUANTITY']}" for li in x])
    df['ORDER_DATE'] = df['ORDER_DATE'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    df['Customer View'] = df['CUSTOMER'].apply(
        lambda x: '<a href="Customer_Orders?ID={}" target="_self">Customer View</a>'.format(x['ID']))
    df['CUSTOMER'] = df['CUSTOMER'].apply(lambda x: f"{x['NAME']} ({x['EMAIL']})")
    st.write(df[['ORDER_DATE', 'LINE_ITEMS', 'CUSTOMER', 'Customer View']].to_html(escape=False, index=False),
             unsafe_allow_html=True)
