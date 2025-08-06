from langchain_neo4j import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.tools.llm   import llm, embeddings
from app.tools.graph import graph

# building the RAG prompt once
instructions = (
    "Use the given context to answer the question. "
    "If you don't know the answer, say you don't know. "
    "Context: {context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", instructions),
    ("human", "{input}")
])

# load the Neo4jVector index & retrieval chain
_neo4jvector = None
_rag_retriever = None

def get_rag_retriever():
    global _neo4jvector, _rag_retriever
    if _rag_retriever is None:
        _neo4jvector = Neo4jVector.from_existing_index(
            embeddings,
            graph=graph,
            index_name="emailEmbeddings",
            node_label="Email",
            text_node_property=["content", "subject", "revisionId"],
            embedding_node_property="embedding",
            retrieval_query="""
RETURN
    node.content AS text,
    score,
    {
        subject: e.subject,
        senderId: e.senderId,
        receiverIds: collect(receiver.personId),
        timeReceived: e.timeReceived,
        emailId: e.emailId,
        documentId: e.documentId
    } AS metadata
"""
        )
        qa_chain      = create_stuff_documents_chain(llm, prompt)
        _rag_retriever = create_retrieval_chain(_neo4jvector.as_retriever(), qa_chain)
    return _rag_retriever


def get_database_email(query: str) -> dict:
    resp = get_rag_retriever().invoke({"input": query})
    # DEBUGGING — log the raw dict
    print("🔍 [DEBUG] get_database_email returned:", resp)
    return resp
