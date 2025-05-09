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

# Import Response_structure directly since we know we're in ZH_01
from output_structure import Response_structure

# Load key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

# client = OpenAI(api_key=api_key)
client = instructor.from_openai(OpenAI(api_key=api_key))


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



def query_llm(prompt: str, image_paths: Optional[List[str]] = None, model: str = "gpt-4o"):
    """
    Queries the LLM with optional image inputs.
    """
    try:
        if image_paths:
            print("Processing images as input")
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful engineering assistant that can help with engineering design problems."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{img_path.split('.')[-1]};base64,{encode_image_to_base64(img_path)}"
                            }
                        }
                        for img_path in image_paths
                    ]
                }
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful engineering assistant that can help with engineering design problems."},
                {"role": "user", "content": prompt}
            ]

        # Fixed: Don't wrap messages in another message
        response = client.chat.completions.create(
                    model=model,
                    response_model=Response_structure,
                    messages=messages,  # Direct use of messages
                )

        return response

    except Exception as e:
        return f"OpenAI API call failed: {e}"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluator", "evaluate.py")
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    return evaluator.evaluate_llm_response

def run_task_k_times(k=1, model="gpt-4o", log_dir="logs"):
    if not os.path.exists("LLM_prompt.txt") or not os.path.exists("evaluate.py"):
        print("Required files not found in current directory")
        return {"task": os.path.basename(os.getcwd()), "pass_count": 0, "total": k}

    prompt = extract_prompt("LLM_prompt.txt")
    print(prompt)
    evaluate_fn = load_evaluator()
    pass_count = 0
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_log.jsonl")

    with open(log_file, "w") as logf:
        for trial in range(k):
            image_paths = collect_image_paths()
            response = query_llm(prompt, image_paths=image_paths, model=model)
            print(response)
            if response:
                passed, detailed_result, score, confidence = evaluate_fn(response)
            else:
                passed, detailed_result, score, confidence = False, {}, 0, 0

            log_entry = {
                "trial": trial,
                "response": response,
                "passed": passed,
                "evaluation_result": detailed_result,
                "score": score,
                "confidence": confidence
            }
            logf.write(str(log_entry) + "\n")
            
            if passed:
                pass_count += 1

    return {"task": os.path.basename(os.getcwd()), "pass_count": pass_count, "total": k}

def main():
    parser = argparse.ArgumentParser(description='Run task evaluation')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (default: gpt-4o)')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to store logs (default: logs)')
    parser.add_argument('--k', type=int, default=1, help='Number of trials to run (default: 1)')
    
    args = parser.parse_args()
    
    # Run the evaluation
    result = run_task_k_times(k=args.k, model=args.model, log_dir=args.log_dir)
    print(result)

if __name__ == "__main__":
    main()