from display_utils import parse_slot_filling_data, set_opacity, set_text_color, set_background_color
import pandas as pd

import requests
import streamlit as st

NGROK_DOMAIN = "http://eez115.ece.ust.hk:5000/"
# NGROK_DOMAIN = "http://localhost:8080/"

with st.sidebar:
    session_id = st.text_input(
        label="Please input your Session ID here:",
        key="session_id",
        type="default",
        value=1,
    )
    domain = st.text_input(
        "Please input the chatbot domain here:",
        key="domain",
        type="default",
        value=NGROK_DOMAIN,
    )

st.title("💬 PAF Result")



if __name__ == "__main__":
    if not session_id:
        st.info("Please input your Session ID on the left pane to check your conversation summary.")
        st.stop()

    if domain != NGROK_DOMAIN:
        NGROK_DOMAIN = domain

    response = requests.post(f"{NGROK_DOMAIN}/get_paf_result", json={"session_id": session_id})
    response = response.json()
    response_data = response.get("responses", {})
    if not response_data:
        st.error("No data found for the given session ID.")
        st.stop()
    conversation_history = response_data.pop("conversation_history", None)
    tree_id = int(session_id.split("_")[-1]) % 8
    paf_result = parse_slot_filling_data(response_data, experiment_variation=tree_id)

    st.write(f"Session ID: {session_id}")
    # Display the PAF result with reduced details if all required columns are present
    if all(col in paf_result.columns for col in ["PAF_Question", "Slot_Display", "Assessed", "PAF_Index"]):
        # Style the PAF result with color coding and custom index
        styled_paf_result = paf_result.set_index("PAF_Index")
        # styled_paf_result = styled_paf_result.style.apply(set_background_color, axis=1, subset=["Assessed"]) # disabled for now
        st.dataframe(
            data=styled_paf_result,
            use_container_width=True,
            column_order=[
                "Assessed",
                "PAF_Question",
                "Slot_Display",
            ],
            column_config={
                "Assessed": "Assessed",
                "PAF_Question": "PAF Questions",
                "Slot_Display": "Patient Answer",
            },
        )
    else:
        # Display the full PAF result (all columns)
        st.dataframe(
            hide_index=True,
            data=paf_result, 
            use_container_width=True
        )
    # st.markdown(paf_result.to_markdown(), unsafe_allow_html=True)
    st.write("### Details")
    [history_tab, slot_filling_tab] = st.tabs(["Conversation History", "Other Info"])
    with history_tab:
        st.write("#### Conversation History")
        # st.dataframe(conversation_history, use_container_width=True)

        with st.container(height=400):
            for turn in conversation_history:
                role = "user" if turn.get("role") == "Patient" else "assistant"
                with st.chat_message(role):
                    st.write(turn.get("utterance"))
    with slot_filling_tab:
        st.write("#### Slot Filling Data")
        table = pd.DataFrame.from_dict(response_data, orient='index')
        columns_to_check = ["slot_name", "slot_value", "question_asked", "patient_answer"]
        all_columns_exist = all(col in table.columns for col in columns_to_check)
        table = table.reset_index(drop=True)[columns_to_check] if all_columns_exist else table
        if not table.empty:
            # remove the rows with empty slot_name
            table = table[table["slot_name"].notna()]
        st.dataframe(table, use_container_width=True)