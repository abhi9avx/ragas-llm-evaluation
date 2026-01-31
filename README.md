# 🎯 Ragas LLM Evaluation Framework

<div align="center">

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Pytest](https://img.shields.io/badge/pytest-passing-green.svg)
![Ragas](https://img.shields.io/badge/ragas-metrics-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**A comprehensive pytest-based framework for evaluating LLM applications using Ragas metrics**

</div>

---

## 🚀 Quick Start (5 Minutes)

### 1️⃣ Clone & Install
```bash
git clone <your-repo-url>
cd ragas-llm-evaluation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Set Your API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3️⃣ Run Tests
```bash
# Run all tests
pytest -s

# Run specific test (works offline with local data)
pytest -s Test3_framework.py
```

### ✅ Expected Output
```
Test3_framework.py Context Recall Score: MetricResult(value=1.0)
.Context Recall Score: MetricResult(value=1.0)
.

======================================= 2 passed in 6.01s =======================================
```

---

## 🌟 Why Ragas?

**Ragas** (Retrieval Augmented Generation Assessment) is a powerful framework for evaluating RAG (Retrieval-Augmented Generation) pipelines. It provides:

- 📊 **Quantitative Metrics** - Measure the quality of your LLM outputs objectively
- 🎯 **Context Precision** - Evaluate how relevant your retrieved context is
- 🔍 **Context Recall** - Measure if all necessary information was retrieved
- ⚡ **Automated Testing** - Integrate quality checks into your CI/CD pipeline
- 🧪 **Reproducible Results** - Consistent evaluation across different runs

> **Why do we need this?** LLMs are powerful but unpredictable. Ragas helps you ensure your RAG system consistently delivers high-quality, accurate responses by measuring key performance indicators.

---

## ✨ Features

- ✅ **Multiple Ragas Metrics** - Context Precision, Context Recall, Faithfulness, and more
- 🔄 **Parameterized Testing** - Test multiple queries with a single test function
- 📁 **Local Test Data** - Fallback to JSON test data when API is unavailable
- 🔐 **Secure** - API keys managed via environment variables
- 🎨 **Clean Architecture** - Modular design with reusable utilities
- 📊 **Detailed Reporting** - Clear test output with scores
- 🛡️ **Hallucination Detection** - Faithfulness metric catches unsupported claims

---

## 🧪 Test Suite

### 📝 Test 1: Context Precision (Without Reference)

**File:** `Test1.py` | **Status:** ⚠️ Requires Internet

**What it does:**
- Evaluates how precise the retrieved context is for answering a query
- Uses `LLMContextPrecisionWithoutReference` metric
- Doesn't require ground truth answers

**How to run:**
```bash
export OPENAI_API_KEY="your-key-here"
pytest -s Test1.py
```

**Example:**
```python
Query: "How many articles are there in the selenium webdriver python course?"
Retrieved Context: Course documentation with "23 articles" mentioned
Score: Measures if the context is relevant and precise
```

**Why it matters:** Ensures your RAG system retrieves only relevant information, avoiding noise and improving response quality.

---

### 🔍 Test 2: Context Recall (With Reference)

**File:** `Test2.py` | **Status:** ⚠️ Requires Internet

**What it does:**
- Measures if all necessary information from the reference is present in retrieved context
- Uses `ContextRecall` metric
- Requires ground truth reference answer

**How to run:**
```bash
export OPENAI_API_KEY="your-key-here"
pytest -s Test2.py
```

**Example:**
```python
Query: "How many articles are there in the selenium webdriver python course?"
Reference: "23 articles"
Retrieved Context: Course documentation
Score: 1.0 (perfect) if "23 articles" is found in context
```

**Why it matters:** Ensures your RAG system doesn't miss critical information needed to answer the question correctly.

---

### 🎯 Test 3: Parameterized Framework Testing

**File:** `Test3_framework.py` | **Status:** ✅ Works Offline

**What it does:**
- Tests multiple queries using a single test function
- Loads test data from JSON file (`testdata/Test3_framework.json`)
- Falls back to local data if API is unavailable
- Scalable approach for testing many scenarios

**How to run:**
```bash
export OPENAI_API_KEY="your-key-here"
pytest -s Test3_framework.py
```

**Architecture:**
```
Test3_framework.py
    ↓
utils.py (get_test_parameters, get_llm_response)
    ↓
testdata/Test3_framework.json (test queries & expected data)
```

**Example Test Data:**
```json
{
  "How many articles are there?": {
    "answer": "23 articles",
    "retrieved_docs": [...]
  }
}
```

**Why it matters:** 
- **Scalability** - Add new test cases by just updating JSON
- **Maintainability** - Separate test data from test logic
- **Reliability** - Works offline with local test data

---

### ✨ Test 4: Faithfulness Metric

**File:** `Test4.py` | **Status:** ✅ Works with Local Data

**What it does:**
- Measures if the LLM's response is factually grounded in the retrieved context
- Uses `Faithfulness` metric from Ragas
- Detects hallucinations and unsupported claims
- Ensures responses don't make up information

**How to run:**
```bash
export OPENAI_API_KEY="your-key-here"
pytest -s Test4.py
```

**Example:**
```python
Query: "How many articles are there in the selenium webdriver python course?"
Response: "There are 23 articles in the Selenium WebDriver Python course."
Context: "This course includes: 17.5 hours on-demand video, Assignments, 23 articles..."
Score: 1.0 (perfect) - Response is fully supported by context
```

**How Faithfulness Works:**

The Faithfulness metric evaluates whether the LLM's response contains only information that can be verified from the retrieved context. Here's the process:

1. **Statement Extraction**: Breaks down the response into individual claims/statements
2. **Verification**: Checks each statement against the retrieved context
3. **Scoring**: Calculates the ratio of supported statements to total statements

**Score Interpretation:**
- **1.0** = Perfect faithfulness - All statements are grounded in context
- **0.8-0.9** = High faithfulness - Most statements supported, minor issues
- **0.5-0.7** = Moderate faithfulness - Some hallucinations present
- **< 0.5** = Low faithfulness - Significant hallucinations or unsupported claims

**Why it matters:**
- **Prevents Hallucinations** - Catches when LLM makes up information
- **Builds Trust** - Ensures responses are factually grounded
- **Quality Assurance** - Validates RAG system reliability
- **Production Safety** - Critical for customer-facing applications

**Real-World Example:**

❌ **Bad (Low Faithfulness):**
```
Context: "Course includes 23 articles"
Response: "The course has 23 articles and was created in 2020 by John Doe"
Score: 0.33 (only 1 of 3 claims supported)
```

✅ **Good (High Faithfulness):**
```
Context: "Course includes 23 articles"
Response: "There are 23 articles in this course"
Score: 1.0 (all claims supported)
```

---

## 📊 Understanding the Metrics

### Context Precision
> **Question:** Is the retrieved context relevant?

- **Score Range:** 0.0 to 1.0
- **Higher is Better:** 1.0 = perfectly relevant context
- **Use Case:** Reduce noise in RAG responses

### Context Recall
> **Question:** Did we retrieve all necessary information?

- **Score Range:** 0.0 to 1.0
- **Higher is Better:** 1.0 = all required info retrieved
- **Use Case:** Ensure completeness of retrieved context

### Faithfulness
> **Question:** Is the response grounded in the retrieved context?

- **Score Range:** 0.0 to 1.0
- **Higher is Better:** 1.0 = no hallucinations, fully grounded
- **Use Case:** Prevent LLM from making up information

---

## 🏗️ Project Structure

```
ragas-llm-evaluation/
├── Test1.py                    # Context Precision test
├── Test2.py                    # Context Recall test
├── Test3_framework.py          # Parameterized framework test
├── Test4.py                    # Faithfulness test
├── conftest.py                 # Pytest fixtures (LLM wrapper)
├── utils.py                    # Utility functions
├── testdata/
│   ├── Test3_framework.json    # Test data for framework tests
│   └── Test4.json              # Test data for faithfulness test
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── run_tests.sh                # Test runner script
```

---

## ⚙️ How to Run Tests

### Method 1: Export API Key (Recommended)
```bash
# Set API key for current session
export OPENAI_API_KEY="sk-your-key-here"

# Run tests
pytest -s Test3_framework.py
```

### Method 2: Inline (Single Command)
```bash
# Run with API key in same command
OPENAI_API_KEY="sk-your-key" pytest -s Test3_framework.py
```

### Method 3: Permanent Setup
Add to `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export OPENAI_API_KEY="sk-your-key"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🔧 Configuration

### conftest.py
Contains shared pytest fixtures:
- `llm_wrapper`: Creates AsyncOpenAI client with GPT-4o

### utils.py
Utility functions:
- `load_test_data()`: Load test data from JSON
- `get_test_parameters()`: Convert test data to pytest format
- `get_llm_response()`: Fetch from API or local data

---

## 📦 Dependencies

```
pytest>=9.0.2
pytest-asyncio>=1.3.0
ragas>=0.4.3
openai>=1.109.1
requests>=2.32.5
langchain>=0.2.16
langchain-openai>=0.1.23
```

---

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY environment variable not set"
**Solution:** Export your API key
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Error: "Connection Error" (Test1.py, Test2.py)
**Solution:** These tests require internet connection to fetch live data. Use Test3 for offline testing.

### Error: "No module named 'ragas'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Add New Metrics** - Implement additional Ragas metrics
2. **Improve Test Coverage** - Add more test scenarios
3. **Documentation** - Enhance examples and explanations
4. **Bug Fixes** - Report and fix issues

### Adding a New Metric

1. Create a new test file (e.g., `Test4_faithfulness.py`)
2. Import the metric from `ragas.metrics.collections`
3. Add test data to `testdata/` if needed
4. Update this README

---

## 📝 License

MIT License - feel free to use this project for learning and production!

---

## 🙏 Acknowledgments

- [Ragas](https://github.com/explodinggradients/ragas) - For the amazing evaluation framework
- [OpenAI](https://openai.com/) - For GPT models
- [Pytest](https://pytest.org/) - For the testing framework

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [Abhinav](https://github.com/abhi9avx) for the LLM community

</div>
