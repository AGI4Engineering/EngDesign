import numpy as np

import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:
        r = llm_response.config.gear_ratio  # gear ratio
        d = llm_response.config.wheel_diameter  # wheel diameter in meters
        C = llm_response.config.battery_capacity  # battery capacity in Wh
        m = llm_response.config.body_mass  # robot mass in kg

        # Constants
        g = 9.81  # m/s^2
        motor_voltage = 24  # V
        torque_max = 0.3  # Nm
        rpm_max = 4000  # rpm
        eff = 0.8  # motor efficiency
        roll_res_coeff = 0.015
        v_required = 3.0  # m/s
        incline_deg = 10
        cruise_speed = 2.5  # m/s
        cruise_time_min = 30  # min

        # Convert wheel radius and motor rpm to linear speed
        wheel_radius = d / 2
        motor_rad_per_sec = (rpm_max * 2 * math.pi) / 60
        wheel_rad_per_sec = motor_rad_per_sec / r
        v_max = wheel_rad_per_sec * wheel_radius

        # Compute torque at wheel
        T_wheel = torque_max * r * eff

        # Climbing force needed (simplified)
        theta = math.radians(incline_deg)
        F_gravity = m * g * math.sin(theta)
        F_rolling = m * g * math.cos(theta) * roll_res_coeff
        F_total = F_gravity + F_rolling
        T_required = F_total * wheel_radius

        # Power for level cruise
        F_rolling_cruise = m * g * roll_res_coeff
        P_total =  F_rolling_cruise * cruise_speed / eff  # watts
        E_required = P_total * cruise_time_min * 60 / 3600  # Wh

        # Evaluation
        if v_max >= v_required:
            v_max_ok = 1
        else:
            v_max_ok = 0
        if T_wheel >= T_required:
            torque_ok = 1
        else:
            torque_ok = 0
        if C >= E_required:
            battery_ok = 1
        else:
            battery_ok = 0
        score = v_max_ok*30+battery_ok*30+torque_ok*40
        passed = score == 100

        details = {
            "v_max_mps": v_max,
            "T_wheel_Nm": T_wheel,
            "T_required_Nm": T_required,
            "C_required_Wh": E_required,
            "C_given":C,
            "passed": passed
        }


        print(details)
        print(score)
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
