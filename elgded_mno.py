import os
import tempfile
import base64
import json
from langchain_huggingface import HuggingFaceEndpoint
import streamlit as st
from pdf2image import convert_from_path
from PIL import ImageEnhance
from langchain_openai import ChatOpenAI
import pandas as pd
import re

llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    model="google/gemma-4-26b-a4b-it",
    temperature=0
)


# ------------------ PDF to Images ------------------
def preprocess_image(image, max_width=1000):
    width, height = image.size
    if width > max_width:
        image = image.resize((max_width, int(max_width * height / width)))
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(1.5)

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    return [preprocess_image(img) for img in images]

def encode_image(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

# ------------------ OCR + Dynamic JSON ------------------
def ocr_and_structure(images):
    prompt = """
you are a procurement analyst assistant. 
1. Read the content of the document (from images).
2. Return only JSON file of the products information (products directory) , no extra text or explanation.
3. Extract ALL products and their components (if found) from the document images and make a structured JSON based on the extracted information.

IMPORTANT RULES:
- Do NOT miss any product or component.
- Do NOT hallucinate or generate data.
- Keep all part numbers EXACTLY as written.
- Do Not mix up the product numbers and serial numbers if found.
- Do NOT modify, normalize, or reformat IDs.
- Becareful to the brackets of the JSON file.
- Treat all pages as one document.
Treat all pages as one document.
"""
    content = [{"type": "text", "text": prompt}]
    for img in images:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img)}"}})

    response = llm.invoke([{"role": "user", "content": content}])
    return response.content

# ------------------ Streamlit App ------------------


def extract_products_only(llm_output):
    try:
        cleaned = re.sub(r"```json|```", "", llm_output).strip()

        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if not match:
            print("No valid JSON object found.")
            return []

        json_str = match.group()

        data = json.loads(json_str)

        return data.get("products", [])

    except Exception as e:
        print("Error parsing products:", e)
        return []
    
def main():
    st.title("Dynamic PDF-to-JSON Agent")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file is not None:
        # Save temp PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_file.read())
            temp_pdf_path = temp_pdf.name
            

        # Convert PDF → Images
        images = pdf_to_images(temp_pdf_path)
        st.subheader(" Extracted Images")
        for img in images:
            st.image(img)

        # OCR + Dynamic JSON
        st.subheader(" Extracted & Structured JSON")
        structured_json = ocr_and_structure(images)
        st.text(structured_json)

        # After getting LLM output
        structured_json = ocr_and_structure(images)

# Extract products only
        products_list = extract_products_only(structured_json)

        st.subheader(" Products Only")
        st.write(products_list)  

# Optional: save as JSON or CSV
        with open("products_only.json", "w", encoding="utf-8") as f:
         json.dump(products_list, f, indent=2, ensure_ascii=False)

        df = pd.DataFrame(products_list)
        df.to_csv("products_only.csv", index=False)

        st.download_button("Download Products JSON", data=json.dumps(products_list, indent=2), file_name="products_only.json", mime="application/json")
        st.download_button("Download Products CSV", data=df.to_csv(index=False), file_name="products_only.csv", mime="text/csv")

if __name__ == "__main__":
    main()