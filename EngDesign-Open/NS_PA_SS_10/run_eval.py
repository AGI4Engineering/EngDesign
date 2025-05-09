import subprocess
import time

def run_files():
    files = [
        'test_eval_o3_high.py',
        'test_eval_o4_mini.py',
        'test_eval_o4_mini_high.py',
        'test_eval_deepseek_chat.py',
        'test_eval_deepseek_r1.py',
        'test_eval_gemini_pro.py',
        'test_eval_gemini_flash.py',
        'test_eval_iterative_openai.py'
    ]
    
    # Run each file
    for file in files:
        print(f"Running: {file}")
        print("-" * 40)
        
        # Run the Python file
        try:
            subprocess.run(['python', file], check=False)
            print(f"Completed: {file}")
        except Exception as e:
            print(f"Error running {file}: {str(e)}")
        
        print("-" * 40)
    
    print("\nAll files have been executed.")

if __name__ == "__main__":
    run_files()