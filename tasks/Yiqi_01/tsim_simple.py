import os
import numpy as np
from typing import List, Tuple
from tsim_components.comp import Compute
from tsim_components.noc import Topo, NoC
import t10_TensorExpression

VALID_SPA_SCORE = 20
VALID_TEM_SCORE = 20
CURVE = 0.5

################################ TSim starts here ################################

def get_score(F_op:List[int], 
              f_t_A_m:int, f_t_A_k:int, f_t_B_k:int, f_t_B_n:int, f_t_C_m:int, f_t_C_n:int,
              t10_time=-1) -> Tuple[float, float, float]:
    
    temp_factors = [[f_t_C_m,f_t_A_m,1],
                    [1,f_t_A_k,f_t_B_k],
                    [f_t_C_n,1,f_t_B_n]]
    score = 0

    noc = NoC(3, Topo.MESH)
    mm_size = np.array([16, 16, 16])
    comp = Compute(16, mm_size, 16, mm_size, 16, 2*mm_size[-1]**2, 2*mm_size[-1], 2)

    texpr = t10_TensorExpression.TensorExpression(op_type=t10_TensorExpression.TensorExpression.OP_TYPE_MATMUL,
                                                  dim_lengths=[128, 5120, 15360],
                                                  variables=[[[0],[2]], [[0],[1]], [[1],[2]]], 
                                                  num_cores=[1472],
                                                  name="matmul",
                                                  max_byte_per_core=625*1024,
                                                  comp=comp,
                                                  noc=noc)
    
    if t10_time == -1:
        texpr.search_optimal_config(num_threads=os.cpu_count())
        config, (mem, t10_time, comp_cycles, shift_cycles) = texpr.get_fastest_config_by_max_mem_size(624*1024)
    print("T10 time: ", t10_time)

    t10_TensorExpression.CORE_UTIL_THRESHOLD = 0.01
    t10_TensorExpression.DATA_PAD_THRESHOLD = 0.01
    if texpr.update_spatial_dim_parts_if_valid(F_op)==False:
        print("Invalid spatial dim parts")
        return score, t10_time, -1
    else:
        score += VALID_SPA_SCORE
    if len(texpr.valid_temporal_dim_var_parts(temp_factors, F_op))==0:
        print("Invalid temporal dim parts")
        return score, t10_time, -1
    else:
        score += VALID_TEM_SCORE

    perf:t10_TensorExpression.perf = texpr.evaluate_config((F_op, temp_factors))[1]
    ai_time = perf.total_cycles
    print("AI time: ", ai_time)

    tot_perf_score = 100 - VALID_SPA_SCORE - VALID_TEM_SCORE
    t10_ai_ratio = t10_time/ai_time
    perf_score = tot_perf_score * t10_ai_ratio**CURVE
    score += perf_score
    return score, t10_time, ai_time

if __name__=="__main__":
    F_op:List[int] = [8, 32, 5]
    f_t_A_m:int = 1
    f_t_A_k:int = 1
    f_t_B_k:int = 8
    f_t_B_n:int = 1
    f_t_C_m:int = 1
    f_t_C_n:int = 32
    F_op:List[int] = [8, 16, 8]
    f_t_A_m:int = 1
    f_t_A_k:int = 4
    f_t_B_k:int = 4
    f_t_B_n:int = 1
    f_t_C_m:int = 1
    f_t_C_n:int = 1
    F_op:List[int] = [8, 1, 120]
    f_t_A_m:int = 1
    f_t_A_k:int = 2
    f_t_B_k:int = 1
    f_t_B_n:int = 8
    f_t_C_m:int = 1
    f_t_C_n:int = 8
    F_op:List[int] = [8, 20, 6]
    f_t_A_m:int = 1
    f_t_A_k:int = 2
    f_t_B_k:int = 2
    f_t_B_n:int = 4
    f_t_C_m:int = 1
    f_t_C_n:int = 20

    # score = get_score(F_op, f_t_A_m, f_t_A_k, f_t_B_k, f_t_B_n, f_t_C_m, f_t_C_n)
    score, t10_time, ai_time = get_score(F_op, f_t_A_m, f_t_A_k, f_t_B_k, f_t_B_n, f_t_C_m, f_t_C_n, t10_time=28672)
    print("Score: ", score)
    