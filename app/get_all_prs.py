from fastapi import FastAPI
import asyncio
import httpx
import os

app = FastAPI()

# GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Limit concurrent requests to avoid rate limits
semaphore = asyncio.Semaphore(10)

@app.get("/")
def root():
    return {"message": "Server is active"}

@app.get("/review/{owner}/{repo}")
async def get_prs(owner: str, repo: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Get all open PRs
        prs_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        response = await client.get(prs_url, headers=HEADERS)
        prs = response.json()
        
        # 2. For each PR, get the files (including diffs)
        async def get_files(pr_number):
            async with semaphore:
                files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
                resp = await client.get(files_url, headers=HEADERS)
                files = resp.json()
                
                # Only keep what matters
                return [{
                    "filename": f.get("filename"),
                    "patch": f.get("patch")  # The diff
                } for f in files]
        
        # 3. Run all PR file requests concurrently
        tasks = [get_files(pr["number"]) for pr in prs]
        all_files = await asyncio.gather(*tasks)
        
        # 4. Build clean PR data
        result = []
        for pr, files in zip(prs, all_files):
            result.append({
                "number": pr["number"],
                "title": pr["title"],
                "author": pr["user"]["login"],
                "repo": f"{owner}/{repo}",
                "files": files
            })
        
        return {"prs": result}