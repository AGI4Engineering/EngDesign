import numpy as np
# import matlab.engine
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Tuple, Dict

def evaluate_llm_response(llm_response) -> Tuple[bool, Dict, int, float]:
    """
    Evaluate the LLM response for a topology optimization task based on a predefined rubric.

    Parameters:
    - llm_response: An object with structure matching ConfigFile.
    - y_true: Ground truth topology (64x64 numpy array with 0/1).
    - C_y: Ground truth compliance value.
    - VF_y: Ground truth volume fraction.

    Returns:
    - passed (bool): Whether the design passed all hard constraints.
    - details (dict): Detailed score breakdown and possible errors.
    - score (int): Total score based on the evaluation rubric.
    - confidence (float): Confidence in result correctness (placeholder metric).
    """
    passed = False
    score = 0
    confidence = 100
    details = {}

    C_y = 5.277
    VF_y = 0.48

    try:
        # y_hat = np.array(llm_response.config.y_hat)
        C_y_hat = llm_response.config.C_y_hat
        VF_y_hat = llm_response.config.VF_y_hat
        # load_y_hat = np.array(llm_response.config.load_y_hat)
        # floating_material_y_hat = llm_response.config.floating_material_y_hat

        # Check shape and binary content of y_hat
        # if y_hat.shape == (64, 64) and np.isin(y_hat, [0, 1]).all():
        #     score += 40
        #     details['y_hat_shape_and_values'] = "Pass"
        # else:
        #     details['y_hat_shape_and_values'] = "Fail"
        # job completed
        score += 10
        # Compliance Error
        CE = abs((C_y_hat - C_y) / C_y)
        if CE < 0.05:
            score += 70
            details['compliance_error'] = f"Pass (CE={CE:.4f})"
        else:
            details['compliance_error'] = f"Fail (CE={CE:.4f})"

        # Volume Fraction Error
        VFE = abs(VF_y_hat - VF_y) / VF_y
        if VFE < 0.02:
            score += 20
            details['volume_fraction_error'] = f"Pass (VFE={VFE:.4f})"
        else:
            details['volume_fraction_error'] = f"Fail (VFE={VFE:.4f})"

        # Load Violation (we assume ground truth load matrix for this check)
        # Load violation = if any load appears at a node where there shouldn't be one
        # Here, we assume y_true also encodes where loads are expected to be.
        # For now, we assume all non-zero loads are acceptable, so LV=0 means all values okay.
        # if np.isfinite(load_y_hat).all():  # placeholder check
        #     score += 20
        #     details['load_violation'] = "Pass (LV=0)"
        # else:
        #     details['load_violation'] = "Fail (non-finite values in load_y_hat)"

        # # Floating Material
        # if not floating_material_y_hat:
        #     score += 20
        #     details['floating_material'] = "Pass (FM=0)"
        # else:
        #     details['floating_material'] = "Fail (FM=1)"

        # Determine pass/fail
        passed = score >= 80  # Example threshold

    except Exception as e:
        details['error'] = str(e)
        confidence = 0
        return False, details, None, None

    return passed, details, score, confidence