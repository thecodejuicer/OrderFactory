import time

import streamlit as st
import altair as alt
import pymongo
from pymongo import MongoClient
import pandas as pd

from queries import state_totals, item_order_totals

company_name = 'Taco Shell'

st.set_page_config(
    page_title=f"{company_name} Stats",
    layout="wide"
)


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=1)
def get_ts_item_sales_data():
    db = client.kafka
    items = db.anonymized_orders_by_state.aggregate(item_order_totals(company_name))
    return list(items)


st.sidebar.markdown(f"# {company_name}")
st.markdown('![Taco Shell.](app/static/taco_shell_logo.png)')

placeholder = st.empty()

while True:
    with placeholder.container():
        items_sold_df = pd.DataFrame(get_ts_item_sales_data())

        rev_col, qty_col = st.columns(2)

        with rev_col:
            total_revenue = items_sold_df[['REVENUE']].sum()
            st.metric("Total Revenue", '${:10.2f}'.format(total_revenue['REVENUE']))

        with qty_col:
            qty_sold = items_sold_df[['QUANTITY_SOLD']].sum()
            st.metric("Items Sold", qty_sold['QUANTITY_SOLD'])

        st.subheader('Item Revenue by State', divider='blue')
        chart = alt.Chart(items_sold_df).mark_bar().encode(
            x='STATE',
            y='REVENUE',
            color='ITEM'
        ).interactive()

        st.altair_chart(chart, theme='streamlit', use_container_width=True)

        time.sleep(1)
