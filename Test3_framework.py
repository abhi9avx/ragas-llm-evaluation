import pytest
import warnings
from ragas import SingleTurnSample
from ragas.metrics.collections import ContextRecall
from utils import get_test_parameters, get_llm_response

warnings.filterwarnings("ignore")

@pytest.mark.asyncio
@pytest.mark.parametrize("getData", get_test_parameters(), indirect=True)
async def test_context_recall(llm_wrapper, getData):
    """Test context recall metric for each query"""
    metric = ContextRecall(llm=llm_wrapper)
    score = await metric.ascore(
        user_input=getData.user_input, 
        retrieved_contexts=getData.retrieved_contexts, 
        reference=getData.reference
    )
    print(f"Context Recall Score: {score}")
    assert score >= 0


@pytest.fixture
def getData(request):
    """Fetch data and create SingleTurnSample"""
    query = request.param["query"]
    reference = request.param["reference"]
    
    response = get_llm_response(query)
    
    return SingleTurnSample(
        user_input=query,
        retrieved_contexts=[doc['page_content'] for doc in response['retrieved_docs']],
        reference=reference
    )
