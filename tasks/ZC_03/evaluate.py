import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    # try:
        # Start MATLAB engine
    confidence = 100
    eng = matlab.engine.start_matlab()
    # Add the path containing verifybounds.m
    current_dir = os.path.dirname(os.path.abspath(__file__))
    eng.addpath(current_dir)

    bar_alpha = matlab.double(llm_response.config.bar_alpha)
    bar_beta = matlab.double(llm_response.config.bar_beta)
    underline_alpha = matlab.double(llm_response.config.under_linealpha)
    underline_beta = matlab.double(llm_response.config.under_linebeta)

    # Run MATLAB evaluation
    passed, details, score = eng.verifybounds(bar_alpha,bar_beta,underline_alpha,underline_beta, nargout=3)
    # Convert MATLAB struct to Python dict
    details = {key: details[key] for key in details.keys()}

    eng.quit()
    return passed, details, score, confidence

    # except Exception as e:
    #     return False, {"error": str(e)}, None, None