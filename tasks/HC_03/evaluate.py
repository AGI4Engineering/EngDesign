import numpy as np
from typing import Dict, Tuple

def evaluate_llm_response(llm_response) -> Tuple[bool, Dict, float, float]:
    """
    Evaluate the phase correlation result between two images.
    
    Args:
        pred (Dict): Prediction output from the model (must contain Dimensionality, Scale, RotationAngle, Translation, R, A)
        gt (Dict): Ground truth values from real imregcorr output.

    Returns:
        passed (bool): Whether all criteria are met
        details (Dict): Detailed error metrics
        score (float): Final score (out of 100)
        confidence: confidence score (out of 100)
    """
    try:
        x = np.array([-2, -1, 0, 1, 2, 3])
        y = np.array([7.9, 2.0, 0.1, 2.2, 6.0, 12.1])

        coeffs = np.polyfit(x, y, deg=2)  # return [a, b, c]
        a, b, c = coeffs
        y_pred = a * x**2 + b * x + c
        
        pred_a = float(llm_response.config.a)
        pred_b = float(llm_response.config.b)
        pred_c = float(llm_response.config.c)
        pred = pred_a * x**2 + pred_b * x + pred_c
        
        pass_a = abs(a - pred_a) < 0.05
        pass_b = abs(b - pred_b) < 0.05
        pass_c = abs(c - pred_c) < 0.05
        pass_y = np.all(abs(y_pred - pred) < 0.1) 

        # --- Scoring ---
        score = 0
        if pass_a:
            score += 20
        if pass_b:
            score += 20
        if pass_c:
            score += 20
        if pass_y:
            score += 40

        passed = score == 100

        details = {
            "Coefficient a is correct": pass_a,
            "Coefficient b is correct": pass_b,
            "Coefficient c is correct": pass_c,
            "Errors in the fit are within acceptable limits": pass_y
        }

        return passed, details, score, 100
    
    except Exception as e:
        return False, {"error": str(e)}, None, None