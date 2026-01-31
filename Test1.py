import os
import pytest
import warnings
# Suppress warnings
warnings.filterwarnings("ignore")

from openai import OpenAI
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithoutReference
from ragas.llms import llm_factory
import requests

# user_input -> query 
# response -> response
# reference -> Ground Truth
# retrieved_context -> Top K retrieved documents

@pytest.mark.asyncio
async def test_context_precision():

    # create object of class for specific metric 
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # power of LLM + method metric -> score 
    client = OpenAI(api_key=apikey)
    llm = llm_factory("gpt-4o", client=client)
    context_precision = LLMContextPrecisionWithoutReference(llm=llm)
    query="How many articles are there in the selenium webdriver python course ?"

    # Feed data
    responseDir = requests.post("https://rahulshettyacademy.com/rag-llm/ask", json = {"question":query,"chat_history":[]} ).json()
    print(responseDir)
    
    sample = SingleTurnSample(
        user_input=query,
        response=responseDir['answer'],
        retrieved_contexts=[doc['page_content'] for doc in responseDir['retrieved_docs']]
    )
    
    # score 
    score = await context_precision.single_turn_ascore(sample)

    print(f"Score: {score}")
    if(score>0.5):
        assert True
    else:
        assert False



# # sample = SingleTurnSample(
#         user_input="How many articles are there in the selenium webdriver python course ?",
#         response="There are 23 articles in the course",
#         retrieved_contexts=[
#             """Complete Understanding on Selenium Python API Methods with real time Scenarios on LIVE Websites
# "Last but not least" you can clear any Interview and can Lead Entire Selenium Python Projects from Design Stage
# This course includes:
# 17.5 hours on-demand video
# Assignments
# 23 articles
# 9 downloadable resources
# Access on mobile and TV
# Certificate of completion
# Requirements""",
            
#             "Cypress -Modern Automation Testing from Scratch + Frameworks.docx",
            
#             """Wish you all the Best! See you all in the course with above topics :)

# Who this course is for:
# Automation Engineers
# Software Engineers
# Manual testers
# Software developers""",
            
#             """What you'll learn
# At the end of this course, You will get complete knowledge on Python Automation using Selenium WebDriver
# You will be able to implement Python Test Automation Frameworks from Scratch with all latest Technlogies
# Complete Understanding of Python Basics with many practise Examples to gain a solid exposure
# You will be learning Python Unit Test Frameworks like PyTest which will helpful for Unit and Integration Testing""",
            
#             """Advanced Selenium User interactions
# End to end Practise Examples to Automate
# PyTest - Unit Testing Framework
# PyTest Fixtures
# PyTest Parameterization
# PyTest Annotations, Command Line Arguments
# Python PyTest Reports
# Log4J Logging Python
# Page object Model Design Pattern
# End to end Framework design from scratch
# Python Data driven Framework using Excel
# Pyxl Examples with Selenium Integration
# Jenkins CI Integration
# GITHUB Version control Management
# All the Best! Happy Testing :)"""
#         ]
#     )
    