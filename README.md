# 🦜️🔗 Ragas LLM Evaluation Framework

> **End-to-end evaluation pipeline for RAG architectures.**

## 📌 Project Overview

This repository provides a comprehensive framework for evaluating Retrieval-Augmented Generation (RAG) systems using [Ragas](https://github.com/explodinggradients/ragas). It includes automated testing pipelines, a synthetic data generator, and an industry-grade dashboard for monitoring quality.

---

## 🚀 Quick Setup

**Prerequisites:** Python 3.10+

1.  **Clone & Install:**
    ```bash
    git clone https://github.com/abhi9avx/ragas-llm-evaluation.git
    cd ragas-llm-evaluation
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configure Environment:**
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

---

## ⚡️ Running Evaluations

### 1️⃣ Run Full Evaluation Suite (Recommended)
Executes all checks and saves results to `results/` for the dashboard.
```bash
python evaluation/run_eval.py
```

### 2️⃣ Run Individual Metrics
| Metric | Command | Description |
| :--- | :--- | :--- |
| **Context Precision** | `pytest Test1.py` | Signal-to-noise ratio in retrieved docs. |
| **Context Recall** | `pytest Test2.py` | Checks if retrieved docs contain ground truth. |
| **Framework Test** | `pytest Test3_framework.py` | Parameterized tests for the Ragas framework. |
| **Faithfulness** | `pytest Test4.py` | Ensures answers are derived *only* from context. |
| **Answer Relevance** | `pytest Test5.py` | Checks if the answer addresses user's query. |
| **Factual Correctness** | `pytest Test5.py` | Validates answer against ground truth. |
| **Topic Adherence** | `pytest Test6.py` | (Multi-Turn) Ensures bot stays on topic. |

---

## 🧬 Synthetic Data Generator
Generate test cases automatically from your documents (`fs11/`).

### Option A: Via Dashboard (UI)
1. Go to sidebar → **Tools** → **Generate Synthetic Data**.
2. Select sample size and click **Start**.

### Option B: Via Command Line (CLI)
```bash
# Generate 10 new samples
python testDataFeaxtory.py 10
```
*Output saved to:* `testdata/generated_testset.json`

---

## 📊 Quality Dashboard
Monitor your metrics, track trends, and compare runs.

```bash
streamlit run dashboard/app.py
```

**Key Features:**
*   **Overview:** KPI cards for latest pass rates and scores.
*   **Trends:** Heatmaps and line charts to track regression.
*   **Deep Dive:** Drill down into specific runs to inspect failed examples.
*   **Comparison:** Radar charts to compare model versions side-by-side.

---

## 📊 Understanding the Metrics

### Context Precision
**Goal:** Evaluate how much of the retrieved context is actually relevant to the question.
- **High Score:** Most retrieved chunks are useful.
- **Low Score:** Too much noise/irrelevant info.

### Context Recall
**Goal:** Evaluate if the retrieval system found all the necessary information to answer the question.
- **High Score:** All relevant info was found.
- **Low Score:** Critical information was missed.

### Faithfulness
**Goal:** Ensure the generated answer is grounded in the retrieved context and not hallucinated.
- **High Score:** Answer is fully supported by context.
- **Low Score:** Model is making things up.

### Answer Relevance
**Goal:** Ensure the answer actually addresses the user's question, regardless of factual correctness.

### Factual Correctness
**Goal:** Compare the generated answer against a "Ground Truth" answer.

### Topic Adherence
**Goal:** For multi-turn conversations, ensure the model doesn't drift off-topic.

---

## 🏗️ Project Structure

```text
ragas-llm-evaluation/
├── evaluation/
│   └── run_eval.py             # Main execution engine
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── testDataFeaxtory.py         # Synthetic data generator
├── results/                    # History of runs (JSON/CSV)
├── fs11/                       # Source documents for generation
├── testdata/                   # JSON test cases
├── Test1.py - Test6.py         # Individual Metric Tests
└── requirements.txt            # Dependencies
```

---

## 👨‍💻 CI/CD Integration
This repo includes a GitHub Action (`.github/workflows/eval.yml`) that:
1. Runs `run_eval.py` on every push.
2. Uploads results as artifacts.
3. Automatically updates the repository with new history (optional).
