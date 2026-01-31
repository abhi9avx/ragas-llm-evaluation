import os
import pytest
import warnings
from ragas import SingleTurnSample
from ragas.metrics.collections import ContextRecall
from ragas.llms import llm_factory
from openai import AsyncOpenAI
import requests

@pytest.fixture
def llm_wrapper():
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=apikey)
    llm = llm_factory("gpt-4o", client=client)
    return llm


@pytest.fixture
def embedding_wrapper():
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=apikey)
    # Import locally to avoid top-level deprecated import warnings if possible, 
    # or just use the one from ragas.embeddings.base
    from ragas.embeddings import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=client)
    return embeddings
    

