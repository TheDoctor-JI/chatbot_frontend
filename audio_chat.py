import base64
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from google_ASR import transcribe_file_with_auto_punctuation
from google_TTS import synthesize_text_with_audio_profile
from utils import (
    initialize_conversation,
    send_message,
    # display_chat,
    parse_chatbot_reply,
    initialize_and_parse_greetings,
)


st.title("💬 PAF Chatbot")


with st.sidebar:
    user_id = st.text_input(
        label="Please input your User ID here:",
        key="user_id",
        type="default",
        value=None,
    )


if __name__ == "__main__":
    if not user_id:
        st.warning("Please input your User ID on the left pane to start conversation.")
        st.stop()
    
    st.info("Please allow the browser to access your microphone.")
    st.info(
        "Please click the microphone button to start conversation. Start talking when the microphone turns red. You may start the conversation with greetings like '你好' or 'Hello' to the chatbot."
    )
    st.info("Please speak in Cantonese.")
    audio_bytes = audio_recorder(sample_rate=44100)
    if "messages" not in st.session_state:
        if audio_bytes:
            response = transcribe_file_with_auto_punctuation(audio_bytes)
            first_alternative = (
                response.results[0].alternatives[0].transcript
                if response.results
                else "could you please repeat?"
            )
            st.chat_message(name="user").write(first_alternative)
            greetings = initialize_conversation(first_alternative)

            user_greetings = {
                "role": "user",
                "content": first_alternative,
                "translation": first_alternative,
            }
            greetings_reply = initialize_and_parse_greetings(user_greetings, greetings)
            greetings_reply_audio = synthesize_text_with_audio_profile(
                greetings_reply, "greetings_reply.wav", "telephony-class-application"
            )
            # st.audio(greetings_reply_audio, format="audio/wav")
            with open("greetings_reply.wav", "rb") as f:
                greetings_reply_audio_stream = f.read()
            audio_base64 = base64.b64encode(greetings_reply_audio_stream).decode(
                "utf-8"
            )
            audio_tag = (
                f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
            )
            st.markdown(audio_tag, unsafe_allow_html=True)
        # display_chat(mode="normal")
    else:
        # display_chat(mode="normal")
        if audio_bytes:
            # Display the audio recorded for debug purpose
            # st.audio(audio_bytes, format="audio/wav")
            response = transcribe_file_with_auto_punctuation(audio_bytes)
            first_alternative = (
                response.results[0].alternatives[0].transcript
                if response.results
                else "could you please repeat?"
            )
            st.chat_message(name="user").write(first_alternative)
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": first_alternative,
                    "translation": first_alternative,
                }
            )
            chatbot_sentence = send_message(first_alternative)
            chatbot_reply = parse_chatbot_reply(chatbot_sentence)
            sound_block = st.empty()
            with st.spinner("Generating audio..."):
                chatbot_reply_audio = synthesize_text_with_audio_profile(
                    chatbot_reply, "chatbot_reply.wav", "telephony-class-application"
                )
                # st.audio(chatbot_reply_audio, format="audio/wav")

                with open("chatbot_reply.wav", "rb") as f:
                    chatbot_reply_audio_stream = f.read()
                audio_base64 = base64.b64encode(chatbot_reply_audio_stream).decode(
                    "utf-8"
                )
                audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}" id={len(st.session_state.messages)}>'
                sound_block.markdown(audio_tag, unsafe_allow_html=True)
