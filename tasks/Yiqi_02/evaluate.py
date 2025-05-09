import numpy as np

import math
import os
import sys
import tsim_simple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def evaluate_llm_response(llm_response):
    try:
        F_op = llm_response.config.F_op
        f_t_A_m = llm_response.config.f_t_A_m
        f_t_A_k = llm_response.config.f_t_A_k
        f_t_B_k = llm_response.config.f_t_B_k
        f_t_B_n = llm_response.config.f_t_B_n
        f_t_C_m = llm_response.config.f_t_C_m
        f_t_C_n = llm_response.config.f_t_C_n

        score, t10_time, ai_time = tsim_simple.get_score(F_op, f_t_A_m, f_t_A_k, f_t_B_k, f_t_B_n, f_t_C_m, f_t_C_n)

        # Evaluation
        passed = (
                score >= tsim_simple.VALID_SPA_SCORE + tsim_simple.VALID_TEM_SCORE
        )

        details = {
            "F_op": F_op,
            "f_t_A_m": f_t_A_m,
            "f_t_A_k": f_t_A_k,
            "f_t_B_k": f_t_B_k,
            "f_t_B_n": f_t_B_n,
            "f_t_C_m": f_t_C_m,
            "f_t_C_n": f_t_C_n,
            "score": score,
            "t10_time": t10_time,
            "ai_time": ai_time,
            "passed": passed
        }
        
        return bool(passed), details, float(score), 100

    except Exception as e:
        return False, {"error": str(e)}, None, None