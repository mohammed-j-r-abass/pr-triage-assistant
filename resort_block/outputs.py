from dotenv import load_dotenv
import os
import httpx
import asyncio
from prompt_assembler import final_prompt
from pr_retriever import get_prs
from prompts import system_prompt

load_dotenv()

# Load API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Check if keys are loaded --> this helps to debug errors very fast
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env file")
if not MISTRAL_API_KEY:
    print("WARNING: MISTRAL_API_KEY not found in .env file")
if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not found in .env file")

# ============================================
# Endpoints
# ============================================
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ============================================
# Headers
# ============================================
GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

MISTRAL_HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# ============================================
# API Call Functions
# ============================================
def call_groq(prompt):
    """Call Groq API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                GROQ_URL,
                headers=GROQ_HEADERS,
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"Groq error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Groq error: {e}")
        return None

def call_mistral(prompt):
    """Call Mistral API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                MISTRAL_URL,
                headers=MISTRAL_HEADERS,
                json={
                    "model": "mistral-small-2603",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
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
    """Call OpenRouter API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                OPENROUTER_URL,
                headers=OPENROUTER_HEADERS,
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"OpenRouter error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"OpenRouter error: {e}")
        return None

# ============================================
# OUTPUT GENERATOR
# ============================================
async def generate_with_rag(user_name, repo_name):
    prs = await get_prs(user_name, repo_name)
    prompt = final_prompt(system_prompt, prs)

    results = await asyncio.gather(
        asyncio.to_thread(call_groq, prompt),
        asyncio.to_thread(call_mistral, prompt),
        asyncio.to_thread(call_openrouter, prompt)
    )
    
    return {
        "groq": results[0],
        "mistral": results[1],
        "openrouter": results[2],
    }

result = asyncio.run(generate_with_rag("mohammed-j-r-abass", "carepoint.github.io"))
print(result)