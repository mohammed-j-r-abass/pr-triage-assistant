from dotenv import load_dotenv #--> Import API keys from dotenv
import os
import httpx
load_dotenv() #--> Activate the keys

#===============================================================
# LOAD MY API KEY (LIKE YOUR TICKET NUMBER) FROM MY .ENV SCRIPT
#===============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
   print("API Key hasn't loaded yet")

#==========================================================
# GO TO THIS ENDPOINT (/chat/completions) FOR YOUR TASK
#==========================================================
url = "https://api.groq.com/openai/v1/chat/completions"

#==============================================================
# THIS IS LIKE MY TICKET CONTAINING MY NUMBER AND WHAT I WANT
#==============================================================
HEADERS = {
   "Authorization": f"Bearer {GROQ_API_KEY}",
   "Content-Type": "application/json"
}

#=============================================================
# 
#=============================================================
def try_model_call(prompt: str):
   with httpx.Client() as client:
      response = client.post(
         url, 
         headers = HEADERS,
         json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
         }
      )
      data = response.json()
      main_response = data["choices"][0]["message"]["content"]

      return main_response
print(try_model_call("What is discrete mth about in college"))