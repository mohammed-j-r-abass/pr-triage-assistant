# app/test_complex.py

import asyncio
import json
from dotenv import load_dotenv
from model_client import call_all_models

load_dotenv()

COMPLEX_CODE = '''
# payment_processor.py - Payment handling module

import os
import json
import hashlib
import hmac
import time
import threading
from datetime import datetime
from decimal import Decimal

STRIPE_SECRET_KEY = "sk_live_1234567890abcdef"
PAYPAL_CLIENT_ID = "AX1bC2dE3fG4hI5jK6lM7nO8pQ9rS0tU"
ADMIN_PASSWORD = "admin123"

user_sessions = {}
transaction_log = []
pending_refunds = []

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def validate_payment(amount, currency, user_id):
    if amount > 0:
        return True
    return False

def process_payment(user_id, amount, card_number, cvv, expiry):
    print(f"Processing payment for user {user_id}: {card_number}, CVV: {cvv}")
    transaction_log.append({
        "user_id": user_id,
        "amount": amount,
        "card_number": card_number[-4:],
        "cvv": cvv,
        "timestamp": datetime.now()
    })
    global pending_refunds
    if amount > 1000:
        pending_refunds.append(user_id)
    result = "success"
    return True

def process_refund(user_id, amount):
    if amount < 0:
        raise ValueError("Invalid refund amount")
    for transaction in transaction_log:
        if transaction.get("user_id") == user_id:
            print(f"Refunding {amount} to user {user_id}")
    import base64
    import random

def get_user_transactions(user_id):
    result = []
    for transaction in transaction_log:
        if transaction["user_id"] == user_id:
            result.append(transaction)
    return result

def validate_card_luhn(card_number):
    sum = 0
    num_digits = len(card_number)
    is_second = False
    for i in range(num_digits - 1, -1, -1):
        d = int(card_number[i])
        if is_second:
            d = d * 2
        sum += d // 10
        sum += d % 10
        is_second = not is_second
    return sum % 10 == 0

class PaymentProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
    def process(self, amount):
        return amount * 1.05

ADMIN_SECRET = "super_secret_admin_key_12345"

def calculate_fee(amount, fee_percentage=2.5):
    if isinstance(fee_percentage, str):
        fee_percentage = float(fee_percentage)
    return amount * (fee_percentage / 100)

event_listeners = []
def add_event_listener(callback):
    event_listeners.append(callback)

def is_valid_amount(amount):
    if amount > 0:
        return False
    else:
        return True
'''

EXPECTED_ISSUES = [
    {"category": "SECURITY", "description": "Hardcoded Stripe secret key", "line": 10},
    {"category": "SECURITY", "description": "Hardcoded PayPal client ID", "line": 11},
    {"category": "SECURITY", "description": "Hardcoded admin password", "line": 12},
    {"category": "SECURITY", "description": "MD5 password hashing (cryptographically broken)", "line": 17},
    {"category": "SECURITY", "description": "Logging card number and CVV in plaintext", "line": 45},
    {"category": "SECURITY", "description": "Storing CVV in transaction log", "line": 53},
    {"category": "SECURITY", "description": "No authentication check in validate_payment", "line": 27},
    {"category": "SECURITY", "description": "No authentication check in process_refund", "line": 70},
    {"category": "SECURITY", "description": "No authentication check in get_user_transactions", "line": 92},
    {"category": "SECURITY", "description": "Hardcoded admin secret key", "line": 120},
    {"category": "BUG", "description": "No validation of amount in validate_payment", "line": 27},
    {"category": "BUG", "description": "No validation of currency in validate_payment", "line": 27},
    {"category": "BUG", "description": "No validation of card number (Luhn check missing)", "line": 41},
    {"category": "BUG", "description": "No validation of expiry date (past dates allowed)", "line": 41},
    {"category": "BUG", "description": "No error handling in process_payment", "line": 41},
    {"category": "BUG", "description": "Race condition with global pending_refunds (not thread-safe)", "line": 58},
    {"category": "BUG", "description": "No validation that refund amount <= original payment", "line": 70},
    {"category": "BUG", "description": "Logic error in is_valid_amount (always returns False)", "line": 135},
    {"category": "BUG", "description": "No error handling for missing user_id in get_user_transactions", "line": 92},
    {"category": "QUALITY", "description": "Unused variable 'result' in process_payment", "line": 61},
    {"category": "QUALITY", "description": "Unused function validate_card_luhn", "line": 101},
    {"category": "QUALITY", "description": "Unused class PaymentProcessor", "line": 113},
    {"category": "QUALITY", "description": "Magic number 1000 in process_payment", "line": 58},
    {"category": "QUALITY", "description": "Unused imports (base64, random)", "line": 80},
    {"category": "PERFORMANCE", "description": "Inefficient loop in process_refund (O(n))", "line": 74},
    {"category": "PERFORMANCE", "description": "Inefficient loop in get_user_transactions", "line": 93},
    {"category": "PERFORMANCE", "description": "Memory leak with event_listeners (never cleaned up)", "line": 130},
    {"category": "BUG", "description": "Type handling issue in calculate_fee (string to float)", "line": 125},
    {"category": "CONCURRENCY", "description": "Global user_sessions dictionary not thread-safe", "line": 14}
]

async def run_complex_test():
    results = await call_all_models(COMPLEX_CODE, "payment_processor.py")
    
    for model_name, response in [
        ("GROQ", results["groq"]),
        ("MISTRAL", results["mistral"]),
        ("OPENROUTER", results["openrouter"])
    ]:
        print(f"\n{model_name}:")
        if response is None:
            print("  No response")
            continue
        try:
            clean = response.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
            clean = clean.strip()
            issues = json.loads(clean)
            print(f"  Found {len(issues)} issues")
            for issue in issues[:5]:
                print(f"    - [{issue.get('severity','?')}] {issue.get('description','')[:80]}")
            if len(issues) > 5:
                print(f"    ... and {len(issues)-5} more")
        except:
            print("  Could not parse response")
            print(response[:300] + "..." if len(response) > 300 else response)

if __name__ == "__main__":
    asyncio.run(run_complex_test())