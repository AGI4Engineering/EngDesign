from typing import List


def check_sampling_validity(samples: List[List[float]], constraint_params: List[float]) -> bool:
    """
    Checks whether each [N, F] point in the list satisfies the constraint:
      - If N is in the interval [1600, 2000], then F <= a * N + b
      - Otherwise, no constraint

    Args:
        samples: A list of lists representing sampled [N, F] points.
        constraint_params: A list [a, b] defining the constraint F_max = a * N + b

    Returns:
        True if all constrained samples are valid, False otherwise.
    """
    a, b = constraint_params
    for [N, F] in samples:
        if 1600 <= N <= 2000:
            F_max = a * N + b
            if F > F_max:
                return False
    return True

def check_lhs_validity(samples: List[List[float]], ranges: List[List[float]]) -> bool:
    """
    Generalized LHS validity checker for n-dimensional samples.

    Args:
        samples: List of lists, each inner list is a sample of d dimensions.
        ranges: List of [min, max] lists for each dimension.

    Returns:
        True if the samples follow LHS rule in all dimensions, False otherwise.
    """
    n = len(samples)
    d = len(ranges)

    if not all(len(p) == d for p in samples):
        raise ValueError("Sample dimensionality does not match range definition.")

    # For each dimension, track which bin has been occupied
    used_bins = [set() for _ in range(d)]

    for sample in samples:
        for dim in range(d):
            val = sample[dim]
            min_val, max_val = ranges[dim]

            # Determine the interval index after normalization
            bin_index = int((val - min_val) / (max_val - min_val) * n)
            bin_index = min(bin_index, n - 1)  # Prevent bin_index = n

            # If two sampling points fall in the same interval
            if bin_index in used_bins[dim]:
                return False
            used_bins[dim].add(bin_index)

    return True

def evaluate_llm_response(llm_response):
    try:
        total_score = 0
        detailed_info = ""

        # LLM predicted output
        config = llm_response.config
        constraint_parameters = config.constraint_parameters
        global_design_points = config.global_design_points
        normalized_speed_factor = config.normalized_speed_factor
        P_range = config.P_range
        G_range = config.G_range
        local_design_points = config.local_design_points

        # Check Task 1
        if constraint_parameters == [-0.0625, 300]:
            total_score += 5
            detailed_info += "Global input constraints in Task 1 are calculated correctly.\n"
            # Check Task 2 -- only when the constraints are calculated correctly can the correct sampling point be outputted
            if len(global_design_points) != 15:
                detailed_info += "The number of sampling points of the global inputs obtained in Task 2 is not 15.\n"
            else:
                if check_sampling_validity(global_design_points, [-0.0625, 300]):
                    total_score += 20
                    detailed_info += "Sampling of global inputs gained from Task 2 satisfies constraints.\n"
                else:
                    detailed_info += "Sampling of global inputs gained from Task 2 doesn't satisfy constraints.\n"
        else:
            detailed_info += "Global input constraints in Task 1 are not calculated correctly.\n"

        # Check Task 2
        if len(global_design_points) == 15:
            if check_lhs_validity(global_design_points, [[1600, 2200], [20, 200]]):
                total_score += 25
                detailed_info += "The sampling points of the global inputs gained from Task 2 satisfy the LHS sampling principle (LHS divides each variable's range into N intervals and ensures each sample uses a unique interval per dimension for uniform coverage).\n"
            else:
                detailed_info += "The sampling points of the global inputs gained from Task 2 don't satisfy the LHS sampling principle (LHS divides each variable's range into N intervals and ensures each sample uses a unique interval per dimension for uniform coverage).\n"

        # Check Task 3
        local = 0
        if normalized_speed_factor == 0.5:
            total_score += 5
            local += 1
            detailed_info += "normalized_speed_factor in Task 3 are calculated correctly.\n"
        else:
            detailed_info += "normalized_speed_factor in Task 3 are not calculated correctly.\n"

        if P_range == [100, 140]:
            total_score += 5
            local += 1
            detailed_info += "P_range in Task 3 are calculated correctly.\n"
        else:
            detailed_info += "P_range in Task 3 are not calculated correctly.\n"

        if G_range == [0.4, 0.65]:
            total_score += 5
            local += 1
            detailed_info += "G_range in Task 3 are calculated correctly.\n"
        else:
            detailed_info += "G_range in Task 3 are not calculated correctly.\n"

        # Check Task 4 -- only when Task 3 is completely correct can the correct sampling point be outputted
        if local == 3:
            if len(local_design_points) != 30:
                detailed_info += "The number of sampling points of the local inputs obtained in Task 4 is not 30.\n"
            else:
                if check_lhs_validity(local_design_points, [[-9, 3], [100, 140], [0.4, 0.65], [0.5, 5]]):
                    total_score += 35
                    detailed_info += "The sampling points of the local inputs gained from Task 4 satisfy the LHS sampling principle (LHS divides each variable's range into N intervals and ensures each sample uses a unique interval per dimension for uniform coverage)."
                else:
                    detailed_info += "The sampling points of the local inputs gained from Task 4 don't satisfy the LHS sampling principle (LHS divides each variable's range into N intervals and ensures each sample uses a unique interval per dimension for uniform coverage)."

        passed = total_score == 100

        details = {
            "detailed information": detailed_info,
            "total_score": total_score
        }

        return passed, details, total_score, 100

    except Exception as e:
        return False, {"error": str(e)}, None, None
