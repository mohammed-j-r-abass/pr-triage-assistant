from dotenv import load_dotenv
import os
import httpx
import asyncio
from prompt_assembler import final_prompt
from pr_retriever import get_prs
from prompts import system_prompt
from consensus_prompt import consensus_model_prompt
from build_consensus_prompt import final_c_prompt

load_dotenv()

# Load API keys from environment
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Check if keys are loaded --> this helps to debug errors very fast
if not MISTRAL_API_KEY:
    print("WARNING: MISTRAL_API_KEY not found in .env file")

# ============================================
# Endpoints
# ============================================
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

# ============================================
# Headers
# ============================================
MISTRAL_HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# ============================================
# API Call Functions
# ============================================
def call_mistral_one(prompt):
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
                print(f"Groq error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Mistral error: {e}")
        return None

def call_mistral_two(prompt):
    """Call Mistral API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                MISTRAL_URL,
                headers=MISTRAL_HEADERS,
                json={
                    "model": "mistral-medium-3-5",
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

def call_mistral_three(prompt):
    """Call Mistral API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                MISTRAL_URL,
                headers=MISTRAL_HEADERS,
                json={
                    "model": "mistral-large-2512",
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

def call_consensus_model(consensus_model_prompt):
    """Call Mistral API using httpx."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                MISTRAL_URL,
                headers=MISTRAL_HEADERS,
                json={
                    "model": "mistral-large-2512",
                    "messages": [{"role": "user", "content": consensus_model_prompt}],
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

# ============================================
# OUTPUT GENERATOR
# ============================================
async def generate_with_rag(user_name, repo_name):
    # Step 1: Fetch PR data
    prs = await get_prs(user_name, repo_name)
    
    # Step 2: Build the user prompt
    user_prompt = final_prompt(system_prompt, prs)
    
    # Step 3: Run all three models in parallel
    results = await asyncio.gather(
                                    asyncio.to_thread(call_mistral_one, user_prompt),
                                    asyncio.to_thread(call_mistral_two, user_prompt),
                                    asyncio.to_thread(call_mistral_three, user_prompt)
                                   )
    
    mistral_one_output = results[0]
    mistral_two_output = results[1]
    mistral_three_output = results[2]

    print(mistral_one_output, mistral_two_output, mistral_three_output)
    # Step 4: Build the consensus prompt
    final_model_prompt = final_c_prompt(consensus_model_prompt,
        mistral_one_output,
        mistral_two_output,
        mistral_three_output
    )
    
    # Step 5: Call the consensus model
    final_output = call_consensus_model(final_model_prompt)
    
    return {
        "consensus": final_output
    }

result = asyncio.run(generate_with_rag("jlvcm", "ha-actualbudget"))
print(result)