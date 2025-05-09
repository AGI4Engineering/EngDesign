import matlab.engine
import os
import sys
import numpy as np

def evaluate_llm_response(llm_response):
    try:
        confidence = 100
        eng = matlab.engine.start_matlab()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)

        # LLM only provides thickness
        Th = float(llm_response.config.Th)
        # Call MATLAB evaluation function
        passed, details, score = eng.eval_L_shape(Th, nargout=3)

        details = {key: details[key] for key in details.keys()}
        eng.quit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None
