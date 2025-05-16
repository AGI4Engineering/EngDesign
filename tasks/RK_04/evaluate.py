import matlab.engine
import os
import sys
import numpy as np

def evaluate_llm_response(llm_response):
    try:
        confidence = 100
        # eng = matlab.engine.start_matlab()

        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # eng.addpath(current_dir)
        details = {}
        score = 0

        # LLM only provides thickness
        vf = float(llm_response.config.VF)
        s_y_hat = float(llm_response.config.s_hat)
        Dsg_feature = str(llm_response.config.Dsg_feature) # **** added
        # Call MATLAB evaluation function
        # y_hat, s_final, v_final = eng.TO_Script_P6(nargout=3)
        # y_hat = np.array(y_hat)
        s_final = 127.0354390356293

        # eng.quit()

        # passed, details, score = eng.eval_L_shape(Th, nargout=3)
        vf_threshold = 0.25
        if vf <= vf_threshold:
            details['vf'] = vf
            details['vf_threshold'] = vf_threshold
            score += 10
        
        s_y = s_final
        if s_y_hat <= 130 and s_y_hat >= 115:
            score += 70
            details['max_stress'] = f"Pass (s_y_hat={s_y_hat:.4f})"
        elif s_y_hat <= 155:
            score += 40
            details['max_stress'] = f"Partially Pass (s_y_hat={s_y_hat:.4f})"
        else:
            details['max_stress'] = f"Fail (s_y_hat={s_y_hat:.4f})"
        # CE = abs((C_y_hat - c_y) / c_y)
        # if CE < 0.05:
        #     score += 60
        #     details['compliance_error'] = f"Pass (CE={CE:.4f})"
        # elif CE < 0.1:
        #     score += 40
        #     details['compliance_error'] = f"Partially Pass (CE={CE:.4f})"
        # else:
        #     details['compliance_error'] = f"Fail (CE={CE:.4f})"

        # if CE < 0.9*c_y:
        #     details['design feasibility'] = "maybe Infeasible"
        
        # **** check here if Dsg_feature == 'Symmetric-X'; if yes Pass this part (+20) else Fail
        if Dsg_feature == 'Symmetric-X':
            score += 20
            details['Dsg_feature'] = "Pass"
        else:
            details['Dsg_feature'] = "Fail"
        passed = score == 100
        
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None
