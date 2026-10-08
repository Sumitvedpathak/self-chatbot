
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()  # Load environment variables from .env file


client = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=200)

def call_llm(text):
    """Call the LLM with the given text and return the response."""
    response = client.invoke([
        ("system", "You are a helpful voice-chat assistant. Reply concisely and naturally."),
        ("human", text),
    ])
    return response.content
