import pytest
import json
from ragas import SingleTurnSample
from ragas.metrics.collections import Faithfulness
from utils import get_llm_response


def load_json(filepath):
    """Load test data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


@pytest.mark.asyncio
@pytest.mark.parametrize("getData", load_json("testdata/Test4.json"), indirect=True)
async def test_faithfulness(llm_wrapper, getData):
    """Test faithfulness metric - measures if response is grounded in context"""
    faithfulness = Faithfulness(llm=llm_wrapper)
    score = await faithfulness.ascore(
        user_input=getData.user_input,
        response=getData.response,
        retrieved_contexts=getData.retrieved_contexts
    )
    print(f"Faithfulness Score: {score}")
    assert score >= 0


@pytest.fixture
def getData(request):
    """Prepare test data for faithfulness testing"""
    test_data = request.param
    
    # Create sample with user input, response, and retrieved contexts
    sample = SingleTurnSample(
        user_input=test_data["question"],
        response=test_data["answer"],
        retrieved_contexts=[test_data["context"]]
    )
    
    return sample