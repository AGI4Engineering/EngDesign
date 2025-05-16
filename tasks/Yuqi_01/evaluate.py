from functools import lru_cache
from math import ceil
import json
from typing import Any
from output_structure import Response_structure


llama3_1_405B_config = {
    "d_model": 16384,
    "num_heads": 128,
    "d_head": 128,
    "num_kv_heads": 8,
    "d_ff": 53248,
    "num_layers": 126,
}


@lru_cache(maxsize=None)
def get_all_stats(
    prefill_or_decode: str = "prefill",
) -> dict[str, tuple[float, float]]:
    '''
    Read the json file and return a mapping of
    str(dp, tp, pp, batch_size) -> (latency, throughput)
    for all configurations.
    '''
    assert prefill_or_decode in ["prefill", "decode"], \
        "prefill_or_decode must be either 'prefill' or 'decode'."
    filepath = f"./llama3_1-405b_5p_inference_{prefill_or_decode}.json"
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def get_llm_inference_stats(
    prefill_or_decode: str = "prefill",
    dp: int = 1,
    tp: int = 1,
    pp: int = 1,
    global_batch_size: int = 1,
) -> tuple[float, float]:
    '''
    Lookup the json files and return (latency, throughput).
    '''
    data = get_all_stats(prefill_or_decode)
    return data[str((dp, tp, pp, global_batch_size))]


def get_best_inference_stats(
    prefill_or_decode: str = "prefill",
    latency_slo: float = float("inf"),
) -> tuple[str, tuple[float, float]]:
    '''
    Lookup the json files and return the best
    (str(dp, tp, pp, batch_size), (latency, throughput)).
    '''
    data = get_all_stats(prefill_or_decode)
    # filter out everything that violates the latency SLO
    data = {
        k: v for k, v in data.items() if v[0] <= latency_slo
    }
    # pick the one with the highest throughput
    best_config = max(data.items(), key=lambda x: x[1][1])
    return best_config


def get_llm_inference_mem_requirement(
    config: dict[str, Any] = llama3_1_405B_config,
    dp: int = 1,
    tp: int = 1,
    pp: int = 1,
    global_batch_size: int = 1,
    input_seqlen: int = 4096,
    output_seqlen: int = 512,
    weight_bytes_per_element: int = 2,
    activation_bytes_per_element: int = 2,
) -> int:
    '''
    Calculate the memory requirement for serving a LLM model with DP/TP/PP.
    @config: path to the config file or the config dict.
    @weight_bytes_per_element: bytes per element for weights. Defaults to FP16.
    @activation_bytes_per_element: bytes per element for activations. Defaults to FP16.

    @return: memory requirement in bytes per chip.
    '''

    batch_size = ceil(global_batch_size / dp)

    num_heads: int = config["num_heads"]
    num_kv_heads: int = config["num_kv_heads"]
    d_head: int = config["d_head"]
    d_model: int = config["d_model"]
    d_ff: int = config["d_ff"]
    num_layers: int = config["num_layers"]

    num_heads = ceil(num_heads / tp)
    num_kv_heads = ceil(num_kv_heads / tp)
    d_ff = ceil(d_ff / tp)
    num_layers_per_chip = ceil(num_layers / pp)
    seqlen = input_seqlen + output_seqlen

    ### Attention Layer ###

    # For GQA, if TP <= # of KV heads, then the KV cache is shared.
    # Otherwise, the KV cache needs to be replicated across TP chips.
    if tp <= num_kv_heads:
        w_attn_kv = d_model * num_kv_heads * d_head * 2
    else:
        w_attn_kv = d_model * num_heads * d_head * 2
    w_attn_q = d_model * num_heads * d_head
    w_attn_qkv = w_attn_kv + w_attn_q
    w_attn_output = num_heads * d_head * d_model
    w_attn = w_attn_qkv + w_attn_output  # attention weights

    a_attn_q = batch_size * seqlen * num_heads * d_head
    if tp <= num_kv_heads:
        a_attn_kv = batch_size * seqlen * num_kv_heads * d_head * 2
    else:
        a_attn_kv = batch_size * seqlen * num_heads * d_head * 2
    a_attn_qkv = a_attn_kv + a_attn_q  # KV cache size + Q activation size
    a_attn = a_attn_qkv  # KV cache needs separate storage, Q activation can be used in place

    ### FFN Layer ###
    w_ff = 3 * d_model * d_ff
    a_ff = 2 * batch_size * seqlen * max(d_ff, d_model)

    total_weights = (w_attn + w_ff) * num_layers_per_chip
    total_act = (a_attn + a_ff) * num_layers_per_chip

    mem = total_weights * weight_bytes_per_element + total_act * activation_bytes_per_element
    return mem


def evaluate_task_1(llm_response: Response_structure) -> tuple[bool, dict, int]:
    answer = llm_response.config.max_width_SA

    passed = answer in [182, 183]
    details = {
        "max_width_solution_min": 182,
        "max_width_solution_max": 183,
        "max_width": answer,
    }
    score = 10 if passed else 0
    return passed, details, score


def evaluate_task_2(llm_response: Response_structure) -> tuple[bool, dict, int]:
    solution = 74
    answer = llm_response.config.HBM_bandwidth_GBps

    passed = solution * 0.9 <= answer <= solution * 1.1
    details = {
        "min_BW_solution_min": solution * 0.9,
        "min_BW_solution_max": solution * 1.1,
        "min_BW": answer,
    }
    score = 10 if passed else 0
    return passed, details, score


def evaluate_task_3(llm_response: Response_structure) -> tuple[bool, dict, int | float]:
    passed = True
    details = {}
    score = 80

    answer = llm_response.config

    # check if all values are even and multiples of 2
    all_answer_values = [
        answer.prefill_DP,
        answer.prefill_TP,
        answer.prefill_PP,
        answer.prefill_batch_size,
        answer.decode_DP,
        answer.decode_TP,
        answer.decode_PP,
        answer.decode_batch_size,
    ]
    all_even = all(x > 0 and (x == 1 or x % 2 == 0) for x in all_answer_values)
    if not all_even:
        details = {
            "comment": "All values must be 1 or multiples of 2.",
        }
        return False, details, 0

    # check if batch sizes are powers of 2
    all_batch_sizes = [
        answer.prefill_batch_size,
        answer.decode_batch_size,
    ]
    all_powers_of_2 = all(x > 0 and (x & (x - 1)) == 0 for x in all_batch_sizes)
    if not all_powers_of_2:
        details = {
            "comment": "Batch sizes must be powers of 2.",
        }
        return False, details, 0

    # check memory constraints for prefill
    mem_bytes_prefill = get_llm_inference_mem_requirement(
        dp=answer.prefill_DP,
        tp=answer.prefill_TP,
        pp=answer.prefill_PP,
        global_batch_size=answer.prefill_batch_size,
        input_seqlen=4096,
        output_seqlen=1,
    )
    # check memory constraints for decode
    mem_bytes_decode = get_llm_inference_mem_requirement(
        dp=answer.decode_DP,
        tp=answer.decode_TP,
        pp=answer.decode_PP,
        global_batch_size=answer.decode_batch_size,
        input_seqlen=4096,
        output_seqlen=512,
    )
    GB_95 = 95 * 1024 * 1024 * 1024
    if mem_bytes_prefill > GB_95 or mem_bytes_decode > GB_95:
        details = {
            "comment": "Memory constraints not satisfied.",
            "prefill_mem_bytes": mem_bytes_prefill,
            "decode_mem_bytes": mem_bytes_decode,
        }
        return False, details, 0

    # lookup latency and throughput performance from json files
    latency_prefill, throughput_prefill = get_llm_inference_stats(
        prefill_or_decode="prefill",
        dp=answer.prefill_DP,
        tp=answer.prefill_TP,
        pp=answer.prefill_PP,
        global_batch_size=answer.prefill_batch_size,
    )
    latency_decode, throughput_decode = get_llm_inference_stats(
        prefill_or_decode="decode",
        dp=answer.decode_DP,
        tp=answer.decode_TP,
        pp=answer.decode_PP,
        global_batch_size=answer.decode_batch_size,
    )
    latency_prefill_slo_TTFT_sec = 0.5  # 500ms
    latency_decode_slo_TPOT_ms = 20  # 20ms

    # check latency SLO violation
    if latency_prefill > latency_prefill_slo_TTFT_sec or latency_decode > latency_decode_slo_TPOT_ms:
        details = {
            "comment": "Latency SLO not satisfied.",
            "latency_prefill": latency_prefill,
            "latency_decode": latency_decode,
        }
        return False, details, 0

    # evaluate throughput
    # score = answer_throughput / ideal_throughput * 40
    best_config_prefill_str, (best_latency_prefill, best_throughput_prefill) = get_best_inference_stats(
        prefill_or_decode="prefill",
        latency_slo=latency_prefill_slo_TTFT_sec,
    )
    best_config_decode_str, (best_latency_decode, best_throughput_decode) = get_best_inference_stats(
        prefill_or_decode="decode",
        latency_slo=latency_decode_slo_TPOT_ms,
    )
    prefill_score = throughput_prefill / best_throughput_prefill * 40
    decode_score = throughput_decode / best_throughput_decode * 40
    score = prefill_score + decode_score
    details = {
        "prefill_throughput": throughput_prefill,
        "prefill_best_throughput": best_throughput_prefill,
        "prefill_best_config": best_config_prefill_str,
        "decode_throughput": throughput_decode,
        "decode_best_throughput": best_throughput_decode,
        "decode_best_config": best_config_decode_str,
        "prefill_score": prefill_score,
        "decode_score": decode_score,
    }
    passed = (score >= 80)

    return passed, details, score


def evaluate_llm_response(llm_response: Response_structure):
    # print(llm_response)
    try:
        confidence = 100

        passed_list = []
        details_list = []
        score_list = []

        for i, eval_task in enumerate([
            evaluate_task_1,
            evaluate_task_2,
            evaluate_task_3,
        ]):
            task_results = eval_task(llm_response)
            passed_list.append(task_results[0])
            details_list.append(task_results[1])
            score_list.append(task_results[2])

        passed = all(passed_list)
        details = {
            f"Task_{i+1}": details_list[i]
            for i in range(len(details_list))
        }
        score = sum(score_list)

        return passed, details, score, confidence

    except Exception as e:
        return False, {"error": str(e)}, None, None

# Check the performance of the reference solution
# num = 8
# den = [1,0]
# alpha = 0.15
# result = evaluate_llm_response(num, den, alpha)
# print(result)

