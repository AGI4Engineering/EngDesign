import matplotlib.pyplot as plt
import numpy as np

class Car:
    def __init__(self, acceleration=1.0, max_velocity=10.0):
        self.position = np.array([0.0, 0.0])
        self.velocity = np.array([0.0, 0.0])
        self.acceleration = acceleration
        self.max_velocity = max_velocity

    def update(self, target, dt):
        direction = target - self.position
        distance = np.linalg.norm(direction)
        if distance < 1e-2:
            return
        direction /= distance
        self.velocity += self.acceleration * direction * dt

        speed = np.linalg.norm(self.velocity)
        if speed > self.max_velocity:
            self.velocity = (self.velocity / speed) * self.max_velocity

        self.position += self.velocity * dt

def generate_track(num_points=300):
    x = np.linspace(0, 50, num_points)
    y = 5 * np.sin(x / 5)
    return np.stack([x, y], axis=1)

def find_lookahead_point(track, position, lookahead_dist, start_index):
    for i in range(start_index, len(track)):
        if np.linalg.norm(track[i] - position) > lookahead_dist:
            return track[i], i
    return track[-1], len(track) - 1

def find_nearest_point(track, position, start_index):
    distances = np.linalg.norm(track[start_index:] - position, axis=1)
    min_idx = np.argmin(distances)
    return distances[min_idx]

def run_simulation(refresh_rate=30, acceleration=2.0, max_velocity=5.0, lookahead_dist=2.0):
    dict = {
    "total_cost": None,
    "total_time": None,
    "off_track_error": None
    }
    cost = refresh_rate* 5 + acceleration * 10  + max_velocity * 8 + lookahead_dist
    dict["cost"] = cost
    if cost > 300:
        print("Design too expensive, you are fired!")
        return False, dict
    print("Budget cost:", cost)
    dt = 1.0 / refresh_rate
    track = generate_track()
    car = Car(acceleration=acceleration, max_velocity=max_velocity)

    fig, ax = plt.subplots()
    track_line, = ax.plot(track[:, 0], track[:, 1], 'g--', label="Track")
    car_dot, = ax.plot([], [], 'ro', label="Car")
    target_dot, = ax.plot([], [], 'bx', label="Target")
    ax.set_xlim(-5, 55)
    ax.set_ylim(-10, 10)
    ax.legend()

    history_x, history_y = [], []
    track_index = 0
    step_count = 0
    total_error = []
    max_off_dist = 0
    while True:
        sim_time = step_count * dt
       
            
        target, next_index = find_lookahead_point(track, car.position, lookahead_dist, track_index)
        car.update(target, dt)


        history_x.append(car.position[0])
        history_y.append(car.position[1])
        step_count += 1
    

        current_error = find_nearest_point(track, car.position, 0)
        total_error.append( current_error)
        
        if(current_error > max_off_dist):
            max_off_dist = current_error
        
        dict["off_track_error"] = max_off_dist
        if(sim_time > 10):
            print("fails as overtimed")
            return False, dict
            
        if(current_error > 1):
            print("fails as drift too much")
            return False , dict
            
        car_dot.set_data([car.position[0]], [car.position[1]])
        target_dot.set_data([target[0]], [target[1]])
        track_index = max(track_index, next_index)
        track_line.set_data(track[track_index:, 0], track[track_index:, 1])
        plt.pause(dt)

        if np.linalg.norm(car.position - track[-1]) < 0.5:
            break


    sim_time = step_count * dt
    print(f"Simulation complete")
    print(f"Total simulated time: {sim_time:.2f} seconds")
    error_cum = sum(total_error) /step_count
    print(f"Average accumulated off-track error: {error_cum:.2f} units")
    
    dict["total_time"] = sim_time
    ax.plot(history_x, history_y, 'r:', label="Trajectory")
    ax.legend()
    plt.show()
    plt.close()
    return True, dict


#if __name__ == "__main__":
##    run_simulation(refresh_rate=15, acceleration=17, max_velocity=6.5, lookahead_dist=3.0)
run_simulation(refresh_rate=10, acceleration=18, max_velocity=7, lookahead_dist=3.0)
#
# run_simulation(refresh_rate=30, acceleration=5, max_velocity=6, lookahead_dist=10)
