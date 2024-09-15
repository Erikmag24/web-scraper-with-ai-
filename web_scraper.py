from typing import Dict, List, Optional
from search_engines import get_search_results
from get_google_search_links import get_google_search_links
from file_processor import process_file
from ollama import generate_with_ollama
from cohere_api import generate_with_cohere
from gpt_api import generate_with_gpt
from bs4 import BeautifulSoup
import requests
from link_processor import process_links
def scrape_and_process(
    query: str,
    translations: Dict[str, str],
    chrome_driver_path: str,
    numero_pagine: int = 1,
    use_ollama: bool = True,
    use_cohere: bool = False,
    use_gpt: bool = False,
    use_ollama_and_gpt: bool = False,
    use_cohere_and_gpt: bool = False,
    use_both: bool = False,
    use_all: bool = False,
    search_engines: Optional[List[str]] = None,
    process_file_path: Optional[str] = None
) -> List[str]:
    output_files = {
        "scraped_texts": "scraped_texts.txt",
        "model_responses": "model_responses.txt",
        "model_output_no_link": "model_output_file_no_link.txt"
    }

    # Initialize output files
    for file_path in output_files.values():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("")

    results = []

    if process_file_path:
        # Process file instead of web scraping
        print(f"Processing file: {process_file_path}")
        process_file(process_file_path, query, output_files["scraped_texts"], use_ollama, use_cohere, use_gpt,
                     use_ollama_and_gpt, use_cohere_and_gpt, use_both, use_all)
    else:
        # Perform web scraping
        for language, translation in translations.items():
            print(f"{language.title()}: {translation}")

            if search_engines:
                for search_engine in search_engines:
                    print(f"Searching on {search_engine}...")
                    links = get_search_results(translation, search_engine, chrome_driver_path, numero_pagine)
                    process_links(links, query, output_files["scraped_texts"], results, use_ollama, use_cohere, use_gpt,
                                  use_ollama_and_gpt, use_cohere_and_gpt, use_both, use_all)
            else:
                # Use Google as fallback if no search engine is specified
                links = get_google_search_links(translation, chrome_driver_path, numero_pagine)
                process_links(links, query, output_files["scraped_texts"], results, use_ollama, use_cohere, use_gpt,
                              use_ollama_and_gpt, use_cohere_and_gpt, use_both, use_all)

    # Final output of responses
    print("Final result:", results)
    return results

