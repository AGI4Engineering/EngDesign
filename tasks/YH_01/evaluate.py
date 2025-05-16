import re
import json
import os
import sys
import subprocess
import shutil
from typing import Dict, List, Any
import codecs
import subprocess
import threading
import signal 
from create_testbench import create_testbench

def run_tcl_script(project_dir, tcl_file, vitis_hls_path, timeout_seconds_each=300, must_contain_success=None):
    try:
        process = subprocess.Popen(
            [vitis_hls_path, "-f", tcl_file],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Start a new process group
        )

        # Buffers to collect output
        stdout_lines = []
        stderr_lines = []

        # Define live-printing + capture with safe exit on closed pipe
        def reader(pipe, buffer, printer):
            try:
                for line in iter(pipe.readline, ''):
                    if not line:
                        break
                    printer(line.rstrip())
                    buffer.append(line)
            except ValueError:
                # Pipe was closed; exit thread gracefully
                pass
            finally:
                try:
                    pipe.close()
                except Exception:
                    pass

        # Create threads to read stdout and stderr live
        stdout_thread = threading.Thread(target=reader, args=(process.stdout, stdout_lines, print))
        stderr_thread = threading.Thread(target=reader, args=(process.stderr, stderr_lines, lambda x: print(x, file=sys.stderr)))

        stdout_thread.start()
        stderr_thread.start()

        process.wait(timeout=timeout_seconds_each)

        stdout_thread.join()
        stderr_thread.join()

        # Check if the command failed
        if process.returncode != 0:
            print(f"\n Error while running {tcl_file} (return code {process.returncode})!")
            sys.exit(1)

        # Combine stdout into one big string for checking
        full_stdout = ''.join(stdout_lines)

        if must_contain_success:
            if must_contain_success not in full_stdout:
                print(f"\n Stage '{tcl_file}' did NOT complete successfully (missing expected message).")
                return False

        print(f"\n {tcl_file} completed successfully!")
        return True

    except subprocess.TimeoutExpired:
        print(f"\n Timeout expired while running {tcl_file}!")

        # Kill the entire process group
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            print(f"Sent SIGTERM to process group {os.getpgid(process.pid)}")
        except Exception as e:
            print(f"Warning: could not kill process group cleanly: {e}")

        # Extra safety: Close pipes
        try:
            process.stdout.close()
            process.stderr.close()
        except Exception:
            pass

        # Join threads safely
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)

        return False
        
def vitis_hls_synthesis(vitis_hls_path, project_name, project_dir, kernel_file, top_function, testbench_file, fpga_part):
    os.makedirs(project_dir, exist_ok=True)

    # Stage 1: Create Project TCL
    create_project_tcl = f"""\
    open_project {project_name}
    set_top {top_function}
    add_files {kernel_file}
    add_files -tb {testbench_file}
    open_solution "solution1"
    set_part "{fpga_part}"
    create_clock -period 5 -name default
    exit
    """

    # Stage 2: Run C Simulation TCL
    run_csim_tcl = f"""\
    open_project {project_name}
    open_solution "solution1"
    csim_design
    exit
    """

    # Stage 3: Run C Synthesis TCL
    run_csynth_tcl = f"""\
    open_project {project_name}
    open_solution "solution1"
    csynth_design
    exit
    """

    # Stage 4: Run Cosimulation TCL
    run_cosim_tcl = f"""\
    open_project {project_name}
    open_solution "solution1"
    cosim_design
    exit
    """

    # Save the TCL scripts
    tcl_scripts = {
        "run_create_project.tcl": create_project_tcl,
        "run_csim.tcl": run_csim_tcl,
        "run_csynth.tcl": run_csynth_tcl,
        "run_cosim.tcl": run_cosim_tcl,
    }

    for filename, content in tcl_scripts.items():
        with open(os.path.join(project_dir, filename), "w") as f:
            f.write(content)

    # Now run them in order
    print("\n=== Running Stage 1: Create Project ===")
    run_tcl_script(project_dir, "run_create_project.tcl", vitis_hls_path=vitis_hls_path, timeout_seconds_each=300)

    print("\n=== Running Stage 2: C Simulation ===")
    try:
        csimPassed = run_tcl_script(project_dir, "run_csim.tcl", vitis_hls_path=vitis_hls_path, timeout_seconds_each=300, must_contain_success="TESTBENCH~PASSED")
    except (subprocess.CalledProcessError, subprocess.SubprocessError, OSError, IOError, BaseException) as e:
        csimPassed = False

    
    if not csimPassed:
        print("\n C Simulation failed. Please check the testbench.")
        return False, None, None

    print("\n=== Running Stage 3: C Synthesis ===")
    try:
        csynthPassed = run_tcl_script(project_dir, "run_csynth.tcl", vitis_hls_path=vitis_hls_path, timeout_seconds_each=600, must_contain_success="Finished Command csynth_design CPU user time")
    except (subprocess.CalledProcessError, subprocess.SubprocessError, OSError, IOError, BaseException) as e:
        csynthPassed = False

    
    if not csynthPassed:
        print("\n C Synthesis failed. Please check the design.")
        return True, False, None

    print("\n=== Running Stage 4: C/RTL Cosimulation ===")
    try:
        cosimPassed = run_tcl_script(project_dir, "run_cosim.tcl", vitis_hls_path=vitis_hls_path, timeout_seconds_each=1000, must_contain_success="*** C/RTL co-simulation finished: PASS ***")
    # *** C/RTL co-simulation finished: PASS ***
    except (subprocess.CalledProcessError, subprocess.SubprocessError, OSError, IOError, BaseException) as e:
        cosimPassed = False
    
    if not cosimPassed:
        print("\n C/RTL Cosimulation failed. Please check the testbench.")
        return True, True, False

    print("\n All stages completed successfully!")
    return True, True, True        

def parse_performance_metrics(lines: List[str]) -> Dict[str, Any]:
    metrics = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('PS:'):
            continue
            
        if line.startswith('|'):
            parts = [p.strip() for p in line.split('|') if p.strip()]
            # Skip headers and separators
            if len(parts) >= 10 and not any(parts[0].startswith(x) for x in ('Modules', '---', '&')):
                # Clean the module name by removing special symbols
                module_name = parts[0].strip('+ o').strip()
                if module_name:
                    # Helper function to extract value and percentage
                    def parse_resource(value):
                        if value == '-':
                            return {'value': '-', 'percentage': '-'}
                        parts = value.split('(')
                        if len(parts) > 1:
                            # Clean up percentage by removing (~, ), and extra spaces
                            percentage = parts[1].replace(')', '').replace('~', '').strip()
                            return {
                                'value': parts[0].strip(),
                                'percentage': percentage
                            }
                        return {'value': value.strip(), 'percentage': '-'}

                    # Create a unique key for each entry
                    entry_key = module_name
                    metrics[entry_key] = {
                        'Slack': parts[2],  # Slack is in the third column (index 2)
                        'Latency': {
                            'cycles': parts[3],
                            'time_ns': parts[4]
                        },
                        'Iteration_Latency': parts[5],
                        'Interval': parts[6],
                        'Trip_Count': parts[7],
                        'Pipeline': parts[8],
                        'Resources': {
                            'BRAM': parse_resource(parts[9]),
                            'DSP': parse_resource(parts[10]),
                            'FF': parse_resource(parts[11]),
                            'LUT': parse_resource(parts[12]),
                            'URAM': parse_resource(parts[13]) if len(parts) > 13 else {'value': '-', 'percentage': '-'}
                        }
                    }
    
    return metrics

def parse_general_info(lines: List[str]) -> Dict[str, Any]:
    general_info = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Only capture the actual information entries
        if line.startswith('*') and ':' in line:
            line = line[1:].strip()  # Remove the asterisk
            key, value = [x.strip() for x in line.split(':', 1)]
            general_info[key] = value
    
    return general_info

def parse_rpt_file(rpt_file: str) -> Dict[str, Any]:
    with open(rpt_file, 'r') as f:
        lines = f.readlines()
    
    result = {
        'Performance_Metrics': {},
        'Synthesis_Summary': {}
    }
    
    # Find section boundaries
    sections = {
        'Performance_Metrics': None,
        'Synthesis_Summary': None
    }
    
    for i, line in enumerate(lines):
        if 'Synthesis Summary Report' in line:
            # Extract just the module name from the title
            module_name = line.split("'")[1]  # Get the text between single quotes
            result['Synthesis_Summary']['Title'] = module_name
            sections['Synthesis_Summary'] = i
        elif 'Performance & Resource Estimates' in line:
            sections['Performance_Metrics'] = i
    
    # Parse each section
    if sections['Synthesis_Summary']:
        # Find the end of the Synthesis Summary section
        next_section = None
        for i, line in enumerate(lines[sections['Synthesis_Summary']:], sections['Synthesis_Summary']):
            if 'Performance & Resource Estimates' in line:
                next_section = i
                break
        
        # Extract the synthesis summary information
        summary_lines = lines[sections['Synthesis_Summary']:next_section] if next_section else lines[sections['Synthesis_Summary']:]
        for line in summary_lines:
            line = line.strip()
            if line.startswith('*'):
                # Remove the asterisk and split by colon
                parts = line[1:].strip().split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    result['Synthesis_Summary'][key] = value
            
            # Extract slack value if present
            if 'Slack' in line and ':' in line:
                slack_parts = line.split(':', 1)
                if len(slack_parts) == 2:
                    result['Synthesis_Summary']['Slack'] = slack_parts[1].strip()
    
    if sections['Performance_Metrics']:
        next_section = None
        for i, line in enumerate(lines[sections['Performance_Metrics']:], sections['Performance_Metrics']):
            if '================================================================' in line:
                next_section = i
                break
        section_lines = lines[sections['Performance_Metrics']:next_section] if next_section else lines[sections['Performance_Metrics']:]
        result['Performance_Metrics'] = parse_performance_metrics(section_lines)
    
    return result

def calculate_score(json_file: str, optimal_values) -> tuple[str, float]:

    optimal_dsp_percent, optimal_ff_percent, optimal_lut_percent = optimal_values

    with open(json_file, 'r') as f:
        result = json.load(f)
    
    # Get the module name from Synthesis_Summary
    module_name = result['Synthesis_Summary']['Title']
    
    # Extract the metrics for this module
    if module_name in result['Performance_Metrics']:
        module_metrics = result['Performance_Metrics'][module_name]
        
        # Check for missing values
        slack = module_metrics.get('Slack', "-")
        latency_cycles = module_metrics.get('Latency', {}).get('cycles', '-')
        latency_ns = module_metrics.get('Latency', {}).get('time_ns', '-')
        dsp = module_metrics.get('Resources', {}).get('DSP', {}).get('percentage', '-')
        ff = module_metrics.get('Resources', {}).get('FF', {}).get('percentage', '-')
        lut = module_metrics.get('Resources', {}).get('LUT', {}).get('percentage', '-')
        
        # Check if any value is missing
        if any(x == '-' for x in [slack, latency_cycles, latency_ns, dsp, ff, lut]):
            return (False, "Missing required metrics in the report", 0)
        
        # Check if slack is negative
        # slack = float(slack)
        # if slack < 0:
        #     return (False, "Slack is negative, design is not wirable: ", 0)
        
        # Calculate score using percentages
        dsp_percent = float(dsp.strip('%'))
        ff_percent = float(ff.strip('%'))
        lut_percent = float(lut.strip('%'))
        
        period_ns = float(latency_ns) / float(latency_cycles)
        freq_ghz = 1 / period_ns
        freq_mhz = freq_ghz * 1000
        
        # TODO: [YH] consider the operation of the module
        score = 0.3 * 1 / (freq_mhz + 1e-3) + (0.4 * dsp_percent/optimal_dsp_percent + 0.2 * ff_percent/optimal_ff_percent + 0.1 * lut_percent/optimal_lut_percent) * 100 
        return (True,"Wirable", score)
    
    return (False, "Module not found in performance metrics", 0)



def evaluate(vitis_hls_path, project_name, test_directory, kernel_file, top_function, testbench_file, fpga_part, optimal_values):
    
    csim, csynth, cosim = vitis_hls_synthesis(vitis_hls_path, project_name, test_directory, kernel_file, top_function, testbench_file, fpga_part)
    
    confidence = 0
    if csim is False:
        return (False, "Simulation failed", 0, 0)
    if csynth is False:
        return (False, "Synthesis failed", 0, 0)
    if cosim:
        confidence = 100
        
    result = parse_rpt_file(project_name + ".hls/" + project_name + "/solution1/syn/report/csynth.rpt")
    
    # Save as JSON for better readability
    with open(project_name + ".hls/" + "evaluation_report.json", 'w') as f:
        json.dump(result, f, indent=4)
    
    # Calculate and add the extracted metrics
    # Also print to console
    with open(project_name + ".hls/" + "evaluation_report.json", 'r') as f:
        result = json.load(f)

    passed, details, score = calculate_score(project_name + ".hls/" + "evaluation_report.json", optimal_values)
    
    return (passed, details, score, confidence)


def evaluate_llm_response(llm_response):

    print("Evaluating LLM response...")
    print(llm_response)

    hls_design = llm_response.config.hls_design
    m_size = int(llm_response.config.parameters.m_size)
    n_size = int(llm_response.config.parameters.n_size)
    k_size = int(llm_response.config.parameters.k_size)
    print(llm_response.config.parameters.optimal_DSP, llm_response.config.parameters.max_DSP)

    optimal_dsp_percent = min(100, llm_response.config.parameters.optimal_DSP / llm_response.config.parameters.max_DSP * 100)
    optimal_ff_percent = min(100, llm_response.config.parameters.optimal_FF / llm_response.config.parameters.max_FF * 100)
    optimal_lut_percent = min(100, llm_response.config.parameters.optimal_LUT / llm_response.config.parameters.max_LUT * 100)
    optimal_values = (optimal_dsp_percent, optimal_ff_percent, optimal_lut_percent)


    
    # Unescape the \n characters into real newlines
    hls_design_unescaped = codecs.decode(hls_design, 'unicode_escape')
    
    print("HLS design received from LLM:")
    print(hls_design_unescaped)
    
    # TODO: change the path to the correct path
    vitis_hls_path = "/tools/Xilinx/Vitis_HLS/2023.2/bin/vitis_hls"
    project_name = "gemm_proj"
    kernel_file = "gemm.cpp"
    top_function = "gemm"
    fpga_part = "xcvc1902-vsvd1760-2MP-e-S"
    testbench_file = "gemm_testbench.cpp"

    # Get the directory where evaluate.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    testbench_path = os.path.join(current_dir, "examples_testbenches", testbench_file)

    print("###############", testbench_path)

    testbench_file = create_testbench(testbench_path, m_size, n_size, k_size)

    # Remove the directory if it exists, then create it
    project_dir = project_name + ".hls"    
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir, exist_ok=True)
    
    # Copy the testbench file to the project directory
    shutil.copy(testbench_path, os.path.join(project_dir, testbench_file))
    
    # Save the kernel file under test_directory
    kernel_path = os.path.join(project_dir, kernel_file)
    with open(kernel_path, 'w') as f:
        f.write(hls_design_unescaped)
    print(f"HLS design saved to {kernel_path}")
    
    passed, details, score, confidence = evaluate(vitis_hls_path, project_name, project_dir, kernel_file, top_function, testbench_file, fpga_part, optimal_values)
    
    return passed, details, score, confidence

if __name__ == "__main__":
    # Example usage
    # vitis_hls_path = "/mnt/sdb1/Xilinx/Vitis_HLS/2023.2/bin/vitis_hls"
    vitis_hls_path = "/tools/Xilinx/Vitis_HLS/2023.2/bin/vitis_hls"
    project_name = "gemm_proj"
    kernel_file = "gemm.cpp"
    top_function = "gemm"
    fpga_part = "xcvc1902-vsvd1760-2MP-e-S"
    testbench_file = "gemm_testbench.cpp"
    gemm_test = "gemm64_example.cpp"   
    
    # Remove the directory if it exists, then create it
    project_dir = project_name + ".hls"    
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir, exist_ok=True)
    
    # Copy the testbench file to the project directory
    shutil.copy(os.path.join("examples_testbenches/", testbench_file), os.path.join(project_dir, testbench_file))
    
    # Copy the test file to the project directory
    shutil.copy(os.path.join("examples_testbenches/", gemm_test), os.path.join(project_dir, kernel_file))

    passed, details, score, confidence = evaluate(vitis_hls_path, project_name, project_dir, kernel_file, top_function, testbench_file, fpga_part)
    print(passed, details, score, confidence)