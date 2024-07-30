import json

import requests
from utils import parse_copd_history, validate_session_history, parse_patient_answer
import pandas as pd
import streamlit as st

NGROK_DOMAIN = "http://eez114.ece.ust.hk:5000/"
# NGROK_DOMAIN = "http://localhost:8080/"

with st.sidebar:
    session_id = st.text_input(
        label="Please input your Session ID here:",
        key="user_id",
        type="default",
        value="",
    )
    domain = st.text_input(
        "Please input the chatbot domain here:",
        key="domain",
        type="default",
        value=NGROK_DOMAIN,
    )

st.title("💬 COPD Questionnaire Result")


if __name__ == "__main__":
    if not session_id:
        st.info("Please input your Session ID on the left pane to check your conversation summary.")
        st.stop()
    # if not domain:
    #     st.info("Please input your domain on the left pane to start conversation.")
    #     st.stop()
    if domain != NGROK_DOMAIN:
        NGROK_DOMAIN = domain

    response = requests.post(f"{NGROK_DOMAIN}/get_copd_result", json={"session_id": session_id})
    response = response.json()
    response_data = response.get("responses", {})
    # with open("exp_data/sample/1.json", "r") as f:
    #     response_data = json.load(f)
    validate_session_history(response_data)

    conversation_history = response_data.pop("conversation_history", [])
    session_id = response_data.pop("sessionID", "")
    patient_answer = response_data.pop("patient_answer", [])

    # Parse the patient answer
    parsed_patient_answer = parse_patient_answer(patient_answer)

    st.write(f"Session ID: {session_id}")
    st.data_editor(data=parsed_patient_answer, use_container_width=True,)
    # for item in parsed_patient_answer:
    #     question, answer = item["Question"], item["Patient Answer"]
    #     st.slider(label=question, min_value=0, max_value=5, value=answer, disabled=True)

    st.write("### Details")
    [history_tab] = st.tabs(["Conversation History"])
    with history_tab:
        st.write("#### Conversation History")
        with st.container(height=400):
            parsed_conversation_history = parse_copd_history(conversation_history)
            for role, utterance in parsed_conversation_history:
                with st.chat_message(role):
                    st.write(utterance)