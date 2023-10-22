import streamlit as st

st.set_page_config(page_title="Home",
                   layout="centered",
                   initial_sidebar_state="expanded")

st.header("Nom Nom Brands", divider='blue')
st.markdown('![Nom Nom Brands.](app/static/nom_nom_logo.png)')

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown('![Pizza Cabin.](app/static/pizza_cabin_logo.png)')

with col2:
    st.markdown('![Taco Shell.](app/static/taco_shell_logo.png)')

tbccol, = st.columns(1)
with tbccol:
    st.markdown('![Tennessee Baked Chicken.](app/static/tennessee_baked_chicken_logo.png)')

st.sidebar.markdown("# Home")
