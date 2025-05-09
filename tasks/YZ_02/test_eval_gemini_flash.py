import argparse
import sys
import os
import base64
import json
from typing import List, Optional, Tuple
import importlib.util
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel
import time
from io import BytesIO
import google.generativeai as genai
from instructor.multimodal import Image
from output_structure import Response_structure


# Load key from .env
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-2.0-flash",
    )
)

# models/gemini-2.5-pro-preview-03-25

# gemini-2.5-pro-preview-03-25


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



def query_llm(prompt: str, model: str = "gemini-2.0-flash", task_dir: str = None):
    """Query the LLM with the given prompt and images."""
    try:
        # contents = []
        # print(image_paths)
        # exit()

        # Add images if provided
        # if image_paths:
        #     message=[
        #         {
        #             "role": "user",
        #             "content": [
        #                 prompt,
        #                 Image.from_path(image_paths[0]),
        #             ],
        #         }
        #     ]
        # else:
        message = [
            {
                "role": "user",
                "content": [
                    prompt
                ],
            }
        ]
        # Make the API call with properly formatted content
        response = client.messages.create(
            messages=message,
            response_model=Response_structure
        )
        
        # Process response
        completion_tokens = response._raw_response.usage_metadata.candidates_token_count
        
        return response, completion_tokens
        
    except Exception as e:
        error_message = str(e)
        print(f"API call failed: {error_message}")
        return f"OpenAI API call failed: {error_message}", 0


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluator", "evaluate.py")
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    return evaluator.evaluate_llm_response

def run_task_k_times(k=3, model="gemini-2.0-flash", log_dir="logs"):
    if not os.path.exists("LLM_prompt.txt") or not os.path.exists("evaluate.py"):
        print("Required files not found in current directory")
        return {"task": os.path.basename(os.getcwd()), "pass_count": 0, "total": k}
    image_paths = collect_image_paths()
    if image_paths:
        print("I am here, having images as input, will not run for this task with gemini models and return")
        return
    for i in range(k):
        print(f"Running trial {i+1} of {k}")
        prompt = extract_prompt("LLM_prompt.txt")
        evaluate_fn = load_evaluator()
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_log_gemini_flash_{i}.jsonl")

        # with open(log_file, "w") as logf:
        with open(log_file, "w", encoding="utf-8") as logf:
            response, completion_tokens = query_llm(prompt, model=model, task_dir=os.path.basename(os.getcwd()))
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
    parser.add_argument('--model', type=str, default='gemini-2.0-flash', help='Model to use (default: gemini-2.0-flash)')
    parser.add_argument('--log_dir', type=str, default='logs', help='Directory to store logs (default: logs)')
    parser.add_argument('--k', type=int, default=3, help='Number of trials to run (default: 1)')
    
    args = parser.parse_args()
    
    # Run the evaluation
    result = run_task_k_times(k=args.k, model=args.model, log_dir=args.log_dir)
    print(result)

if __name__ == "__main__":
    main()