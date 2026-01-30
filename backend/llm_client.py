import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=API_KEY)

# Use valid model names
EMBEDDING_MODEL = "models/text-embedding-004"
GENERATION_MODEL = "gemini-flash-latest"

def get_embedding(text: str) -> list[float]:
    """Generates embedding for the given text."""
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise

def get_query_embedding(text: str) -> list[float]:
    """Generates embedding for a query."""
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        raise

def generate_answer(query: str, context_chunks: list[str]) -> str:
    """Generates an answer based on context chunks."""
    model = genai.GenerativeModel(GENERATION_MODEL)
    
    context_text = "\n\n".join(context_chunks)
    
    prompt = f"""You are a helpful and creative AI assistant analyzing a document.
    
    Use the provided DOCUMENT EXCERPTS as context to answer the user's QUESTION.
    
    GUIDELINES:
    1. For factual questions, answer strictly based on the excerpts.
    2. For creative or summary requests (e.g. "write a story", "summarize"), use the excerpts as inspiration and source material. You allowed to synthesized a creative response as long as it is grounded in the document's themes.
    3. If the excerpts are completely irrelevant to the question, state "I don't know based on the provided document."

    DOCUMENT EXCERPTS:
    {context_text}
    
    QUESTION:
    {query}
    
    ANSWER:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error generating answer: {e}")
        return f"Sorry, I encountered an error while generating the answer. Details: {str(e)}"
