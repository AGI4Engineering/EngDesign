import subprocess
import time

def run_files():
    # List of files to run
    files = [
        'test_eval_gemini_pro.py',
        'test_eval_iterative_openai.py'
    ]
    
    # Run each file
    for i, file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Running: {file}")
        print("-" * 40)
        
        # Run the Python file
        try:
            subprocess.run(['python3', file], check=False)
            print(f"Completed: {file}")
        except Exception as e:
            print(f"Error running {file}: {str(e)}")
        
        print("-" * 40)
        
        # Small delay between runs
        if i < len(files):
            time.sleep(1)
    
    print("\nAll files have been executed.")

if __name__ == "__main__":
    run_files()