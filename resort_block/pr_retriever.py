#======================================================
#PR MODELLING BLOCK
#======================================================
from fastapi import FastAPI, HTTPException
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Limit concurrent requests to avoid rate limits
semaphore = asyncio.Semaphore(10)

#=======================================================
#Server to receive and manage PR data
#=======================================================
server = FastAPI()

@server.get("/")
def root():
   return {"message": "Server is active!"}

#====================================================================
#Load and process auth data..allowing me access to my github repo
#====================================================================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_HEADER = {
   "Authorization": f"Bearer {GITHUB_TOKEN}"
}

#====================================================================
#Get key data from GitHub API
#====================================================================

@server.get("/retrive/{owner}/{repo}")
async def get_prs(owner: str, repo: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Get all open PRs
        prs_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        try:
            response = await client.get(prs_url, headers=GITHUB_HEADER)
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="GitHub took too long to respond. Please try again."
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Could not connect to GitHub. Check your internet."
            )
        # Handle wrong repo/owner
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{owner}/{repo}' not found. Check the owner and repo name."
            )
        # Handle rate limits
        if response.status_code == 403:
            reset_time = response.headers.get("X-RateLimit-Reset")
            if reset_time:
                import time
                reset_dt = time.gmtime(int(reset_time))
                detail = f"GitHub rate limit exceeded. Resets at {time.strftime('%H:%M:%S', reset_dt)} UTC."
            else:
                detail = "GitHub rate limit exceeded. Please wait and try again."
            raise HTTPException(status_code=429, detail=detail)
        # Handle other errors
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub error: {response.status_code}"
            )
        prs = response.json()
        if not prs:
            return {"prs": [], "message": "No open pull requests found."}
        

        # 2. For each PR, get the important files
        async def get_files(pr_number):
            async with semaphore:
                files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
                try:
                    resp = await client.get(files_url, headers=GITHUB_HEADER)
                except:
                    return []  # If a single PR fails, skip it
                if resp.status_code != 200:
                    return []  # Skip failed PRs
                files = resp.json()
                return [{
                    "filename": f.get("filename"),
                    "patch": f.get("patch")
                } for f in files]
        

        # 3. Run all PR file requests concurrently
        tasks = [get_files(pr["number"]) for pr in prs]
        all_files = await asyncio.gather(*tasks)
        

        # 4. Build clean PR data
        relevant_pr_data = []
        for pr, files in zip(prs, all_files):
            relevant_pr_data.append({
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"],
                "repo": f"{owner}/{repo}",
                "files": files #contains filename and diff
            })
        return {"prs": relevant_pr_data}