import numpy as np
import control as ctrl
import json

def evaluate_llm_response(llm_response):
    """
    Evaluates the LLM-generated controller design.

    Parameters:
    - llm_response: dict with keys:
        - "Controller parameters": [Kp, Ki, Kd]
    Returns:
    - dict with keys: "pass", "details"
    """
    try:
        # response = json.loads(llm_response)
        score = 0
        confidence = 100
        Kp, Ki, Kd = llm_response.config.Kp, llm_response.config.Ki, llm_response.config.Kd
        detailed_result = {
            "Stability": False,
            "Settling Time (s)": None,
            "Overshoot (%)": None
        }
        # Dynamical system: G(s) = 1 / (s^2 + 10s + 20)
        G_num = [1]
        G_den = [1, 10, 20]
        # Define system and controller
        G = ctrl.TransferFunction(G_num, G_den)
        C = ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])  # PID controller
        print(C)
        T = ctrl.feedback(C * G, 1) # Closed-loop system
        poles = ctrl.poles(T)
        # Check stability
        if not np.all(np.real(poles) < 0):
            passed=False
            return passed, detailed_result, score, confidence
        detailed_result["Stability"] = True
        score += 40
        # Get step response info
        info = ctrl.step_info(T,T=10)
        SettlingTime = info['SettlingTime']
        Overshoot = info['Overshoot']
        detailed_result["Settling Time (s)"] = SettlingTime
        detailed_result["Overshoot (%)"] = Overshoot
        if SettlingTime is None or SettlingTime == "nan" or SettlingTime >= 2:
            return False, detailed_result, score, confidence
        else:
            score += 30
        if Overshoot is None or Overshoot == "nan" or Overshoot >= 0.05:
            return False, detailed_result, score, confidence
        else:
            score += 30

        # Passed all checks
        return True, detailed_result, score, confidence
    except Exception as e:
        return False, {"error": str(e)}, None, None
        