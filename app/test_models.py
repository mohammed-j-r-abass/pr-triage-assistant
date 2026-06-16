import asyncio
from dotenv import load_dotenv
from model_client import call_all_models

# Load environment variables
load_dotenv()

async def test():
    print("Starting test...")  # Add this line to confirm it's running
    
    prompt = """
Review this code change for bugs and security issues:

def divide(a, b):
    return a / b

Return issues in plain text.
"""
    
    print("Calling all three models...")
    results = await call_all_models(prompt)
    
    print("\n" + "="*50)
    print("GROQ RESPONSE:")
    print("="*50)
    print(results.get("groq", "No response"))
    
    print("\n" + "="*50)
    print("MINSTRAL RESPONSE:")
    print("="*50)
    print(results.get("mistral", "No response"))
    
    print("\n" + "="*50)
    print("OPENROUTER RESPONSE:")
    print("="*50)
    print(results.get("openrouter", "No response"))

if __name__ == "__main__":
    print("Running test...")
    asyncio.run(test())