import streamlit as st
import requests
import random

NGROK_DOMAIN = "http://eez115.ece.ust.hk:5000/"


def initialize_conversation(text: str = ""):
    st.session_state["session_id"] = random.randint(10000000, 500000000)
    query = {
        "text": "INITIALIZE-SESSION",
        "session_id": st.session_state["session_id"],
        "message_list": [
            "This is a magic phrase to initialize grace agent to welcome intent."
        ],
        "redo": False,
    }
    r = requests.post(f"{NGROK_DOMAIN}/dialogue", json=query)
    if r.status_code != 200:
        chatbot_message = {
            "responses": {
                "next_question_text": "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
            },
            "status": False,
        }
        st.error(
            "Network unstable. Please type your input and send again. Your history won't be lost."
        )
    else:
        # st.success("Message sent!")
        reply = r.json()
        # chatbot_message = reply.get("responses", {}).get("text", "")
        chatbot_message = reply
        chatbot_message["status"] = True
    return chatbot_message


def send_message(text=""):
    if not text:
        return ""
    query = {
        "text": text,
        "session_id": st.session_state["session_id"],
        "message_list": [text],
        "redo": False,
    }
    # st.success("Message sent! Start processing...")
    r = requests.post(f"{NGROK_DOMAIN}/dialogue", json=query)
    if r.status_code != 200:
        chatbot_message = {
            "responses": {
                "next_question_text": "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
            },
            "status": False,
        }
        # "Sorry I didn't hear you due to network issue. Can you wait for a few seconds and type it again?"
        error_message = "Network unstable. Please type your input and send again. Your history won't be lost."
        st.error(error_message)
    else:
        reply = r.json()
        # chatbot_message = reply.get("responses", {}).get("text", "")
        chatbot_message = reply
        chatbot_message["status"] = True
        st.success("Processing Finished!")
    return chatbot_message


def display_chat(mode: str = "normal"):
    """Display chat history

    Args:
        mode (str, optional): model of conversation, either "normal" or "log". Defaults to "normal".
    """
    if mode == "normal":
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message(msg["role"]).write(msg["content"])
            elif msg["role"] == "assistant":
                st.write(
                    {
                        "relevance": msg["relevance"],
                        "level": msg["level"],
                        "scaffold_method": msg["scaffold_method"],
                    }
                )
                st.chat_message(msg["role"]).write(msg["content"])


def initialize_and_parse_greetings(user_greetings, greetings):
    greetings_translation = greetings.get("responses", {}).get("next_question_text", "")
    st.session_state["messages"] = [
        user_greetings,
        {
            "role": "assistant",
            "content": greetings_translation,
            "response": greetings,
            "relevance": greetings.get("user_input", {}).get(
                "relevance", "start conversation"
            ),
            "level": greetings.get("user_input", {}).get("level", ""),
            "scaffold_method": greetings.get("responses", {}).get(
                "scaffold_method", "start conversation"
            ),
            "original_response": greetings,
        },
    ]
    # st.chat_message("assistant").write(greetings_translation)
    return greetings_translation


def parse_chatbot_reply(chatbot_sentence):
    chatbot_sentence_translation = chatbot_sentence.get("responses", {}).get(
        "next_question_text", ""
    )

    other_SFQs = {}
    sfq_list = chatbot_sentence.get("candidate_sf_questions", [])
    if sfq_list:
        for sfq in sfq_list:
            sf_method = sfq.get("scaffolding method", "")
            sf_question = sfq.get("question", "")
            if sf_method and sf_question:
                other_SFQs[sf_method] = sf_question

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": chatbot_sentence_translation,
            "response": chatbot_sentence,
            "relevance": chatbot_sentence.get("user_input", {}).get("relevance", ""),
            "level": chatbot_sentence.get("user_input", {}).get("level", ""),
            "scaffold_method": chatbot_sentence.get("responses", {}).get(
                "scaffold_method", ""
            ),
            "other_SFQs": other_SFQs if other_SFQs else {},
            "original_response": chatbot_sentence,
        }
    )
    # st.chat_message("assistant").write(chatbot_sentence_translation)
    return chatbot_sentence_translation
