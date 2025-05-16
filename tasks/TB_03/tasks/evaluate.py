#!/usr/bin/env python3
"""
evaluate.py — ECE 483 Mini‑Project **MP3** auto‑grader

Changes from MP4 version ➜
1. **All paths use `mp3` instead of `mp4`.**
2. **Rubric updated (rubrics.txt) — 5 specs × 20 pts each:**
   * DC Gain ≥ 40 dB
   * fUGF ≥ 50 MHz
   * CMRR ≥ 80 dB
   * ICMR ≥ 0.8 V
   * Proper netlist naming & pin order
3. `run_autograder_script()` now passes the MP number ("mp3") as the first
   CLI arg to `run_autograder.sh` so the shell script selects the correct testbench.
4. Dummy harness at bottom defaults to **mp3**.
"""

from __future__ import annotations
import os, re, json, subprocess
from typing import Tuple, Dict, Any
import numpy as np, pandas as pd   # kept to satisfy template imports


# ────────────────── helper: run shell script ──────────────────

def run_autograder_script(script_path: str, mp_num: str) -> Tuple[bool, str | None]:
    """Execute *run_autograder.sh* with the MP number as first CLI argument."""
    try:
        # normalise line endings & ensure executable
        with open(script_path, "rb") as fh:
            data = fh.read().replace(b"\r\n", b"\n")
        with open(script_path, "wb") as fh:
            fh.write(data)
        os.chmod(script_path, 0o755)

        res = subprocess.run(
            ["bash", script_path, mp_num],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Shell error: {res.stderr.strip()}")
        return True, None
    except Exception as exc:
        return False, str(exc)


# ────────────────── helper: parse log & score ──────────────────

def parse_log_and_score(log_path: str, netlist_ok: bool) -> Dict[str, Any]:
    """Read *CDS_mp3.log*, extract metrics, apply MP3 rubric, return details."""
    if not os.path.isfile(log_path):
        return {"error": f"log file not found: {log_path}",
                "score": 0, "passed": False}

    # Values to capture (initialised to None)
    metrics = {k: None for k in (
        "dc_gain_db",    # AV0
        "ugf_mhz",       # fUGF
        "cmrr_db",       # CMRR
        "icmr_v",        # ICMR (V)
    )}

    label_map = {
        "dc_gain_db": "Simulated DC Gain:",
        "ugf_mhz":    "Simulated Unity Gain Frequency:",
        "cmrr_db":    "Simulated CMRR:",
        "icmr_v":     "Simulated ICMR:",
    }

    # extract first floating‑point number that follows each label
    with open(log_path, "r") as fh:
        for line in fh:
            if "Simulated" not in line:
                continue
            clean = line.lstrip("\\o").strip()
            for key, label in label_map.items():
                if clean.startswith(label):
                    m = re.search(r"([-+]?[0-9]*\.?[0-9]+)", clean[len(label):])
                    if m:
                        metrics[key] = float(m.group(1))
                    break

    if any(v is None for v in metrics.values()):
        return {"error": "one or more metrics missing",
                "metrics": metrics, "score": 0, "passed": False}

    # ───── apply MP3 rubric (20 pts per spec) ─────
    sub = {
        "dc_gain": 20 if metrics["dc_gain_db"] >= 40 else 0,
        "ugf":     20 if metrics["ugf_mhz"]   >= 50 else 0,
        "cmrr":    20 if metrics["cmrr_db"]   >= 80 else 0,
        "icmr":    20 if metrics["icmr_v"]    >= 0.8 else 0,
        "netlist": 20 if netlist_ok else 0,
    }

    total  = int(sum(sub.values()))
    passed = total == 100

    return {"metrics": metrics,
            "sub_scores": sub,
            "score": total,
            "passed": passed}


# ────────────────── helper: netlist format check ──────────────

def check_netlist_format(netlist_path: str) -> bool:
    """Return **True** if the .subckt line contains the expected pin order."""
    expected = ["fc_ota", "VDD", "VSS", "ibn10u", "vin", "vip", "vout"]
    try:
        with open(netlist_path, "r") as fh:
            for line in fh:
                if line.lower().startswith(".subckt"):
                    tokens = line.strip().split()
                    # tokens[0] is '.subckt'
                    return tokens[1:] == expected
    except Exception:
        pass
    return False


# ────────────────── required entry point ──────────────────────

def evaluate_llm_response(llm_response):
    """Entry point called by the evaluation harness."""
    try:
        confidence = 100  # fixed for code‑based grading

        # ─── 1 · Save netlist ───
        mp_num   = getattr(getattr(llm_response, "config", object()),
                           "mp_number", "mp3")
        save_dir = f"/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_{mp_num}/dut_netlist"
        os.makedirs(save_dir, exist_ok=True)
        netlist_path = os.path.join(save_dir, "netlist_tianles3")

        netlist = (
            getattr(getattr(llm_response, "config", object()), "netlist", None)
            or getattr(llm_response, "netlist", None)
            or (isinstance(llm_response, dict) and llm_response.get("netlist"))
        )
        if not netlist:
            raise ValueError("LLM response missing 'config.netlist'")

        with open(netlist_path, "w") as fh:
            fh.write(netlist)

        # validate naming & pin order early
        netlist_ok = check_netlist_format(netlist_path)

        # ─── 2 · Run Cadence + autograder ───
        cur_dir   = os.path.dirname(os.path.abspath(__file__))
        shell_path = os.path.join(cur_dir, "run_autograder.sh")
        ok, err   = run_autograder_script(shell_path, mp_num)
        if not ok:
            passed, details, score = False, {"error": err}, 0
        else:
            # ─── 3 · Parse log & compute score ───
            log_path = (
                f"/home/tianles3/cadence/simulation/"
                f"ece483_sp25_AG/tb_{mp_num}/CDS_{mp_num}.log"
            )
            details = parse_log_and_score(log_path, netlist_ok)
            passed  = bool(details.get("passed", False))
            score   = int(details.get("score", 0))

        # ---- print once for human confirmation ----
        print(json.dumps({
            "passed": passed,
            "score": score,
            "confidence": confidence,
            "details": details.get("metrics", {}) |
                        {"netlist_ok": netlist_ok}
        }))

        return passed, details, score, confidence

    except Exception as exc:
        print(json.dumps({
            "passed": False,
            "score": 0,
            "confidence": 100,
            "error": str(exc)
        }))
        return False, {"error": str(exc)}, 0, 100


# ────────────────── optional manual test ──────────────────────
if __name__ == "__main__":
    class DummyCfg:
        netlist = "* dummy"
        mp_number = "mp3"
    class DummyResp:
        config = DummyCfg()
    evaluate_llm_response(DummyResp())
