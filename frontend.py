# First
import requests
import streamlit as st
import random
with st.sidebar:
    chatbot_endpoint = st.text_input(
        "May I know your user ID? Please tell me here:", key="chatbot_endpoint", type="default"
    )
st.title("💬 Chatbot")

def initialize():
    query = {
        "text": "This is a magic phrase to initialize grace agent to welcome intent.",
        "session_id": st.session_state["session_id"],
        "message_list": [],
        "redo": False,
    }
    r = requests.post("https://certain-quagga-directly.ngrok-free.app/dialogflow_result", json=query)
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
    st.session_state["session_id"] = random.randint(10000000, 500000000)


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
        "session_id": st.session_state["session_id"],
        "message_list": [],
        "redo": False,
    }
    st.success("Message sent! Start processing...")
    r = requests.post("https://certain-quagga-directly.ngrok-free.app/dialogflow_result", json=query)
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

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    chatbot_sentence = send_message(prompt)

    st.session_state.messages.append({"role": "assistant", "content": chatbot_sentence})
    st.chat_message("assistant").write(chatbot_sentence)
