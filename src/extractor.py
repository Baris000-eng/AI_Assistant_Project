import os
import json
from groq import Groq
from dotenv import load_dotenv
from src.models import OrderExtractionResult

load_dotenv()

def extract_orders_from_messages(messages: list[str]) -> OrderExtractionResult:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    schema_json = json.dumps(OrderExtractionResult.model_json_schema(), indent=2)

    system_prompt = f"""
    You are an operations assistant for WAXCAT studios in Hamburg, Germany.
    Extract material order items from studio messages and return only the valid JSON data matching the exact schema below.

    JSON Schema:
    {schema_json}

    Rules:
    1. Keep studio names consistent and clean (e.g., 'Innenstadt', 'Eimsbüttel', 'Wandsbek').
    2. Keep product names consistent and clean (e.g., 'Nitrilhandschuhe M', 'Tape', 'Kochsalzlösung').
    3. If a message omits the quantity OR the unit (e.g., "noch Kochsalzlösung"), set quantity=null, unit=null, and is_complete=false.
    4. Do not guess missing quantities.
    5. When is_complete=false, draft a polite, concise German clarification question addressed to that specific studio asking for the exact quantity and unit (mentioning standard units if known from the other orders, e.g., Flaschen).
    """

    user_content = "Process the following studio messages:\n" + "\n".join(f"- {msg}" for msg in messages)

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.0, # set to 0.0 for deterministic material order items extraction 
    )

    raw_json = response.choices[0].message.content
    return OrderExtractionResult.model_validate_json(raw_json)