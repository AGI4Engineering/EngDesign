import argparse
import sys
import os
import subprocess
import base64
import json
from openai import OpenAI
from typing import List, Optional, Tuple
import importlib.util
import instructor
from pydantic import BaseModel
import google.generativeai as genai
from anthropic import Anthropic


client = None

def init_client(model: str, api_key: str):
    """
    Initialize an instructor client based on model name.

    Parameters:
    - model: model name string, e.g., "gpt-4o"
    - api_key: your API key for the respective provider

    Returns:
    - instructor client instance
    """
    if model in ["gpt-4o", "o1", "o3", "o4-mini"]:
        # Initialize OpenAI client
        return instructor.from_openai(OpenAI(api_key=api_key))
    
    elif model.startswith("gemini"):
        # Configure Gemini
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(model_name=f"models/{model}")
        return instructor.from_gemini(gemini_model)

    elif model.startswith("deepseek"):
        # DeepSeek is OpenAI-compatible but requires custom base_url
        deepseek_openai = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        return instructor.from_openai(deepseek_openai, mode=instructor.Mode.MD_JSON)
    
    elif model.startswith("claude"):
        return instructor.from_anthropic(Anthropic(api_key=api_key), mode=instructor.Mode.ANTHROPIC_JSON)

    else:
        raise ValueError(f"Unsupported model name: {model}")

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
        with open(prompt_path, "r",  encoding='utf-8') as f:
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
    Queries the LLM with optional image inputs for specified models.

    Parameters:
    - prompt: textual prompt
    - image_paths: list of image paths to attach (if using a vision model)
    - model: model name string
    - reasoning_effort: reasoning strength for OpenAI non-gpt-4o models
    - response_structure: pydantic response structure to enforce output format

    Returns:
    - model response (parsed if response_structure is provided), and token usage if available
    """
    try:
        if model in ["gpt-4o", "o1", "o3", "o4-mini"]:
            # OpenAI API
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
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ]
                    }
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


        elif model.startswith("gemini"):
            # Gemini API
            if image_paths:
                print("I am here, having images as input")
                # Gemini vision input: a sequence of parts
                parts = [{"text": prompt}] + [
                    {
                        "inline_data": {
                            "mime_type": f"image/{img_path.split('.')[-1]}",
                            "data": encode_image_to_base64(img_path)
                        }
                    }
                    for img_path in image_paths
                ]
            else:
                parts = [{"text": prompt}]
            
            response = client.chat.completions.create(
                response_model=response_structure,
                messages = [{"role": "user","content": parts}]
            )

            completion_tokens = response._raw_response.usage_metadata.candidates_token_count
            return response, completion_tokens


        elif model.startswith("deepseek"):
            messages = [
                {"role": "user", "content": prompt}
            ]
            response = client.chat.completions.create(
                        model=model,
                        response_model=response_structure,
                        messages=messages,
                    )

            completion_tokens = response._raw_response.usage.completion_tokens
            return response, completion_tokens
        

        elif model.startswith("claude"):
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

            if model == "claude-3-7-thinking":
                response = client.messages.create(
                            model="claude-3-7-sonnet-20250219",
                            max_tokens = 20000,
                            thinking={"type": "enabled",
                                    "budget_tokens": 16000},
                            messages=messages,
                            response_model = response_structure,
                        )
            elif model == "claude-3-7":
                response = client.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens = 4096,
                        messages=messages,
                        response_model = response_structure,
                    )
            else:
                return f"Unsupported model: {model}", 0

            completion_tokens = response._raw_response.usage.output_tokens
            return response, completion_tokens
        

        else:
            return f"Unsupported model: {model}", 0

    except Exception as e:
        return f"LLM API call failed: {e}", 0


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
        
        return evaluate_fn
    except Exception as e:
        print(f"Error loading evaluator: {str(e)}")
        raise

def run_task_k_times(task_path: str, k=3, model="gpt-4o", reasoning_effort="medium", log_dir="logs"):
    # Save the current directory to prevent chdir from affecting other paths
    original_cwd = os.getcwd()
    
    prompt_path = os.path.join(task_path, "LLM_prompt.txt")
    evaluator_path = os.path.join(task_path, "evaluate.py")
    images_dir = os.path.join(task_path, "images")
    log_dir = os.path.join(task_path, "logs")  # save log inside task folder
    output_structure_path = os.path.join(task_path, "output_structure.py")

    # Change the current working directory to the specified task path
    os.chdir(task_path)

    if not os.path.exists(output_structure_path):
        print(f"Skipping {task_path}: Missing output_structure.py")
        os.chdir(original_cwd)
        return

    Response_structure = load_output_structure(output_structure_path)

    if not os.path.exists(prompt_path) or not os.path.exists(evaluator_path):
        print(f"Skipping {task_path}: Missing LLM_prompt.txt or evaluate.py")
        os.chdir(original_cwd)
        return
    
    print("="*40)
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
            if isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif hasattr(obj, "item") and callable(getattr(obj, "item")):  # Handle NumPy types
                try:
                    return obj.item()
                except ValueError:
                    return obj.tolist()
            elif hasattr(obj, "__dict__") or hasattr(obj, "_asdict"):  # Handle custom objects
                if hasattr(obj, "_asdict") and callable(obj._asdict):
                    return convert_to_serializable(obj._asdict())
                else:
                    return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
            else:
                return str(obj)  # Convert any other types to string
                
        log_entry = convert_to_serializable(log_entry)

        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "w") as logf:
            logf.write(json.dumps(log_entry) + "\n")
        
        print(f"Trial {i + 1} for {os.path.basename(task_path)} completed: passed={passed}, score={score}")

    # Restore the original working directory
    os.chdir(original_cwd)

def main():
    parser = argparse.ArgumentParser(description='Run task evaluation across multiple task folders')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (default: gpt-4o)')
    parser.add_argument('--api_key', type=str, required=True, help='API key for OpenAI or Gemini')
    parser.add_argument('--reasoning_effort', type=str, default='medium', help='Reasoning effort to use (default: medium)')
    parser.add_argument('--k', type=int, default=3, help='Number of trials to run (default: 3)')
    parser.add_argument('--task_dir', type=str, required=True, help='Directory containing task folders')
    parser.add_argument('--only_task', type=str, help='If set, only run this specific task')
    parser.add_argument('--task_list', nargs='*', help='List of specific tasks to run (if empty, all tasks will run)')
    args = parser.parse_args()

    global client
    client = init_client(args.model, args.api_key)
    
    if args.only_task:
        # Subprocess mode: only run a single specified task
        task_path = os.path.abspath(os.path.join(args.task_dir, args.only_task))
        run_task_k_times(task_path=task_path, k=args.k, model=args.model, reasoning_effort=args.reasoning_effort)
        return

    if args.task_list:
        subfolders = args.task_list
    else:
        subfolders = [f for f in os.listdir(args.task_dir)
                    if os.path.isdir(os.path.join(args.task_dir, f))]


    for subfolder in subfolders:
        task_path = os.path.abspath(os.path.join(args.task_dir, subfolder))
        if not os.path.exists(task_path):
            print(f"Task folder '{subfolder}' not found in {args.task_dir}")
            continue

        subprocess.run([
            sys.executable, __file__,
            "--model", args.model,
            "--api_key", args.api_key,
            "--reasoning_effort", args.reasoning_effort,
            "--k", str(args.k),
            "--task_dir", args.task_dir,
            "--only_task", subfolder
        ])

if __name__ == "__main__":
    main()
