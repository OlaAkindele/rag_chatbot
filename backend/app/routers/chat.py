import json
from fastapi import APIRouter
from pydantic import BaseModel
from app.tools.agent import generate_response 
from app.core.config import settings
from app.tools.evaluation import evaluate_rag_model

# create a router instance to collect chat related endpoints
router = APIRouter()

# Defining the request schema for incoming chat messages
class ChatRequest(BaseModel):
    message:    str  
    session_id: str = "default"

# defining the response schema that the endpoint will return
class ChatResponse(BaseModel):
    reply:             str
    retrieval_context: str
    accuracy:          float

@router.post("/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    POST /api/chat/
    Accepts a ChatRequest, invokes the chat agent and evaluation,
    and returns a structured ChatResponse.
    """
    # get the chatbot reply and the retrieval context
    reply, context = generate_response(req.message, req.session_id)

    #  ensuring context is a string
    if not isinstance(context, str):
        context = json.dumps(context, indent=2)

    # run the evaluation (rag_eval)
    accuracy = evaluate_rag_model(req.message, reply, context, model_type="opeanai", model_name=settings.openai_model)

    # return everything
    return ChatResponse(
        reply=reply,
        retrieval_context=context,
        accuracy=accuracy
    )

