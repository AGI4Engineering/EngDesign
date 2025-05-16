import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evaluation.llm_judge import LLMJudge

def evaluate_llm_response(llm_response):
    passed = False
    score = 0
    details = {}
    confidence = 100
    try:
        A = np.array(llm_response.config.A).tolist()
        B = np.array(llm_response.config.B).tolist()
        beta = llm_response.config.beta
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        try:
            passed, details, score = eng.evaluate_H_inf_controller(
                matlab.double(A),
                matlab.double(B),
                beta,
                nargout=3
            )
        except Exception as e:
            passed = False
            details = {"error": str(e)}
            score = 0
            confidence = 0
        return passed, details, score, confidence
        
    except Exception as e:
        return False, {"error": str(e)}, None, None
