import requests

# Set your GitHub API token here for authentication (optional but recommended for higher rate limits)
GITHUB_API_TOKEN = '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'
headers = {
    'Authorization': f'Bearer {GITHUB_API_TOKEN}'
}

def search_repo_by_name(repo_name):
    """Search for a GitHub repository by name and return its owner and URL."""
    url = f"https://api.github.com/search/repositories?q={repo_name}+in:name"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['total_count'] > 0:
            repo_data = data['items'][0]  # Get the first result
            owner = repo_data['owner']['login']
            repo_url = repo_data['html_url']
            return owner, repo_url
        else:
            print(f"No repository found for {repo_name}")
            return None, None
    else:
        print(f"Failed to search for {repo_name}: {response.status_code}")
        return None, None

def get_repos_info(repo_list):
    """Get owners and URLs for a list of GitHub repositories."""
    repo_info_list = []
    for repo_name in repo_list:
        owner, repo_url = search_repo_by_name(repo_name)
        if owner and repo_url:
            repo_info_list.append((owner, repo_url))
    return repo_info_list

def read_repo_list(file_path):
    """Read repository names from a file."""
    with open(file_path, 'r') as file:
        repo_list = file.read().splitlines()
    return repo_list

def export_repo_urls(repo_info_list, output_file):
    """Export the repository owner and URL to a file."""
    with open(output_file, 'w') as file:
        for owner, repo_url in repo_info_list:
            file.write(f"{repo_url}\n")

if __name__ == "__main__":
    # Read repository names from the repo_list.txt file
    repo_file_path = 'repo_list.txt'  # Change this to the path of your file
    repo_names = read_repo_list(repo_file_path)
    
    # Get repo info (owner and URL)
    repo_info_list = get_repos_info(repo_names)
    
    # Export the owner and URL to repo_urls.txt
    output_file = 'repo_urls.txt'
    export_repo_urls(repo_info_list, output_file)
    
    print(f"Repository URLs have been exported to {output_file}")
