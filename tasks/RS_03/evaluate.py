import numpy as np
#import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evaluation.llm_judge import LLMJudge


def evaluate_llm_response(llm_response):
    try:

        from CorAcc import CorAcc

        setupFileName = "SetupFile.json"

        score = 0
        passed = True
        confidence = 100

            # object instantiation
        coracc = CorAcc(setupFileName)
        force_on_neck = coracc.run()

        neck_force_diff = force_on_neck - llm_response.config.force_on_neck
        

        details = {"corner_acceleration_differnce": neck_force_diff}

        if abs(neck_force_diff) <= 1:
            score += 50
        if abs(neck_force_diff) <= 2:
            score += 25
        if abs(neck_force_diff) <= 3:
            score += 15
        if abs(neck_force_diff) <= 4:
            score += 10

        if score == 0:
            passed = False

        return passed, details, score, confidence

    except Exception as e:
        return False, ("error: ", str(e)), None, None

