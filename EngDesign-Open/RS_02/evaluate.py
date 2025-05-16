import numpy as np
#import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))



def evaluate_llm_response(llm_response):
    try:

        from FullCarAcc import FullCarAcc

        setupFileName = "SetupFile.json"

        score = 0
        passed = True
        confidence = 100

            # object instantiation
        fullCarAcc = FullCarAcc(setupFileName)
        max_acc, max_dec = fullCarAcc.run()

        max_acc_diff = max_acc - llm_response.config.max_acc
        max_dec_diff = max_dec - llm_response.config.max_dec
        

        details = {"Max_acceleration_differnce": max_acc_diff, "Max_deceleration_difference": max_dec_diff}

        if abs(max_acc_diff) <= 0.5 and abs(max_dec_diff) <= 0.5:
            score += 50
        if abs(max_acc_diff) <= 1 and abs(max_dec_diff) <= 1:
            score += 25
        if abs(max_acc_diff) <= 1.5 and abs(max_dec_diff) <= 1.5:
            score += 15
        if abs(max_acc_diff) <= 2 and abs(max_dec_diff) <= 2:
            score += 10

        if score == 0:
            passed = False

        return passed, details, score, confidence

    except Exception as e:
        return False, ("error: ", str(e)), None, None

