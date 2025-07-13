# auth/authenticator.py

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_authenticator():
    try:
        with open("config.yaml") as file:
            config = yaml.load(file, Loader=SafeLoader)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        return authenticator

    except Exception as e:
        st.error(f"Errore nel caricamento del file di configurazione: {e}")
        return None
