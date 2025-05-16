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
│   └── …                     
├── iterative_result/      # Logs from iterative design runs with GPT‑4o, o1, o3, o4‑mini
└── evaluation/            # Driver scripts & helpers for running the benchmark
    └── eval_openai_llm.py
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


