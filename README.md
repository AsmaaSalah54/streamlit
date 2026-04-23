# OCR to Structured Data Pipeline

This project extracts text from images using OCR and converts it into structured JSON using a Large Language Model. It is designed as a simple, modular pipeline that transforms unstructured visual data into clean, usable formats.

## Overview

The pipeline processes input images, extracts raw text, and then uses an LLM to organize that text into a structured JSON format. It is suitable for use cases such as document processing, form extraction, and data digitization.

## Features

* Image to text extraction using OCR
* Structuring raw text into JSON using LLMs (Qwen via OpenRouter)
* Modular and extensible pipeline
* Support for large inputs through chunking
* Environment-based configuration for API keys

## Architecture

Images → OCR → Raw Text → LLM → Structured JSON

## Tech Stack

* Python
* LangChain
* OpenRouter (Qwen models)
* OCR tools (Tesseract or PaddleOCR)
* python-dotenv

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory and add:

```env
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

Run the main script:

```bash
python main.py
```

Or call the core function directly:

```python
structured_json = ocr_and_structure(images)
print(structured_json)
```

## Project Structure

```
.
├── main.py
├── pipeline.py
├── utils/
├── images/
├── requirements.txt
└── README.md
```

## Notes

* Large inputs are split into smaller chunks to avoid token and context limits.
* Make sure your API key has sufficient credits.
* Adjust `max_tokens` based on your expected output size.

## Future Work

* Add a simple UI (e.g., Streamlit)
* Extend support to PDF inputs
* Improve multilingual OCR support
* Add support for multiple LLM providers

## Author

Asmaa Salah

## License

This project is licensed under the MIT License.
