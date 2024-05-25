import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

GITHUB_TOKEN = config.get('github', 'token', fallback=None)

print("\tGITHUB_TOKEN=[",GITHUB_TOKEN,"]")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN in the config.ini file")

# Use GITHUB_TOKEN in your requests

# Replace with your personal access token if needed


# The anonymized email address
anonymized_email = "octocat@users.noreply.github.com"

# Extract the username from the email
username = anonymized_email.split('@')[0]

# GitHub API endpoint to fetch user details
url = f"https://api.github.com/users/{username}"

# Headers for authentication
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Make the request to GitHub API
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    user_data = response.json()
    print(f"Username: {user_data['login']}")
    print(f"User ID: {user_data['id']}")
    print(f"Name: {user_data.get('name', 'N/A')}")
    print(f"Public Repos: {user_data['public_repos']}")
    print(f"Followers: {user_data['followers']}")
    print(f"Following: {user_data['following']}")
else:
    print(f"Failed to fetch user details: {response.status_code}")


