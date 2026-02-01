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

## ⚡️ Detailed Manual Testing Guide

You can run individual tests to check specific aspects of your RAG pipeline. Here is exactly what each test does:

### 🔍 Test 1: Retrieval Precision (`Test1.py`)
**Goal:** Check if the documents retrieved by your vector database are actually relevant to the user's query.
- **What it does:** Sends a query, looks at the retrieved documents, and calculates the signal-to-noise ratio.
- **How to run:**
  ```bash
  pytest -s Test1.py
  ```

### 🧠 Test 2: Retrieval Recall (`Test2.py`)
**Goal:** Ensure your system is finding *all* the necessary information needed to answer the question.
- **What it does:** Compares the retrieved documents against a "Golden Reference" to ensure no critical facts are missing.
- **How to run:**
  ```bash
  pytest -s Test2.py
  ```

### 🏗️ Test 3: Framework Reliability (`Test3_framework.py`)
**Goal:** Run a parameterized suite of tests to validate the framework itself stability.
- **What it does:** Loads multiple test cases from `testdata/Test3_framework.json` and runs them in batch to ensure the evaluation engine works across different inputs.
- **How to run:**
  ```bash
  pytest -s Test3_framework.py
  ```

### 🛡️ Test 4: Hallucination Check (`Test4.py`)
**Goal:** Measure **Faithfulness** - ensure the LLM isn't making things up.
- **What it does:** Checks if every claim in the generated answer can be supported by the retrieved context. If the LLM generates info not in the docs, this test fails.
- **How to run:**
  ```bash
  pytest -s Test4.py
  ```

### ✅ Test 5: Answer Quality (`Test5.py`)
**Goal:** Measure **Answer Relevance** and **Factual Correctness**.
- **What it does:** 
  1. Checks if the answer actually addresses the specific question asked (Relevance).
  2. Compares the answer against a known ground truth to verify accuracy (Correctness).
- **How to run:**
  ```bash
  pytest -s Test5.py
  ```

### 🔄 Test 6: Conversation Flow (`Test6.py`)
**Goal:** Measure **Topic Adherence** for chatbots.
- **What it does:** Simulates a multi-turn conversation (User -> Bot -> User -> Bot) and ensures the bot doesn't drift off-topic or get distracted.
- **How to run:**
  ```bash
  pytest -s Test6.py
  ```

---

## 🏭 Synthetic Data Factory (`testDataFeaxtory.py`)

Running low on test cases? We built a tool to generate them for you automatically.

**What it does:**
1. Reads all documents from the `fs11/` folder (supports `.docx`).
2. Uses GPT-4 to "read" the docs and think of realistic questions a user might ask.
3. Generates the corresponding Ground Truth answers.
4. Saves this new dataset to `testdata/generated_testset.json`.

**How to run (Command Line):**
```bash
# Generate 10 new test samples
python testDataFeaxtory.py 10
```

---

## 📊 Quality Dashboard

We have a professional dashboard to visualize your results.

**How to open:**
```bash
streamlit run dashboard/app.py
```

**What you will see:**
1. **Overview Page:** Trends of how your LLM is performing over time.
2. **Tools Tab (Sidebar):** A UI version of the Data Factory. You can generate tests here without using the command line.
3. **Deep Dive:** Click on specific runs to see exactly where the model failed (side-by-side comparison of User Query vs. Model Answer).

---

## 🤖 Automated Evaluation Pipeline

To run everything at once and update the specific dashboard history:

```bash
python evaluation/run_eval.py
```
*This script runs all the metrics above and saves a permanent record to the `results/` folder.*

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
