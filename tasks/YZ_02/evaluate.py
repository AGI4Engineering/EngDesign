import numpy as np
import matlab.engine
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def evaluate_llm_response(llm_response):
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_SG_filter.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        
        # Get converter coefficients from LLM response
        coeff_list_1 = matlab.double(llm_response.config.coeff_list_1)
        coeff_list_2 = matlab.double(llm_response.config.coeff_list_2)
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_SG_filter(coeff_list_1, coeff_list_2, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# # Check the performance of the reference solution
# coeff_list_1 = [6.352, 1.379, 0.513, 0.316]
# coeff_list_2 = [0.509, 0.1922, -0.001485]
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, coeff_list_1, coeff_list_2):
#         self.coeff_list_1 = coeff_list_1
#         self.coeff_list_2 = coeff_list_2
# llm_response = LLMResponse(coeff_list_1, coeff_list_2)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
