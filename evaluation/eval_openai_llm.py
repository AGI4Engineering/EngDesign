import argparse
import sys
import os
import base64
import json
from openai import OpenAI
from typing import List, Optional, Tuple
import importlib.util
import instructor
from pydantic import BaseModel


# Load key from .env
api_key = "your_openai_api_key"

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

# client = OpenAI(api_key=api_key)
client = instructor.from_openai(OpenAI(api_key=api_key), mode=instructor.Mode.JSON_O1)

def load_output_structure(output_structure_path: str):
    spec = importlib.util.spec_from_file_location("output_structure", output_structure_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Response_structure

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

def collect_image_paths(image_dir:str) -> List[str]:
    """
    Check for an 'images' folder and return list of image file paths if exists.
    """
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

def query_llm(prompt: str, image_paths: Optional[List[str]] = None, model: str = "gpt-4o", reasoning_effort: str = "medium", response_structure: Optional[BaseModel] = None):
    """
    Queries the LLM with optional image inputs.

    Parameters:
    - prompt: textual prompt
    - image_paths: list of image paths to attach (if using a vision model)
    - model: OpenAI model name (e.g., "gpt-4" or "gpt-4-vision-preview")
    - task_dir: directory of the current task

    Returns:
    - the assistant's reply or error message
    - number of completion tokens used
    """
    try:
        if image_paths:
            print("I am here, having images as input")
            messages = [
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
                {"role": "user", "content": prompt}
            ]
        
        if model == "gpt-4o":
            response = client.chat.completions.create(
                    model=model,
                    response_model=response_structure,
                    messages=messages,
                )
        else:
            response = client.chat.completions.create(
                        model=model,
                        reasoning_effort=reasoning_effort,
                        response_model=response_structure,
                        messages=messages,
                    )

        # Extract completion tokens
        completion_tokens = response._raw_response.usage.completion_tokens

        return response, completion_tokens

    except Exception as e:
        return f"OpenAI API call failed: {e}", 0


def load_evaluator(evaluator_path: str):
    """
    Load the evaluator module from the given path and handle imports for local modules.
    """
    try:
        # Get the directory containing the evaluator
        evaluator_dir = os.path.dirname(evaluator_path)
        
        # Temporarily add the evaluator directory to sys.path
        sys.path.insert(0, evaluator_dir)
        
        # Load the evaluator module
        spec = importlib.util.spec_from_file_location("evaluator", evaluator_path)
        evaluator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluator)
        
        # Get the evaluate function
        evaluate_fn = evaluator.evaluate_llm_response
        
        # Remove the directory from sys.path to avoid conflicts
        sys.path.pop(0)
        
        return evaluate_fn
    except Exception as e:
        print(f"Error loading evaluator: {str(e)}")
        raise

def run_task_k_times(task_path: str, k=3, model="gpt-4o", reasoning_effort="medium", log_dir="logs"):
    prompt_path = os.path.join(task_path, "LLM_prompt.txt")
    evaluator_path = os.path.join(task_path, "evaluate.py")
    images_dir = os.path.join(task_path, "images")
    log_dir = os.path.join(task_path, "logs")  # save log inside task folder
    output_structure_path = os.path.join(task_path, "output_structure.py")
    if not os.path.exists(output_structure_path):
        print(f"Skipping {task_path}: Missing output_structure.py")
        return

    Response_structure = load_output_structure(output_structure_path)

    if not os.path.exists(prompt_path) or not os.path.exists(evaluator_path):
        print(f"Skipping {task_path}: Missing LLM_prompt.txt or evaluate.py")
        return
    
    print(f"Processing task: {os.path.basename(task_path)}")

    prompt = extract_prompt(prompt_path)
    evaluate_fn = load_evaluator(evaluator_path)
    image_paths = collect_image_paths(images_dir)

    for i in range(k):
        print(f"Running trial {i + 1} of {k} for {os.path.basename(task_path)}")
        response, completion_tokens = query_llm(prompt, image_paths=image_paths, model=model, reasoning_effort=reasoning_effort, response_structure=Response_structure)
        print(f"{model} response: {response}")
        if response:
            passed, detailed_result, score, _ = evaluate_fn(response)
        else:
            passed, detailed_result, score, _ = False, {}, None, None
        
        if reasoning_effort == "high":
            if model == "o4-mini":  
                log_file = os.path.join(log_dir, f"{os.path.basename(task_path)}_log_o4_mini_high_{i}.jsonl")
            else:
                log_file = os.path.join(log_dir, f"{os.path.basename(task_path)}_log_{model}_high_{i}.jsonl")
        else:
            log_file = os.path.join(log_dir, f"{os.path.basename(task_path)}_log_{model}_{i}.jsonl")
        
        log_entry = {
            "completion_tokens": completion_tokens,
            "response": str(response),
            "passed": passed,
            "evaluation_result": detailed_result,
            "score": score,
        }
        # Convert log_entry to be JSON serializable
        def convert_to_serializable(obj):
            if hasattr(obj, "item"):  # Handle NumPy types
                return obj.item()
            elif hasattr(obj, "__dict__"):  # Handle custom objects
                return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)  # Convert any other types to string
                
        log_entry = convert_to_serializable(log_entry)
        
        with open(log_file, "w") as logf:
            logf.write(json.dumps(log_entry) + "\n")
        
        print(f"Trial {i + 1} for {os.path.basename(task_path)} completed: passed={passed}, score={score}")

def main():
    parser = argparse.ArgumentParser(description='Run task evaluation across multiple task folders')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (default: gpt-4o)')
    parser.add_argument('--reasoning_effort', type=str, default='medium', help='Reasoning effort to use (default: medium)')
    parser.add_argument('--k', type=int, default=3, help='Number of trials to run (default: 3)')
    parser.add_argument('--task_dir', type=str, required=True, help='Directory containing task folders')
    args = parser.parse_args()
    
    subfolders = [f for f in os.listdir(args.task_dir) 
                 if os.path.isdir(os.path.join(args.task_dir, f))]
    
    subfolders = ["RK_01"]


    for subfolder in subfolders:
        task_path = os.path.join(args.task_dir, subfolder)
        run_task_k_times(task_path=task_path, k=args.k, model=args.model, reasoning_effort=args.reasoning_effort)

if __name__ == "__main__":
    main()