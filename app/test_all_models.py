# app/test_all_models.py

import asyncio
import json
from dotenv import load_dotenv
from model_client import (
    call_groq,
    call_mistral,
    call_openrouter,
    call_openrouter_claude,
    call_openrouter_deepseek,
    call_openrouter_gemini
)
from prompts import build_review_prompt

load_dotenv()

# Same complex code as before
COMPLEX_CODE = '''
# user_auth.py - User authentication module

import sqlite3
import hashlib
import os

# Hardcoded secret key - SECURITY ISSUE
SECRET_KEY = "hardcoded_secret_12345"

def get_user_db():
    """Connect to the user database."""
    conn = sqlite3.connect('users.db')
    return conn

def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): The username
        password (str): The password
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # SECURITY ISSUE: SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True
    else:
        return False

def get_user_info(user_id):
    """
    Get user information by user ID.
    
    Args:
        user_id (int): The user ID
    
    Returns:
        dict: User information
    """
    # SECURITY ISSUE: No authentication check
    # BUG: No validation of user_id type
    # BUG: No error handling
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_password(user_id, new_password):
    """
    Update a user's password.
    
    Args:
        user_id (int): The user ID
        new_password (str): The new password
    """
    # BUG: No hashing of password before storing
    # SECURITY ISSUE: No authentication check
    # QUALITY: No error handling
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET password = '{new_password}' WHERE id = {user_id}")
    conn.commit()
    conn.close()

# BUG: Function defined but never used
def log_audit_event(event):
    print(f"Audit: {event}")

# QUALITY ISSUE: Unused import
import datetime
'''

EXPECTED_ISSUES = [
    "Hardcoded secret key",
    "SQL injection",
    "Plaintext password",
    "Missing authentication",
    "No validation of user_id",
    "No error handling",
    "Unused function",
    "Unused import"
]

async def test_model(name, call_func, prompt):
    """Test a single model and return results."""
    print(f"Testing {name}...")
    try:
        response = await asyncio.to_thread(call_func, prompt)
        if response is None:
            return {"name": name, "response": None, "issues": []}
        
        # Parse JSON
        clean = response.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        
        issues = json.loads(clean)
        return {"name": name, "response": response, "issues": issues}
    except Exception as e:
        return {"name": name, "response": None, "error": str(e)}

async def run_all_tests():
    print("="*70)
    print("COMPARING ALL MODELS ON COMPLEX CODE")
    print("="*70)
    
    # Build the prompt
    prompt = build_review_prompt(COMPLEX_CODE, "user_auth.py")
    
    # Define models to test
    models = [
        ("Groq (Llama)", call_groq),
        ("Mistral", call_mistral),
        ("OpenRouter (Qwen)", call_openrouter),
        ("OpenRouter (Claude)", call_openrouter_claude),
        ("OpenRouter (DeepSeek)", call_openrouter_deepseek),
        ("OpenRouter (Gemini)", call_openrouter_gemini),
    ]
    
    # Test each model
    results = []
    for name, call_func in models:
        result = await test_model(name, call_func, prompt)
        results.append(result)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    for result in results:
        print(f"\n{result['name']}:")
        print("-"*50)
        
        if result.get("error"):
            print(f"  ERROR: {result['error']}")
            continue
        
        if result["response"] is None:
            print("  No response")
            continue
        
        issues = result.get("issues", [])
        if not issues:
            print("  No issues found")
            continue
        
        print(f"  Found {len(issues)} issues:")
        for issue in issues[:5]:  # Show first 5
            severity = issue.get("severity", "UNKNOWN")
            category = issue.get("category", "UNKNOWN")
            desc = issue.get("description", "No description")
            print(f"    [{severity}] [{category}] {desc[:60]}...")
        
        if len(issues) > 5:
            print(f"    ... and {len(issues) - 5} more")
    
    # Comparison table
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    
    print(f"\n{'Model':<25} {'Issues Found':<15} {'Status'}")
    print("-"*70)
    
    for result in results:
        name = result['name']
        issues = result.get('issues', [])
        count = len(issues) if issues else 0
        status = "OK" if count > 0 else "FAIL"
        print(f"{name:<25} {count:<15} {status}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())