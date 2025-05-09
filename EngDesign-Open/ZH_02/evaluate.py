import numpy as np
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:
        r = llm_response.config.r

        v0 = 7800  # m/s
        rho0 = 1.225  # kg/m^3
        rho = 0.004 # kg/m^3 at 40km
        CD = 0.47
        m = 250  # kg
        h = 400000  # m
        g = 9.81  # m/s^2
        k = 1.7415e-4  # Earth Sutton-Graves coefficient

        # 1. Peak heat flux [W/m^2]
        q_max = k * ((rho / r) ** 0.5) * v0 ** 3

        # 2. Total heat load [J/m^2] conservative estimate: all KE + PE into heat per unit area
        total_energy = 0.5 * m * v0 ** 2 + m * g * h - 0.5 * m * 5500 ** 2  # in J
        total_energy *= 0.5
        area = math.pi * r ** 2  # m^2
        Q = total_energy / area  # in J/m^2

        # 3. Peak deceleration [m/s^2]
        a_max = (CD * 0.0004 * area * 5500 ** 2) / (2 * m)

        # Evaluation
        passed = (
                q_max <= 10000000 and
                Q <= 100000000 and
                a_max <= 30 * g
        )

        details = {
            "r": r,
            "q_max_W_per_cm2": q_max,
            "Q_J_per_m2": Q,
            "a_max_mps2": a_max,
            "passed": passed
        }

        # Score (optional simple rubric)
        score = (q_max <= 10000000) * 30 + (Q <= 100000000) * 30 + (a_max <= 30 * g) * 40

        print(details)
        print(score)
        if score == 100:
            passed = True
        else:
            passed = False
        return passed,details, score,100

    except Exception as e:
        return False, {"error": str(e)}, None, None




# # Check the performance of the reference solution
# tau = 21.3
# theta = 14.7
# num = [23.24, 0.9]
# den = [25.82, 0]
# # Create a class to hold the response data
# class LLMResponse:
#     def __init__(self, theta, tau, num, den):
#         self.theta = theta
#         self.tau = tau
#         self.num = num
#         self.den = den
# llm_response = LLMResponse(theta, tau, num, den)
# passed, details, score, confidence = evaluate_llm_response(llm_response)
# print(f"Passed: {passed}, Score: {score}, Confidence: {confidence}")
# print(f"Details: {details}")
