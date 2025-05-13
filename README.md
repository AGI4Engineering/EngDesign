# EngDesign

**EngDesign** is a benchmark of 101 structured engineering‑design tasks spanning multiple domains. This repository supports our NeurIPS Datasets & Benchmarks track submission, "Toward Engineering AGI: Benchmarking the Engineering Design Capabilities of LLMs."

Of these 101 tasks, 48 rely on proprietary scientific softwares (e.g., MATLAB or Cadence) and may not run on every system. We provide the complete input datasets and evaluation scripts for these tasks as well —— simply follow the detailed setup instructions to configure the required environments and run them.

The remaining 53 tasks have no license restrictions and can be evaluated using our hand‑authored scripts. To remove licensing barriers, we’ve extracted these into **EngDesign-Open**, a standalone subset whose repository includes evaluation scripts for all 53 tasks without any proprietary dependencies.

Our evaluation framework currently integrates with twelve LLM variants: GPT‑4o, o1, o3, o3‑high, o4‑mini, o4‑mini‑high, Gemini‑2.0‑flash, Gemini‑2.5‑pro‑preview‑05‑06, DeepSeek‑Chat, DeepSeek‑Reasoner, Claude‑3‑7‑Sonnet, and Claude‑3‑7‑Sonnet (Extended Reasoning Mode).

---
## 🚀 Run EngDesign-Open

EngDesign-Open contains **all 53 tasks without license restrictions**. You can run them by following these steps:

### 1. Install and Log in to Docker

- Register at [hub.docker.com](https://hub.docker.com/) and **verify your email**.
- Download and install Docker Desktop on your machine: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Launch Docker Desktop and log in to your account.
- Make sure Docker Desktop has access to your drive (check settings).

### 2. Authenticate via CLI

In a terminal, run:

   ```bash
   docker login -u your_dockerhub_username
   ```

### 3. Build the Docker Image

Run the following command in the root directory of this project:

   ```bash
   docker build -t engdesign-sim .
   ```

### 4. Start a Docker Container

Mount your local project directory and start a bash session in the container:

   ```bash
   docker run -it --rm -v the_actual_full_path_to_your_local_project_directory --entrypoint bash engdesign-sim
   ```

### 5. Run the Benchmark Tasks

Once inside the container (you'll see a prompt like root@xxxxxxxxxxxx:/app#), you can run benchmark tasks using the following commands.

#### (1) Run All Tasks with a Given Model

   ```bash
   xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
     python3 evaluation/evaluate_llm.py \
     --model gpt-4o \
     --api_key your_openai_api_key \
     --task_dir ./EngDesign-Open \
     --k 1
   ```

#### (2) Run Specific Tasks with a Given Model

   ```bash
   xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
     python3 evaluation/evaluate_llm.py \
     --model gpt-4o \
     --api_key your_openai_api_key \
     --task_dir ./EngDesign-Open \
     --task_list AB_01 AB_02 \
     --k 1
   ```

#### 🛠️ Parameter Descriptions

| Parameter           | Description                                                                                   |
|---------------------|-----------------------------------------------------------------------------------------------|
| `--task_dir`        | Directory containing the task folders (e.g. `./EngDesign-Open`)                               |
| `--task_list`       | *(Optional)* Names of specific tasks to run (e.g. `AB_01 AB_02`). If not set, all tasks will run    |
| `--model`           | Model to use (Names of the twelve LLM variants using in the commands are: gpt-4o, o1, o3, o3‑high, o4‑mini, o4‑mini‑high, gemini-2.0-flash, gemini-2.5-pro-preview-05-06, deepseek-chat, deepseek-reasoner, claude-3-7, and claude-3-7-thinking)|
| `--api_key`         | Your API key for the corresponding provider (OpenAI, Google, DeepSeek, Anthropic, etc.)                |
| `--k`               | Number of repetitions per task                                                                |
| `--reasoning_effort`| *(Optional)* Use `high` for o3 or o4-mini models with high-effort reasoning mode                              |

### 6. Example Commands for All 12 Supported Models

#### OpenAI Models

(1) gpt-4o:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model gpt-4o \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(2) o1 - OpenAI GPT-4 variant (baseline configuration):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model o1 \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(3) o3 - OpenAI GPT-4 variant (enhanced reasoning):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model o3 \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(4) o3-high - OpenAI GPT-4 variant (high-effort reasoning mode):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model o3 \
  --reasoning_effort high \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(5) o4-mini - OpenAI GPT-4 Mini (lightweight version):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model o4-mini \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(6) o4-mini-high - OpenAI GPT-4 Mini (high-effort reasoning mode):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model o4-mini \
  --reasoning_effort high \
  --api_key your_openai_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

#### Gemini Models (Google)

(1) gemini-2.0-flash:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model gemini-2.0-flash \
  --api_key your_gemini_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(2) gemini-2.5-pro-preview-05-06:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model gemini-2.5-pro-preview-05-06 \
  --api_key your_gemini_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

#### DeepSeek Models

(1) deepseek-chat:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model deepseek-chat \
  --api_key your_deepseek_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(2) deepseek-reasoner:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model deepseek-reasoner \
  --api_key your_deepseek_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

#### Claude Models (Anthropic)

(1) claude-3-7-sonnet:
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model claude-3-7 \
  --api_key your_anthropic_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

(2) claude-3-7-sonnet (extended reasoning mode):
```bash
xvfb-run -a -e /dev/stdout --server-args="-screen 0 1024x768x24" \
  python3 evaluation/evaluate_llm.py \
  --model claude-3-7-thinking \
  --api_key your_anthropic_api_key \
  --task_dir ./EngDesign-Open \
  --task_list AB_01 AB_02 \
  --k 1
```

### 7. Other Important Information

#### (1) Replace API Keys

Make sure to replace the api_key in the commands with your actual API keys for the corresponding provider.

#### (2) Find the Task Outputs

You can find the model's corresponding output files in the `logs` folder within each task directory, where you can view the scores and the model's generated outputs.

### 8. Exit the Container

Type ```exit``` to quit the container shell.

### Optional Cleanup

Remove the image if needed:

   ```bash
   docker image rm engdesign-sim
   ```

---

## 🚀 Run Tasks Requiring Scientific Softwares

---

## 📂 Repository Layout

```text
├── tasks/                       # 101 individual task folders
│   ├── <task_id>/               # e.g. XG_01
│   │   ├── LLM_prompt.txt       # Prompt presented to the LLM
│   │   ├── output_structure.py  # Defines the expected JSON/Python output schema via instructor
│   │   ├── evaluate.py          # Runs simulations & computes evaluation results
│   │   ├── images/              # (Optional) Input images for multimodal tasks
│   │   └── logs/                # Our evaluation logs
│   └── ...
├── EngDesign-Open/              # The task folders without license restrictions
│   ├── <task_id>/
│   └── ...
├── iterative_result/            # Logs from iterative design runs with GPT‑4o, o1, o3, o4‑mini
├── evaluation/                  # The driver script for running the benchmark
│   └── evaluate_llm.py
├── Dockerfile                   # Docker configuration for containerized benchmarking
└── docker_requirements.txt      # Dependency list for installing in the Docker environment
````
