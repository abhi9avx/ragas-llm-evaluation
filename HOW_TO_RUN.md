# 🚀 How to Run the Ragas LLM Evaluation Platform

This guide covers everything from setting up the environment to running specific tests, generating synthetic data, and monitoring quality via the dashboard.

## 1️⃣ Setup & Installation

**Prerequisites:** Python 3.10+

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abhi9avx/ragas-llm-evaluation.git
    cd ragas-llm-evaluation
    ```
2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set Environment Variables:**
    Create a `.env` file or export directly:
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```

---

## 2️⃣ Running Tests

You can run tests individually or as a full suite.

### 🏃 Run All Tests (Recommended)
This runs the full evaluation pipeline and saves results for the dashboard.
```bash
python evaluation/run_eval.py
```

### 🔬 Run Individual Metrics
| Metric | Command | Description |
| :--- | :--- | :--- |
| **Context Precision** | `pytest Test1.py` | Measures signal-to-noise ratio in retrieved docs. |
| **Context Recall** | `pytest Test2.py` | Checks if retrieved docs contain the ground truth. |
| **Framework Test** | `pytest Test3_framework.py` | Parameterized tests for the Ragas framework. |
| **Faithfulness** | `pytest Test4.py` | Ensures answers are derived *only* from context. |
| **Answer Relevance** | `pytest Test5.py` | Checks if the answer addresses the user's query. |
| **Topic Adherence** | `pytest Test6.py` | (Multi-Turn) Ensures the bot stays on topic. |

---

## 3️⃣ 🧬 Generating Synthetic Test Data

Don't have enough test cases? Use our generator to create them from your documents.

### Option A: From the Dashboard (Easiest)
1.  Launch the dashboard (see below).
2.  Open the **"Tools"** section in the sidebar.
3.  Click **"Generate Synthetic Data"**.
4.  Select the number of samples and click **Start**.

### Option B: From Command Line
Ingest documents from the `fs11/` directory and generate a test set.
```bash
# Generate 10 new test samples
python testDataFeaxtory.py 10
```
Output is saved to `testdata/generated_testset.json`.

---

## 4️⃣ 📊 Launching the Dashboard

Visualize your test results, track trends, and compare model performance.

```bash
streamlit run dashboard/app.py
```

**Features:**
*   **Overview:** High-level pass rates and latest run stats.
*   **Trends:** Track how your metrics (Faithfulness, Precision, etc.) improve or regress over time.
*   **Deep Dive:** Inspect individual failures (User Input vs Response).
*   **Comparison:** Compare two evaluation runs side-by-side.

---

## 📂 Project Structure Map

*   `evaluation/run_eval.py`: **Main Entry Point**. Runs evaluations and saves history.
*   `dashboard/app.py`: Code for the Streamlit dashboard.
*   `testDataFeaxtory.py`: Script for generating synthetic data.
*   `TestX.py`: Individual unit tests for specific Ragas metrics.
*   `results/`: Stores JSON/CSV reports of every run.
