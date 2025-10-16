import numpy as np
from oct2py import Oct2Py
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def evaluate_llm_response(llm_response):
    try:
        # Start Octave engine
        confidence = 100
        oc = Oct2Py()
        # Add the path containing evaluate_controller.m
        current_dir = os.path.dirname(os.path.abspath(__file__))
        oc.addpath(current_dir)
        # Get controller coefficients from LLM response
        a11 = llm_response.config.a11
        a12 = llm_response.config.a12
        a21 = llm_response.config.a21
        a22 = llm_response.config.a22
        b11 = llm_response.config.b11
        b21 = llm_response.config.b21
        k1 = llm_response.config.k1
        k2 = llm_response.config.k2
        l1 = llm_response.config.l1
        l2 = llm_response.config.l2
        s1 = llm_response.config.s1
        s2 = llm_response.config.s2
        s3 = llm_response.config.s3
        s4 = llm_response.config.s4
        # Run Octave evaluation
        passed, details, score = oc.evaluate_controller(
            a11, a12, a21, a22, b11, b21, k1, k2, l1, l2, s1, s2, s3, s4, nout=3
        )
        # Convert Octave struct to Python dict
        # Oct2Py 会自动转换，但我们可以确保它是字典
        if hasattr(details, '_fields'):
            details = {key: getattr(details, key) for key in details._fields}
        elif not isinstance(details, dict):
            details = dict(details)
        oc.exit()
        return passed, details, score, confidence
    except Exception as e:
        return False, {"error": str(e)}, None, None
