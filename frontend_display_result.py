# First
import json
import random
import pandas as pd

import requests
import streamlit as st

NGROK_DOMAIN = "http://eez115.ece.ust.hk:5000/"
# NGROK_DOMAIN = "http://localhost:8080/"

with st.sidebar:
    session_id = st.text_input(
        label="Please input your Session ID here:",
        key="user_id",
        type="default",
        value="382725594",
    )
    domain = st.text_input(
        "Please input the chatbot domain here:",
        key="domain",
        type="default",
        value=NGROK_DOMAIN,
    )

st.title("💬 PAF Result")



if __name__ == "__main__":
    # if "user_id" not in st.session_state or st.session_state.get("user_id") is None:
    if not session_id:
        st.info("Please input your Session ID on the left pane to start conversation.")
        st.stop()
    # if not domain:
    #     st.info("Please input your domain on the left pane to start conversation.")
    #     st.stop()
    if domain != NGROK_DOMAIN:
        NGROK_DOMAIN = domain

    response = requests.post(f"{NGROK_DOMAIN}/get_paf_result", json={"session_id": session_id})
    response = response.json()
    table = pd.DataFrame.from_dict(response.get("responses", {}), orient='index')
    table = table.reset_index(drop=True)[["slot_name", "slot_value", "question_asked", "patient_answer"]]
    st.write(f"Session ID: {session_id}")
    st.data_editor(table)