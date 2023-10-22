import time

import streamlit as st
import altair as alt
import pymongo
from pymongo import MongoClient
import pandas as pd

from queries import state_totals, item_order_totals

st.set_page_config(
    page_title="Pizza Cabin Stats",
    layout="wide"
)

company_name = 'All Company'


@st.cache_resource
def init_connection() -> MongoClient:
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()


@st.cache_data(ttl=5)
def get_all_item_sales_data():
    db = client.kafka
    items = db.anonymized_orders_by_state.aggregate([{
        '$group': {
            '_id': {
                'FACTORY': '$FACTORY',
                'STATE': '$STATE'
            },
            'REVENUE': {
                '$sum': {
                    '$toDouble': '$ITEM.PRICE'
                }
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'FACTORY': '$_id.FACTORY',
            'STATE': '$_id.STATE',
            'REVENUE': 1,
        }
    }])
    return list(items)


st.sidebar.markdown(f"# {company_name}")
st.header("All Company", divider='blue')
st.markdown('![Nom Nom Brands.](app/static/nom_nom_logo.png)')

placeholder = st.empty()

while True:
    with placeholder.container():
        items_sold_df = pd.DataFrame(get_all_item_sales_data())

        rev_col, pc_col, ts_col, tbc_col = st.columns(4)

        with rev_col:
            total_revenue = items_sold_df[['REVENUE']].sum()
            st.metric("Total Revenue", '${:10.2f}'.format(total_revenue['REVENUE']))

        with pc_col:
            total_revenue = items_sold_df.loc[items_sold_df['FACTORY'] == 'Pizza Cabin'][['REVENUE']].sum()
            st.metric("Pizza Cabin", '${:10.2f}'.format(total_revenue['REVENUE']))

        with ts_col:
            total_revenue = items_sold_df.loc[items_sold_df['FACTORY'] == 'Taco Shell'][['REVENUE']].sum()
            st.metric("Taco Shell", '${:10.2f}'.format(total_revenue['REVENUE']))

        with tbc_col:
            total_revenue = items_sold_df.loc[items_sold_df['FACTORY'] == 'Tennessee Baked Chicken'][['REVENUE']].sum()
            st.metric("Tennessee Baked Chicken", '${:10.2f}'.format(total_revenue['REVENUE']))

        st.subheader('Item Revenue by State', divider='blue')
        chart = alt.Chart(items_sold_df).mark_bar().encode(
            x='STATE',
            y='REVENUE',
            color='FACTORY'
        ).interactive()

        st.altair_chart(chart, theme='streamlit', use_container_width=True)

        time.sleep(5)
