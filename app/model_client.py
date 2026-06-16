from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import asyncio
from groq import Groq
from prompts import build_review_prompt

# Load API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Check if keys are loaded (optional debug)
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env file")
if not MISTRAL_API_KEY:
    print("WARNING: MISTRAL_API_KEY not found in .env file")
if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not found in .env file")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Mistral AI endpoint and headers
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# OpenRouter endpoint and headers
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

def call_groq(prompt):
    """Call Groq API and return the response."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def call_mistral(prompt):
    """Call Mistral AI API and return the response."""
    try:
        with httpx.Client() as client:
            response = client.post(
                MISTRAL_URL,
                headers=MISTRAL_HEADERS,
                json={
                    "model": "mistral-small-2603",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60.0
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Mistral error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Mistral error: {e}")
        return None

def call_openrouter(prompt):
    """Call OpenRouter API and return the response."""
    try:
        with httpx.Client() as client:
            response = client.post(
                OPENROUTER_URL,
                headers=OPENROUTER_HEADERS,
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60.0
            )
            if response.status_code == 200:
                data = response.json()
                # Debug: print the structure
                print(f"OpenRouter response keys: {data.keys()}")
                return data["choices"][0]["message"]["content"]
            else:
                print(f"OpenRouter error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return None
    
async def call_all_models(diff_text, file_name="unknown"):
    """
    Call all three models in parallel with the review prompt.
    
    Args:
        diff_text (str): The git diff or code to review
        file_name (str): The file being reviewed
    
    Returns:
        dict: Responses from all three models
    """
    # Build the prompt
    prompt = build_review_prompt(diff_text, file_name)
    
    # Run all three calls in parallel
    results = await asyncio.gather(
        asyncio.to_thread(call_groq, prompt),
        asyncio.to_thread(call_mistral, prompt),
        asyncio.to_thread(call_openrouter, prompt)
    )
    
    return {
        "groq": results[0],
        "mistral": results[1],
        "openrouter": results[2],
        "prompt": prompt
    }