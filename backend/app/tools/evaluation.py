from typing import Union
import json
from app.core.config import settings
from rag_evaluation.evaluator import evaluate_response # for rag evaluation (rag_eval)

def evaluate_rag_model(
    query: str,
    response: str,
    source_document: Union[str, dict],
    model_type: str,
    model_name: str,
) -> float:
    """
    Uses rag_evaluation.evaluator to get a Dataframe of scores,
    then extracts the Overall Accuracy (percentage), converts to 0–1 float.
    """
    # gpt_evaluation.evaluator wants a plain text document
    if isinstance(source_document, dict):
        # if context pass as dict, jsonify or join:
        doc_text = json.dumps(source_document, indent=2)
    else:
        doc_text = source_document

    # call the rag_evaluation, default model comes from the settings
    df = evaluate_response(
        query,
        response,
        doc_text,
        model_type= "openai",
        model_name=settings.openai_model,
    )
    # df has columns: Metric, Score (Normalized), Score (%)
    # get the last row “Overall Accuracy”
    overall_pct = float(df.loc[df["Metric"] == "Overall Accuracy", "Score (%)"].iloc[0])
    print("EVAL DF:", df)
    print("Overall Accuracy:", overall_pct)
    # convert to 0–1
    return overall_pct / 100.0
