import requests
import json
from datetime import datetime
def fetch_workflow_runs(owner, repo, workflow_id, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflow runs for {owner}/{repo}: {e}")
        return []

    return response.json().get('workflow_runs', [])

def fetch_jobs(owner, repo, run_id, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs for run {run_id} in {owner}/{repo}: {e}")
        return []

    return response.json().get('jobs', [])

def search_jobs_by_name_or_steps(jobs, search_term="build"):
    search_term = search_term.lower()
    filtered_jobs = []

    for job in jobs:
        # Check if the search term is in the job name
        if search_term in job['name'].lower():
            filtered_jobs.append(job)
        else:
            # Check if the search term is in the steps' names
            for step in job.get('steps', []):
                if search_term in step['name'].lower():
                    filtered_jobs.append(job)
                    break  # If one step matches, we don't need to check others
    
    return filtered_jobs

def fetch_workflows(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching workflows for {owner}/{repo}: {e}")
        return []

    workflows = response.json().get('workflows', [])
    return workflows

def extract_repo_info(url):
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    return None, None

def main():
    token = "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"  # Replace with your personal access token
    workflow_jobs_file = 'workflow_jobs.json'
    
    # Read repository URLs from file
    with open('repo_urls.txt', 'r') as file:
        repo_urls = file.readlines()
    
    # Dictionary to store repository names and their job names containing "build"
    repo_jobs = {}
    repos = []
    repo_workflows = []
    repo_runs = []
    repo_jobs = []
    for repo_url in repo_urls:
        repo_url = repo_url.strip()
        if repo_url:
            owner, repo = extract_repo_info(repo_url)
            if owner and repo:
                print(f"Fetching workflows for {owner}/{repo}...")
                workflows = fetch_workflows(owner, repo, token)
                workflows_duration_minutes = 0 
                if workflows:
                    
                    for workflow in workflows:
                        workflow_id = workflow['id']
                        workflow_runs = fetch_workflow_runs(owner, repo, workflow_id, token)

                        runs_duration_minutes = 0 
                        
                        for run in workflow_runs:
                            run_id = run['id']
                            jobs = fetch_jobs(owner, repo, run_id, token)
                            filtered_jobs = search_jobs_by_name_or_steps(jobs, search_term="build")
                            jobs_duration_minutes = 0
                            
                            if filtered_jobs:
                                
                                for job in filtered_jobs:
                                    start_time = datetime.fromisoformat(job['started_at'][:-1])
                                    end_time = datetime.fromisoformat(job['completed_at'][:-1]) if job.get('completed_at') else start_time
                                    job_duration_minutes = (end_time - start_time).total_seconds()/60
                                    jobs_duration_minutes += job_duration_minutes
                                    job_info = {
                                        "job_name": job['name'],
                                        "job_id": job['id'],
                                        "job_duration": job_duration_minutes
                                    }
                                    repo_jobs.append(job_info)
                                    print(f"job_duration_minutes: {job_duration_minutes}")
                            
                                runs_duration_minutes += jobs_duration_minutes
                                repo_runs.append({
                                    "run_name": run['display_title'],
                                    "run_id": run['id'],
                                    "run_duration": jobs_duration_minutes,
                                    "jobs":  repo_jobs
                                    })
                                print(f"run_duration_minutes: {jobs_duration_minutes}")
                        
                        workflows_duration_minutes += runs_duration_minutes
                        if runs_duration_minutes != 0:
                            repo_workflows.append({
                                "Workflow_name": workflow['name'],
                                "Workflow_id": workflow['id'],
                                "Workflow_duration": runs_duration_minutes,
                                "runs": repo_runs
                            })
                            print(f"workflows_duration_minutes: {runs_duration_minutes}")
                        
                    
                    print(f"Total workflows_duration_minutes: {workflows_duration_minutes}")
                    repos.append({
                        "repo_name": repo,
                        "repo_url": repo_url,
                        "repo_duration": workflows_duration_minutes,
                        "actions": repo_workflows
                    })
                
    # Write the repo names and job info to workflow_jobs.json
    with open(workflow_jobs_file, 'w') as json_file:
        json.dump(repos, json_file, indent=4)

if __name__ == "__main__":
    main()
