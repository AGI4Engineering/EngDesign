#!/usr/bin/env python3
"""
evaluate.py — ECE 483 Mini-Project auto-grader
(prints the four return values for quick verification)
"""

from __future__ import annotations
import os, re, json, subprocess
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd   # kept to satisfy template imports


# ────────────────── helper: run shell script ──────────────────
def run_autograder_script(script_path: str) -> tuple[bool, str | None]:
    """Normalize line endings, make the script executable, and run it."""
    try:
        with open(script_path, "rb") as fh:
            data = fh.read().replace(b"\r\n", b"\n")
        with open(script_path, "wb") as fh:
            fh.write(data)
        os.chmod(script_path, 0o755)

        res = subprocess.run(
            ["bash", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if res.returncode != 0:
            raise RuntimeError(f"Shell error: {res.stderr.strip()}")
        return True, None
    except Exception as exc:
        return False, str(exc)


# ────────────────── helper: JSON log read/write ───────────────
def _save_json_log(resp, summary) -> str:
    """
    Write `evaluation_logs/eval_YYYYMMDD_HHMMSS.json`
    containing the original LLM response plus the grading summary.
    Return the absolute file path.
    """
    folder = Path(__file__).with_suffix("").parent / "evaluation_logs"
    folder.mkdir(exist_ok=True)

    fname = folder / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Try to keep the original structure; fall back to str() if not JSON-serialisable
    try:
        resp_dump = json.loads(json.dumps(resp, default=lambda o: o.__dict__))
    except Exception:
        resp_dump = str(resp)

    with open(fname, "w") as fh:
        json.dump({"llm_response": resp_dump, **summary}, fh, indent=2)
    return str(fname)


def _load_eval_log(path: str) -> dict:
    """Return the parsed JSON log; on failure return an empty dict."""
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception:
        return {}


# ────────────────── helper: parse log & compute score ─────────
def parse_log_and_score(log_path: str) -> dict:
    """Extract metrics from the Cadence log file and compute rubric scores."""
    if not os.path.isfile(log_path):
        return {"error": f"log file not found: {log_path}",
                "score": 0, "passed": False}

    metrics = {k: None for k in
               ("dc_gain_db", "ugf_mhz", "pm_deg",
                "icmr_v", "io_err_mv", "idc_ua")}

    label_map = {
        "dc_gain_db": "Simulated DC Gain:",
        "ugf_mhz":    "Simulated Unity Gain Frequency:",
        "pm_deg":     "Simulated Phase Margin:",
        "icmr_v":     "Simulated ICMR:",
        "io_err_mv":  "Simulated Input-Output Error:",
        "idc_ua":     "Simulated DC Current Consumption:",
    }

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

    sub = {}
    sub["dc_gain"] = 35 if metrics["dc_gain_db"] >= 60 else 20 if metrics["dc_gain_db"] >= 55 else 0
    sub["ugf"]     = 15 if metrics["ugf_mhz"]   >= 50 else  5 if metrics["ugf_mhz"]   >= 40 else 0
    sub["pm"]      = 15 if metrics["pm_deg"]    >= 60 else  5 if metrics["pm_deg"]    >= 50 else 0
    icmr_mv        = metrics["icmr_v"] * 1e3
    sub["icmr"]    = 15 if icmr_mv             >= 600 else  5 if icmr_mv             >= 500 else 0
    sub["io_err"]  = 10 if metrics["io_err_mv"] <= 0.6 else 5 if metrics["io_err_mv"] <= 1.8 else 0
    sub["idc"]     = 10 if metrics["idc_ua"]    <= 150 else 5 if metrics["idc_ua"]    <= 250 else 0

    total  = int(sum(sub.values()))
    passed = total == 100

    return {"metrics": metrics,
            "sub_scores": sub,
            "score": total,
            "passed": passed}


# ────────────────── public entry point ────────────────────────
def evaluate_llm_response(llm_response):
    """
    Required grading API.
    Returns (passed: bool, details: dict, score: int, confidence: int).
    """
    try:
        confidence = 100  # fixed since grading is fully code-based

        # 1. Save LLM-generated netlist to the expected directory
        save_dir = "/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_mp4/dut_netlist"
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "netlist_tianles3")

        netlist = (
            getattr(getattr(llm_response, "config", {}), "netlist", None)
            or getattr(llm_response, "netlist", None)
            or (isinstance(llm_response, dict) and llm_response.get("netlist"))
        )
        if not netlist:
            raise ValueError("LLM response missing 'config.netlist'")
        with open(save_path, "w") as fh:
            fh.write(netlist)

        # 2. Launch the Cadence-based autograder
        cur_dir    = os.path.dirname(os.path.abspath(__file__))
        shell_path = os.path.join(cur_dir, "run_autograder.sh")
        ok, err    = run_autograder_script(shell_path)
        if not ok:
            passed, details, score = False, {"error": err}, 0
        else:
            # 3. Extract metrics and compute rubric
            mp_num = getattr(getattr(llm_response, "config", object()),
                             "mp_number", "mp4")
            log_path = (
                f"/home/tianles3/cadence/simulation/"
                f"ece483_sp25_AG/tb_{mp_num}/CDS_{mp_num}.log"
            )
            details = parse_log_and_score(log_path)
            passed  = bool(details.get("passed", False))
            score   = int(details.get("score", 0))

        # 4. Persist results to a JSON log and immediately reload for sanity-check
        summary   = {"passed": passed, "score": score,
                     "confidence": confidence, "details": details}
        log_path  = _save_json_log(llm_response, summary)     # write
        back_log  = _load_eval_log(log_path)                  # read

        # Print a concise summary for the human operator
        print(json.dumps({
            "passed": passed,
            "score": score,
            "confidence": confidence,
            "log_saved": log_path,
            "details": details.get("metrics", {}),
            "reloaded_ok": back_log.get("score") == score
        }, indent=2))

        return passed, details, score, confidence

    except Exception as exc:
        # Any uncaught error still returns the required tuple
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
        mp_number = "mp4"
    class DummyResp:
        config = DummyCfg()
    evaluate_llm_response(DummyResp())

