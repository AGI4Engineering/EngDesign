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
        # Add the path containing evaluate_battery.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        evaluate_battery_dir = os.path.join(current_dir, 'evaluate_battery')
        eng.addpath(evaluate_battery_dir)
        
        # Get antenna coefficients from LLM response
        numCells_p = llm_response.numCells_p
        numCells_s = llm_response.numCells_s
        NumChannel = llm_response.NumChannel
        Flowrate = llm_response.Flowrate
        ChannelDia = llm_response.ChannelDia
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_battery(numCells_p, numCells_s, NumChannel, Flowrate, ChannelDia, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# # Check the performance of the reference solution
# numCells_p = 3.0
# numCells_s = 5.0
# NumChannel = 3.0
# Flowrate = 1.0
# ChannelDia = 0.002
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, numCells_p, numCells_s, NumChannel, Flowrate, ChannelDia):
#         self.numCells_p = numCells_p
#         self.numCells_s = numCells_s
#         self.NumChannel = NumChannel
#         self.Flowrate = Flowrate
#         self.ChannelDia = ChannelDia
# llm_response = LLMResponse(numCells_p, numCells_s, NumChannel, Flowrate, ChannelDia)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
