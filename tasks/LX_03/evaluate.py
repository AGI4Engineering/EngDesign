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
        p1 = llm_response.config.p1
        p2 = llm_response.config.p2
        ts = llm_response.config.ts
        N = llm_response.config.N
        pm = llm_response.config.pm

        k1 = llm_response.config.k1
        k2 = llm_response.config.k2
        k3 = llm_response.config.k3
        k4 = llm_response.config.k4

        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_controller(
            p1, p2, ts, N, pm, k1, k2, k3, k4, nargout=3
        )
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        eng.quit()
        return passed, details, score, confidence
    except Exception as e:
        return False, {"error": str(e)}, None, None
