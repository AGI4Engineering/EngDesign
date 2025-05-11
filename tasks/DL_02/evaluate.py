import numpy as np
import os
import json

# from tasks.DL_01.simulation_results.baseline_configuration import configuration_base
# from tasks.DL_01.simulation_results.xdb_operations import load_xdb, decode_configuration

ground_truth_file = "simulation_results/ground_truth_layout.json"

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
        details = {}
        # construct the result dictionary
        for i, workload_name in enumerate(llm_response.config.workload_names):
            # print(f"Workload Name: {workload_name}")
            # print(f"Workload Result: {llm_response.config.workloads[i]}")
            result = {}
            result["Overprovisioning_Ratio"] = llm_response.config.workloads[i].res.over_provisioning
            result["Flash_Channel_Count"] = llm_response.config.workloads[i].res.num_channels
            result["Chip_No_Per_Channel"] = llm_response.config.workloads[i].res.num_chips
            result["Die_No_Per_Chip"] = llm_response.config.workloads[i].res.num_dies
            result["Plane_No_Per_Die"] = llm_response.config.workloads[i].res.num_planes
            result["Block_No_Per_Plane"] = llm_response.config.workloads[i].res.num_blocks
            result["Page_No_Per_Block"] = llm_response.config.workloads[i].res.num_pages
            result["Page_Capacity"] = 4096
            tuning_result[workload_name] = result
        for workload in tuning_result.keys():
            # print("Workload: ", workload)
            # print("Tuning Result: ", tuning_result[workload])
            assert workload in workload_name_mapper, f"Workload {workload} not found in workload name mapper"
            workload_translated = workload_name_mapper[workload]
            assert workload_translated in ground_truth, f"Workload {workload} not found in ground truth"
            if workload_translated not in selected_workload:
                continue
            
            found_match = False
            success_res = False
            for conf, success in ground_truth[workload_translated]:
                if conf == tuning_result[workload]:
                    found_match = True
                    success_res = success
                    break
                # else:
                    # print(f"Not Got it for {name} in workload {workload_translated}")
            multi = 1
            for key in tuning_result[workload].keys():
                if key == "Overprovisioning_Ratio":
                    continue
                multi *= tuning_result[workload][key]
            if multi >= 0.85 * 2196875771904 and multi <= 1.05 * 2196875771904:
                found_match = True
            details[workload] = {"Tuning Result": tuning_result[workload], "Success": success_res}
            if found_match:
                if success_res:
                    score += 100
                else:
                    score += 10
        # score = score / len(tuning_result)
        score = score / len(selected_workload)
        print(f"Score: {score}")
        passed = score == 100
        return passed, {"score": score}, score, 100
        
                
    except Exception as e:
        return False, {"error": str(e)}, None, None
