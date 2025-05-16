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
        # y_hat, c_final, v_final = eng.TO_Script_P4(nargout=3)
        # y_hat = np.array(y_hat)
        # print("y_hat shape", y_hat.shape)
        # print("compliance", c_final)
        c_final = 0.010279918646740807
        # eng.TO_Script_P2(nargout=0)

        # passed, details, score = eng.eval_L_shape(Th, nargout=3)
        vf_threshold = 0.15
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
            
        # **** check here if Dsg_feature == 'Symmetric-XY'; if yes Pass this part (+20) else Fail (may give some partial credit (+10) if 'Symmetric-X')
        if Dsg_feature == 'Symmetric-XY':
            score += 20
            details['Dsg_feature'] = "Pass"
        elif Dsg_feature == 'Symmetric-X':
            score += 10
            details['Dsg_feature'] = "Partially Pass"
        else:
            details['Dsg_feature'] = "Fail"
        passed = score == 100 
        
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None
