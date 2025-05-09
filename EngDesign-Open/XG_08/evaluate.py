import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    passed = False
    score = 0
    details = {
        "membership_function_score": 0,
        "rule_list_score": 0,
        "tip1_score": 0, 
        "tip2_score": 0,
        "rule_list_error": None,
        "tip1_error": None,
        "tip2_error": None
    }
    confidence = 100
    try:
        score = 0
        passed = True
        details = {}

        # Task 1: Check membership functions
        membership_functions = [
            (llm_response.config.MISSING_type1, "gaussmf", [1.5, 0], llm_response.config.MISSING_parameters1),
            (llm_response.config.MISSING_type2, "gaussmf", [1.5, 5], llm_response.config.MISSING_parameters2),
            (llm_response.config.MISSING_type3, "gaussmf", [1.5, 10], llm_response.config.MISSING_parameters3),
            (llm_response.config.MISSING_type4, "trapmf", [-2, 0, 1, 3], llm_response.config.MISSING_parameters4),
            (llm_response.config.MISSING_type5, "trapmf", [7, 9, 10, 12], llm_response.config.MISSING_parameters5),
            (llm_response.config.MISSING_type6, "trimf", [0, 5, 10], llm_response.config.MISSING_parameters6),
            (llm_response.config.MISSING_type7, "trimf", [10, 15, 20], llm_response.config.MISSING_parameters7),
            (llm_response.config.MISSING_type8, "trimf", [20, 25, 30], llm_response.config.MISSING_parameters8)
        ]

        for i, (type_actual, type_expected, params_expected, params_actual) in enumerate(membership_functions, 1):
            if type_actual == type_expected:
                score += 2
            if params_actual == params_expected:
                score += 2
            if type_actual != type_expected or params_actual != params_expected:
                passed = False
        
        details["membership_function_score"] = score

        # Task 2: Check rule list
        expected_rules = [[1, 1, 1, 1, 2], [2, 0, 2, 1, 1], [3, 2, 3, 1, 2]]
        if llm_response.config.MISSING_rule_list == expected_rules:
            score += 26
            details["rule_list_score"] = 26
        else:
            passed = False
            details["rule_list_error"] = "Rule list is not correct"

        # Task 3: Check tips
        if abs(llm_response.config.MISSING_tip1 - 5.5586) < 0.1:
            score += 25
            details["tip1_score"] = 25
        else:
            passed = False
            details["tip1_error"] = "Tip for input 1 is not correct"


        if abs(llm_response.config.MISSING_tip2 - 15.5415) < 0.1:
            score += 25
            details["tip2_score"] = 25
        else:
            passed = False
            details["tip2_error"] = "Tip for input 2 is not correct"

        return passed, details, score, confidence
    except Exception as e:
        return "Evaluation failed", {"error": str(e)}, None, None

