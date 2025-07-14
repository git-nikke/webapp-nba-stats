import streamlit as st
from auth.authenticator import load_authenticator
from utils.db import check_connection
from tabs import create_tab_medie_stagione, create_tab_giocatore

st.set_page_config(
    page_title="NBA Analytics",
    layout="wide",
    initial_sidebar_state="auto",
)

authenticator = load_authenticator()
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state['authentication_status']:

    st.sidebar.write(f"Welcome *{st.session_state['name']}*!")
    authenticator.logout(key="Logout", location="sidebar")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(":red[WebApp NBA Analytics]")
        st.markdown("### :blue[Nicolò Casale]")
    with col2:
        st.image("images/nbalogo.png")

    if check_connection():
        tab_medie_stagione, tab_giocatore = st.tabs(["Season mean", "Single player"])
        with tab_medie_stagione:
            create_tab_medie_stagione()
        with tab_giocatore:
            create_tab_giocatore()

elif st.session_state['authentication_status'] is False:
    st.error("Wrong username or password.")
else:
    st.info("insert credentials to log in.")
