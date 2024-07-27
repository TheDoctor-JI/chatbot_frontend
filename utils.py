import re

import pandas as pd
import yaml

def parse_copd_history(conversation_history: dict):
    """Parse the conversation history into a list of tuples containing the role and utterance.

    Args:
        conversation_history (dict): The conversation history to be parsed.

    Returns:
        list: A list of tuples containing the role and utterance of each turn in the conversation history.
    """
    conversation = []
    for turn in conversation_history:
        role = "user" if turn["role"] == "Patient" else "assistant"
        conversation.append((role, turn["utterance"]))
    return conversation

def validate_session_history(session_history: dict):
    """Validate the session history format.

    Args:
        session_history (dict): The session history to be validated.

    Raises:
        ValueError: If the session history is empty.
        TypeError: If the session history is not a dictionary.
        ValueError: If the session history does not contain the necessary keys: name, sessionID, conversation_history and patient_answer.
        ValueError: If the conversation history is empty.
        TypeError: If the conversation history is not a list.
        TypeError: If each turn in the conversation history is not a dictionary.
        ValueError: If each turn in the conversation history does not have the keys: role and utterance.
        ValueError: If the role in the conversation history is not either "Patient" or "Grace".
        ValueError: If the name in the session history is not "COPD".
    """
    # Validate the session history format
    if not session_history:
        raise ValueError("Session history is empty.")
    if not isinstance(session_history, dict):
        raise TypeError("Session history should be a dictionary. But get: {}".format(session_history))
    # Check if the session history contains the necessary keys: name, sessionID, conversation_history and patient_answer
    if not all(key in session_history for key in ["name", "sessionID", "conversation_history", "patient_answer"]):
        raise ValueError("Session history should have keys: name, sessionID, conversation_history and patient_answer. But get: {}".format(session_history))
    # Check if the conversation history is a list of dicts, and the dicts should have keys: role and utterance
    conversation_history = session_history["conversation_history"]
    # Check the format of the conversation history
    if not conversation_history:
        raise ValueError("Conversation history is empty.")
    if not isinstance(conversation_history, list):
        raise TypeError(
            "Conversation history should be a list. But get: {}".format(
                conversation_history
            )
        )
    if not all(isinstance(turn, dict) for turn in conversation_history):
        raise TypeError(
            "Each turn in conversation history should be a dictionary. But get: {}".format(
                conversation_history
            )
        )
    if not all("role" in turn and "utterance" in turn for turn in conversation_history):
        raise ValueError(
            "Each turn in conversation history should have 'role' and 'utterance' keys. But get: {}".format(
                conversation_history
            )
        )
    # Check if the role is either "Patient" or "Grace"
    if not all(turn["role"] in ["Patient", "Grace"] for turn in conversation_history):
        raise ValueError(
            "The role in conversation history should be either 'Patient' or 'Grace'. But get: {}".format(
                conversation_history
            )
        )
    # Check if the name is "COPD"
    if session_history["name"] != "COPD":
        raise ValueError(
            "The name in session history should be 'COPD'. But get: {}".format(
                session_history["name"]
            )
        )
    

def parse_patient_answer(patient_answer: list):
    """Parse the patient answer into a DataFrame.

    Args:
        patient_answer (list): The patient answer to be parsed.

    Returns:
        pd.DataFrame: The parsed patient answer in a DataFrame format.
    """
    # Match the question id and exact question wording
    with open("COPD_questionnaire.yaml", "r") as f:
        questions = yaml.safe_load(f)
    COPD_QUESTIONNAIRE = questions["COPD_QUESTIONNAIRE"]
    # Parse the patient answer into a list of dicts, with key "Question" and "Patient Answer"
    parsed_patient_answer = []
    for i, item in enumerate(patient_answer):
        question_id, real_question, answer = item["question_id"], item["question"], item["answer"]
        question = COPD_QUESTIONNAIRE[question_id]
        parsed_patient_answer.append({"Question": question, "Patient Answer": int(answer), "Index": i+1})

    # Convert the answer to pd.DataFrame with "Index" as the dataframe index
    df = pd.DataFrame(parsed_patient_answer)
    df.set_index("Index", inplace=True)

    return df