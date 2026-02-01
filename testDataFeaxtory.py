import os
import pytest
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset import TestsetGenerator
import nltk

# Ensure tokens are set
if not os.getenv("OPENAI_API_KEY"):
    # Fallback to key provided in comments if mostly for local testing, 
    # but strictly we should rely on env vars for security.
    # Leaving strict check to ensure user sets it.
    pass

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

# Setup paths
# User's path: /Users/rahulshetty/documents/fs11/
# Correct local path: /Users/abhinav/Documents/LLMEvaluation/fs11/
base_dir = os.path.dirname(os.path.abspath(__file__))
fs11_path = os.path.join(base_dir, "fs11")

def test_dataGen():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    langchain_llm = LangchainLLMWrapper(llm)
    embed = OpenAIEmbeddings()
    
    loader = DirectoryLoader(
        path=fs11_path,
        glob="**/*.docx",
        loader_cls=UnstructuredWordDocumentLoader
    )
    
    print(f"Loading documents from {fs11_path}...")
    docs = loader.load()
    print(f"Loaded {len(docs)} documents.")
    
    generate_embeddings = LangchainEmbeddingsWrapper(embed)
    generator = TestsetGenerator(llm=langchain_llm, embedding_model=generate_embeddings)
    
    print("Generating testset (size=20)...")
    dataset = generator.generate_with_langchain_docs(docs, testset_size=20)
    
    # Save to file instead of just printing
    output_path = os.path.join(base_dir, "testdata", "generated_testset.json")
    dataset.to_pandas().to_json(output_path, orient="records", indent=4)
    print(f"Testset generated and saved to {output_path}")
    
    # print(dataset.to_list())
    # dataset.upload() # Uncomment if RAGAS_APP_TOKEN is set and upload is desired

if __name__ == "__main__":
    test_dataGen()