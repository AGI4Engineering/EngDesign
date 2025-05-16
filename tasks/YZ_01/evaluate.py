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
        # Add the path containing evaluate_converter.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        
        # Get converter coefficients from LLM response
        Fpass = llm_response.config.Fpass
        Fstop = llm_response.config.Fstop
        Ast = llm_response.config.Ast
        Ap = llm_response.config.Ap
        Factor_1 = llm_response.config.Factor_1
        Factor_2 = llm_response.config.Factor_2
        
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_converter(Fpass, Fstop, Ast,
                                                        Ap, Factor_1, Factor_2, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# # Check the performance of the reference solution
# Fpass = 10.0
# Fstop = 15.36
# Ast = 45.0
# Ap = 0.1
# Factor_1 = 2.0
# Factor_2 = 2.0
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, Fpass, Fstop, Ast, Ap, Factor_1, Factor_2):
#         self.Fpass = Fpass
#         self.Fstop = Fstop
#         self.Ast = Ast
#         self.Ap = Ap
#         self.Factor_1 = Factor_1
#         self.Factor_2 = Factor_2
# llm_response = LLMResponse(Fpass, Fstop, Ast, Ap, Factor_1, Factor_2)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
