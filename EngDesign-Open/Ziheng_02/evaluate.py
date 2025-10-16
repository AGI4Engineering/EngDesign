from oct2py import Oct2Py
import os
def evaluate_llm_response(llm_response):
     """
     1) Launch Octave, run evaluate_robot.m to compute:
          poles, tr, GM, PM
     2) Pull those variables back into Python
     3) Apply the rubric:
          - Stability (50 pts): all poles have neg. real parts
          - Rise time   (30 pts): tr < 0.2 s
          - Gain margin (10 pts): GM > 3 dB
          - Phase margin(10 pts): PM > 30°
     Returns:
          passed    (bool),
          details   (dict of raw values and pass/fail flags),
          score     (int),
          confidence (int, always 100)
     """
     try:
          # 1) Start Octave engine and add current folder
          oc = Oct2Py()
          # Get the directory where this evaluate.py file is located
          current_dir = os.path.dirname(os.path.abspath(__file__))
          oc.addpath(current_dir)

          theta = llm_response.config.theta

          passed, details, score = oc.evaluate_robot(theta, nout=3)

          oc.exit()



          # 9) Return the 4‐tuple
          return passed, details, score, 100
     except Exception as e:
          return False, {"error": str(e)}, None, None
# if __name__ == "__main__":
#     ok, det, sc, conf = evaluate_llm_response()
#     print(f"Passed: {ok}")
#     print(f"Score:  {sc}/100   Confidence: {conf}")
#     print("Details:")
#     for k, v in det.items():
#         print(f"  {k}: {v}")
