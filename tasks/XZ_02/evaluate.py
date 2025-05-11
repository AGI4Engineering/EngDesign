import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from evaluation.llm_judge import LLMJudge


def evaluate_llm_response(llm_response):
    try:
        # Extract config data from the LLM response
        config = llm_response.config
        
        # Initialize scoring variables
        score = 0
        details = {
            "path_representation": {
                "path_completeness": 0,  # 20 points
                "regular_sampling": 0    # 15 points
            },
            "constraint_validation": {
                "obstacle_clearance": 0,  # 25 points
                "turning_radius": 0       # 25 points
            },
            "performance_metrics": {
                "computation_time": 0,    # 5 points
                "nodes_explored": 0       # 10 points
            }
        }
        
        # Path completeness (20 points)
        if config.path and len(config.path) > 0:
            # Check start pose
            start_pose = config.path[0]
            if abs(start_pose[0] - 0) < 0.1 and abs(start_pose[1] - 0) < 0.1 and abs(start_pose[2] - np.pi) < 0.1:
                details["path_representation"]["path_completeness"] += 5
            
            # Check end pose
            end_pose = config.path[-1]
            if abs(end_pose[0] - 49) < 0.1 and abs(end_pose[1] - 39) < 0.1 and abs(end_pose[2] - np.pi/2) < 0.1:
                details["path_representation"]["path_completeness"] += 5
            
            # Check path format (x,y,θ) tuples
            valid_format = True
            for pose in config.path:
                if len(pose) != 3:
                    valid_format = False
                    break
            
            if valid_format:
                details["path_representation"]["path_completeness"] += 10
        
        # Regular sampling intervals (15 points)
        if config.path and len(config.path) > 1:
            # Check if distances between consecutive points are consistent
            distances = []
            for i in range(1, len(config.path)):
                dx = config.path[i][0] - config.path[i-1][0]
                dy = config.path[i][1] - config.path[i-1][1]
                distance = np.sqrt(dx**2 + dy**2)
                distances.append(distance)
            
            if len(distances) > 0:
                avg_distance = sum(distances) / len(distances)
                consistent_sampling = True
                
                for d in distances:
                    # Allow some tolerance in sampling consistency (±20%)
                    if abs(d - avg_distance) > 0.2 * avg_distance and avg_distance > 0.1:
                        consistent_sampling = False
                        break
                
                if consistent_sampling:
                    details["path_representation"]["regular_sampling"] += 15
        
        # Obstacle clearance validation (25 points)
        if config.min_obstacle_distance is not None:
            if config.min_obstacle_distance >= 0.5:
                details["constraint_validation"]["obstacle_clearance"] += 25
            elif config.min_obstacle_distance > 0:
                # Partial points if some clearance but not enough
                details["constraint_validation"]["obstacle_clearance"] += 10
        
        # Turning radius constraint validation (25 points)
        if config.max_curvature is not None:
            # Curvature = 1/radius, so max curvature of 0.25 corresponds to min turning radius of 4m
            if config.max_curvature <= 0.25:
                details["constraint_validation"]["turning_radius"] += 25
            elif config.max_curvature <= 0.3:
                # Partial points if close to the constraint
                details["constraint_validation"]["turning_radius"] += 10
        
        # Computation time reporting (5 points)
        if config.computation_time is not None:
            details["performance_metrics"]["computation_time"] += 5
        
        # Number of nodes/states explored reporting (10 points)
        if config.nodes_explored is not None:
            details["performance_metrics"]["nodes_explored"] += 10
        
        # Calculate total score
        for category in details:
            for metric in details[category]:
                score += details[category][metric]
        
        # Determine if passed (typically >85%)
        passed = score >= 85
        
        return passed, details, score, 100  # 100 confidence for code-based evaluation
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        return False, {"error": str(e)}, 0, 0