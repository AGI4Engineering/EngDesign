
import numpy as np
import os
import sys
from s1 import run_simulation
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def evaluate_llm_response(llm_response):
    try:
        r = llm_response.config.refresh_rate
        a = llm_response.config.acceleration
        v = llm_response.config.max_velocity
        l = llm_response.config.lookahead_distance
        passed, dict = run_simulation(r,a,v,l)
        if(passed):
            score = 100
        else:
            score = 0
        return passed, dict, score, 100
        
    except Exception as e:
        return False, {"error": str(e)}, None, None
