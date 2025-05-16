import math
from typing import List, Tuple
from pydantic import BaseModel
from output_structure import Response_structure

# Define the three cases and their limits
CASES = {
    "case1": {
        "threads": [(0,5),(2,3),(4,8),(6,6),(8,4)],
        "limit": 17.0
    },
    "case2": {
        "threads": [(0,10),(1,2),(3,7),(5,5)],
        "limit": 17.0
    },
    "case3": {
        "threads": [(0,2),(2,2),(4,2),(6,2),(8,2),(10,2)],
        "limit": 8.0
    }
}

# Helper function to simulate Round-Robin scheduling, therefore average waiting time
# and number of context switches.
def simulate_rr(threads: List[Tuple[int,int]], quantum: int) -> Tuple[float,int]:
    """
    Simulate Round-Robin scheduling on `threads` with the given `quantum`.
    Returns (avg_waiting_time, context_switches), where waiting is computed as
    finish_time - arrival_time - burst_time.
    """
    n = len(threads)
    arrival = [t[0] for t in threads]
    burst   = [t[1] for t in threads]
    remaining = burst.copy()
    time = 0
    queue: List[int] = []
    context_switches = 0
    prev = None
    completed = 0
    finish = [0]*n

    while completed < n:
        # enqueue any arrived, unfinished threads
        for i in range(n):
            if arrival[i] <= time and remaining[i] > 0 and i not in queue:
                queue.append(i)
        if not queue:
            time += 1
            continue

        idx = queue.pop(0)
        if prev is not None and prev != idx:
            context_switches += 1
        prev = idx

        run = min(quantum, remaining[idx])
        time += run
        remaining[idx] -= run

        # enqueue newly arrived threads
        for i in range(n):
            if arrival[i] <= time and remaining[i] > 0 and i not in queue and i != idx:
                queue.append(i)

        if remaining[idx] > 0:
            queue.append(idx)
        else:
            finish[idx] = time
            completed += 1

    # compute waiting times
    waits = [finish[i] - arrival[i] - burst[i] for i in range(n)]
    avg_wait = sum(waits) / n
    return avg_wait, context_switches

def evaluate_llm_response(llm_response: Response_structure):
    try:
        score = 0
        details = {}
        passed = True

        # Check time_quantum is integer
        tq = llm_response.config.time_quantum
        if isinstance(tq, int):
            score += 10
            details['time_quantum_is_integer'] = True
        else:
            details['time_quantum_is_integer'] = False
            passed = False

        # Evaluate each case
        for case_name, info in CASES.items():
            threads = info['threads']
            limit = info['limit']
            avg_true, cs_true = simulate_rr(threads, tq)
            qc_true = tq * 0.5
            # combined_cost = avg_waiting_time + context_switches + quantum_cost
            combined = avg_true + cs_true + qc_true

            # Extract reported values
            rep = getattr(llm_response.config, case_name)
            avg_rep = rep.avg_waiting_time
            cs_rep  = rep.context_switches
            qc_rep  = rep.quantum_cost

            # whether avg_waiting_time is computed correctly
            if math.isclose(avg_true, avg_rep, rel_tol=1e-3, abs_tol=1e-3):
                score += 5
                details[f"{case_name}_avg_waiting_time_correct"] = True
            else:
                details[f"{case_name}_avg_waiting_time_correct"] = False
                passed = False

            # whether context_switches is computed correctly
            if cs_true == cs_rep:
                score += 5
                details[f"{case_name}_context_switches_correct"] = True
            else:
                details[f"{case_name}_context_switches_correct"] = False
                passed = False

            # whether quantum_cost is computed correctly
            if math.isclose(qc_true, qc_rep, rel_tol=1e-3, abs_tol=1e-3):
                score += 5
                details[f"{case_name}_quantum_cost_correct"] = True
            else:
                details[f"{case_name}_quantum_cost_correct"] = False
                passed = False

            # whether combined_cost is within limit
            if combined <= limit + 1e-3:
                score += 15
                details[f"{case_name}_combined_cost_is_within_limit"] = True
            else:
                details[f"{case_name}_combined_cost_is_within_limit"] = False
                passed = False

        return passed, details, score, 100

    except Exception as e:
        return False, {"error": str(e)}, None, None