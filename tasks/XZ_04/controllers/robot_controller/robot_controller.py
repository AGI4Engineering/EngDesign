from controller import Robot, Supervisor
import numpy as np
import math

class RobotController:
    def __init__(self):
        # Create the Robot instance
        self.robot = Supervisor()
        
        # Get the time step of the current world
        self.timestep = int(self.robot.getBasicTimeStep())
        
        # Get robot node to control its position
        self.robot_node = self.robot.getSelf()
        self.translation_field = self.robot_node.getField("translation")
        
        # Trajectory will be set by the evaluation script
        # Format: (time, x, y, z, velocity, acceleration)
        self.trajectory = [(0.0, 0.0, 0.0, 0.0, 0.0, 0.5), (0.5, 0.125, 0.125, 0.0, 0.25, 0.5), (1.0, 0.5, 0.5, 0.0, 0.5, 0.5), (1.5, 1.0, 1.0, 0.0, 0.75, 0.5), (2.0, 1.625, 1.625, 0.0, 1.0, 0.0), (3.0, 2.625, 2.625, 0.0, 1.0, 0.0), (4.0, 3.625, 3.625, 0.0, 1.0, 0.0), (5.0, 4.625, 4.625, 0.0, 1.0, 0.0), (6.0, 4.5, 5.625, 0.0, 1.0, 0.0), (7.0, 3.5, 6.625, 0.0, 1.0, 0.0), (8.0, 2.5, 7.625, 0.0, 1.0, 0.0), (9.0, 1.5, 8.625, 0.0, 1.0, 0.0), (10.0, 0.5, 9.625, 0.0, 1.0, 0.0), (11.0, 0.5, 10.625, 0.0, 1.0, 0.0), (12.0, 1.0, 11.625, 0.0, 1.0, 0.0), (13.0, 2.0, 12.625, 0.0, 1.0, 0.0), (14.0, 3.0, 13.625, 0.0, 1.0, 0.0), (15.0, 4.0, 14.625, 0.0, 1.0, 0.5), (15.5, 4.625, 15.25, 0.0, 1.25, 0.5), (16.0, 5.375, 16.0, 0.0, 1.5, 0.5), (16.5, 6.25, 16.875, 0.0, 1.75, 0.5), (17.0, 7.25, 17.875, 0.0, 2.0, 0.0), (17.5, 8.25, 18.875, 0.0, 2.0, 0.0), (18.0, 9.25, 19.875, 0.0, 2.0, 0.0), (18.5, 10.25, 20.875, 0.0, 2.0, 0.0), (19.0, 11.25, 21.875, 0.0, 2.0, -0.5), (19.5, 12.125, 22.75, 0.0, 1.75, -0.5), (20.0, 12.875, 23.5, 0.0, 1.5, -0.5), (20.5, 13.5, 24.125, 0.0, 1.25, -0.5), (21.0, 14.0, 24.25, 0.0, 1.0, -0.5), (21.5, 14.375, 24.25, 0.0, 0.75, -0.5), (22.0, 14.625, 24.25, 0.0, 0.5, 0.0), (23.0, 15.125, 24.25, 0.0, 0.5, 0.0), (24.0, 15.625, 24.25, 0.0, 0.5, 0.0), (25.0, 16.125, 24.25, 0.0, 0.5, 0.0), (26.0, 16.625, 24.25, 0.0, 0.5, 0.0), (27.0, 17.125, 24.25, 0.0, 0.5, 0.0), (28.0, 17.625, 24.25, 0.0, 0.5, 0.0), (29.0, 18.125, 24.25, 0.0, 0.5, 0.0), (30.0, 18.625, 24.125, 0.0, 0.5, -0.5), (30.5, 18.825, 24.0, 0.0, 0.25, -0.5), (31.0, 19.0, 24.0, 0.0, 0.0, 0.0)]  # Path from LLM response
        
        # Metrics
        self.path_length = 0.0
        self.travel_time = 0.0
        self.nodes_explored = 0
        
        # Zone validation
        self.zone_violations = []
    
    def calculate_path_length(self):
        """Calculate the total path length"""
        path_length = 0.0
        for i in range(1, len(self.trajectory)):
            p1 = (self.trajectory[i-1][1], self.trajectory[i-1][2], self.trajectory[i-1][3])
            p2 = (self.trajectory[i][1], self.trajectory[i][2], self.trajectory[i][3])
            segment_length = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
            path_length += segment_length
        return path_length
    
    def validate_zone_constraints(self):
        """Validate that the entire trajectory stays within allowed zones"""
        violations = []
        for i, point in enumerate(self.trajectory):
            x, y = point[1], point[2]
            zone = self.get_zone(x, y)
            if zone == "OUTSIDE_ZONE":
                violations.append((i, x, y))
        return violations
    
    def get_zone(self, x, y):
        """Determine which zone a point is in based on its coordinates"""
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
    
    def run(self):
        # First validate the trajectory for zone constraints
        self.zone_violations = self.validate_zone_constraints()
        if self.zone_violations:
            print("WARNING: Trajectory contains points outside allowed zones:")
            for i, (idx, x, y) in enumerate(self.zone_violations[:5]):
                print(f"  Point {idx}: ({x:.2f}, {y:.2f}) - OUTSIDE_ZONE")
            if len(self.zone_violations) > 5:
                print(f"  ...and {len(self.zone_violations) - 5} more violations")
        
        # Current trajectory point index
        current_index = 0
        
        # Simulation time
        sim_time = 0.0
        
        # Main control loop
        while self.robot.step(self.timestep) != -1:
            # Convert milliseconds to seconds
            dt = self.timestep / 1000.0
            sim_time += dt
            
            # Find current trajectory point based on simulation time
            while current_index < len(self.trajectory) - 1 and sim_time >= self.trajectory[current_index + 1][0]:
                current_index += 1
            
            if current_index >= len(self.trajectory) - 1:
                # Reached the end of trajectory
                # Set the robot to the final position
                final_pos = [self.trajectory[-1][1], self.trajectory[-1][2], self.trajectory[-1][3]]
                self.translation_field.setSFVec3f(final_pos)
                
                # Record metrics
                self.travel_time = sim_time
                self.path_length = self.calculate_path_length()
                self.nodes_explored = len(self.trajectory)
                
                # Print results
                print(f"Mission complete!")
                print(f"Final position: {final_pos}")
                print(f"Total travel time: {self.travel_time:.2f} seconds")
                print(f"Total path length: {self.path_length:.2f} meters")
                print(f"Trajectory points: {self.nodes_explored}")
                print(f"Zone violations: {len(self.zone_violations)}")
                
                # Exit simulation
                self.robot.simulationQuit(0)
                break
            
            # Interpolate between current and next trajectory point
            current_point = self.trajectory[current_index]
            next_point = self.trajectory[current_index + 1]
            
            # Linear interpolation factor
            if next_point[0] == current_point[0]:  # Avoid division by zero
                t = 0
            else:
                t = (sim_time - current_point[0]) / (next_point[0] - current_point[0])
            
            # Interpolate position
            x = current_point[1] + t * (next_point[1] - current_point[1])
            y = current_point[2] + t * (next_point[2] - current_point[2])
            z = current_point[3] + t * (next_point[3] - current_point[3])
            
            # Set robot position
            self.translation_field.setSFVec3f([x, y, z])
            
            # Get current velocity and zone
            current_velocity = current_point[4] + t * (next_point[4] - current_point[4])
            zone = self.get_zone(x, y)
                
            # Print status every second
            if int(sim_time) > int(sim_time - dt):
                print(f"Time: {sim_time:.2f}s | Pos: ({x:.2f}, {y:.2f}, {z:.2f}) | Velocity: {current_velocity:.2f}m/s | Zone: {zone}")
                
                # Check speed constraints
                if zone == "WHITE_ZONE" and current_velocity > 1.0:
                    print(f"  WARNING: Exceeding WHITE_ZONE speed limit ({current_velocity:.2f} > 1.0 m/s)")
                elif zone == "RED_ZONE" and current_velocity > 2.0:
                    print(f"  WARNING: Exceeding RED_ZONE speed limit ({current_velocity:.2f} > 2.0 m/s)")
                elif zone == "GREEN_ZONE" and current_velocity > 0.5:
                    print(f"  WARNING: Exceeding GREEN_ZONE speed limit ({current_velocity:.2f} > 0.5 m/s)")
                elif zone == "OUTSIDE_ZONE":
                    print(f"  ERROR: Robot is outside allowed zones")

# Main function
def main():
    controller = RobotController()
    controller.run()

# Call the main function
if __name__ == "__main__":
    main()