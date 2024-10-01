import os
import json
from langchain.evaluation import JsonEqualityEvaluator
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from utils import extract_prefilter


LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
LANGCHAIN_ENDPOINT = os.environ.get("LANGCHAIN_ENDPOINT")


def get_feedback(results):

    client = Client(api_url=LANGCHAIN_ENDPOINT, api_key=LANGCHAIN_API_KEY)

    return list(
        client.list_feedback(
            run_ids=[
                r.id for r in client.list_runs(project_name=results.experiment_name)
            ],
            feedback_key="custom_json_evaluator",
        )
    )


def langsmith_app(inputs):
    output = extract_prefilter(inputs["query"])
    return {"output": output}


evaluator = JsonEqualityEvaluator()


def custom_json_evaluator(run: Run, example: Example) -> dict:
    try:
        parsed_json = json.loads(run.outputs["output"])
        example = example.outputs["result"]
        return {"key": "custom_json_evaluator", "score": int(parsed_json == example)}
    except json.JSONDecodeError:
        return {"key": "custom_json_evaluator", "score": 0}
    except:  # pylint: disable=bare-except
        return {"key": "custom_json_evaluator", "score": 0}


def test_json_extract() -> None:
    """Test all json are correctly extracted"""
    experiment_results = evaluate(
        langsmith_app,
        data="JSON-dataset",
        evaluators=[custom_json_evaluator],
    )

    # I didn't forget this print here
    # Is to search the current experiment in langsmith
    print("experiment", experiment_results.experiment_name)

    # Check doc, this will be changed in next releases
    # The server have some delay to log the result
    feedback_results = get_feedback(experiment_results)
    print(feedback_results)
    while len(feedback_results) == 0:
        feedback_results = get_feedback(experiment_results)
        print(feedback_results)

    # All examples must be positive
    all_results_are_true = all(map(lambda row: row.score == 1, feedback_results))
    assert all_results_are_true
