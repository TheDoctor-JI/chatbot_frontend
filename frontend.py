# First
import random

import requests
import streamlit as st
from Azure_translate import Azure_Translate

# NGROK_DOMAIN = "https://certain-quagga-directly.ngrok-free.app"
NGROK_DOMAIN = "http://20.222.209.72:5010"

with st.sidebar:
    chatbot_endpoint = st.text_input(
        "May I know your user ID? Please tell me here:",
        key="chatbot_endpoint",
        type="default",
    )
    language = st.selectbox(
        "Please select your language:",
        ("Please select", "English", "Cantonese"),
        key="select_language",
    )
    translator = Azure_Translate()
st.title("💬 Chatbot")


def initialize():
    st.session_state["session_id"] = random.randint(10000000, 500000000)
    query = {
        "text": "This is a magic phrase to initialize grace agent to welcome intent.",
        "session_id": st.session_state["session_id"],
        "message_list": ["This is a magic phrase to initialize grace agent to welcome intent."],
        "redo": False,
    }
    r = requests.post(
        f"{NGROK_DOMAIN}/dialogflow_result", json=query
    )
    if r.status_code != 200:
        chatbot_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(chatbot_message)
    else:
        # st.success("Message sent!")
        reply = r.json()
        chatbot_message = reply.get("responses", {}).get("text", "")
    return chatbot_message


if "user_id" not in st.session_state:
    if not chatbot_endpoint:
        st.info("Please input your User ID on the left pane to start conversation.")
        st.stop()
    st.session_state["user_id"] = chatbot_endpoint

if "language" not in st.session_state:
    if not language or language == "Please select":
        st.info("Please select your language on the left pane.")
        st.stop()
    st.session_state["language"] = language


if "messages" not in st.session_state:
    greetings = initialize()

    greetings_translation = greetings
    st.session_state["messages"] = [{
        "role": "assistant", "content": greetings_translation,
        "translation": greetings
    }]
    st.chat_message("assistant").write(greetings_translation)
else:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


def send_message(text=""):
    if not text:
        return ""
    query = {
        "text": text,
        "session_id": st.session_state["session_id"],
        "message_list": [text],
        "redo": False,
    }
    st.success("Message sent! Start processing...")
    r = requests.post(
        f"{NGROK_DOMAIN}/dialogflow_result", json=query
    )
    if r.status_code != 200:
        chatbot_message = "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
        error_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(error_message)
    else:
        reply = r.json()
        chatbot_message = reply.get("responses", {}).get("text", "")
        st.success("Processing Finished!")
    return chatbot_message


if prompt := st.chat_input():
    if not chatbot_endpoint:
        st.info("Please input your User ID.")
        st.stop()
    if not language or language == "Please select":
        st.info("Please select your language.")
        st.stop()

    st.chat_message("user").write(prompt)


    prompt_translation = prompt

    st.session_state.messages.append(
        {"role": "user", "content": prompt, "translation": prompt_translation}
    )

    chatbot_sentence = send_message(prompt_translation)


    chatbot_sentence_translation = chatbot_sentence

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": chatbot_sentence_translation,
            "translation": chatbot_sentence,
        }
    )
    st.chat_message("assistant").write(chatbot_sentence_translation)

# st.download_button(
#     "Download Conversation History",
#     st.session_state.messages,
#     file_name=f"{chatbot_endpoint}conversation_history.json",
# )