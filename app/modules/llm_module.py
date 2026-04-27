# LLM Module
import google.generativeai as genai
import json
from app.config.settings import GEMINI_API_KEY, LLM_MODEL, CHUNK_SIZE, OVERLAP, QA_PER_CHUNK, CHUNK_TOKEN_THRESHOLD
from app.modules.vector_db_module import chunk_text

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(LLM_MODEL)

def generate_qa(text):
    # If text is longer than a chunk, generate Q&A per chunk.
    if len(text) > CHUNK_SIZE:
        chunks = chunk_text(text)
    else:
        chunks = [text]

    structured_qa = []
    for idx, chunk in enumerate(chunks):
        qa_list = generate_qa_for_chunk(chunk)
        structured_qa.append({
            "chunk_index": idx,
            "chunk_text": chunk,
            "qas": qa_list
        })
    return structured_qa

def generate_qa_for_chunk(chunk):
    prompt = f"""Generate {QA_PER_CHUNK} multiple choice questions from the following text. Return as JSON array of objects, each with 'question', 'options' (array of 4 strings), 'answer' (the correct option text).

Text: {chunk}

Example: [{{"question": "What is...", "options": ["A", "B", "C", "D"], "answer": "A"}}]
"""
    response = model.generate_content(prompt)
    try:
        qa_list = json.loads(response.text.strip('```json\n').strip('```'))
        return qa_list
    except:
        return []