import numpy as np
import matlab.engine
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def evaluate_llm_response(llm_response):
    try:
        # Start MATLAB engine
        confidence = 100
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        # Get controller coefficients from LLM response
        a11 = llm_response.config.a11
        a12 = llm_response.config.a12
        a21 = llm_response.config.a21
        a22 = llm_response.config.a22
        b11 = llm_response.config.b11
        b21 = llm_response.config.b21
        k1 = llm_response.config.k1
        k2 = llm_response.config.k2
        l1 = llm_response.config.l1
        l2 = llm_response.config.l2
        s1 = llm_response.config.s1
        s2 = llm_response.config.s2
        s3 = llm_response.config.s3
        s4 = llm_response.config.s4
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_controller(
            a11, a12, a21, a22, b11, b21, k1, k2, l1, l2, s1, s2, s3, s4, nargout=3
        )
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        eng.quit()
        return passed, details, score, confidence
    except Exception as e:
        return False, {"error": str(e)}, None, None
