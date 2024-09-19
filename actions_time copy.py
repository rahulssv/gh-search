import requests
import json
from datetime import datetime

# GitHub token for authentication
TOKEN = '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'

# Function to get workflow details
def get_workflows(repo_url):
    headers = {'Authorization': f'token {TOKEN}'}
    owner, repo = repo_url.split('/')[-2:]
    workflows_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    
    response = requests.get(workflows_url, headers=headers)
    workflows = response.json().get('workflows', [])
    
    workflow_data = []
    all_workflow_duration = 0
    for workflow in workflows:
        workflow_id = workflow['id']
        workflow_name = workflow['name']
        runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        runs_response = requests.get(runs_url, headers=headers)
        runs = runs_response.json().get('workflow_runs', [])
        runs_count = runs_response.json().get('total_count', [])
        
        duration_minutes = 0
        for run in runs:
            timing_url = f"https://api.github.com/repos/{owner}/{repo}/ations/runs/{run['id']}/timing"
            timing_response = requests.get(timing_url, headers=headers)
            timing = timing_response.json().get('run_duration_ms', '')
            # start_time = datetime.fromisoformat(run['created_at'][:-1])
            # end_time = datetime.fromisoformat(run['updated_at'][:-1]) if run.get('updated_at') else start_time
            if timing.strip():  # Ensure timing is not empty or whitespace
                duration_minutes += int(timing)/60000
            else:
                # Handle the case where timing is empty
                duration_minutes += 0
            # duration_minutes += int(timing)/60000
            # duration_minutes += (end_time - start_time).total_seconds()/60
        average_run_duration = round(duration_minutes/len(runs))
        total_average_duration_minutes = runs_count*average_run_duration
        workflow_data.append({
            'workflow_name': workflow_name,
            'workflow_runs': runs_count,
            'average_run_duration_minutes': average_run_duration,
            'total_duration_minutes': total_average_duration_minutes
        })
        all_workflow_duration += total_average_duration_minutes
    
    return workflow_data, all_workflow_duration

# Read repo URLs from the file
with open('repo_urls.txt') as file:
    repo_urls = [line.strip() for line in file]

# Collect workflow data for each repo and export to a JSON file
all_workflows_data = {}

for repo_url in repo_urls:
    print(f"Fetching data for: {repo_url}")
    workflows, duration = get_workflows(repo_url)
    all_workflows_data[repo_url] = workflows, duration

# Write the workflows data to workflows.json
with open('workflows.json', 'w') as json_file:
    json.dump(all_workflows_data, json_file, indent=4)

print("Workflow data saved to workflows.json")
