import os
import numpy as np


def parse_solution_txt(filepath="solution.txt"):
    bottom_left = None
    bottom_right = None
    top_right = None
    top_left = None
    task2_length = None
    task3_length = None

    with open(os.path.join(os.path.dirname(__file__), filepath), "r") as f:
        lines = f.readlines()

    mode = None
    corners = []

    for line in lines:
        line = line.strip()
        if line.startswith("## Task 1"):
            mode = "task1"
        elif line.startswith("## Task 2"):
            mode = "task2"
        elif line.startswith("## Task 3"):
            mode = "task3"
        elif line and not line.startswith("#"):
            if mode == "task1":
                try:
                    line = line.strip("()")
                    x, y = map(float, line.split(","))
                    corners.append((x, y))
                except:
                    pass
            elif mode == "task2":
                try:
                    task2_length = float(line)
                except:
                    pass
            elif mode == "task3":
                try:
                    task3_length = float(line)
                except:
                    pass

    if len(corners) == 4:
        bottom_left, bottom_right, top_right, top_left = corners

    return bottom_left, bottom_right, top_right, top_left, task2_length, task3_length

def evaluate_llm_response(llm_response):
    try:
        # Ground truth
        bl_ref, br_ref, tr_ref, tl_ref, task2_ref, task3_ref = parse_solution_txt()

        # LLM predicted output
        config = llm_response.config
        bl_pred = config.Bottom_left
        br_pred = config.Bottom_right
        tr_pred = config.Top_right
        tl_pred = config.Top_left
        task2_pred = config.task2_length
        tol2 = config.tol2
        task3_pred = config.task3_length
        tol3 = config.tol3

        detailed_info = ""
        total_score = 0

        # Determine if two points are almost identical
        def point_equal(p, q, tol=1e-3):
            if p is None or q is None:
                return False
            return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol

        # Determine if the path length is within tolerance
        def length_within_tolerance(pred, ref, tol):
            if pred is None or ref is None:
                return False
            return abs(pred - ref) <= tol

        # Task 1
        if point_equal(bl_pred, bl_ref):
            total_score += 5
            detailed_info += "The coordinates of the vertex in the bottom-left corner of the costmap is correct.\n"
        else:
            detailed_info += "The coordinates of the vertex in the bottom-left corner of the costmap is wrong.\n"
        
        if point_equal(br_pred, br_ref):
            total_score += 5
            detailed_info += "The coordinates of the vertex in the bottom-right corner of the costmap is correct.\n"
        else:
            detailed_info += "The coordinates of the vertex in the bottom-right corner of the costmap is wrong.\n"
        
        if point_equal(tr_pred, tr_ref):
            total_score += 5
            detailed_info += "The coordinates of the vertex in the top-right corner of the costmap is correct.\n"
        else:
            detailed_info += "The coordinates of the vertex in the top-right corner of the costmap is wrong.\n"
        
        if point_equal(tl_pred, tl_ref):
            total_score += 5
            detailed_info += "The coordinates of the vertex in the top-left corner of the costmap is correct.\n"
        else:
            detailed_info += "The coordinates of the vertex in the top-left corner of the costmap is wrong.\n"

        # Task 2
        if length_within_tolerance(task2_pred, task2_ref, tol2):
            total_score += 40
            detailed_info += "The total path length for Task 2 is correct.\n"
        else:
            detailed_info += "The total path length for Task 2 is wrong.\n"

        # Task 3
        if length_within_tolerance(task3_pred, task3_ref, tol3):
            total_score += 40
            detailed_info += "The total path length for Task 3 is correct.\n"
        else:
            detailed_info += "The total path length for Task 3 is wrong.\n"

        passed = total_score == 100

        details = {
            "detailed information": detailed_info,
            "total_score": total_score
        }

        return passed, details, total_score, 100

    except Exception as e:
        return False, {"error": str(e)}, None, None
