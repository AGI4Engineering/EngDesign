import os
import sys
import subprocess
import json

def evaluate_llm_response(llm_response):
    """
    Invoke the external run_autograder.sh script to evaluate the LLM response.
    Before running, strip any Windows‐style CRLF endings so Bash won’t choke on '$'\\r''.
    Expects the script to print a JSON object:
      { "passed": bool,
        "details": dict,
        "score": int,
        "confidence": int (optional) }
    """
    try:
        # default confidence for code-based judgment
        confidence = 100

        # locate the shell script alongside this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'run_autograder.sh')

        # sanitize CRLF -> LF in place
        with open(script_path, 'rb') as f:
            data = f.read().replace(b'\r\n', b'\n')
        with open(script_path, 'wb') as f:
            f.write(data)
        # ensure it’s executable
        os.chmod(script_path, 0o755)

        # run the autograder script
        result = subprocess.run(
            ['bash', script_path],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        # if it failed, return stderr
        if result.returncode != 0:
            return False, {'error': result.stderr.strip()}, None, None

        # parse its JSON output
        output = json.loads(result.stdout)
        passed     = output.get('passed', False)
        details    = output.get('details', {})
        score      = output.get('score')
        confidence = output.get('confidence', confidence)

        return passed, details, score, confidence

    except Exception as e:
        return False, {'error': str(e)}, None, None


if __name__ == '__main__':
    # quick smoke test
    class DummyConfig: pass
    class DummyResponse: config = DummyConfig()
    passed, details, score, confidence = evaluate_llm_response(DummyResponse())
    print(f"passed={passed}, score={score}, confidence={confidence}")
    print("details:", details)
