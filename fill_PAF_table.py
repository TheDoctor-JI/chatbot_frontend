import re

import pandas as pd

# 'cough_existence', 'sputum_existence', 'sputum_amount', 'sputum_color', 'history_of_falling', 'ambulatory_aid', 'vision_problem', 'weight_loss_existance', 'weight_loss_amount', 'appetite_loss', 'denture', 'denture_option', 'special_diet', 'food_preference'
PAF_Question_Mapping = {
    "Coughing": "cough_existence",
    "Sputum": "sputum_existence",
    "Amount": "sputum_amount",
    "Color": "sputum_color",
    # "History of Falling": 'history_of_falling',
    # "Ambulatory Aid": 'ambulatory_aid',
    # "Vision": 'vision_problem',
    "Weight Loss": "weight_loss_existance",
    "Weight Loss Amount": "weight_loss_amount",
    "Appetite Loss": "appetite_loss",
    # "Denture": 'denture',
    # "Denture Type": 'denture_option',
    # "Special Diet": 'special_diet',
    "Food Preference": "food_preference",
}

PAF_Questions = list(PAF_Question_Mapping.keys())
PAF_Questions_Bilingual = [
    "Coughing 請問有冇咳？",
    "Sputum 請問有冇痰？",
    "\t – \t Sputum Amount 有痰的話，有幾多量？",
    "\t – \t Sputum Color 痰顏色係咩？",
    # "History of Falling 有冇跌過？",
    # "Ambulatory Aid 有冇用過行動輔助器具？",
    # "Vision Problem 視力問題？",
    "Weight Loss 有冇體重下降？",
    "\t – \t Weight Loss Amount 輕咗幾多？",
    "Appetite Loss 胃口差别？",
    # "Denture 有冇假牙？",
    # "Denture Type 假牙係固定定可拆卸？",
    # "Special Diet 有冇特別飲食？",
    "Food Preference 咩唔食？",
]

PAF_Index = {
    0: "1",
    1: "2",
    2: "2.1",
    3: "2.2",
    4: "3",
    5: "3.1",
    6: "4",
    7: "5",
}


def fill_paf_table(original_data: dict) -> pd.DataFrame:
    """
    Fill the PAF table with the user input and the chatbot response.
    :param data_table: the PAF table
    :return: the updated PAF table
    """
    paf_result = {
        "PAF_Question": PAF_Questions_Bilingual,
        "PAF_Result": [" "] * len(PAF_Questions),
        # "Need Follow-up": [""] * len(PAF_Questions),
    }
    try:
        # Before finishing, fill the not applicable ones with N.A.
        # Mannually adding N.A. to the not appicable follow-up questions
        original_data = fill_NA_follow_up_questions(original_data)
        for i, question in enumerate(PAF_Questions):
            slot_key = PAF_Question_Mapping[question]
            slot_filling_info = original_data.get(slot_key, None)
            if slot_filling_info:
                paf_result["PAF_Result"][i] = convert_paf_questionnaire_line(
                    slot_key, slot_filling_info.get("slot_value", "N.A.")
                )
        # final_table = pd.DataFrame(paf_result, index=PAF_Index.values())
        final_table = pd.DataFrame.from_dict(paf_result).rename(index=PAF_Index)
    except Exception:
        paf_result = {}
        final_table = pd.DataFrame.from_dict(paf_result)
    return final_table


def fill_NA_follow_up_questions(ori_data: dict):
    if (
        process_slot_string(ori_data.get("sputum_existence", {}).get("slot_value", ""))
        == "no"
    ):
        ori_data["sputum_amount"] = {"slot_value": "N.A."}
        ori_data["sputum_color"] = {"slot_value": "N.A."}
    if (
        process_slot_string(
            ori_data.get("weight_loss_existance", {}).get("slot_value", "")
        )
        == "no"
    ):
        ori_data["weight_loss_amount"] = {"slot_value": "N.A."}
    return ori_data


def process_slot_string(input_string):
    """Remove non-alphabet characters from a string. Change all remaining characters to lower case.

    Args:
        input_string (_type_): a string

    Returns:
        str: a string with only alphabet characters and all lower case
    """
    return re.sub(r"[^a-zA-Z]", "", input_string).lower()


def convert_paf_questionnaire_line(slot_key, slot_value: str):
    if slot_key in [
        "cough_existence",
        "sputum_existence",
        "history_of_falling",
        "vision_problem",
        "weight_loss_existance",
        "appetite_loss",
        "denture",
        "special_diet",
        "food_preference",
    ]: # binary questions
        processed_slot_value = process_slot_string(slot_value)
        if processed_slot_value not in ["yes", "no"]:
            return slot_value
        else:
            if processed_slot_value == "yes":
                return "☐ No \t ☑️ Yes"
            else:
                return "☑️ No \t ☐ Yes"
    elif slot_value == "N.A.":
        return slot_value
    else:
        return slot_value
