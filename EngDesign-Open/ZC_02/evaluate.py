import numpy as np
from oct2py import Oct2Py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:
        # Start Octave engine
        confidence = 100
        oc = Oct2Py()
        # Add the path containing verifyalpha.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        oc.addpath(current_dir)

        # Get controller coefficients from LLM response
        alpha = llm_response.config.alpha

        # Run Octave evaluation
        passed, details, score = oc.verifyalpha(alpha, nout=3)

        # Convert Octave struct to Python dict
        details = {key: details[key] for key in details.keys()}

        oc.exit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None