# First
import requests
import streamlit as st

with st.sidebar:
    chatbot_endpoint = st.text_input(
        "May I please know your user ID?", key="chatbot_endpoint", type="default"
    )
st.title("💬 Chatbot")

def initialize():
    query = {
        "text": "This is a magic phrase to initialize grace agent to welcome intent.",
        "session_id": 0,
        "message_list": [],
        "redo": False,
    }
    r = requests.post("http://20.222.209.72:5010/dialogflow_result", json=query)
    if r.status_code != 200:
        chatbot_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(chatbot_message)
    else:
        # st.success("Message sent!")
        reply = r.json()
        chatbot_message = reply.get("responses", {}).get("text", "")
    return chatbot_message

if "messages" not in st.session_state:
    greetings = initialize()
    st.session_state["messages"] = [
        {"role": "assistant", "content": greetings}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

def send_message(text=""):
    if not text:
        return ""
    query = {
        "text": text,
        "session_id": 0,
        "message_list": [],
        "redo": False,
    }
    r = requests.post("http://20.222.209.72:5010/dialogflow_result", json=query)
    if r.status_code != 200:
        chatbot_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(chatbot_message)
    else:
        st.success("Message sent!")
        reply = r.json()
        chatbot_message = reply.get("responses", {}).get("text", "")
    return chatbot_message

if prompt := st.chat_input():
    if not chatbot_endpoint:
        st.info("Please input your User ID.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    chatbot_sentence = send_message(prompt)

    st.session_state.messages.append({"role": "assistant", "content": chatbot_sentence})
    st.chat_message("assistant").write(chatbot_sentence)
