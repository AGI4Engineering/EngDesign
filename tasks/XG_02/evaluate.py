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
        
        # Run MATLAB evaluation
        passed, details, score = eng.evaluate_controller(num, den, nargout=3)
        
        # Convert MATLAB struct to Python dict
        details = {key: details[key] for key in details.keys()}
        
        eng.quit()
        return passed, details, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None

# Check the performance of the reference solution
# num = [1.4493e+03, 5.0291e+05, 8.1368e+09, 2.5012e+12]
# den = [1, 1.8372e+03, 6.8929e+06, 2.4391e+09, -7.0209e+11]
# result = evaluate_llm_response(num, den)
# print(result)


