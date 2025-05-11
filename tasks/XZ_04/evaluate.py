import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import subprocess
import json
from pathlib import Path
import time
import re
import math
from typing import List, Tuple, Dict, Any

def evaluate_llm_response(llm_response):
    try:
        # Extract config data from the LLM response
        config = llm_response.config
        
        # Step 1: Convert trajectory data to format usable by controller
        path_3d = []
        for point in config.trajectory:
            path_3d.append((point.time, point.x, point.y, point.z, point.velocity, point.acceleration))
        
        # Step 2: Update the robot_controller.py with the trajectory
        update_controller_with_trajectory(path_3d)
        
        # Step 3: Run the Webots simulation
        simulation_success = run_simulation()
        if not simulation_success:
            return False, {"error": "Simulation failed to run"}, 0, 0
        
        # Step 4: Evaluate the results based on rubrics
        # Initialize scoring variables
        score = 0
        details = {
            "path_validity": 0,
            "speed_constraints": 0,
            "path_within_allowed_zone": 0,
            "implementation_details": 0
        }
        
        # Path validity (40 points)
        if config.trajectory and len(config.trajectory) > 0:
            # Check start point (10 points)
            start_point = config.trajectory[0]
            if (start_point.x == 0 and start_point.y == 0 and start_point.z == 0):
                details["path_validity"] += 10
            
            # Check end point (10 points)
            end_point = config.trajectory[-1]
            if (end_point.x == 19 and end_point.y == 24 and end_point.z == 0):
                details["path_validity"] += 10
            
            # Check for obstacle collisions (20 points)
            obstacles = extract_obstacles_from_world()
            
            collision_free = True
            for point in config.trajectory:
                point_tuple = (point.x, point.y, point.z)
                
                # Check if the point position collides with any obstacle
                if is_collision(point_tuple, obstacles):
                    collision_free = False
                    break
            
            if collision_free:
                details["path_validity"] += 20
        
        # Path within allowed zone (20 points)
        if config.trajectory and len(config.trajectory) > 0:
            within_zones = True
            for point in config.trajectory:
                zone = get_zone(point.x, point.y)
                if zone == "OUTSIDE_ZONE":
                    within_zones = False
                    break
            
            if within_zones:
                details["path_within_allowed_zone"] += 20
        
        # Speed constraints (30 points)
        if config.trajectory and len(config.trajectory) > 0:
            white_zone_valid = True
            red_zone_valid = True
            green_zone_valid = True
            
            for point in config.trajectory:
                zone = get_zone(point.x, point.y)
                
                if zone == "WHITE_ZONE" and point.velocity > 1.0:
                    white_zone_valid = False
                elif zone == "RED_ZONE" and point.velocity > 2.0:
                    red_zone_valid = False
                elif zone == "GREEN_ZONE" and point.velocity > 0.5:
                    green_zone_valid = False
            
            if white_zone_valid:
                details["speed_constraints"] += 10
            if red_zone_valid:
                details["speed_constraints"] += 10
            if green_zone_valid:
                details["speed_constraints"] += 10
        
        # Implementation details (10 points)
        if config.trajectory and len(config.trajectory) > 1:
            details["implementation_details"] += 4  # Complete ordered list of coordinates
        
        if config.travel_time is not None:
            details["implementation_details"] += 3  # Travel time reported
        
        if config.path_length is not None:
            details["implementation_details"] += 3  # Path length reported
        
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

def update_controller_with_trajectory(trajectory):
    """
    Update the robot_controller.py file with the trajectory from LLM response
    """
    try:
        controller_path = os.path.join(os.getcwd(), "controllers", "robot_controller", "robot_controller.py")
        
        # Ensure the file exists
        if not os.path.exists(controller_path):
            print(f"ERROR: Controller file not found at {controller_path}")
            return False
        
        # Read the existing controller code
        with open(controller_path, 'r') as f:
            controller_code = f.read()
        
        # Format the trajectory as a string for insertion
        trajectory_str = str(trajectory)
        
        # Look for the pattern where we need to insert the trajectory
        pattern = r'trajectory\s*=\s*\[\].*?#\s*Trajectory data'
        pattern2 = r'trajectory\s*=\s*\[.*?\].*?#\s*Trajectory data'
        
        if re.search(pattern, controller_code):
            # Replace the empty trajectory with our data
            new_controller_code = re.sub(
                pattern, 
                f'trajectory = {trajectory_str}  # Trajectory data', 
                controller_code
            )
        elif re.search(pattern2, controller_code):
            # Replace existing trajectory with our data
            new_controller_code = re.sub(
                pattern2, 
                f'trajectory = {trajectory_str}  # Trajectory data', 
                controller_code
            )
        else:
            # If the specific pattern isn't found, try to find any trajectory variable
            pattern_general = r'trajectory\s*=\s*\[.*?\]'
            if re.search(pattern_general, controller_code):
                new_controller_code = re.sub(
                    pattern_general,
                    f'trajectory = {trajectory_str}',
                    controller_code
                )
            else:
                print("ERROR: Could not find trajectory variable in controller file")
                return False
        
        # Write the updated code back to the file
        with open(controller_path, 'w') as f:
            f.write(new_controller_code)
        
        print(f"Updated trajectory in robot_controller.py")
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

def get_zone(x: float, y: float) -> str:
    """
    Determine which zone a point is in based on its coordinates
    
    WHITE_ZONE: x in [-5, 5], y in [0, 15]
    RED_ZONE: x in [-5, 5], y in [15, 30]
    GREEN_ZONE: x in [5, 20], y in [20, 30]
    """
    # WHITE_ZONE: centered at (0.11, 7.12) with size 10x15
    if -4.89 <= x <= 5.11 and -0.38 <= y <= 14.62:
        return "WHITE_ZONE"
    
    # RED_ZONE: centered at (0.11, 22.11) with size 10x15
    if -4.89 <= x <= 5.11 and 14.61 <= y <= 29.61:
        return "RED_ZONE"
    
    # GREEN_ZONE: centered at (12.63, 24.61) with rotated dimensions
    if 5.13 <= x <= 20.13 and 19.61 <= y <= 29.61:
        return "GREEN_ZONE"
    
    return "OUTSIDE_ZONE"

def extract_obstacles_from_world():
    """
    Extract obstacle positions from the world file
    """
    obstacles = []
    
    # Parse obstacle positions from world info
    obstacle_positions = [
        (-0.41, 4.78, 0.5),  # OBSTACLE_2
        (1.58, 11.04, 0.5),  # OBSTACLE_3
        (3.24, 21.69, 0.5),  # OBSTACLE_1
        (-1.76, 18.4, 0.5),  # OBSTACLE_4
        (13.45, 24.52, 0.5)  # OBSTACLE_5
    ]
    
    obstacle_size = (1, 1, 1)  # All obstacles are 1x1x1 boxes
    
    for pos in obstacle_positions:
        for x_offset in np.linspace(-obstacle_size[0]/2, obstacle_size[0]/2, 5):
            for y_offset in np.linspace(-obstacle_size[1]/2, obstacle_size[1]/2, 5):
                x = pos[0] + x_offset
                y = pos[1] + y_offset
                obstacles.append((x, y, 0))
    
    return obstacles

def is_collision(point, obstacles):
    """
    Check if a point collides with any obstacle
    Consider the robot radius of 0.5m and obstacle edges
    """
    robot_radius = 0.5
    
    for obstacle in obstacles:
        # Calculate distance from point to obstacle
        distance = math.sqrt((point[0] - obstacle[0])**2 + 
                            (point[1] - obstacle[1])**2)
        
        # If distance is less than robot radius, it's a collision
        if distance < robot_radius:
            return True
    
    return False