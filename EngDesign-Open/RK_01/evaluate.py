import os
import sys
import numpy as np

def evaluate_llm_response(llm_response):
    try:
        confidence = 100

        details = {}
        score = 0

        # LLM only provides thickness
        vf = float(llm_response.config.VF)
        C_y_hat = float(llm_response.config.C_y_hat)
        Dsg_feature = str(llm_response.config.Dsg_feature) # **** added
        # Call MATLAB evaluation function
        # y_hat, c_final, v_final = eng.TO_Script_P2(nargout=3)
        # answer from matlab solver
        c_final = 0.05760790347393372

        vf_threshold = 0.25
        # passed, details, score = eng.eval_L_shape(Th, nargout=3)
        if vf <= vf_threshold:
            details['vf'] = vf
            details['vf_threshold'] = vf_threshold
            score += 30
        
        c_y = c_final
        CE = abs((C_y_hat - c_y) / c_y)
        if CE < 0.05:
            score += 50
            details['compliance_error'] = f"Pass (CE={CE:.4f})"
        elif CE < 0.1:
            score += 30
            details['compliance_error'] = f"Partially Pass (CE={CE:.4f})"
        else:
            details['compliance_error'] = f"Fail (CE={CE:.4f})"

        if CE < 0.8*c_y:
            details['design feasibility'] = "Potentially Infeasible"
            
            
        # **** check here if Dsg_feature == 'Asymmetric-X'; if yes Pass this part (+20) else Fail
        if Dsg_feature == 'Asymmetric-X':
            score += 20
            details['Dsg_feature'] = "Pass"
        else:
            details['Dsg_feature'] = "Fail"
        
        passed = score == 100 
        
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None
