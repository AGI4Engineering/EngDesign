import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from evaluation.llm_judge import LLMJudge

import subprocess
import json
from pathlib import Path
import time
import re

def evaluate_llm_response(llm_response):
    try:
        # Extract config data from the LLM response
        config = llm_response.config
        
        # Step 1: Update the robot_controller.py with the path from LLM response
        update_controller_with_path(config.task_path)
        
        # Step 2: Run the Webots simulation
        simulation_success = run_simulation()
        if not simulation_success:
            return False, {"error": "Simulation failed to run"}, 0, 0
        
        # Step 3: Evaluate the results based on rubrics
        # Initialize scoring variables
        score = 0
        details = {
            "path_validity": 0,
            "path_optimality": 0,
            "algorithm_implementation": 0,
            "path_format": 0
        }
        
        # Path validity (50 points)
        if config.task_path and len(config.task_path) > 0:
            # Check start point (10 points)
            start_point = config.task_path[0]
            if len(start_point) == 2:  # Handle 2D points
                start_point = (start_point[0], start_point[1], 0)
            if tuple(start_point) == (0, 0, 0):
                details["path_validity"] += 10
            
            # Check end point (10 points)
            end_point = config.task_path[-1]
            if len(end_point) == 2:  # Handle 2D points
                end_point = (end_point[0], end_point[1], 0)
            if tuple(end_point) == (49, 39, 0):
                details["path_validity"] += 10
            
            # Check for obstacle collisions (30 points)
            # Extract obstacle positions from the world file
            obstacles = extract_obstacles_from_world()
            
            collision_free = True
            for node in config.task_path:
                # Convert 2D node to 3D if needed
                if len(node) == 2:
                    node_tuple = (node[0], node[1], 0)
                else:
                    # Convert node to tuple for comparison if it's not already
                    node_tuple = tuple(node) if not isinstance(node, tuple) else node
                
                # Check if the node position collides with any obstacle
                if is_collision(node_tuple, obstacles):
                    collision_free = False
                    break
            
            if collision_free:
                details["path_validity"] += 30
        
        # Path optimality (30 points)
        if config.task_path_length:
            # Reference optimal length from solution.txt is 106.75
            optimal_length = 106.75
            ratio = config.task_path_length / optimal_length
            
            if ratio <= 1.05:
                details["path_optimality"] = 30
            elif ratio <= 1.1:
                details["path_optimality"] = 10
            elif ratio <= 1.2:
                details["path_optimality"] = 5
            # else: 0 points (path length >20% longer than optimal)
        
        # Algorithm implementation (10 points)
        if config.task_algorithm:
            details["algorithm_implementation"] += 3
        
        if config.task_nodes_explored is not None:
            details["algorithm_implementation"] += 3
        
        if config.task_connectivity:
            details["algorithm_implementation"] += 2
        
        # Execution time is not explicitly required in the LLM_prompt.txt or output_structure.py,
        # but we can add 2 points as in the original evaluate.py if it's reported somewhere in reasoning
        if hasattr(config, 'execution_time') or (hasattr(llm_response, 'reasoning') and 
                                             re.search(r'execution time|runtime|\btime\b', llm_response.reasoning, re.IGNORECASE)):
            details["algorithm_implementation"] += 2
        
        # Path format (10 points)
        if config.task_path and len(config.task_path) > 1:
            # Complete ordered list of coordinates (5 points)
            details["path_format"] += 5
            
            # Check if all coordinates are valid integers (5 points)
            valid_integers = True
            for node in config.task_path:
                # Check each coordinate in the node
                for coord in node:
                    if not isinstance(coord, int):
                        valid_integers = False
                        break
                if not valid_integers:
                    break
            
            if valid_integers:
                details["path_format"] += 5
        
        # Calculate total score
        score = sum(details.values())
        
        # Determine if passed
        passed = score >= 80
        
        confidence = 100  # 100 confidence for code-based evaluation
        
        return passed, details, score, confidence
        
    except Exception as e:
        import traceback
        print(f"Error during evaluation: {str(e)}")
        print(traceback.format_exc())
        return False, {"error": str(e)}, None, None

def update_controller_with_path(path_3d):
    """
    Update the robot_controller.py file with the path from LLM response
    """
    try:
        controller_path = os.path.join(os.getcwd(), "controllers", "robot_controller", "robot_controller.py")
        
        with open(controller_path, 'r') as f:
            controller_code = f.read()
        
        # Convert 2D points to 3D points if needed
        processed_path = []
        for point in path_3d:
            if len(point) == 2:
                processed_path.append((point[0], point[1], 0))
            else:
                processed_path.append(tuple(point))
        
        # Replace the path in the controller code using a more flexible pattern
        path_str = str(processed_path)
        
        # More flexible regex pattern that allows for whitespace variations
        pattern = r'path_3d\s*=\s*\[\].*?#.*?Path from LLM response'
        replacement = f'path_3d = {path_str}  # Path from LLM response'
        
        new_controller_code = re.sub(pattern, replacement, controller_code)
        
        # Verify the replacement worked
        if new_controller_code == controller_code:
            print("WARNING: Path replacement didn't change the file - pattern may not have matched.")
            # Fallback: try to find path_3d assignment more generally
            pattern = r'path_3d\s*=\s*\[.*?\]'
            new_controller_code = re.sub(pattern, f'path_3d = {path_str}', controller_code)
            
            # Check if the fallback worked
            if new_controller_code == controller_code:
                print("ERROR: Unable to update path in controller file.")
                return False
        
        with open(controller_path, 'w') as f:
            f.write(new_controller_code)
        
        print(f"Updated robot_controller.py with path from LLM response")
        print(f"Path: {path_str[:100]}{'...' if len(path_str) > 100 else ''}")
        return True
        
    except Exception as e:
        import traceback
        print(f"Error updating controller: {str(e)}")
        print(traceback.format_exc())
        return False

def run_simulation():
    """
    Run the Webots simulation
    """
    try:
        # Path to Webots executable
        webots_path = "/usr/local/webots/webots"
        world_path = os.path.join(os.getcwd(), "worlds", "construction_site.wbt")
        
        # Command to run Webots in batch mode
        cmd = [webots_path, "--batch", "--mode=fast", world_path]
        
        print(f"Running simulation with command: {' '.join(cmd)}")
        
        # Run the simulation and wait for it to complete
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Simulation failed with return code {process.returncode}")
            print(f"STDOUT: {stdout.decode('utf-8')}")
            print(f"STDERR: {stderr.decode('utf-8')}")
            return False
        
        print("Simulation completed successfully")
        return True
    
    except Exception as e:
        print(f"Error running simulation: {str(e)}")
        return False

def extract_obstacles_from_world():
    """
    Extract obstacle positions from the world file as described in LLM_prompt.txt
    """
    obstacles = []
    
    # Parse obstacle positions from LLM_prompt.txt
    
    # Vertical wall from (10,5) to (10,35)
    for y in range(5, 36):
        obstacles.append((10, y, 0))
    
    # Horizontal wall from (10,20) to (40,20)
    for x in range(10, 41):
        obstacles.append((x, 20, 0))
    
    # Vertical wall from (30,0) to (30,15)
    for y in range(0, 16):
        obstacles.append((30, y, 0))
    
    # Obstacle cluster from (20,25) to (25,30)
    for x in range(20, 26):
        for y in range(25, 31):
            obstacles.append((x, y, 0))
    
    # Random obstacles
    random_obstacles = [
        (15, 10, 0),  # OBSTACLE_1
        (25, 5, 0),   # OBSTACLE_2
        (35, 25, 0),  # OBSTACLE_3
        (40, 30, 0),  # OBSTACLE_4
        (45, 15, 0)   # OBSTACLE_5
    ]
    obstacles.extend(random_obstacles)
    
    return obstacles

def is_collision(point, obstacles):
    """
    Check if a point collides with any obstacle
    """
    # Make sure point has 3 coordinates
    if len(point) < 3:
        # If point has only 2 coordinates, assume z=0
        point_3d = (point[0], point[1], 0)
    else:
        point_3d = point
    
    # Consider the point as a collision if it's directly on an obstacle
    return point_3d in obstacles