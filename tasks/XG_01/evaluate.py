import numpy as np
import matlab.engine
import os

def evaluate_llm_response(llm_response):
    # print(llm_response)
    try:
        # Start MATLAB engine
        eng = matlab.engine.start_matlab()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        eng.addpath(current_dir)
        
        # Get controller coefficients from LLM response
        num = matlab.double(llm_response.config.num)
        den = matlab.double(llm_response.config.den)
        alpha = float(llm_response.config.alpha)
        
        # Run MATLAB evaluation
        passed, details, score = eng.disk_margin_eval(num, den, alpha, nargout=3)

        details = {key: details[key] for key in details.keys()}
        
        eng.quit()

        ## write the code to evaluate 
        return passed, details, score, 100 
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# Check the performance of the reference solution
# num = 8
# den = [1,0]
# alpha = 0.15
# result = evaluate_llm_response(num, den, alpha)
# print(result)

