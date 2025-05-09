import sys
from controller import Supervisor
import json

# Get the robot instance
supervisor = Supervisor()

# Get the time step
time_step = int(supervisor.getBasicTimeStep())

# Get the robot node
robot_node = supervisor.getSelf()
translation_field = robot_node.getField("translation")

# Get root node for adding visualization elements
root_node = supervisor.getRoot()
children_field = root_node.getField("children")

# Path from llm_reponse (replace with actual response from LLM)
path_3d = [(0, 0, 0), (1, 1, 0), (2, 2, 0), (3, 3, 0), (4, 4, 0), (5, 5, 0), (6, 6, 0), (7, 7, 0), (8, 8, 0), (9, 9, 0), (10, 10, 0), (11, 11, 0), (12, 12, 0), (13, 13, 0), (14, 14, 0), (15, 15, 0), (16, 16, 0), (17, 17, 0), (18, 18, 0), (19, 19, 0), (20, 20, 0), (21, 21, 0), (22, 22, 0), (23, 23, 0), (24, 24, 0), (25, 25, 0), (26, 26, 0), (27, 27, 0), (28, 28, 0), (29, 29, 0), (30, 30, 0), (31, 31, 0), (32, 32, 0), (33, 33, 0), (34, 34, 0), (35, 35, 0), (36, 36, 0), (37, 37, 0), (38, 38, 0), (39, 39, 0), (40, 40, 0), (41, 41, 0), (42, 42, 0), (43, 43, 0), (44, 44, 0), (45, 45, 0), (46, 46, 0), (47, 47, 0), (48, 48, 0), (49, 39, 0)]  # Path from LLM response

# Visualize the planned path
for i, point in enumerate(path_3d):
    # Create a small sphere to mark the path
    # Swap X and Y coordinates to match the world file coordinates
    sphere_string = f'''
    DEF PATH_MARKER_{i} Solid {{
      translation {point[0]} {point[1]} 0.5
      children [
        Shape {{
          appearance PBRAppearance {{
            baseColor 0 0.8 0
            roughness 0.2
            metalness 0
          }}
          geometry Sphere {{
            radius 0.2
            subdivision 2
          }}
        }}
      ]
    }}
    '''
    children_field.importMFNodeFromString(-1, sphere_string)
    
    # Step simulation occasionally to avoid overloading
    if i % 10 == 0:
        supervisor.step(10)

# Move robot along the path
for waypoint in path_3d:
    # Correctly assign X and Y from the path waypoint
    target_x, target_y = waypoint[0], waypoint[1]
    
    # Get current position
    current_pos = translation_field.getSFVec3f()
    
    # Calculate direction vector
    dx = target_x - current_pos[0]
    dy = target_y - current_pos[1]
    distance = (dx**2 + dy**2)**0.5
    
    # Normalize direction vector
    if distance > 0:
        dx /= distance
        dy /= distance
    
    # Move until reaching the waypoint
    while distance > 0.5:  # Distance threshold
        # Calculate new position with limited speed
        step_distance = min(0.5, distance)  # Move speed
        new_x = current_pos[0] + dx * step_distance
        new_y = current_pos[1] + dy * step_distance
        
        # Update position
        translation_field.setSFVec3f([new_x, new_y, current_pos[2]])
        
        # Step simulation
        if supervisor.step(time_step) == -1:
            break
        
        # Update current position and distance
        current_pos = translation_field.getSFVec3f()
        dx = target_x - current_pos[0]
        dy = target_y - current_pos[1]
        distance = (dx**2 + dy**2)**0.5

# Run for a few more steps to display the final result
for _ in range(50):
    if supervisor.step(time_step) == -1:
        break

# Terminate the simulation
supervisor.simulationQuit(0)