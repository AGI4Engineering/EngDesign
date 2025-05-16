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
            "path_validity": 0,
            "path_optimality": 0,
            "algorithm_implementation": 0,
            "path_format": 0
        }
        
        # Path validity (50 points)
        if config.task1_path and len(config.task1_path) > 0:
            # Check start point (10 points)
            if config.task1_path[0] == [0, 0, 0]:
                details["path_validity"] += 10
            
            # Check end point (10 points)
            if config.task1_path[-1] == [49, 39, 0]:
                details["path_validity"] += 10
            
            # Check for obstacle collisions (30 points)
            obstacles = [
                # Vertical wall
                *[(10, y, 1) for y in range(5, 36)],
                # Horizontal wall
                *[(x, 20, 1) for x in range(10, 41)],
                # Vertical wall
                *[(30, y, 1) for y in range(0, 16)],
                # Cluster of obstacles
                *[(x, y, 1) for x in range(20, 26) for y in range(25, 31)],
                # Random obstacles
                (15, 10, 1), (25, 5, 1), (35, 25, 1), (40, 30, 1), (45, 15, 1)
            ]
            
            collision_free = True
            for node in config.task1_path:
                if (node[0], node[1], 1) in obstacles:
                    collision_free = False
                    break
            
            if collision_free:
                details["path_validity"] += 30
        
        # Path optimality (30 points)
        if config.task1_path_length:
            optimal_length = 100  # approximate optimal length
            ratio = config.task1_path_length / optimal_length
            
            if ratio <= 1.05:
                details["path_optimality"] = 30
            elif ratio <= 1.1:
                details["path_optimality"] = 10
            elif ratio <= 1.2:
                details["path_optimality"] = 5
            # else: 0 points (path length >20% longer than optimal)
        
        # Algorithm implementation (10 points)
        if config.task1_algorithm:
            details["algorithm_implementation"] += 3
        
        if config.task1_nodes_explored is not None:
            details["algorithm_implementation"] += 3
        
        if config.task1_connectivity:
            details["algorithm_implementation"] += 2
        
        if config.task1_execution_time is not None:
            details["algorithm_implementation"] += 2
        
        # Path format (10 points)
        if config.task1_path and len(config.task1_path) > 1:
            # Complete ordered list of coordinates (5 points)
            details["path_format"] += 5
            
            # Check if all coordinates are valid integers (5 points)
            valid_integers = True
            for node in config.task1_path:
                if not all(isinstance(coord, int) for coord in node):
                    valid_integers = False
                    break
            
            if valid_integers:
                details["path_format"] += 5
        
        # Calculate total score
        score = sum(details.values())
        
        # Determine if passed
        passed = score >= 75
        
        return passed, details, score, 100  # 100 confidence for code-based evaluation
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        return False, {"error": str(e)}, 0, 0