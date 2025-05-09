# EngDesign

A benchmark of 101 structured engineering design tasks spanning multiple domains.

This repository contains all tasks included in **EngDesign**, developed for our NeurIPS Datasets and Benchmarks track submission:
**"Toward Engineering AGI: Benchmarking the Engineering Design Capabilities of LLMs."**

### 📁 Repository Structure

The repository includes a `tasks` folder with 101 engineering design tasks. Each task is organized as a separate folder containing at least the following components:

* **`LLM_prompt.txt`**: The task description presented to the LLM.
* **`output_structure.py`**: A Python script that defines the expected structured output format for the task.
* **`evaluate.py`**: An evaluation script that runs simulations using the LLM-generated outputs and computes performance metrics.
* **`images/`** *(optional)*: A directory containing images used as part of the task input (for multimodal tasks).
* **`logs/`**: A directory containing all the evaluation logs for the task.
* **Other utility files**: Additional Python scripts or resources needed to support evaluation.

### ⚠️ Requirements

Some tasks rely on domain-specific simulation tools such as **MATLAB** or **SPICE**, which may not be available in all environments. Please refer to the individual task folders for tool-specific instructions.
