import json
import os
import re

import pandas as pd

# 'cough_existence', 'sputum_existence', 'sputum_amount', 'sputum_color', 'history_of_falling', 'ambulatory_aid', 'vision_problem', 'weight_loss_existance', 'weight_loss_amount', 'appetite_loss', 'denture', 'denture_option', 'special_diet', 'food_preference'

PAF_Questions_Headings = [
    "Coughing", "Sputum", "Amount", "Color", "History of Falling", "Ambulatory Aid", "Vision", "Weight Loss", "Weight Loss Amount", "Appetite Loss", "Denture", "Denture Type", "Special Diet", "Food Preference"
]

PAF_Questions_Bilingual = [
    "Coughing 請問有冇咳？",
    "Sputum 請問有冇痰？",
    "\t – \t Sputum Amount 有痰的話，有幾多量？",
    "\t – \t Sputum Color 痰顏色係咩？",
    "History of Falling 有冇跌過？",
    "Ambulatory Aid 有冇用過行動輔助器具？",
    "Vision Problem 視力問題？",
    "Weight Loss 有冇體重下降？",
    "\t – \t Weight Loss Amount 輕咗幾多？",
    "Appetite Loss 胃口差别？",
    "Denture 有冇假牙？",
    "\t – \t Denture Type 假牙係固定定可拆卸？",
    "Special Diet 有冇特別飲食？",
    "Food Preference 咩唔食？",
]

PAF_Question_Slot_Names = [
    "cough_existence", "sputum_existence", "sputum_amount", "sputum_color", "history_of_falling", "ambulatory_aid", "vision_problem", "weight_loss_existance", "weight_loss_amount", "appetite_loss", "denture", "denture_option", "special_diet", "food_preference"
]

PAF_Question_ID = [
    "q1_0_coughing_existance", "q2_0_sputum_existance", "q2_1_sputum_amount", "q2_2_sputum_colour", "q3_0_history_falling", "q3_1_ambulatory_aid", "q4_0_vision", "q5_0_lose_weight_existance", "q5_1_lose_weight_amount", "q5_2_decreased_appetite", "q6_0_denture", "q6_1_dental_followup_fixed_or_removable", "q7_0_diet", "q7_2_food_preference"
]

PAF_Questions = PAF_Questions_Headings
PAF_Questions_Index = [
    "1", "2", "2.1", "2.2", "3", "4", "5", "6", "6.1", "7", "8", "8.1", "9", "10"
]

def fill_experiment_conditions():
    # find all json files in the questions_trees folder
    experiment_conditions = {}
    for file in os.listdir("questions_trees"):
        if file.endswith(".json"):
            # find the integer in the filename and use it as the tree_id
            tree_id = int(re.findall(r'\d+', file)[0])
            with open(os.path.join("questions_trees", file)) as f:
                data = json.load(f)
            # find the key of data that is a valid PAF_Question_ID
            assessed_question_ids = [key for key in data if key in PAF_Question_ID]
            # create a list of booleans to indicate whether the question is assessed
            experiment_conditions[tree_id] = [key in assessed_question_ids for key in PAF_Question_ID]
    return experiment_conditions

def parse_slot_filling_data(data: dict, experiment_variation = -1) -> pd.DataFrame:
    experiment_conditions = fill_experiment_conditions()
    questions_assessed = (
        [True] * len(PAF_Questions)
        if (experiment_variation == -1 or experiment_variation == 8)
        else experiment_conditions[experiment_variation]
    )
    PAF_table = pd.DataFrame(
        {
            "PAF_Question": PAF_Questions_Bilingual,
            "PAF_Header": PAF_Questions_Headings,
            "PAF_Slot_Name": PAF_Question_Slot_Names,
            "PAF_Index": PAF_Questions_Index,
            "Slot_Value": [""] * len(PAF_Questions),
            "Patient_Answer": [""] * len(PAF_Questions),
            "Slot_Display": [""] * len(PAF_Questions),
            "PAF_Question_ID": PAF_Question_ID,
            "Assessed": questions_assessed,
        }
    )
    for slot_key, slot_filling_info in data.items():
        if slot_key in PAF_Question_Slot_Names:
            slot_index = PAF_Question_Slot_Names.index(slot_key)
            PAF_table.at[slot_index, "Slot_Value"] = slot_filling_info.get("slot_value", "")
            PAF_table.at[slot_index, "Patient_Answer"] = slot_filling_info.get("patient_answer", "")
            PAF_table.at[slot_index, "Slot_Display"] = convert_paf_questionnaire_line(
                slot_key, slot_filling_info.get("slot_value", "")
            )
    # Fill the N.A. for follow-up questions if follow-up questions are not asked
    PAF_table = fill_NA_follow_up_questions(PAF_table)
    return PAF_table

def fill_NA_follow_up_questions(ori_data: pd.DataFrame):
    if (
        process_slot_string(ori_data.at[1, "Slot_Value"]) == "no"
    ):
        ori_data.at[2, "Slot_Value"] = "N.A."
        ori_data.at[3, "Slot_Value"] = "N.A."
    if (
        process_slot_string(
            ori_data.at[7, "Slot_Value"]
        )
        == "no"
    ):
        ori_data.at[8, "Slot_Value"] = "N.A."
    return ori_data

def color_coding(row):
    return (
        ["background-color:grey"] * len(row)
        if row.Assessed
        else ["background-color:white"] * len(row)
    )

def set_opacity(s):
    return ["opacity: 0.5" if v else "" for v in s]

def set_text_color(s):
    return ["color: grey" if v else "" for v in s]

def set_background_color(s):
    return ["background-color:lightgrey" if v else "background-color:white" for v in s]


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
