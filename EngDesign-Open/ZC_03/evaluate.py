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
        # Add the path containing verifybounds.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        oc.addpath(current_dir)

        bar_alpha = llm_response.config.bar_alpha
        bar_beta = llm_response.config.bar_beta
        underline_alpha = llm_response.config.under_linealpha
        underline_beta = llm_response.config.under_linebeta

        # Run Octave evaluation
        passed, details, score = oc.verifybounds(bar_alpha,bar_beta,underline_alpha,underline_beta, nout=3)
        # Convert Octave struct to Python dict
        details = {key: details[key] for key in details.keys()}

        oc.exit()
        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None