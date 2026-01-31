import os
import pytest
import warnings
from ragas import SingleTurnSample
from ragas.metrics import ContextRecall
from ragas.llms import llm_factory
from openai import OpenAI
import requests

# Suppress warnings
warnings.filterwarnings("ignore")

@pytest.mark.asyncio
async def test_context_recall():
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=apikey)
    llm = llm_factory("gpt-4o", client=client)
    
    # Correctly initialize the metric
    context_recall_metric = ContextRecall(llm=llm)
    
    query="How many articles are there in the selenium webdriver python course ?"


    # Feed data
    responseDir = requests.post("https://rahulshettyacademy.com/rag-llm/ask", json = {"question":query,"chat_history":[]} ).json()
    print(responseDir)
    
    # Context recall needs: user_input, retrieved_contexts, and reference (ground truth)
    sample = SingleTurnSample(
        user_input=query,
        retrieved_contexts=[doc['page_content'] for doc in responseDir['retrieved_docs']],
        reference="23 articles" # Using a more descriptive reference based on the expected answer
    )

    context_recall_score = await context_recall_metric.single_turn_ascore(sample)
    print(f"Context Recall Score: {context_recall_score}")
    
    # Assert score is good (1.0 expected for perfect retrieval)
    assert context_recall_score > 0.5