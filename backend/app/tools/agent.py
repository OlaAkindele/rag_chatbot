import logging
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_neo4j import Neo4jChatMessageHistory

from app.tools.cypher import run_cypher
from app.tools.vector import get_database_email
from app.tools.llm import llm
from app.tools.graph import graph
from app.tools.cypher import run_cypher, get_cypher_chain, answer_chain



# Fallback chat chain
system_instructions = """
You are a database expert providing information about an email database.
Use only the provided context to answer. If you don't know, say you don't know.
Always include relevant IDs and dates for reference.
"""
fallback_prompt = ChatPromptTemplate.from_messages([
    ("system", system_instructions),
    ("human", "{input}"),
])
fallback_chat = fallback_prompt | llm | StrOutputParser()


# Tool wrappers that unwrap all possible output keys
def cypher_tool(question: str) -> str:
    """
    Translates question => Cypher => runs it => returns the textual result.
    Handles both {'output':...} and {'result':...} dicts.
    """
    resp = run_cypher(question)
    if isinstance(resp, dict):
        # GraphCypherQAChain sometimes returns {'query':..., 'result':...}
        if "output" in resp:
            return resp["output"]
        if "result" in resp:
            return resp["result"]
    # fallback to string
    return str(resp)

# vector search for retriever
def vector_tool(question: str) -> str:
    """
    Runs your RAG retriever, and returns:
      1) the plain text answer
      2) a human-readable dump of the metadata dict
    so that the agent sees both when it does Observation: …
    """
    resp = get_database_email(question)
    if isinstance(resp, dict):
        # unwrap the actual answer
        answer = (
            resp.get("output")
            or resp.get("result")
            or resp.get("answer")
            or ""
        )
        meta = resp.get("metadata", {})
        # build a little "Metadata: key1=…; key2=…" tail
        meta_str = "; ".join(f"{k}={v}" for k, v in meta.items())
        if meta_str:
            return f"{answer}\n\nMetadata: {meta_str}"
        return answer

    # fallback
    return str(resp)


# Register tools
tools = [
    Tool.from_function(
        name="Email database information",
        description="Translate question into Cypher and run it against the email schema",
        func=cypher_tool,
    ),
    Tool.from_function(
        name="Email Database Search",
        description="Semantic search over email content",
        func=vector_tool,
    ),
    Tool.from_function(
        name="General Chat",
        description="Fallback chat when no other tool applies",
        func=fallback_chat.invoke,
    ),
]


# 4) Conversation memory (Neo4j-backed)

def get_memory(session_id: str):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# React prompt with exact Thought/Action/…/Final Answer 
agent_prompt = PromptTemplate.from_template("""
You are a database expert providing information about an email database.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to the email database, sender, or receiver.
Always include relevant IDs and dates provided in the context for reference.
Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.

TOOLS:
------
You have access to the following tools:
{tools}

Context:
{context}

To use a tool, please use the following format:
Thought: Do I need to use a tool? Yes
Action: one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

Tool usage rules:
1. Always try "Email database information" first.
2. If that yields no result, use "Email Database Search".
3. Use "General Chat" only if neither tool helps.

When you have the final answer (or decide no tool is needed), use:
Thought: Do I need to use a tool? No
Final Answer: [your response here]

Conversation history:
{chat_history}

New question: {input}
{agent_scratchpad}
""")


# Wire up the ReAct agent + executor + history wrapper
react_agent = create_react_agent(llm, tools, agent_prompt)

agent_executor = AgentExecutor(
    agent=react_agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5,  
)

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)


# generating response
def generate_response(user_input: str, session_id: str = "default"):
    """
    1) Run the GraphCypherQAChain in verbose mode to log Generated Cypher + Full Context (raw records).
    2) Summarize those raw records into `context` via answer_chain (or fall back to vector).
    3) Invoke the ReAct agent with that context so you get Thought/Action/Observation/Final Answer logs.
    Returns: (final_bot_reply, context)
    """

    # Raw Cypher for FULL CONTEXT logging
    cypher_chain = get_cypher_chain()
    raw_resp = cypher_chain.invoke({"query": user_input})
    # raw_resp is a dict with "result": [ {record}, … ]
    raw_records = raw_resp.get("result", []) if isinstance(raw_resp, dict) else []
    # Print full context:
    print(f"Full Context: {raw_records}")

    # Turn raw_records into a summary strin
    if raw_records:
        # use second LLMChain that we wired up as 'answer_chain'
        summary = answer_chain.run(
            query=user_input,
            results=raw_records,
            question=user_input,
        )
    else:
        # no cypher hits, then fall back to your RAG retriever
        vec = get_database_email(user_input)
        if isinstance(vec, dict):
            summary = vec.get("output") or vec.get("result") or vec.get("answer") or ""
        else:
            summary = str(vec)

    context = summary

    # Finally invoke the React agent
    out = chat_agent.invoke(
        {"input": user_input, "context": context},
        {"configurable": {"session_id": session_id}}
    )

    # out["output"] is the agent’s Final Answer
    return out["output"], context
