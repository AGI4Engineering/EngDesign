import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    details = {}
    confidence = 100
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)

        # Get controller coefficients from LLM response
        C_num = llm_response.config.C_num
        C_den = llm_response.config.C_den
        omega_r = llm_response.config.omega_r
        beta_r = llm_response.config.beta_r
        
        try:
            # Run MATLAB evaluation
            passed, details, score = eng.roll_over(matlab.double(C_num), matlab.double(C_den), omega_r, beta_r, nargout=3)
            
            # Convert MATLAB struct to Python dict
            details = {key: details[key] for key in details.keys()}
            
        except matlab.engine.MatlabExecutionError as matlab_err:
            eng.quit()
            return False, {"error": f"MATLAB Error: {str(matlab_err)}"}, 0, confidence
            
        eng.quit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": f"Python Error: {str(e)}"}, 0, confidence
