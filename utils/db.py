import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

# Connessione al DB
def connect_db(dialect, username, password, host, dbname):
    try:
        engine = create_engine(f'{dialect}://{username}:{password}@{host}/{dbname}')
        conn = engine.connect()
        return conn
    except SQLAlchemyError as e:
        st.sidebar.error(f"Errore: {e}")
        return False

def connect_handler():
    load_dotenv()
    conn = connect_db(
        dialect="mysql+pymysql",
        username = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = os.getenv("DB_HOST"),
        dbname = os.getenv("DB_NAME")
    )
    if conn:
        st.session_state["connection"] = conn
        st.session_state["connection_success"] = True
        st.toast("Connesso al DB")
    else:
        st.session_state["connection"] = False
        st.session_state["connection_success"] = False
        st.sidebar.error("Errore nella connessione")

def disconnect_handler():
    st.session_state["connection"] = False
    st.session_state["connection_success"] = False

def check_connection():
    if "connection" not in st.session_state:
        st.session_state["connection"] = False
    if "connection_success" not in st.session_state:
        st.session_state["connection_success"] = False

    # Visual feedback
    if st.session_state["connection_success"]:
        st.sidebar.success("Connesso al DB")
    else:
        st.sidebar.info("Non connesso al DB")

    st.sidebar.button("Connetti al DB", disabled=st.session_state["connection_success"], on_click=connect_handler)
    st.sidebar.button("Disconnetti", disabled=not st.session_state["connection_success"], on_click=disconnect_handler)

    return bool(st.session_state["connection"])

# Esecuzione Query
def execute_query(conn, query, params=None):
    try:
        result = conn.execute(text(query), params or {})
        return result
    except Exception as e:
        st.error(f"Errore nell'esecuzione della query: {e}")
        return None

# Ottenere tutti i giocatori
def get_all_players():
    query = """
        SELECT DISTINCT slug FROM (
            SELECT slug FROM dunkest_stats_2018_19
            UNION
            SELECT slug FROM dunkest_stats_2019_20
            UNION
            SELECT slug FROM dunkest_stats_2020_21
            UNION
            SELECT slug FROM dunkest_stats_2021_22
            UNION
            SELECT slug FROM dunkest_stats_2022_23
            UNION
            SELECT slug FROM dunkest_stats_2023_24
            UNION
            SELECT slug FROM dunkest_stats_2024_25
        ) AS all_players
        ORDER BY slug ASC;
    """
    result = execute_query(st.session_state["connection"], query)
    return [row[0] for row in result.fetchall()] if result else []
