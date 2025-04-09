import pandas as pd
import csv
import ollama
from ollama import generate
from ollama import Options
import json
from typing import Dict, Any, List
import re
import streamlit as st


def load_knowledge_base(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        return json.load(f)


def process_csv(file_path: str) -> List[Dict[str, str]]:
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def get_prompt(category):
    # Load the JSON data
    with open('data/promptExample.json', 'r') as file:
        data = json.load(file)

    if category not in data:
        return None, None

    input_dict = data[category]['input']
    output_str = data[category]['output']

    input_str = json.dumps(input_dict, indent=2)

    return input_str, output_str


def get_kb_context_mod(category: str, specs: Dict[str, str], kb: Dict[str, Any]) -> str:
    context = []
    category_kb = kb.get(category, {})
    for spec, value in specs.items():
        if spec in category_kb:
            spec_info = category_kb[spec]

            if value is not None:
                # Check if the value is in the spec_info (which maps values to descriptions)
                if value in spec_info:
                    description = spec_info[value]
                    context.append(f"\n -> {spec}: {value} - {description}")
                else:
                    # Handle cases where value is not in the spec_info
                    context.append(f"{spec}: {value} - No description available")

    return "\n".join(context)


def get_kb_context(category: str, specs: Dict[str, str], kb: Dict[str, Any]) -> str:
    context = []
    category_kb = kb.get(category, {})

    for spec, value in specs.items():
        if spec in category_kb:
            spec_info = category_kb[spec]

            if "ranges" in spec_info:
                if value is not None:
                    print(value)
                    match = re.search(r'(\d+\.?\d*)\s*([a-zA-Z]*)', value)
                    val = match.group(1)
                    for range_info in spec_info["ranges"]:
                        try:
                            if range_info["min"] <= float(val) <= range_info["max"]:
                                context.append(f"{spec}: {value} - {range_info['description']}")
                                break
                        except ValueError:
                            pass

            elif "types" in spec_info:
                if value is not None:
                    if value in spec_info["types"]:
                        type_info = spec_info["types"][value]
                        context.append(f"{spec}: {value} - {type_info['description']}")

    return "\n".join(context)


def generate_prompt(product_specs, kb: Dict[str, Any]) -> str:
    product_specs = {k: v for k, v in product_specs.items() if v != "None"}

    category = product_specs["Category"]
    kb_context = get_kb_context_mod(category, product_specs, kb)

    input_str, output_str = get_prompt(category)

    prompt = f"""
Please generate a compelling product description for the following {category}:

Product Specifications:
{json.dumps(product_specs, indent=2)}

Additional Product Context:

{kb_context}

Instructions:
1. Based on these specifications and the additional context, please write a compelling product description. 
2. The description should highlight the key features and their benefits,
   and suggest ideal use cases for this product. Please ensure the tone is professional yet appealing to potential customers.
3. Use additional Product context only for for getting key features that benefit the customer.

Only provide product description as response.

Example input:
{input_str}

Example output:
{output_str}
Product Description:
"""
    print(prompt)
    return prompt


def generate_desc(prompt):
    response = generate(model='llama3.1',
                        prompt=prompt,
                        options={
                            'temperature': 0.4
                        },
                        stream=False)
    return response['response']


# @st.cache_resource
def compute(csv_file_path):
    kb_file_path = "./tech_components_dataset.json"
    products = process_csv(csv_file_path)
    knowledge_base = load_knowledge_base(kb_file_path)

    for product in products:
        prompt = generate_prompt(product, knowledge_base)
        product["Product Description"] = generate_desc(prompt)
    products_df = pd.DataFrame(products)
    return products_df
