import json
import os
import pandas as pd

if __name__ == "__main__":
    # Load the data from the JSON file
    with open('ground_truth.json', 'r') as f:
        simulator_results = json.load(f)

    # the structure of the best answer is 
    # { "target_workload" : { "parameter" :  } }
    best_answer = {}

    for workload in simulator_results:
        # for each parameter, if there is a possible value, put it into best_answer[workload]
        # the format is [parameter_name, parameter_value, direction]
        best_answer[workload] = {}
        for name in simulator_results[workload]:
            for value, direction, success in simulator_results[workload][name]:
                if success:
                    if name not in best_answer[workload]:
                        best_answer[workload][name] = []
                    best_answer[workload][name].append([value, direction])
        print(f"Number of valid values for {workload}: {len(best_answer[workload])}")
                
