import os
import sys
import json
import asyncio
from datetime import datetime
import pandas as pd
from ragas import SingleTurnSample, EvaluationDataset, evaluate
import warnings
# Filter specific deprecation warnings from ragas
warnings.filterwarnings("ignore", category=DeprecationWarning, module="ragas")

from ragas import SingleTurnSample, MultiTurnSample, EvaluationDataset, evaluate
from ragas.messages import HumanMessage, AIMessage
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    AnswerRelevancy,
    FactualCorrectness,
    TopicAdherenceScore
)
from langchain_openai import OpenAIEmbeddings
from ragas.llms import llm_factory
from openai import AsyncOpenAI

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_test_data, get_llm_response

async def main():
    print("🚀 Starting Ragas Evaluation Run...")
    
    # 1. Setup LLM and Embeddings
    apikey = os.getenv("OPENAI_API_KEY")
    if not apikey:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = AsyncOpenAI(api_key=apikey)
    llm_model = llm_factory("gpt-4o", client=client)
    # Use LangChain embeddings for compatibility with old metrics
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=apikey)
    
    # 2. Define Metrics
    # Single Turn Metrics
    metrics = [
        ContextPrecision(llm=llm_model),
        ContextRecall(llm=llm_model),
        Faithfulness(llm=llm_model),
        AnswerRelevancy(llm=llm_model, embeddings=embeddings_model),
        FactualCorrectness(llm=llm_model),
        TopicAdherenceScore(llm=llm_model)
    ]
    
    print(f"Metrics defined: {[type(m) for m in metrics]}")
    # Verify strict instance check if needed, though Ragas check seems to be failing
    from ragas.metrics.base import Metric
    for i, m in enumerate(metrics):
        if not isinstance(m, Metric):
             print(f"⚠️ Metric {i} ({type(m)}) is not an instance of ragas.metrics.base.Metric")

    # 3. Load Data
    print("📂 Loading test data...")
    samples = []

    # Load Single Turn Data (Test5.json)
    try:
        raw_data_5 = load_test_data("Test5.json")
        for item in raw_data_5:
            # Simple single turn processing
            if "answer" not in item:
                 responseDict = get_llm_response(item)
                 item["answer"] = responseDict["answer"]
                 item["retrieved_contexts"] = [doc["page_content"] for doc in responseDict.get("retrieved_docs", [])]
            
            contexts = item.get("retrieved_contexts", [])
            if not contexts and "retrieved_docs" in item:
                 contexts = [doc["page_content"] if isinstance(doc, dict) else doc for doc in item["retrieved_docs"]]
                
            sample = SingleTurnSample(
                user_input=item["question"],
                response=item["answer"],
                retrieved_contexts=contexts,
                reference=item["reference"]
            )
            samples.append(sample)
    except Exception as e:
        print(f"⚠️ Could not load Test5.json: {e}")

    # Load Multi Turn Data (Test6.json)
    try:
        raw_data_6 = load_test_data("Test6.json")
        for item in raw_data_6:
            if "conversation" in item:
                conversation = []
                for msg in item["conversation"]:
                    if msg["role"] == "user":
                        conversation.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        conversation.append(AIMessage(content=msg["content"]))
                
                sample = MultiTurnSample(
                    user_input=conversation,
                    reference_topics=item.get("reference_topics", [])
                )
                samples.append(sample)
    except Exception as e:
        print(f"⚠️ Could not load Test6.json: {e}")
        
    print(f"✅ Loaded {len(samples)} samples.")

    # 4. Run Evaluation
    # Separate samples by type as EvaluationDataset requires homogeneous samples
    single_turn_samples = [s for s in samples if isinstance(s, SingleTurnSample)]
    multi_turn_samples = [s for s in samples if isinstance(s, MultiTurnSample)]

    print(f"⚡ Running Ragas evaluation for {len(single_turn_samples)} single-turn samples...")
    results_single = {}
    if single_turn_samples:
        eval_dataset_single = EvaluationDataset(single_turn_samples)
        # Filter metrics relevant for single turn (TopicAdherenceScore can be both but lets rely on internal checks or strict split)
        # Actually Ragas metrics usually handle their own types or return N/A.
        # But for strictly single turn samples, TopicAdherence might fail if it expects MultiTurnSample inputs.
        # Let's pass all metrics and assume Ragas handles it OR filter if needed.
        # TopicAdherenceScore is MultiTurnMetric, others are SingleTurnMetric.
        # Using all metrics on SingleTurnSample might crash if incompatible.
        # Let's try passing all - if it fails we filter.
        # Update: We know ContextPrecision etc are SingleTurn. TopicAdherence is MultiTurn.
        
        single_turn_metrics = [m for m in metrics if not isinstance(m, TopicAdherenceScore)]
        results_single = evaluate(dataset=eval_dataset_single, metrics=single_turn_metrics)
    
    results_multi = {}
    if multi_turn_samples:
         print(f"⚡ Running Ragas evaluation for {len(multi_turn_samples)} multi-turn samples...")
         eval_dataset_multi = EvaluationDataset(multi_turn_samples)
         # Filter metrics for multi turn
         multi_turn_metrics = [m for m in metrics if isinstance(m, TopicAdherenceScore)]
         results_multi = evaluate(dataset=eval_dataset_multi, metrics=multi_turn_metrics)

    # Merge results
    # Ragas Results object behaves like a dict but also has methods.
    # To combine, we will merge the underlying dictonaries of scores.
    # Note: This simple merge creates a combined summary, but 'results' object functionality might be limited.
    # For reporting we mainly need the scores.
    
    # We will construct a combined Dataframe for details and a combined dict for summary
    
    df_single = results_single.to_pandas() if results_single else pd.DataFrame()
    df_multi = results_multi.to_pandas() if results_multi else pd.DataFrame()
    
    # Align columns
    df = pd.concat([df_single, df_multi], ignore_index=True)
    
    print("✅ Evaluation complete.")
    # print(results) # Can't print unified results object easily without one object
    
    # 5. Save Results
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Save Detailed CSV
    df["run_id"] = timestamp
    csv_path = os.path.join(results_dir, f"{timestamp}_details.csv")
    df.to_csv(csv_path, index=False)
    print(f"💾 Saved detailed results to {csv_path}")
    
    # Save Summary JSON
    # We calculate summary from the full dataframe to average across all samples where metric applies
    summary = df.mean(numeric_only=True).to_dict()
    summary["run_id"] = timestamp
    summary["timestamp"] = datetime.now().isoformat()
    summary["total_samples"] = len(samples)
    
    json_path = os.path.join(results_dir, f"{timestamp}_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"💾 Saved summary to {json_path}")

if __name__ == "__main__":
    asyncio.run(main())
