# evaluate.py
import subprocess
from output_structure import Response_structure
import os

def evaluate_llm_response(llm_response):
    """
    Called by test_eval.py. Expects an instance of Response_structure.
    Returns: (passed: bool, details: dict, score: int, confidence: int)
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    code_path = os.path.join(current_dir, "code.sv")
    tb_path = os.path.join(current_dir, "tb.sv")
    vvp_path = os.path.join(current_dir, "user_tb.vvp")

    # 1) Dump the DUT into code.sv
    with open(code_path, "w") as f:
        f.write(llm_response.code)

    # 2) Compile with Icarus Verilog
    compile_cmd = [
        "iverilog", "-g2012",
        "-o", vvp_path,
        vvp_path,  # generated DUT
        tb_path     # golden testbench
    ]
    cmp = subprocess.run(compile_cmd, capture_output=True, text=True)
    if cmp.returncode != 0:
        return False, {"compile_error": cmp.stderr.strip()}, 0, 0

    # 3) Simulate
    sim = subprocess.run(["vvp", vvp_path], capture_output=True, text=True)
    output = sim.stdout + sim.stderr

    # 4) Parse up to three sub-tests
    failed = set()
    for line in output.splitlines():
        if "[FAIL] Test 0" in line: failed.add(0)
        if "[FAIL] Test 1" in line: failed.add(1)
        if "[FAIL] Test 2" in line: failed.add(2)

    t0 = (0 not in failed)
    t1 = (1 not in failed)
    t2 = (2 not in failed)
    passed = t0 and t1 and t2

    # 5) Score per rubrics
    score = 30 * t0 + 35 * t1 + 35 * t2
    confidence = 100

    details = {
        "test0_pass": t0,
        "test1_pass": t1,
        "test2_pass": t2
    }
    return passed, details, score, confidence