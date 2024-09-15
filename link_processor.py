from gpt_api import generate_with_gpt
from ollama import generate_with_ollama
from cohere_api import generate_with_cohere
import requests
from bs4 import BeautifulSoup
import urllib3
from requests.exceptions import ConnectTimeout, RequestException, HTTPError
from urllib3.exceptions import MaxRetryError
import time


def fetch_and_extract_text(link):
    """
    Fetches the content of the provided link and extracts text using BeautifulSoup.

    :param link: The URL to fetch content from.
    :return: Extracted text or None if an error occurs.
    """
    try:
        response = requests.get(link, verify=False, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        else:
            print(f"Errore durante la richiesta: {response.status_code}")
            return None
    except (HTTPError, ConnectTimeout, MaxRetryError, RequestException) as e:
        print(f"Errore di richiesta al link {link}: {e}")
        return None


def generate_response(prompt, use_ollama, use_cohere, use_gpt, use_ollama_and_gpt,
                      use_cohere_and_gpt, use_both, use_all):
    """
    Generates a response using selected AI models based on the provided flags.

    :param prompt: The text prompt to pass to the AI models.
    :param use_ollama, use_cohere, use_gpt, use_ollama_and_gpt,
           use_cohere_and_gpt, use_both, use_all: Flags indicating which AI models to use.
    :return: A combined response string from the selected models.
    """
    responses = []

    if use_ollama or use_all or use_both or use_ollama_and_gpt:
        response_text_ollama = generate_with_ollama(model="llama3.1", prompt=prompt, options={"temperature": 0.7})
        responses.append(f"Ollama: {response_text_ollama}")

    if use_cohere or use_all or use_both or use_cohere_and_gpt:
        response_text_cohere = generate_with_cohere(prompt=prompt, temperature=0.7)
        responses.append(f"Cohere: {response_text_cohere}")

    if use_gpt or use_all or use_ollama_and_gpt or use_cohere_and_gpt:
        response_text_gpt = generate_with_gpt(prompt=prompt, temperature=0.7)
        responses.append(f"GPT: {response_text_gpt}")

    return "\n".join(responses) if responses else "Nessun modello selezionato."


def process_links(links, query, output_file, x, use_ollama, use_cohere, use_gpt,
                  use_ollama_and_gpt, use_cohere_and_gpt, use_both, use_all):
    """
    Processes the provided links by extracting text and generating responses using selected AI models.

    :param links: List of URLs to process.
    :param query: Search query to extract specific content from the text.
    :param output_file: File to save extracted text.
    :param x: List to collect generated responses.
    :param use_ollama, use_cohere, use_gpt, use_ollama_and_gpt, use_cohere_and_gpt, use_both, use_all: Flags to select AI models.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



    for link in links:
        print(f"Processing link: {link}")
        text = fetch_and_extract_text(link)

        # Write extracted text to the output file immediately after fetching
        if text:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"Link: {link}\n\nTesto:\n{text}\n\n{'='*50}\n\n")

            prompt = (
                f"fai un riassunto molto corto del testo ma esplicativo{text}."
            )

            response_text = generate_response(
                prompt, use_ollama, use_cohere, use_gpt, use_ollama_and_gpt,
                use_cohere_and_gpt, use_both, use_all
            )

            # Append response to the list and write responses to appropriate files
            if response_text:
                print(f"Risposta: {response_text}")
                x.append(response_text)

                with open("model_responses.txt", 'a', encoding='utf-8') as model_f:
                    model_f.write(f"Link: {link}\nRisposta:\n{response_text}\n{'='*50}\n\n")

                with open("model_output_file_no_link.txt", 'a', encoding='utf-8') as no_link_f:
                    no_link_f.write(f"\n{response_text},\n")

    # Reduce responses only if more than one is collected
    if len(x) > 1:
        print("Avvio della riduzione delle risposte finali...")
        X = 20  # Size of response groups to aggregate
        reduced_responses = []

        for i in range(0, len(x), X):
            subset = x[i:i + X]
            aggregated_text = " ".join(subset)
            prompt = f'Estrai "{query}" dal seguente testo: {aggregated_text} Rispondi solo con "{query}" in italiano, separate da virgole.'

            reduced_response = generate_response(
                prompt, use_ollama, use_cohere, use_gpt, use_ollama_and_gpt,
                use_cohere_and_gpt, use_both, use_all
            )

            # Write each reduced response immediately after generation
            if reduced_response:
                reduced_responses.append(reduced_response)

        print("Risultato finale:", reduced_responses)
        return reduced_responses
    else:
        print("Risultato finale:", x)
        return x



# This file contains the core logic for processing the scraped links and generating responses using AI models.
# It includes functions for fetching and extracting text from web pages (fetch_and_extract_text()).
# The generate_response() function coordinates the use of different AI models based on user flags.
# The process_links() function is the main workflow, called by scrape_and_process.py to handle each batch of links.
# It also handles the reduction of responses when multiple results are collected.