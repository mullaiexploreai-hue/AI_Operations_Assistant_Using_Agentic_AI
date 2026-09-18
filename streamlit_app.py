"""Entry point: `streamlit run streamlit_app.py`."""
import streamlit as st

from views import customer_chat

st.set_page_config(page_title="AI Operations Assistant", layout="wide")
customer_chat.render()
