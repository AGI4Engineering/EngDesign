#!/usr/bin/env python3
"""
evaluate.py — ECE 483 Mini-Project MP1 auto-grader
(updated for MP1: common-source amplifier)
"""

from __future__ import annotations
import os, re, json, subprocess
from datetime import datetime
from pathlib import Path


# ─────────── helper: run shell script ─────────────

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


# ─────────── helper: JSON log read/write ──────────

def _save_json_log(resp, summary) -> str:
    folder = Path(__file__).with_suffix("").parent / "evaluation_logs"
    folder.mkdir(exist_ok=True)
    fname = folder / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        resp_dump = json.loads(json.dumps(resp, default=lambda o: o.__dict__))
    except Exception:
        resp_dump = str(resp)
    with open(fname, "w") as fh:
        json.dump({"llm_response": resp_dump, **summary}, fh, indent=2)
    return str(fname)

def _load_eval_log(path: str) -> dict:
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception:
        return {}


# ─────────── helper: parse log & compute score (FOR MP1) ────────

def parse_log_and_score(log_path: str) -> dict:
    """Extract metrics from the Cadence log file and compute MP1 rubric scores."""
    if not os.path.isfile(log_path):
        return {"error": f"log file not found: {log_path}", "score": 0, "passed": False}

    metrics = {"dc_gain_vv": None, "bw_mrads": None, "vout_mv": None}
    label_map = {
        "dc_gain_vv": "Simulated DC Gain:",
        "bw_mrads":   "Simulated -3dB Frequency:",
        "vout_mv":    "Simulated VOUT:",
    }

    with open(log_path, "r") as fh:
        for line in fh:
            if "Simulated" not in line:
                continue
            clean = re.sub(r'^\\+o\s*"?', '', line).strip()
            for key, label in label_map.items():
                if clean.startswith(label):
                    m = re.search(r"([-+]?[0-9]*\.?[0-9]+)", clean[len(label):])
                    if m:
                        metrics[key] = float(m.group(1))
                    break

    if any(v is None for v in metrics.values()):
        return {"error": "one or more metrics missing", "metrics": metrics, "score": 0, "passed": False}

    sub = {}
    # DC Gain check (5 V/V with 2% tolerance = 4.9~5.1)
    sub["dc_gain"] = 30 if 4.9 <= metrics["dc_gain_vv"] <= 5.1 else 15 if 4.75 <= metrics["dc_gain_vv"] <= 5.25 else 0
    # 3dB Bandwidth check (>50 Mrad/s full; >45 Mrad/s partial)
    sub["bandwidth"] = 35 if metrics["bw_mrads"] >= 50 else 15 if metrics["bw_mrads"] >= 45 else 0
    # VOUT check (900mV +/-2% = 882-918 mV; +/-5% = 855-945mV)
    sub["vout"] = 35 if 882 <= metrics["vout_mv"] <= 918 else 15 if 855 <= metrics["vout_mv"] <= 945 else 0

    total = int(sum(sub.values()))
    passed = total >= 40  # arbitrary: if at least two specs partial or one spec full, considered "pass"

    return {"metrics": metrics, "sub_scores": sub, "score": total, "passed": passed}


# ─────────── public entry point ──────────

def evaluate_llm_response(llm_response):
    try:
        confidence = 100

        # 1. Save netlist
        save_dir = "/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_mp1/dut_netlist"
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

        # 2. Launch Cadence autograder
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        shell_path = os.path.join(cur_dir, "run_autograder.sh")
        ok, err = run_autograder_script(shell_path)

        if not ok:
            passed, details, score = False, {"error": err}, 0
        else:
            log_path = f"/home/tianles3/cadence/simulation/ece483_sp25_AG/tb_mp1/CDS_mp1.log"
            details = parse_log_and_score(log_path)
            passed = bool(details.get("passed", False))
            score = int(details.get("score", 0))

        # 3. Save and verify logs
        summary = {"passed": passed, "score": score, "confidence": confidence, "details": details}
        log_path = _save_json_log(llm_response, summary)
        back_log = _load_eval_log(log_path)

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
        print(json.dumps({
            "passed": False,
            "score": 0,
            "confidence": 100,
            "error": str(exc)
        }))
        return False, {"error": str(exc)}, 0, 100


if __name__ == "__main__":
    class DummyCfg:
        netlist = "* dummy"
    class DummyResp:
        config = DummyCfg()
    evaluate_llm_response(DummyResp())
