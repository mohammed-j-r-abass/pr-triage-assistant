#============Flask Server============#
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'PR Reviewer is running'

@app.route('/health')
def health():
    return {'status': 'ok'}

# ---- adding a webhook endpoint ----
@app.route('/webhook', methods=['POST'])
def webhook():
    # Get the JSON payload from GitHub
    payload = request.get_json()
    
    # Get the event type from the headers
    event_type = request.headers.get('X-GitHub-Event')

    #Make sure the event type is a pull request event
    if event_type != "pull_request":
        return 200, jsonify({"status": "ignored", "reason": "not a pull request event"})
    
    #Check to make sure the action is either 'opened', 'synchronize', or 'reopened'
    action = payload.get('action')
    if action not in ['opened', 'synchronize', 'reopened']:
        return 200, jsonify({"status": "ignored", "reason": f"action '{action}' is not relevant"})
    
    # Get the PR number if it exists
    pr_number = None
    if payload and 'pull_request' in payload:
        pr_number = payload['pull_request']['number']
        repo = payload['repository']['full_name']
        print(f" Received {event_type} event: {action} PR #{pr_number} on {repo}")
    
    # Return a response to GitHub
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)