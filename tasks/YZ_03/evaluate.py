import numpy as np
import matlab.engine
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from evaluation.llm_judge import LLMJudge

def evaluate_llm_response(llm_response):
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_antenna.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        
        # Get antenna coefficients from LLM response
        relativeBW = llm_response.relativeBW
        r = llm_response.r
        D = llm_response.D
        turns = llm_response.turns
        pitch = llm_response.pitch
        side = llm_response.side
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_antenna(relativeBW, r, D, turns, pitch, side, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# # Check the performance of the reference solution
# relativeBW = 0.45
# r = 0.3e-3
# D = 56e-3
# turns = 17.5
# pitch = 11.2
# side = 600e-3
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, relativeBW, r, D, turns, pitch, side):
#         self.relativeBW = relativeBW
#         self.r = r
#         self.D = D
#         self.turns = turns
#         self.pitch = pitch
#         self.side = side
# llm_response = LLMResponse(relativeBW, r, D, turns, pitch, side)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
