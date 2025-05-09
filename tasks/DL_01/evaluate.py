import numpy as np
import os
import json

# from tasks.DL_01.simulation_results.baseline_configuration import configuration_base
# from tasks.DL_01.simulation_results.xdb_operations import load_xdb, decode_configuration

ground_truth_file = "/Users/xingang/Desktop/Engineering-Design-Benchmark/tasks/DL_01/simulation_results/ground_truth.json"

workload_name_mapper = {
    "Big Data Analytics": "MapReduce",
    "Cloud Storage": "CloudStorage",
    "Database": "TPCC",
    "Key-Value Store": "YCSB",
    "Advertisement": "AdspayLoad",
    "WebSearch": "WebSearch",
    "Maps" : "LiveMapsBackEnd"
}

selected_workload = ["MapReduce", "CloudStorage", "TPCC", "YCSB", "AdspayLoad", "WebSearch", "LiveMapsBackEnd"]

def evaluate_llm_response(llm_response):
    try:
        # while True:
        # first convert the LLM Response into a json dictionary
        ground_truth = json.load(open(ground_truth_file, "r"))
        # the response structure: {
        #     Workload_Name : { Conf_Name : Value },
        # ... }
        score = 0
        tuning_result = {}
        # construct the result dictionary
        for i, workload_name in enumerate(llm_response.config.workload_names):
            # print(f"Workload Name: {workload_name}")
            # print(f"Workload Result: {llm_response.config.workloads[i]}")
            tuning_result[workload_name] = {}
            for j, name in enumerate(llm_response.config.workloads[i].parameter_names):
                # print(f"Name: {name}")
                # print(f"Value: {llm_response.config.workloads[i].values[j]}")
                ans = -1
                if llm_response.config.workloads[i].values[j] != "impossible":
                    # check if the value is a float
                    try:
                        ans = float(llm_response.config.workloads[i].values[j])
                    except ValueError:
                        print(f"Value {llm_response.config.workloads[i].values[j]} is not a float")
                        ans = -1
                else:
                    ans = "impossible"
                if ans == -1:
                    ans = "impossible"
                tuning_result[workload_name][name] = {"Tuning Result": ans}
        for workload in tuning_result.keys():
            # print("Workload: ", workload)
            # print("Tuning Result: ", tuning_result[workload])
            assert workload in workload_name_mapper, f"Workload {workload} not found in workload name mapper"
            workload_translated = workload_name_mapper[workload]
            assert workload_translated in ground_truth, f"Workload {workload} not found in ground truth"

            if workload_translated not in selected_workload:
                continue

            details = {}
            
            for name in tuning_result[workload]:
                # print(f"Name: {name}")
                # print(f"Tuning Result: {tuning_result[workload][name]}")
                tresult = tuning_result[workload][name]["Tuning Result"]
                name = "_".join(name.split(" "))
                if name not in ground_truth[workload_translated]:
                    # print(f"Name {name} not found in ground truth for workload {workload_translated}")
                    continue
                gt = ground_truth[workload_translated][name]
                possible_set = []
                for val, dir, success in gt:
                    if success:
                        possible_set.append([val, dir])
                if len(possible_set) == 0:
                    if tresult == "impossible":
                        score += 10
                    # print(f"Impossible tuning result for {name} in workload {workload_translated}")
                    continue
                if tresult == "impossible":
                    # print(f"Tuning result impossible for {name} in workload {workload_translated}")
                    continue
                # check if the result is in the possible set
                gotit = False
                count = 0
                # sort possibkle set by the first element
                possible_set = sorted(possible_set, key=lambda x: x[0])
                for val, dir in possible_set:
                    if dir and float(tresult) > val:
                        gotit = True
                        break
                    elif not dir and float(tresult) < val:
                        gotit = True
                        break
                    elif float(tresult) == val:
                        gotit = True
                        break
                    elif count == 0 and dir and float(tresult) < val:
                        # this is an approximation
                        gotit = True
                        break
                    elif count == 0 and not dir and float(tresult) > val:
                        # this is an approximation
                        gotit = True
                        break

                details[name] = {"Tuning Result": tresult, "Direction": dir, "Value": val, "passed": gotit}
                if gotit: 
                    score += 20
                # else:
                    # print(f"Not Got it for {name} in workload {workload_translated}")
        # score = score / len(tuning_result)
        score = score / len(selected_workload)
        passed = score == 100
        return passed, details, score, 100
        
                
    except Exception as e:
        return False, {"error": str(e)}, None, None
    # try:
    #     # Start MATLAB engine
    #     eng = matlab.engine.start_matlab()
    #     # Add the path containing evaluate_controller.m
    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     eng.addpath(current_dir)
        
    #     # Get controller coefficients from LLM response
    #     num = matlab.double(llm_response.config.num)
    #     den = matlab.double(llm_response.config.den)
    #     alpha = float(llm_response.config.alpha)
        
    #     # Run MATLAB evaluation
    #     passed, details, score = eng.disk_margin_eval(num, den, alpha, nargout=3)

    #     details = {key: details[key] for key in details.keys()}
        
    #     eng.quit()
    #     return passed, details, score, 100 
        
    # except Exception as e:
    #     return False, {"error": str(e)}, None, None