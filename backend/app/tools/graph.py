from langchain_neo4j import Neo4jGraph
from app.core.config import settings

# connect to neo4j database
graph = Neo4jGraph(
    url=settings.neo4j_uri,
    username=settings.neo4j_username,
    password=settings.neo4j_password,
)

