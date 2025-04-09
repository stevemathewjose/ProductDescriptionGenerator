import csv
import json
import ollama
from duckduckgo_search import DDGS
from typing import List, Dict, Any
from ollama import generate


def custom_duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results


def process_info(item, search_content):
    # item = search_results["item"]
    # search_content = search_results["search_content"]

    prompt = f"""
    You are an AI assistant specialized in analyzing individual product specifications and extracting key advantages and relevant details of things which benifits a user. Your task is to review the given product specification and provide a concise summary of its benefits and notable features.

    Instructions:
    1. Carefully analyze the provided product specification and any additional information.
    2. Generate a concise product description focusing on key features, pros, technical specifications, unique selling points or special features.
    3. If applicable, explain how these features contribute to improved performance, user experience, or functionality.
    4. Aim for a description of 1-2 sentences that effectively communicates the product's value to potential customers.
    5. Only include information that is explicitly stated in the provided specifications or is a direct, factual inference from that data.
    6. If information about the advantages is missing for the given Product Specification and you are confident in your knowledge about standard features for this type of product, you may include this information, clearly indicating it as a general industry standard.
    7. If you cannot confidently provide information or make inferences, state "Insufficient information Available."
    8. Only provide the concise product description as the response, since we will be using this response directly later.

    Now, analyze the following product specification and create a description based on these guidelines:

    Product Specification: {item}
    Information: {search_content}
    """

    response = generate(model='llama3.1',
                        prompt=prompt,
                        options={
                            'temperature': 0.5
                        },
                        stream=False)
    return response['response']


def process_spec(category, spec_name, spec_value):
    query = "How good is " + category + " " + spec_value + " " + spec_name
    search_result = custom_duckduckgo_search(query)
    all_text = " ".join([result['body'] for result in search_result])
    description = process_info(spec_value, all_text)

    return description


def process_info(item, search_content):
    print("Processing knowledge")

    prompt = f"""
    You are an AI assistant specialized in analyzing individual product specifications and extracting key advantages and relevant details of things which benifits a user. Your task is to review the given product specification and provide a concise summary of its benefits and notable features.

    Instructions:
    1. Carefully analyze the provided product specification and any additional information.
    2. Generate a concise product description focusing on key features, materials, and technical specifications, unique selling points or special features.
    3. If applicable, explain how these features contribute to improved performance, user experience, or functionality.
    4. Aim for a description of 1-2 sentences that effectively communicates the product's value to potential customers.
    5. Only include information that is explicitly stated in the provided specifications or is a direct, factual inference from that data.
    6. If information is missing and you are confident in your knowledge about standard features for this type of product, you may include this information, clearly indicating it as a general industry standard.
    7. If you cannot confidently provide information or make inferences, state "Insufficient information Available."
    8. Only provide the concise product description as the response, since we will be using this response directly later.

    Now, analyze the following product specification and create a description based on these guidelines:

    Specification: {item}
    Information: {search_content}
    """

    response = generate(model='llama3.1',
                        prompt=prompt,
                        options={
                            'temperature': 0.3
                        },
                        stream=False)
    return response['response']


def custom_duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    print("Fetching knowledge")
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
    return results


def load_existing_json(json_file_path: str) -> Dict[str, Any]:
    try:
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}


def generate_json_from_csv(csv_file_path: str, json_file_path: str, ignore_columns: set):
    existing_data = load_existing_json(json_file_path)

    result = existing_data

    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        csv_columns = reader.fieldnames

        if not csv_columns:
            return

        ignore_columns = ignore_columns.intersection(csv_columns)
        for row in reader:
            category = row['Category']

            if category not in result:
                result[category] = {}

            for key, value in row.items():
                if key not in ignore_columns and value and value.lower() != 'none':
                    if key not in result[category]:
                        result[category][key] = {}

                    if value not in result[category][key]:
                        print("Processing: " + value)
                        processed_value = process_spec(category, key, value)
                        result[category][key][value] = processed_value
                    else:
                        existing_description = result[category][key][value]
                        if not existing_description or existing_description.lower() == 'none':
                            print(f"Updating: {value}")
                            processed_value = process_spec(category, key, value)
                            result[category][key][value] = processed_value

    for category in list(result.keys()):
        for key in list(result[category].keys()):
            if key in ignore_columns:
                del result[category][key]
            else:
                for value in list(result[category][key].keys()):
                    if value not in [row.get(key, '') for row in csv.DictReader(open(csv_file_path))]:
                        del result[category][key][value]

        if not result[category]:
            del result[category]

    with open(json_file_path, 'w') as json_file:
        json.dump(result, json_file, indent=4)

