import logging
from neo4j.exceptions import CypherSyntaxError
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from app.tools.llm import llm
from app.tools.graph import graph


# prompt template for generating cypher queries
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer tasked with translating user questions into Cypher queries to retrieve relevant information from an email database.

Guidelines:
1. Convert the user's question based on the provided schema.
2. Use only the relationship types and properties specified in the schema.
3. Do not use any relationship types or properties not included in the schema.
4. Do not return entire nodes or embedding properties.
5. Always return the 'emailId' and 'timeReceived' properties of the Email node for reference, along with any other properties necessary to answer the question.

Example of Cypher Statements:

1. To find who sent an email:
```
MATCH (sender:Person)-[:SENT]->(e:Email)
WHERE e.emailId = 12452948
RETURN sender, e.emailId, e.revisionId, e.timeReceived, e.content
```

2. To find who received an email:
```
MATCH (receiver:Person)-[:RECEIVED]->(e:Email)
WHERE e.emailId = 12452948
RETURN receiver, e.emailId, e.revisionId, e.timeReceived, e.content
```

3. To find all emails where the sender and receiver are specified:
```
MATCH (sender:Person)-[:SENT]->(e:Email)<-[:RECEIVED]-(receiver:Person)
WHERE e.emailId = 12452948
RETURN sender, e.emailId, receiver, e.revisionId, e.timeReceived, e.content
```

4. To find email person where the subject or email content is specified:
```
MATCH (sender:Person)-[:SENT]->(e:Email)
WHERE toLower(e.subject) CONTAINS toLower('pull tester training')
    OR toLower(e.content) CONTAINS toLower('pull tester training')
RETURN sender, e.emailId, e.revisionId, e.timeReceived, e.content
```

5. To find emails based on their subject or content:
```
MATCH (e:Email)
WHERE toLower(e.subject) CONTAINS toLower('Stevenage Turnback Project')
   OR toLower(e.content) CONTAINS toLower('Stevenage Turnback Project')
RETURN e.emailId, e.revisionId, e.timeReceived, e.senderName, e.subject, e.content 

```

6. To find emails based on a person's name and a specified subject:
```
MATCH (sender:Person)-[:SENT]->(e:Email)
WHERE toLower(sender.email) CONTAINS toLower('Amy Holt')
    AND (toLower(e.subject) CONTAINS toLower('Stevenage Contract')
         OR toLower(e.content) CONTAINS toLower('Stevenage Contract'))
RETURN sender, e.emailId, e.revisionId, e.timeReceived, e.content

```


Schema:
{schema}

Question:
{question}

Cypher Query:
"""

cypher_prompt = ChatPromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

# Build the raw‐results chain (return_direct=True => we get a list of dicts)
_cypher_chain: GraphCypherQAChain | None = None

def get_cypher_chain() -> GraphCypherQAChain:
    global _cypher_chain
    if _cypher_chain is None:
        _cypher_chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            cypher_prompt=cypher_prompt,
            return_direct=True,            
            verbose=True,
            allow_dangerous_requests=True,
        )
    return _cypher_chain

# answer backup prompt, same as before to ensure metadata like IDs are not omited
ANSWER_PROMPT_TEMPLATE = """
You ran this Cypher query:

{query}

It returned these raw records:
{results}

User’s original question:
{question}

You are a database expert providing information about an email database.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to the email database, sender, or receiver.
Always include relevant IDs and dates provided in the context for reference.
Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.




Do not simply dump the full content, just weave the metadata like IDs and timestamps in your answer.


Final Answer:
"""
answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
answer_chain  = LLMChain(llm=llm, prompt=answer_prompt)

# run_cypher(), get raw records, ask the LLM to to give response
def run_cypher(query: str) -> dict:
    """
    1) Generate & execute a Cypher query (raw records returned).
    2) Feed those records into a second LLMChain that:
       - give response based on the content
       - include email's emailId, timeReceived etc cleanly.
    """
    print (query)
    chain = get_cypher_chain()
    try:
        # step 1: run the query
        resp    = chain.invoke({"query": query})
        records = resp.get("result") or []

        # step 2: craft the narrative + metadata
        answer = answer_chain.run(
            query=query,
            results=records,
            question=query,
        )

        return {"output": answer}

    except CypherSyntaxError:
        return {"output": ""}  # fallback to vector if Cypher fails
    except Exception as e:
        logging.warning(f"run_cypher unexpected error: {e}")
        return {"output": ""}