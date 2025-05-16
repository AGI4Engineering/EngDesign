#!/usr/bin/env python3
"""
evaluate.py — ECE 483 Mini‑Project **MP3** auto‑grader

Changes from the previous MP4 script
------------------------------------
1. **All file paths and default `mp_number` set to "mp3".**
2. **Scoring rubric updated** (see rubrics.txt): five design specs × 20 pts.
   * DC Gain ≥ 40 dB
   * Unity‑Gain Frequency ≥ 50 MHz
   * CMRR ≥ 80 dB
   * ICMR ≥ 0.8 V
   * Proper netlist naming & pin order
3. **Persistent logging** — every evaluation writes a JSON log containing
   the LLM response and the full evaluation result to
   `./evaluation_logs/eval_YYYYMMDD_HHMMSS.json`.

The script still implements the required callable `evaluate_llm_response()`
returning `(passed, details, score, confidence)`.
"""
from __future__ import annotations
import os, re, json, subprocess
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd  # kept to satisfy template imports

###############################################################################
# Helper utilities                                                             #
###############################################################################

def run_autograder_script(script_path: str, mp_number: str) -> tuple[bool, str | None]:
    """Execute the provided shell script with *unix* line endings and proper
    permissions.  The first CLI argument is the MP number (e.g. "mp3")."""
    try:
        # normalise line endings (avoids `\r` errors)
        with open(script_path, "rb") as fh:
            data = fh.read().replace(b"\r\n", b"\n")
        with open(script_path, "wb") as fh:
            fh.write(data)
        os.chmod(script_path, 0o755)

        res = subprocess.run(
            ["bash", script_path, mp_number],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Shell error: {res.stderr.strip()}")
        return True, None
    except Exception as exc:
        return False, str(exc)


def extract_metrics_from_log(log_path: str) -> dict[str, float | None]:
    """Pull the relevant numeric results out of the Cadence log file."""
    metrics = {
        "dc_gain_db": None,
        "ugf_mhz":    None,
        "cmrr_db":    None,
        "icmr_v":     None,
    }
    label_map = {
        "dc_gain_db": "Simulated DC Gain:",
        "ugf_mhz":    "Simulated Unity Gain Frequency:",
        "cmrr_db":    "Simulated CMRR:",
        "icmr_v":     "Simulated ICMR:",
    }

    if not os.path.isfile(log_path):
        return metrics

    with open(log_path, "r", errors="ignore") as fh:
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
    return metrics


def check_netlist_pins(netlist_path: str) -> bool:
    """Ensure the student‑generated netlist uses the correct name & pin order.
    Requirement (from template):
      .subckt fc_ota VDD VSS ibn10u vin vip vout"""
    try:
        with open(netlist_path, "r", errors="ignore") as fh:
            for line in fh:
                if line.strip().startswith(("subckt", ".subckt")):
                    parts = re.split(r"\s+", line.strip())
                    # Expected format: .subckt fc_ota VDD VSS ibn10u vin vip vout
                    exp = [".subckt", "fc_ota", "VDD", "VSS", "ibn10u", "vin", "vip", "vout"]
                    return parts[:len(exp)] == exp
    except Exception:
        pass
    return False


def score_metrics(metrics: dict[str, float | None], netlist_ok: bool) -> tuple[int, dict[str,int]]:
    """Apply the MP3 rubric to the measurement data and netlist check."""
    sub_scores: dict[str, int] = {}

    # 1. DC Gain ≥ 40 dB
    sub_scores["dc_gain"] = 20 if (metrics.get("dc_gain_db") or 0) >= 40 else 0
    # 2. fUGF ≥ 50 MHz
    sub_scores["ugf"] = 20 if (metrics.get("ugf_mhz") or 0) >= 50 else 0
    # 3. CMRR ≥ 80 dB
    sub_scores["cmrr"] = 20 if (metrics.get("cmrr_db") or 0) >= 80 else 0
    # 4. ICMR ≥ 0.8 V
    sub_scores["icmr"] = 20 if (metrics.get("icmr_v") or 0) >= 0.8 else 0
    # 5. Netlist naming & pin order
    sub_scores["netlist"] = 20 if netlist_ok else 0

    total = int(sum(sub_scores.values()))
    return total, sub_scores


def save_evaluation_log(llm_response, summary: dict) -> str:
    """Persist a JSON log that captures *everything* we just did."""
    log_dir = Path(__file__).with_suffix("").parent / "evaluation_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"eval_{ts}.json"

    # Attempt to JSON‑serialize the LLM response; fall back to str().
    try:
        resp_json = json.loads(json.dumps(llm_response, default=lambda o: o.__dict__))
    except Exception:
        resp_json = str(llm_response)

    with open(log_path, "w") as fh:
        json.dump({
            "timestamp": ts,
            "llm_response": resp_json,
            "evaluation": summary
        }, fh, indent=2)
    return str(log_path)

###############################################################################
# Required entry point                                                        #
###############################################################################

def evaluate_llm_response(llm_response):
    """Primary interface called by the grader harness."""
    confidence = 100  # fixed for code‑based grading

    try:
        # 1) Save netlist ------------------------------------------------------
        save_dir = "/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_mp3/dut_netlist"
        os.makedirs(save_dir, exist_ok=True)
        netlist_path = os.path.join(save_dir, "netlist_tianles3")

        netlist = (
            getattr(getattr(llm_response, "config", {}), "netlist", None)
            or getattr(llm_response, "netlist", None)
            or (isinstance(llm_response, dict) and llm_response.get("netlist"))
        )
        if not netlist:
            raise ValueError("LLM response missing 'netlist'.")
        with open(netlist_path, "w") as fh:
            fh.write(netlist)

        # 2) Run simulation ----------------------------------------------------
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        shell_path = os.path.join(cur_dir, "run_autograder.sh")
        ok, err = run_autograder_script(shell_path, "mp3")
        if not ok:
            details = {"error": err}
            score = 0
            passed = False
        else:
            # 3) Parse Cadence log + compute score ----------------------------
            log_path = "/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_mp3/CDS_mp3.log"
            metrics = extract_metrics_from_log(log_path)
            net_ok = check_netlist_pins(netlist_path)
            score, sub_scores = score_metrics(metrics, net_ok)
            passed = score == 100
            details = {
                "metrics": metrics,
                "sub_scores": sub_scores,
                "score": score,
                "passed": passed,
            }

        # 4) Persist evaluation log -------------------------------------------
        summary = {
            "passed": passed,
            "score": score,
            "confidence": confidence,
            "details": details,
        }
        log_file_path = save_evaluation_log(llm_response, summary)

        # Console print for quick sanity check
        print(json.dumps({**summary, "log_saved": log_file_path}, indent=2))

        return passed, details, score, confidence

    except Exception as exc:
        err_summary = {
            "passed": False,
            "score": 0,
            "confidence": confidence,
            "error": str(exc),
        }
        # still log the error so the user can inspect it later
        try:
            save_evaluation_log(llm_response, err_summary)
        except Exception:
            pass  # ignore any issues in error‑path logging
        print(json.dumps(err_summary, indent=2))
        return False, {"error": str(exc)}, 0, confidence

###############################################################################
# Manual test stub                                                            #
###############################################################################
if __name__ == "__main__":
    class DummyCfg:
        netlist = "* dummy netlist\n.subckt fc_ota VDD VSS ibn10u vin vip vout"
    class DummyResp:
        config = DummyCfg()
    evaluate_llm_response(DummyResp())
