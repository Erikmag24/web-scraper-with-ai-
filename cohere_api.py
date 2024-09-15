# cohere_api.py
import cohere
import time
from httpx import RemoteProtocolError
from typing import Optional
from config import COHERE_API_KEY, COHERE_MODEL

def generate_with_cohere(prompt: str, temperature: float = 0.3, retries: int = 3) -> Optional[str]:
    """
    Generate a response using the Cohere API with retry mechanism.

    Args:
        prompt (str): The input prompt for the Cohere model.
        temperature (float): Controls randomness in generation. Default is 0.3.
        retries (int): Number of retry attempts in case of RemoteProtocolError. Default is 3.

    Returns:
        Optional[str]: The generated response, or None if all retries fail.
    """
    co = cohere.Client(COHERE_API_KEY)
    
    for attempt in range(retries):
        try:
            stream = co.chat_stream(
                model=COHERE_MODEL,
                message=prompt,
                temperature=temperature,
                chat_history=[],
                prompt_truncation='AUTO',
                connectors=[{"id": "web-search"}]
            )

            response = "".join(event.text for event in stream if event.event_type == "text-generation")
            return response
        
        except RemoteProtocolError as e:
            print(f"Attempt {attempt + 1} failed with RemoteProtocolError: {e}")
            if attempt < retries - 1:
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("All retry attempts failed.")
                raise  # Re-raise the last exception if all retries fail

    return None  # This line should never be reached due to the raise in the except block



# This file provides an interface to the Cohere API for text generation.
# It includes error handling and retry logic to manage potential API connection issues.
# The main function, generate_with_cohere(), is called by link_processor.py when Cohere AI is requested.
# It's designed to work with streaming responses from the Cohere API for efficient processing of long outputs.