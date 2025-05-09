import numpy as np

import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def evaluate_llm_response(llm_response):
    try:
        angle = llm_response.config.angle  # glide angle in degrees
        volume = llm_response.config.volume  # vehicle volume in m^3
        mass = llm_response.config.mass  # vehicle mass in kg

        # Constants
        rho_water = 1025  # kg/m^3
        g = 9.81  # m/s^2
        depth = 400  # meters
        P0 = 100  # W
        l = 0.05  # W/kg
        k = 0.2  # W/m
        C_max = 200  # Wh
        V_max = 1.0  # m^3
        V_min = 0.2  # m^3
        v_glide = 1.0  # m/s
        total_mission_time = 2 * 3600  # s

        # Convert angle to radians
        theta_rad = math.radians(angle)

        # 1. Horizontal range
        horizontal_distance = 2 * depth / math.tan(theta_rad)
        time_to_complete = depth / math.sin(theta_rad) / v_glide

        def power_at_depth(z):
            return P0 + l * mass + k * z

        # Integrate power over depth (numerical trapezoidal integration)
        z_samples = 1000
        dt = time_to_complete / z_samples
        total_energy = 0
        for i in range(z_samples):
            z = i * dt * v_glide * math.sin(theta_rad)
            total_energy += power_at_depth(z) * dt
        total_energy_Wh = total_energy * 2 / 3600  # Convert J to Wh

        # Evaluation constraints
        constraints = {
            "range_ok": horizontal_distance >= 4000,
            "time_ok": time_to_complete <= total_mission_time / 2,
            "energy_ok": total_energy_Wh <= C_max,
            "volume_ok": volume <= V_max and volume >= V_min,
            "density_ok": mass / volume <= rho_water and mass >= 200
        }

        score = sum(constraints.values()) * 20
        passed = score == 100

        details = {
            "horizontal_distance_m": horizontal_distance,
            "time_seconds": time_to_complete * 2,
            "energy_required_Wh": total_energy_Wh,
            "volume_m3": volume,
            "density_kg_per_m3": mass / volume,
            "passed": passed
        }

        print(details)
        print(score)
        return passed, details, score, 100

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
