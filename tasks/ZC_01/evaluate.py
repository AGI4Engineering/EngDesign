import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:
        # Start MATLAB engine
        confidence = 100
        eng = matlab.engine.start_matlab()
        # Add the path containing verifyK.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)

        # Get controller coefficients from LLM response
        K = matlab.double(llm_response.config.K)

        # Run MATLAB evaluation
        passed, details, score = eng.verifyK(K, nargout=3)

        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}

        eng.quit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None