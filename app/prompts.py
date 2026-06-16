# app/prompts.py

def build_review_prompt(diff_text, file_name="unknown"):
    """
    Build a structured prompt for code review with specific focus areas.
    
    Args:
        diff_text (str): The git diff or code to review
        file_name (str): The name of the file being reviewed
    
    Returns:
        str: The complete prompt for the AI models
    """
    
    # Safety check: if diff_text is None or empty, use a default message
    if not diff_text:
        diff_text = "No code provided to review."
    
    if not file_name:
        file_name = "unknown"
    
    prompt = f'''
You are an expert code reviewer analyzing code changes in a pull request. Your job is to find real issues that matter.

## File: {file_name}

## Code to review:
{diff_text}

## Examples of good responses:

Example 1:
[
  {{
    "file": "{file_name}",
    "line": 10,
    "severity": "HIGH",
    "category": "SECURITY",
    "description": "Hardcoded Stripe secret key exposed in source code. Anyone with access to the repository can steal it.",
    "suggestion": "Store STRIPE_SECRET_KEY in environment variables or a secrets manager like Vault.",
    "reasoning": "Hardcoded secrets are a critical security risk and should never appear in source code."
  }}
]

Example 2:
[
  {{
    "file": "{file_name}",
    "line": 45,
    "severity": "HIGH",
    "category": "BUG",
    "description": "Division by zero occurs here if b is 0. This will crash the program.",
    "suggestion": "Add a check: if b == 0: raise ValueError('Cannot divide by zero')",
    "reasoning": "Unhandled division by zero causes runtime crashes. This is a critical bug."
  }}
]

## What to look for (in order of importance):

### 1. SECURITY ISSUES (HIGHEST PRIORITY)
- SQL injection vulnerabilities (string concatenation in queries)
- Hardcoded secrets, API keys, passwords, tokens
- Missing authentication or authorization checks
- Command injection
- Exposed sensitive data in logs, errors, or responses
- Insecure direct object references
- Path traversal vulnerabilities
- Use of broken cryptographic algorithms (MD5, SHA1)

### AUTHENTICATION & AUTHORIZATION
- Missing authentication decorators or middleware
- Functions that modify data without checking user permissions
- API endpoints that don't validate user roles
- Hardcoded admin bypass checks
- Functions that expose sensitive data without verifying ownership
- Missing session or token validation

### 2. BUGS & LOGIC ERRORS
- Division by zero, null pointer exceptions
- Off-by-one errors in loops
- Incorrect conditional logic (== vs =, wrong operators)
- Missing edge case handling (empty lists, negative values)
- Unhandled exceptions
- Incorrect type handling
- Race conditions
- Infinite loops

### 3. CODE QUALITY
- Code duplication (DRY violations)
- Lack of error handling
- Poor naming conventions (unclear variable/function names)
- Missing documentation (functions, classes, complex logic)
- Overly complex code (hard to read/maintain)
- Unused imports, variables, or functions
- Performance issues (inefficient loops, unnecessary computations)

### 4. BEST PRACTICES
- Following language-specific conventions (PEP 8 for Python)
- Clean, readable, maintainable code
- Proper error messages (helpful, not generic)
- Proper separation of concerns
- Using appropriate data structures

## Output Format

Return your findings as a JSON array with this exact structure. Each issue must include your reasoning and a specific fix suggestion. Keep responses concise and clear - descriptions and suggestions should be 2-4 sentences each.

```json
[
  {{
    "file": "{file_name}",
    "line": 42,
    "severity": "HIGH|MEDIUM|LOW",
    "category": "SECURITY|BUG|QUALITY|BEST_PRACTICE",
    "description": "A detailed explanation of what the issue is and why it matters. Explain the potential impact.",
    "suggestion": "A specific, actionable fix for this issue. Include code examples if helpful.",
    "reasoning": "Your reasoning behind the severity and category. Explain why you flagged this as HIGH or MEDIUM."
  }}
]

If you find no issues, return: []

Return ONLY the JSON array, nothing else. Do not include markdown or explanations.
'''

    # Debug: confirm prompt is not empty
    print(f"Debug: Prompt length = {len(prompt)} characters")
    
    return prompt