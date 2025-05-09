import numpy as np
import math
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def evaluate_llm_response(llm_response):
    try:
        cfg = llm_response.config
        cluster_kb = cfg.cluster_kb
        T = cfg.small_threshold_kb
        reported_frag = cfg.frag_overhead
        reported_meta = cfg.meta_overhead

        details = {}
        score = 0

        # Check whether cluster_kb is power of 2
        is_p2_cluster = (cluster_kb & (cluster_kb - 1) == 0) and cluster_kb > 0
        details['cluster_power_of_2'] = is_p2_cluster
        if is_p2_cluster:
            score += 5

        # Check whether cluster_kb is in range
        in_range_cluster = 4 <= cluster_kb <= 1024
        details['cluster_in_range'] = in_range_cluster
        if in_range_cluster:
            score += 5

        # Check whether small_threshold_kb is power of 2
        is_p2_threshold = (T & (T - 1) == 0) and T > 0
        details['threshold_power_of_2'] = is_p2_threshold
        if is_p2_threshold:
            score += 10

        # Check whether frag_overhead is calculated correctly
        P_small = 0.8 * (1 - math.exp(-T / 4.1))
        P_big = 1 - P_small
        cluster_bytes = cluster_kb * 1024 # in bytes
        W_small = cluster_bytes - 2 * 1024
        W_large = cluster_bytes / 2
        W_avg = P_small * W_small + P_big * W_large
        frag_calc = (W_avg * 1_000_000) / (2**40)  # fraction
        frag_calc_pct = frag_calc * 100 # percentage
        # compare with reported_frag (percentage)
        frag_correct = abs(frag_calc_pct - reported_frag) < 1e-6
        details['frag_calc_correct'] = frag_correct
        if frag_correct:
            score += 20

        # 5. Check whether frag_overhead meets requirement
        frag_meets = frag_calc_pct <= 0.5
        details['frag_meets_requirement'] = frag_meets
        if frag_meets:
            score += 20

        # CHeck whether meta_overhead is calculated correctly
        cluster_number = (2**40) / cluster_bytes
        meta_calc_pct = cluster_number * 4 / (2**40)  # percentage
        meta_correct = abs(meta_calc_pct - reported_meta) < 1e-6
        details['meta_calc_correct'] = meta_correct
        if meta_correct:
            score += 20

        # 7. meta_overhead meets requirement (≤ 0.05%)
        meta_meets = meta_calc_pct <= 0.05
        details['meta_meets_requirement'] = meta_meets
        if meta_meets:
            score += 20

        passed = is_p2_cluster and in_range_cluster and is_p2_threshold and (frag_correct and frag_meets) and (meta_correct and meta_meets)
        confidence = 100
        return passed, details, score, confidence
 
    except Exception as e:
        return False, {"error": str(e)}, None, None