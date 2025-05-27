import neo4j

# attempt to import the internal Neo4j Driver class to monkey-patch connectivity checks
try:
    from neo4j._sync.driver import Driver as _Driver
except ImportError:
    _Driver = None

if _Driver:
    _Driver.verify_connectivity = lambda self, *args, **kwargs: None # disable the built-in verify_connectivity call, so it becomes a no-op, to avoids blocking at startup if the database isn't available immediately

# No-op out the schema-refresh in Neo4jGraph
try:
    from langchain_neo4j.graphs.neo4j_graph import Neo4jGraph
    # disable the in-__init__ call to `self.refresh_schema()`
    Neo4jGraph.refresh_schema = lambda self, *args, **kwargs: None
except ImportError:
    pass




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router

# create the FastAPI application instance
app = FastAPI(title="Experimental Database Assistant Chatbot")
# adding CORS middleware so that any frontend can call this API without CORS errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include the chat router under the /api/chat prefix, and all endpoints defined in app/routers/chat.py will live under /api/chat.
app.include_router(chat_router, 
                   prefix="/api/chat", 
                   tags=["chat"])
