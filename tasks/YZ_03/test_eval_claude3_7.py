import argparse
import sys
import os
import base64
import json
from openai import OpenAI
from typing import List, Optional, Tuple
import importlib.util
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel
from anthropic import Anthropic

# Import Response_structure directly since we know we're in ZH_01
from output_structure import Response_structure


# Load key from .env
load_dotenv()
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
if claude_api_key:
    os.environ["ANTHROPIC_API_KEY"] = claude_api_key

# client = OpenAI(api_key=api_key)
client = instructor.from_anthropic(Anthropic(api_key=claude_api_key), mode=instructor.Mode.ANTHROPIC_JSON)


def extract_prompt(prompt_path: str) -> str:
    """
    Extract the prompt from the LLM_prompt.txt file.
    """
    try:
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find prompt file at {prompt_path}")
    except Exception as e:
        raise Exception(f"Error reading prompt file: {str(e)}")

def collect_image_paths() -> List[str]:
    """
    Check for an 'images' folder and return list of image file paths if exists.
    """
    image_dir = os.path.join("images")
    if not os.path.isdir(image_dir):
        return []

    image_files = [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"))
    ]
    return image_files

def encode_image_to_base64(image_path: str) -> str:
    """
    Encodes an image file as a base64 string for use in vision-enabled LLMs.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



def query_llm(prompt: str, image_paths: Optional[List[str]] = None, model: str = "claude-3-7-sonnet-20250219", task_dir: str = None):
    """
    Queries the LLM with optional image inputs.

    Parameters:
    - prompt: textual prompt
    - image_paths: list of image paths to attach (if using a vision model)
    - model: Claude model name (e.g., "claude-3-7-sonnet-20250219")
    - task_dir: directory of the current task

    Returns:
    - the assistant's reply or error message
    - number of completion tokens used
    """
    try:
        content = []
        # Add any images if provided
        if image_paths:
            content.append({
                "type": "text",
                "text": prompt
            })
            print("Adding images to prompt")
            for img_path in image_paths:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{img_path.split('.')[-1]}", 
                        "data": encode_image_to_base64(img_path)
                    }
                })
            messages = [
                {"role": "user", "content": content}
            ]
        else:
            messages = [
                {"role": "user", "content": prompt}
            ]
        response = client.messages.create(
                    model=model,
                    max_tokens = 4096,
                    messages=messages,
                    response_model = Response_structure,
                )

        # Extract completion tokens
        completion_tokens = response._raw_response.usage.output_tokens

        return response, completion_tokens

    except Exception as e:
        return f"OpenAI API call failed: {e}", 0


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluator", "evaluate.py")
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    return evaluator.evaluate_llm_response

def run_task_k_times(k=3, model="gpt-4o", log_dir="logs"):
    if not os.path.exists("LLM_prompt.txt") or not os.path.exists("evaluate.py"):
        print("Required files not found in current directory")
        return {"task": os.path.basename(os.getcwd()), "pass_count": 0, "total": k}

    for i in range(k):
        print(f"Running trial {i+1} of {k}")
        prompt = extract_prompt("LLM_prompt.txt")
        evaluate_fn = load_evaluator()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_log_claude3_7_{i}.jsonl")

        # with open(log_file, "w") as logf:
        with open(log_file, "w", encoding="utf-8") as logf:
            image_paths = collect_image_paths()
            response, completion_tokens = query_llm(prompt, image_paths=image_paths, model=model, task_dir=os.path.basename(os.getcwd()))
            if response:
                passed, detailed_result, score, _ = evaluate_fn(response)
            else:
                passed, detailed_result, score, _ = False, {}, 0, 0

            print(f"Trial {i+1} completed, passed: {passed}, score: {score}")
            log_entry = {
                "completion_tokens": completion_tokens,
                "response": response,
                "passed": passed,
                "evaluation_result": detailed_result,
                "score": score,
            }
            logf.write(str(log_entry) + "\n")
            
        

    return 

def main():
    parser = argparse.ArgumentParser(description='Run task evaluation')
    parser.add_argument('--model', type=str, default='claude-3-7-sonnet-20250219', help='Model to use (default: o1)')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to store logs (default: logs)')
    parser.add_argument('--k', type=int, default=3, help='Number of trials to run (default: 1)')
    
    args = parser.parse_args()
    
    # Run the evaluation
    result = run_task_k_times(k=args.k, model=args.model, log_dir=args.log_dir)
    print(result)

if __name__ == "__main__":
    main()