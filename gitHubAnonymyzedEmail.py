import argparse
import networkx as nx
from loguru import logger
from rich.console import Console
from rich.progress import track

# Initialize the Rich console
console = Console()

# For the GitHub REST APY
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Use GITHUB_TOKEN in your requests
# Replace with your personal access token if needed

GITHUB_TOKEN = config.get('github', 'token', fallback=None)

print("\tGITHUB_TOKEN=[",GITHUB_TOKEN,"]")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN in the config.ini file")



import requests
import json

def deanonymize_github_user(email):
    if '@users.noreply.github.com' not in email:
        raise ValueError("The provided email address is not a valid GitHub noreply email.")

    # Extract the username part from the email
    try:
        username = email.split('+')[1].split('@')[0]
    except IndexError:
        raise ValueError("Unable to extract GitHub username from the email address.")

    # GitHub API URL for the user's profile
    url = f"https://api.github.com/users/{username}"

    # Perform the API request
    response = requests.get(url)

    if response.status_code == 200:
        user_data = response.json()
        
        # Extracting affiliation/organization information
        affiliation = user_data.get('company', 'No affiliation/organization available')
        
        return {
            "username": username,
            "affiliation": affiliation,
            "profile_url": user_data.get("html_url"),
            "name": user_data.get("name", "Name not available"),
            "location": user_data.get("location", "Location not available"),
            "bio": user_data.get("bio", "Bio not available"),
        }
    else:
        raise ValueError(f"Failed to retrieve information for GitHub user: {username}")

# Example Usage
email = "userID+username@users.noreply.github.com"
try:
    result = deanonymize_github_user(email)
    print(json.dumps(result, indent=4))
except ValueError as e:
    print(e)



def iterate_graph(input_file, output_file):
    try:
        # Read the input GraphML file
        logger.info(f"Reading input GraphML file: {input_file}")
        G = nx.read_graphml(input_file)

        # Create a new directed graph for the output
        G_copy = nx.DiGraph()

        # Copy nodes from the input graph to the new graph
        for node in track(G.nodes(), description="Copying nodes..."):
            G_copy.add_node(node)
            logger.debug(f"Copied node: {node}")

        # Optionally, copy edges if needed
        # for edge in G.edges():
        #     G_copy.add_edge(*edge)
        #     logger.debug(f"Copied edge: {edge}")

        # Write the copied graph to the output GraphML file
        logger.info(f"Writing output GraphML file: {output_file}")
        nx.write_graphml(G_copy, output_file)

        console.print(f"[bold green]Successfully copied the graph to {output_file}[/bold green]")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Copy nodes from an input GraphML file to an output GraphML file.")
    parser.add_argument("input", type=str, help="Input GraphML file path")
    parser.add_argument("output", type=str, help="Output GraphML file path")
    
    args = parser.parse_args()

    # Call the function to copy the graph
    copy_graph(args.input, args.output)

if __name__ == "__main__":
    main()






# The anonymized email address
#anonymized_email = "13885442+dothinking@users.noreply.github.com"
anonymized_email = "ThomasHagebols@users.noreply.github.com"

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

    print()
    print(f"email: {user_data['email']}")
    print(f"company: {user_data['company']}")

    print()

    for key, value in user_data.items():
        print(f"{key}: {value}")    
else:
    print(f"Failed to fetch user details: {response.status_code}")


