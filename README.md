# Product Description Generator

**Generate intelligent, SEO-optimized product descriptions** by analyzing structured product data and enriching it with contextual knowledge scraped from the internet. Ideal for e-commerce businesses aiming to enhance product discoverability and conversion.

## Overview

This tool uses:

- CSV input of product attributes  
- Web search (DuckDuckGo) for real-world context (e.g., "How good is Intel i5 12th Gen?")  
- LLMs (via Ollama) to generate natural-sounding, benefit-focused descriptions  
- Enhances SEO and user engagement on product listings

## Tech Stack

- **Python**
- **Streamlit** for UI
- **Ollama** (with LLaMA 3.1 model) for LLM-based generation
- **DuckDuckGo Search** via `duckduckgo_search`
- **Pandas**, **CSV**, **Regex**, **JSON**

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure Ollama is installed and the `llama3.1` model is pulled

```bash
ollama pull llama3.1
```

> You must have [Ollama](https://ollama.com/) running locally before using this app.

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

---

## Input CSV Example

Sample CSV

```csv
Category,Brand,Model,GPU,Processor,RAM
Laptop,Dell,XPS 15,NVIDIA RTX 4060,Intel i7 13th Gen,16GB DDR5
```

---

## Example Output

For the above entry, a generated description may look like:

> "Experience stunning performance with the Dell XPS 15, powered by the Intel i7 13th Gen processor and NVIDIA RTX 4060 GPU — perfect for gaming, content creation, and multitasking. With 16GB DDR5 RAM, expect ultra-smooth responsiveness for even the most demanding tasks."

---
