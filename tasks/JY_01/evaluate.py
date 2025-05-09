import numpy as np 
import os 
import sys 
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
 
def M_lp(theta):
    theta_rad = np.radians(2 * theta)  
    return 0.5 * np.array([
        [1, np.cos(theta_rad), np.sin(theta_rad), 0],
        [np.cos(theta_rad), np.cos(theta_rad)**2, np.cos(theta_rad)*np.sin(theta_rad), 0],
        [np.sin(theta_rad), np.cos(theta_rad)*np.sin(theta_rad), np.sin(theta_rad)**2, 0],
        [0, 0, 0, 0]
    ])
def M_qwp(phi):
    phi_rad = np.radians(2 * phi)  
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(phi_rad), np.sin(phi_rad), 0],
        [0, -np.sin(phi_rad), np.cos(phi_rad), 0],
        [0, 0, 0, -1]
    ])
def calculate_final_stokes(S_in, angle12, angle22, angle32):
    
    M1 = M_lp(angle12)   
    M2 = M_qwp(angle22)  
    M3 = M_lp(angle32)   
    
   
    M_total = M3 @ M2 @ M1
    
   
    S_out = M_total @ S_in
    return S_out
def evaluate_llm_response(llm_response): 
   try: 
       # Start MATLAB engine 
       confidence = 100 
    #    eng = matlab.engine.start_matlab() 
       # Add the path containing evaluate_controller.m 
       current_dir = os.path.dirname(os.path.abspath(__file__)) 
    #    eng.addpath(current_dir) 
       # Get controller coefficients from LLM response 
    
       S_in = np.array([1.0, 0.6, 0.2, 0.0])
       S_gt = np.array([-0.3,0.3,0,0])
       angle12 = llm_response.config.angle12
       angle22 = llm_response.config.angle22
       angle32 = llm_response.config.angle32
       S_out= calculate_final_stokes( S_in, angle12, angle22, angle32) 
       
       diffs = np.abs(S_out - S_gt)
       within_tolerance = diffs <= 0.05
       score = int(np.sum(within_tolerance) * 20)
       if( score==80 ):
           score+=20 
       passed = score >= 75
       details = {
        f"S{i}": {
            "predicted": float(S_out[i]),
            "ground_truth": float(S_gt[i]),
            "diff": float(diffs[i]),
            "within_tolerance": bool(within_tolerance[i])
        }
        for i in range(4)
       }
       return passed, details, score, confidence 
       
   except Exception as e: 
       return False, {"error": str(e)}, None, None