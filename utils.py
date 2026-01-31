import requests
import json
import os


def load_test_data(file_name="Test3_framework.json"):
    """Load test data from JSON file"""
    path = os.path.join(os.path.dirname(__file__), 'testdata', file_name)
    with open(path, 'r') as f:
        return json.load(f)


def get_test_parameters():
    """Convert test data to pytest parameters format"""
    test_data = load_test_data()
    return [{"query": query, "reference": data["answer"]} for query, data in test_data.items()]


def get_llm_response(query):
    """Get response from API or local test data"""
    if isinstance(query, dict):
        query = query["question"]
        
    try:
        response = requests.post(
            "https://rahulshettyacademy.com/rag-llm/ask", 
            json={"question": query, "chat_history": []},
            timeout=5
        )
        if response.status_code != 200:
            raise ValueError(f"API returned status code {response.status_code}")
            
        return response.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, ValueError):
        # Use local test data if API unavailable
        test_data = load_test_data()
        if query in test_data:
            return test_data[query]
        raise ValueError(f"Query not found: {query}")