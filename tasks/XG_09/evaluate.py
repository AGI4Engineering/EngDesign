import numpy as np
import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evaluation.llm_judge import LLMJudge

def evaluate_llm_response(llm_response):
    
    passed = False
    score = 0
    confidence = 100
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)

        # Get controller coefficients from LLM response
        sx = llm_response.config.sx
        sy = llm_response.config.sy
        wa = llm_response.config.wa
        wb = llm_response.config.wb
        wc = llm_response.config.wc
        ba = llm_response.config.ba
        bb = llm_response.config.bb
        bc = llm_response.config.bc
        
        try:
            # Run MATLAB evaluation
            passed, details, score = eng.edge_detection_evaluation(sx, sy, wa, wb, wc, ba, bb, bc, nargout=3)
            
            # Convert MATLAB struct to Python dict
            details = {key: details[key] for key in details.keys()}
            
        except matlab.engine.MatlabExecutionError as matlab_err:
            eng.quit()
            return False, {"error": f"MATLAB Error: {str(matlab_err)}"}, 0, confidence
            
        eng.quit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": f"Python Error: {str(e)}"}, 0, confidence
