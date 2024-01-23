import pandas as pd

# 'cough_existence', 'sputum_existence', 'sputum_amount', 'sputum_color', 'history_of_falling', 'ambulatory_aid', 'vision_problem', 'weight_loss_existance', 'weight_loss_amount', 'appetite_loss', 'denture', 'denture_option', 'special_diet', 'food_preference'
PAF_Question_Mapping = {
    "Coughing": 'q1_0_coughing_existance', 
    "Sputum": 'q2_0_sputum_existance', 
    "Amount": 'q2_1_sputum_amount',
    "Color": 'q2_2_sputum_colour',
    # "History of Falling": 'q3_0_history_falling',
    # "Ambulatory Aid": 'q3_1_ambulatory_aid',
    # "Vision": 'q4_0_vision',
    "Weight Loss": 'q5_0_lose_weight_existance',
    "Weight Loss Amount": 'q5_1_lose_weight_amount',
    "Appetite Loss": 'q5_2_decreased_appetite',
    # "Denture": 'q6_0_denture',
    # "Denture Type": 'q6_1_dental_followup_fixed_or_removable',
    # "Special Diet": 'q7_0_diet',
    "Food Preference": 'q7_2_food_preference'
}

PAF_Questions = list(PAF_Question_Mapping.keys())
PAF_Questions_Bilingual = [
    "Coughing 請問有冇咳？",
    "Sputum 請問有冇痰？",
    "Sputum Amount 有痰的話，有幾多量？",
    "Sputum Color 痰顏色係咩？",
    # "History of Falling 有冇跌過？",
    # "Ambulatory Aid 有冇用過行動輔助器具？",
    # "Vision Problem 視力問題？",
    "Weight Loss 有冇體重下降？",
    "Weight Loss Amount 輕咗幾多？",
    "Appetite Loss 胃口差别？",
    # "Denture 有冇假牙？",
    # "Denture Type 假牙係固定定可拆卸？",
    # "Special Diet 有冇特別飲食？",
    "Food Preference 咩唔食？",
]

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
                paf_result["PAF_Result"][i] = convert_paf_questionnaire_line(slot_key, slot_filling_info.get("slot_value", "N.A."))
            
            
            
    except Exception:
        paf_result = {}
    return pd.DataFrame(paf_result)

def fill_NA_follow_up_questions(ori_data: dict):
    if ori_data.get("q2_0_sputum_existance", {}).get("slot_value", "").lower() == "no":
        ori_data["q2_1_sputum_amount"] = {"slot_value": "N.A."}
        ori_data["q2_2_sputum_colour"] = {"slot_value": "N.A."}
    if ori_data.get("q5_0_lose_weight_existance", {}).get("slot_value", "").lower() == "no":
        ori_data["q5_1_lose_weight_amount"] = {"slot_value": "N.A."}
    return ori_data


def convert_paf_questionnaire_line(slot_key, slot_value:str):
    if slot_key in ["q1_0_coughing_existance", "q2_0_sputum_existance", "q3_0_history_falling", "q4_0_vision", "q5_0_lose_weight_existance", "q5_2_decreased_appetite", "q6_0_denture", "q7_0_diet"]:
        if slot_value.lower() not in ["yes", "no"]:
            return slot_value
        else:
            if slot_value.lower() == "yes":
                return "☐ No \t ☑️ Yes"
            else:
                return "☑️ No \t ☐ Yes"
    elif slot_value == "N.A.":
        return slot_value
    else:
        return slot_value