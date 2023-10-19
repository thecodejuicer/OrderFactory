import streamlit as st

st.set_page_config(page_title="Home",
                   layout="centered",
                   initial_sidebar_state="expanded")

st.header("Happy Food Company", divider='blue')

col1, col2 = st.columns(2)

with col1:
    st.markdown('![Pizza Cabin.](app/static/pizza_cabin_logo.png)')

with col2:
    st.markdown('![Taco Shell.](app/static/taco_shell_logo.png)')

st.markdown('![Tennessee Baked Chicken.](app/static/tennessee_baked_chicken_logo.png)')

st.sidebar.markdown("# Home")
