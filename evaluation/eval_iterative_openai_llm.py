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


# Load key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

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

def query_llm(prompt: str, image_paths: Optional[List[str]] = None, model: str = "gpt-4o", response_structure: Optional[BaseModel] = None):
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

def run_task_k_times(task_path: str, log_path: str, k=10, model="gpt-4o", subfolder=None):
    prompt_path = os.path.join(task_path, "LLM_prompt.txt")
    evaluator_path = os.path.join(task_path, "evaluate.py")
    images_dir = os.path.join(task_path, "images")
    log_dir = os.path.join(log_path, subfolder)  # save log inside task folder
    output_structure_path = os.path.join(task_path, "output_structure.py")
    if not os.path.exists(output_structure_path):
        print(f"Skipping {task_path}: Missing output_structure.py")
        return
    Response_structure = load_output_structure(output_structure_path)

    print(f"Processing task: {os.path.basename(task_path)}")


    original_prompt = extract_prompt(prompt_path)
    evaluate_fn = load_evaluator(evaluator_path)
    image_paths = collect_image_paths(images_dir)

    response_history = {}
    evaluation_history = {}
    responses_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_responses.txt")
    evaluations_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_evaluations.txt")
    for i in range(k):
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{os.path.basename(os.getcwd())}_log_{model}_iteration_{i}.jsonl")
        print(f"Running iteration {i+1} for task {os.path.basename(os.getcwd())}")
        if i == 0:
            prompt = original_prompt
        else:
            prompt = prompt_w_feedback
        
        # print(f"Prompt for iteration {i+1}: {prompt}")
        response, completion_tokens = query_llm(prompt, image_paths=image_paths, model=model, response_structure=Response_structure)
        response_history[i+1] = response
        if response:
            passed, detailed_result, score, _ = evaluate_fn(response)
            evaluation_history[i+1] = detailed_result
            with open(log_file, "w") as logf:
                    log_entry = {
                        "iteration": i+1,
                        "completion_tokens": completion_tokens,
                        "passed": passed,
                        "score": score,
                    }
                    logf.write(str(log_entry) + "\n")
            if passed:
                print(f"Task {os.path.basename(os.getcwd())} passed with {i+1} iterations")
                # Write final successful responses and evaluations to json files
                with open(responses_file, "w", encoding="utf-8") as f:
                    for j in range(1, i+2):
                        f.write(f"Attempt {j}:\n{response_history[j]}\n")
                    
                with open(evaluations_file, "w", encoding="utf-8") as f:
                    for j in range(1, i+2):
                        f.write(f"Attempt {j}:\n{evaluation_history[j]}\n")
                break
            else:
                print(f"Task {os.path.basename(os.getcwd())} failed with {i+1} iterations")
                all_responses = "\n\n".join([f"Attempt {j}:\n{response_history[j]}" for j in range(1, i+2)])
                all_evaluations = "\n\n".join([f"Attempt {j}:\n{evaluation_history[j]}" for j in range(1, i+2)])
                prompt_w_feedback = original_prompt + "\n\n" + "Here are your responses from the previous attempts:\n\n " + all_responses + "\n\n" + "Here are the evaluation feedback from the previous attempts:\n\n " + all_evaluations + "\n\n" + "Please address the feedback and propose a new solution."

        if i == k-1:
            print(f"Task {os.path.basename(os.getcwd())} failed with {i+1} iterations")
            # Write final successful responses and evaluations to json files
            with open(responses_file, "w", encoding="utf-8") as f:
                for j in range(1, i+2):
                    f.write(f"Attempt {j}:\n{response_history[j]}\n")
            with open(evaluations_file, "w", encoding="utf-8") as f:
                for j in range(1, i+2):
                    f.write(f"Attempt {j}:\n{evaluation_history[j]}\n")

def main():
    parser = argparse.ArgumentParser(description='Run task evaluation across multiple task folders')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (default: gpt-4o)')
    parser.add_argument('--reasoning_effort', type=str, default='medium', help='Reasoning effort to use (default: medium)')
    parser.add_argument('--k', type=int, default=10, help='Number of trials to run (default: 3)')
    parser.add_argument('--task_dir', type=str, required=True, help='Directory containing task folders')
    args = parser.parse_args()
    # find subfolders that should be excluded
    
    # excluded_folders = ["XZ_03", "XZ_04", "RS_01", "RS_02", "RS_03", "YJ_01", "XW_01", "XW_02", "XW_03", "XW_04", "NS_PA_SS_02", "NS_PA_SS_03", "NS_PA_SS_04", "NS_PA_SS_05", "NS_PA_SS_06", "NS_PA_SS_07", "NS_PA_SS_08", "NS_PA_SS_09", "NS_PA_SS_10", "HJ_01"]
    # subfolders = [f for f in os.listdir(args.task_dir) 
    #              if os.path.isdir(os.path.join(args.task_dir, f)) 
    #              and f not in excluded_folders]
    # subfolders = ["NS_PA_SS_01","NS_PA_SS_02","NS_PA_SS_03","NS_PA_SS_04","NS_PA_SS_05","NS_PA_SS_06","NS_PA_SS_07","NS_PA_SS_08","NS_PA_SS_09","NS_PA_SS_10","qjlim2_04","XG_13","Ziheng_02","Ziheng_03"]
    # subfolders = ["NS_PA_SS_02"]
    # evaluated_folders = [f for f in os.listdir("/Users/xingang/Desktop/Engineering-Design-Benchmark/iterative_exp")]
    save_path = "/Users/xingang/Desktop/Engineering-Design-Benchmark/iterative_o3"
    evaluated_folders = [f for f in os.listdir(save_path)]
    log_path = save_path

    subfolder = ["RK_01","RK_02","RK_03","RK_04"]

    for subfolder in subfolder:
        task_path = os.path.join(args.task_dir, subfolder)
        if subfolder in evaluated_folders:  
            continue
        try:
            run_task_k_times(task_path=task_path, log_path=log_path, k=args.k, model=args.model, subfolder=subfolder)
            evaluated_folders.append(subfolder)
        except Exception as e:
            print(f"Error running task {subfolder}: {e}")

    # print(f"Excluded folders: {excluded_folders}")

if __name__ == "__main__":
    main()