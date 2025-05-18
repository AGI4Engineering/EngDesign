# EngDesign

**EngDesign** is a benchmark of 101 structured engineering‑design tasks spanning multiple domains. This repository supports our NeurIPS Datasets & Benchmarks track submission:  
**“Toward Engineering AGI: Benchmarking the Engineering Design Capabilities of LLMs.”**

---

## 📂 Repository Layout

```text
├── tasks/                 # 101 individual task folders
│   ├── <task_id>/        # e.g. XG_01
│   │   ├── LLM_prompt.txt      # Prompt presented to the LLM
│   │   ├── output_structure.py # Defines the expected JSON/Python output schema via instructor
│   │   ├── evaluate.py         # Runs simulations & computes evaluation results
│   │   ├── images/             # (Optional) Input images for multimodal tasks
│   │   └── logs/               # Our evaluation logs
│   └── ...
├── EngDesign-Open/
│   ├── <task_id>/
│   └── ...
├── iterative_result/      # Logs from iterative design runs with GPT‑4o, o1, o3, o4‑mini
└── evaluation/            # Driver scripts & helpers for running the benchmark
    ├── eval_openai_llm.py
    └── eval_openai_llm_new.py
````

---

## 🚀 Quickstart

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your OpenAI key**
   Edit the top of `evaluation/eval_openai_llm.py` (or set the `OPENAI_API_KEY` environment variable).

3. **Run the full benchmark**

   ```bash
   python evaluation/eval_openai_llm.py --task_dir tasks
   ```

> **Note:**
>
> * Some tasks rely on external tools (e.g., MATLAB, SPICE), which may not be excuable for all machines.



---
## How to Run All Open Source Tasks (EngDesign-Open)

EngDesign-Open contains **all 53 open source tasks**. You can run them by following these steps:

### Setup Instructions

#### 1. Install and Log in to Docker

- Register at [hub.docker.com](https://hub.docker.com/) and **verify your email**.
- Download and install Docker Desktop on your machine: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Launch Docker Desktop and log in to your account.
- Make sure Docker Desktop has access to your drive (check settings).

#### 2. Replace API Keys

Replace the top of evaluation/eval_openai_llm_new.py with your actual OpenAI API keys before building the container.

#### 3. Authenticate via CLI

In a terminal, run:

   ```bash
   docker login -u your_dockerhub_username
   ```

#### 4. Build the Docker Image

Run the following command in the root directory of this project:

   ```bash
   docker build -t engdesign-sim .
   ```

#### 5. Start a Docker Container

Mount your local project directory and start a bash session in the container:

   ```bash
   docker run -it --rm -v the_actual_full_path_to_your_local_project_directory --entrypoint bash engdesign-sim
   ```

#### 6. Run the Benchmark Tasks

Once inside the container (you'll see a prompt like root@xxxxxxxxxxxx:/app#), run one of the following:

##### (1) Run All Tasks

   ```bash
   xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
   python3 evaluation/eval_openai_llm_new.py \
   --task_dir ./EngDesign-Open --model gpt-4o --k 1
   ```

##### (2) Run Specific Tasks

   ```bash
   xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
   python3 evaluation/eval_openai_llm_new.py \
   --task_dir ./EngDesign-Open --task_list AB_01 AB_02 --model gpt-4o --k 1
   ```

##### Parameter Description
   --task_dir: Directory containing the task folders
   --task_list: (Optional) Names of specific tasks to run (If not set, all tasks in EngDesign-Open will be run.)
   --model: Model to use, e.g., gpt-4o
   --k: Number of repetitions per task

#### 7. Exit the Container

Type ```exit``` to quit the container shell.

#### Optional Cleanup

Remove the image if needed:

   ```bash
   docker image rm engdesign-sim
   ```