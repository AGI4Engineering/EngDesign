import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evaluation.llm_judge import LLMJudge

def evaluate_llm_response(llm_response):
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        
        # Get controller coefficients from LLM response
        theta = llm_response.config.theta
        tau = llm_response.config.tau
        num = matlab.double(llm_response.config.num)
        den = matlab.double(llm_response.config.den)
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_controller(theta, tau, num, den, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# # Check the performance of the reference solution
# tau = 21.3
# theta = 14.7
# num = [23.24, 0.9]
# den = [25.82, 0]
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, theta, tau, num, den):
#         self.theta = theta
#         self.tau = tau
#         self.num = num
#         self.den = den
# llm_response = LLMResponse(theta, tau, num, den)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
