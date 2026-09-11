import os
import json
import google.generativeai as genai
from typing import Optional
from app.models import VehicleFilter
from app.concepts import CONCEPTS

def init_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    return genai.GenerativeModel(model_name)

def parse_llm(query: str) -> Optional[VehicleFilter]:
    model = init_gemini()
    if not model:
        return None

    # We provide the concept mappings to the LLM so it knows how to resolve fuzzy terms
    concept_str = json.dumps(CONCEPTS, indent=2)

    prompt = f"""
You are a car search parser. Extract search filters from the user's query into the following JSON schema.
If the query contains fuzzy concepts (like "family car" or "fuel efficient"), map them to concrete filter fields using this reference:
{concept_str}

User query: "{query}"

Output ONLY a valid JSON object matching the requested schema. Do not include markdown code blocks.
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=VehicleFilter.model_json_schema()
            ),
            # In a real app we'd use GEMINI_TIMEOUT_SECONDS but genai python client
            # uses transport timeout args which are tricky to set directly via generate_content.
            # We'll rely on the default timeout or handle it at the caller level.
        )
        data = json.loads(response.text)
        return VehicleFilter(**data)
    except Exception as e:
        print(f"LLM parse error: {e}")
        return None
