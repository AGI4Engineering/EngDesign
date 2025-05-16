import matlab.engine
import os
def evaluate_llm_response(llm_response):
     """
     1) Launch MATLAB, run evaluate_controller.m to compute:
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
          # 1) Start MATLAB engine and add current folder
          eng = matlab.engine.start_matlab()
          # Get the directory where this evaluate.py file is located
          current_dir = os.path.dirname(os.path.abspath(__file__))
          eng.addpath(current_dir)
          # If the MATLAB function is in a different directory, add that too
          # For example, if it's in a 'matlab' subdirectory:
          matlab_dir = os.path.join(current_dir, 'matlab')
          if os.path.exists(matlab_dir):
              eng.addpath(matlab_dir)

          theta = matlab.double(llm_response.config.theta)

          passed, details, score = eng.evaluate_robot(theta, nargout=3)

          eng.quit()



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
