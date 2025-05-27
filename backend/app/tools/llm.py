from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# monkey-patch ChatOpenAI.__init__ to drop any unexpected “proxies” kwarg
_orig_init = ChatOpenAI.__init__
def _init_no_proxies(self, *args, **kwargs):
    kwargs.pop("proxies", None)
    return _orig_init(self, *args, **kwargs)
ChatOpenAI.__init__ = _init_no_proxies


from app.core.config import settings
# instantiate the chat model without client_kwargs
llm = ChatOpenAI(
    openai_api_key=settings.openai_api_key,
    model_name=settings.openai_model,   
    temperature=0.0,
)

# instantiate embeddings normally
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.openai_api_key
)


