#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
This module  deanonymizes GitHub noreply emails in gramphML files created with ScrapLogGit2Net
"""



import sys
import os

import argparse
import networkx as nx

from typing import Tuple 

import time
from time import sleep 


# Combining loguru with rich provides a powerful logging setup that enhances readability and adds visual appeal to your logs. This integration makes it easier to debug and monitor applications by presenting log messages in a clear, color-coded, and structured format while using loguru's other features, such as log rotation and filtering,
from loguru import logger

# You can then print strings or objects to the terminal in the usual way. Rich will do some basic syntax highlighting and format data structures to make them easier to read.
from rich import print as rprint


# For complete control over terminal formatting, Rich offers a Console class.
# Most applications will require a single Console instance, so you may want to create one at the module level or as an attribute of your top-level object. 
from rich.console import Console

# Initialize the console
console = Console()

# JSON gets easier to understand 
from rich import print_json
from rich.json import JSON





# Strings may contain Console Markup which can be used to insert color and styles in to the output.
from rich.markdown import Markdown

# Python data structures can be automatically pretty printed with syntax highlighting.
from rich import pretty
from rich.pretty import pprint
pretty.install()

# Rich has an inspect() function which can generate a report on any Python object. It is a fantastic debug aid
from rich import inspect
from rich.color import Color

#Rich supplies a logging handler which will format and colorize text written by Python’s logging module.
from rich.logging import RichHandler

# Add RichHandler to the loguru logger
logger.remove()  # Remove the default logger
logger.add(
    RichHandler(console=console, show_time=True, show_path=True, rich_tracebacks=True),
    format="{message}",  # You can customize this format as needed
    level="DEBUG",  # Set the desired logging level
    #level="INFO",  # Set the desired logging level
)


# Rich’s Table class offers a variety of ways to render tabular data to the terminal.
from rich.table import Table


# Rich provides the Live  class to to animate parts of the terminal
# It's handy to annimate tables that grow row by row 
from rich.live import Live

# Rich provides the Align class to align rendable objects
from rich.align import Align

# Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the ‘task’, a progress bar, percentage complete, and estimated time remaining.
from rich.progress import Progress, TaskID

# Rich has a Text class you can use to mark up strings with color and style attributes.
from rich.text import Text


from rich.traceback import Traceback 

# For configuring 
from rich.traceback import install
# Install the Rich Traceback handler with custom options
install(
    show_locals=True,  # Show local variables in the traceback
    locals_max_length=10, locals_max_string=80, locals_hide_dunder=True, locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    # suppress=[your_module],  # Suppress tracebacks from specific modules
    #max_frames=3,  # Limit the number of frames shown
    max_frames=5,  # Limit the number of frames shown
    #width=50,  # Set the width of the traceback display
    width=100,  # Set the width of the traceback display
    extra_lines=3,  # Show extra lines of code around the error
    theme="solarized-dark",  # Use a different color theme
    word_wrap=True,  # Enable word wrapping for long lines
)



# For the GitHub REST API
import requests
import configparser

# Use cache as there are API request hourly limits 
import requests_cache
from github import Github, GithubException, RateLimitExceededException

# Set up requests-cache
requests_cache.install_cache('github_cache', expire_after=3600)

config = configparser.ConfigParser()
config.read('config.ini')

# Use GITHUB_TOKEN in your requests
# Replace with your personal access token if needed

GITHUB_TOKEN = config.get('github', 'token', fallback=None)
CURRENT_PROJECT = config.get('github', 'current_project', fallback=None)


rprint("\t Accessing GitHub Rest API with GITHUB_TOKEN=[",GITHUB_TOKEN,"]")

if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN in the config.ini file")

if not CURRENT_PROJECT:
    raise ValueError("Please set the current project in the config.ini file")

git_hub_auth_headers = {'Authorization': GITHUB_TOKEN}


# For validating a GraphML File
import xml.etree.ElementTree as ET



def log_messages() -> None: 
    rprint("\n\t [green] Testing logger messages:\n")
    
    # Log messages at different levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    rprint("\n")
    
def console_messages() -> None: 
    
    rprint("\n\t [green] Testing console messages:\n")

    markdown_text = Markdown("# This is a heading\n\n- This is a list item\n- Another item")
    console.print(markdown_text)

    
    # An example of a styled message
    console.print("[bold blue]Welcome to [blink]Rich[/blink]![/bold blue]")
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.")
    console.print("[bold red]Error:[/bold red] Something went wrong. Please try again.")


    # Other examples

    console.print([1, 2, 3])
    console.print("[blue underline]Looks like a link")
    console.print(locals())
    console.print("FOO", style="white on blue")
    
    console.print(inspect("test-string", methods=True))

    # Logging with time console.log("Hello, World!")

    # json and low level examples 
    console.print_json('[false, true, null, "foo"]')
    console.log(JSON('["foo", "bar"]'))
    console.out("Locals", locals())

    # The rule
    console.rule("[bold red]Chapter 2")


def demonstrate_traceback_exceptions():

    # Define functions that raise specific exceptions
    def raise_index_error():
        my_list = [1, 2, 3]
        return my_list[5]  # Index out of range

    def raise_key_error():
        my_dict = {'a': 1, 'b': 2}
        return my_dict['c']  # Key not found

    def raise_value_error():
        return int("not_a_number")  # Value conversion error

    def raise_type_error():
        return 'string' + 5  # Type operation error

    def raise_file_not_found_error():
        with open('non_existing_file.txt') as f:
            return f.read()  # File not found

    # List of exception functions
    exception_functions = [
        ("IndexError", raise_index_error),
        ("KeyError", raise_key_error),
        ("ValueError", raise_value_error),
        ("TypeError", raise_type_error),
        ("FileNotFoundError", raise_file_not_found_error)
    ]

    for exc_name, func in exception_functions:
        try:
            func()  # Call the function that raises an exception
        except Exception as e:
            # Print the exception traceback using Rich
            console.print(f"[bold yellow]{exc_name} occurred:[/bold yellow]", style="bold red")
            # Print formatted traceback using Rich
            console.print(Traceback(), style="bold red")
            console.print("-" * 40)  # Separator for clarity

def status_messages():

    
    console.print("[blue] Counting started")
    # Create the status spinner and progress bar
    with console.status("[bold green]Processing... Counting to 100", spinner="dots") as status:
        # Loop from 1 to 100
        for i in range(1, 101):
            sleep(0.03)  # Simulate work being done

    console.print("[green]Counting completed!")

def display_advanced_text():

    # Create various styles and formats
    text1 = Text("Bold and Italic", style="bold italic cyan")
    text2 = Text(" Underlined with Green", style="underline green")
    text3 = Text(" Strike-through and Red", style="strike red")
    text4 = Text(" Background Color", style="on yellow")
    text5 = Text(" Custom Font Style", style="bold magenta on black")

    # Combine different styles into one Text object
    combined_text = Text()
    combined_text.append("Rich Text Features:\n", style="bold underline")
    combined_text.append(text1)
    combined_text.append(text2)
    combined_text.append("\n")
    combined_text.append(text3)
    combined_text.append(text4)
    combined_text.append("\n")
    combined_text.append(text5)
    
    # Print the advanced text
    console.print(combined_text)


def display_emojis():
    # Initialize the console
    console = Console()

    # List of 30 emojis with descriptions
    emojis = [
        ("Smiley Face", "😀"),
        ("Thumbs Up", "👍"),
        ("Rocket", "🚀"),
        ("Heart", "❤️"),
        ("Sun", "☀️"),
        ("Star", "⭐"),
        ("Face with Sunglasses", "😎"),
        ("Party Popper", "🎉"),
        ("Clap", "👏"),
        ("Fire", "🔥"),
        ("100", "💯"),
        ("Thumbs Down", "👎"),
        ("Check Mark", "✔️"),
        ("Cross Mark", "❌"),
        ("Lightning Bolt", "⚡"),
        ("Flower", "🌸"),
        ("Tree", "🌳"),
        ("Pizza", "🍕"),
        ("Ice Cream", "🍦"),
        ("Coffee", "☕"),
        ("Wine Glass", "🍷"),
        ("Beer Mug", "🍺"),
        ("Camera", "📷"),
        ("Laptop", "💻"),
        ("Books", "📚"),
        ("Globe", "🌍"),
        ("Envelope", "✉️"),
        ("Gift", "🎁"),
        ("Calendar", "📅"),
        ("Alarm Clock", "⏰"),
        ("Basketball", "🏀")
    ]

    # Print each emoji with its description
    for description, emoji in emojis:
        # Create a rich text object with some styling
        text = Text(f"{description}: {emoji}", style="bold magenta")
        console.print(text)


    
def progress_bars_demo():
    # Create the progress bar
    with Progress() as progress:
        # Add two tasks for the progress bars
        task1 = progress.add_task("[green]Counting to 100...", total=100)
        task2 = progress.add_task("[blue]Counting to 200...", total=200)
        
        # Loop until both tasks are complete
        while not progress.finished:
            sleep(0.05)  # Simulate work being done
            progress.update(task1, advance=1)  # Update the first progress bar
            #progress.console.print(f"Working on")
            progress.update(task2, advance=0.5)  # Update the second progress bar more slowly
            
    print("Counting to 100 and 200 completed!")


    

    

def check_file_exists(file_path):
    return os.path.isfile(file_path)

def is_valid_graphml(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        logger.debug(f"checking graphml file root tag {root.tag=}")

        # Check if the root tag is 'graphml'
        if  'graphml' in root.tag:
            return True
        return False
    except ET.ParseError:
        return False




def get_rate_limit():
    logger.info("get_rate_limit()")
    response = requests.get("https://api.github.com/rate_limit",headers=git_hub_auth_headers)
    data = response.json()
    return data["resources"]["core"]

def display_rate_limit():
    logger.info("display_rate_limit()")

    table = Table(show_header=False, box=None)
    table.add_column("")
    table.add_column("")

    
    rate_limit = get_rate_limit()
    table.rows = [
            ("Limit:", str(rate_limit["limit"])),
            ("Used:", str(rate_limit["used"])),
            ("Remaining:", str(rate_limit["remaining"])),
        ]
    aligned_table = Align.right(table)
    console.print(aligned_table)
    
    
def print_GitHub_user_data(user_data:dict) -> None: 
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key")
    table.add_column("Value")

    for key, value in user_data.items():
        table.add_row(key, str(value))

    console.print(table)

    


 
already_known_user_affiliations = {}
""" 
Global dictionary
already_known_user_affiliations key is email 
already_known_user_affiliations value is a tuble[str,str] with (email,affiliation)
"""


def get_user_organizations(username):
    """
    Fetch the organizations a GitHub user belongs to.

    Parameters:
    - username (str): The GitHub username.

    Returns:
    - list: A list of organization names (str) the user belongs to.
    """
    url = f'https://api.github.com/users/{username}/orgs'
    

    
    response = requests.get(url, headers=git_hub_auth_headers)
    
    if response.status_code == 200:
        orgs_data = response.json()
        organizations = [org['login'] for org in orgs_data]

        
        console.print("\n")
        console.print(":star_struck: :astonished: Wow, that's amazing. !")
        console.print("Found organizations for {username}:")
        for org in organizations:
            console.print(f"{org=}")
        console.print("\n")
        
        
        return organizations
    else:
        print(f"Failed to retrieve organizations: {response.status_code}")
        return []



def deanonymize_github_user_with_cache_andPyGuthub(email: str) -> tuple[str, str]:
    """
    De-anonymizes a GitHub user based on their email address.
    Uses cache for avoiding REST API  request limits 
    Once it hits those limits, it sleeps for an hour 

    Args:
        email (str): The email address of the GitHub user.

    Returns:
        tuple[str, str]: A tuple containing the email address and affiliation of the GitHub user.
            The first element of the tuple is the email address (str), and the second
            element is the affiliation (str). If the email address or affiliation cannot
            be determined, the corresponding element in the tuple will be None.
    """

    logger.info(f"Checking API requre reate limit")
    display_rate_limit()
    
    logger.info(f"Deanonymizing GitHub user for {email=}")
    

    if '@users.noreply.github.com' not in email:
        raise ValueError("The provided email address is not a valid GitHub noreply email.")

    if email in globals()['already_known_user_affiliations']:
        logger.info(f"Key {email=} already exists in the global dictionary. Not calling API")
        return globals()['already_known_user_affiliations'][email]

    GitHub_email = "unknown-by-GitHub"
    GitHub_affiliation = "unknown-by-GitHub"

    # Extract the username from the email address
    try:
        if '+' in email:
            username = email.split('+')[1].split('@')[0]
        else:
            username = email.split('@')[0]
    except IndexError:
        raise ValueError("Unable to extract GitHub username from the email address.")

    # Use PyGithub to retrieve the user's public profile information
    g = Github(GITHUB_TOKEN)
    try:
        user = g.get_user(username)
        logger.debug(f"Successfully retrieved information for GitHub user: {username}")

        print_GitHub_user_data(user.raw_data)

        if user.email:
            GitHub_email = user.email

        if user.company:
            GitHub_affiliation = user.company

        # We must also check organizations
        logger.info(f"Checking if the user {username=} is a member of one or more organizations")
        organizations = [org.login for org in user.get_orgs()]
        console.print(f"Organizations for {username}: {organizations}")

        # If there was sume results from the users.get_orgs call  and they are not the home-assistant project 
        if organizations and organizations[0] != 'home-assistant':
            GitHub_affiliation = organizations[0] 

    except RateLimitExceededException:
        logger.warning("API rate limit exceeded. Sleeping for one hour...")
        time.sleep(3600)
        logger.info("Resuming API requests...")
        return deanonymize_github_user(email)

    except GithubException as e:
        logger.warning("Unexpected API message")
        logger.info(f'{e.data["message"]=}')

    globals()['already_known_user_affiliations'][email] = (GitHub_email, GitHub_affiliation)
    return (GitHub_email, GitHub_affiliation)
    
def deanonymize_github_user(email: str) -> tuple[str, str]:
    """
    De-anonymizes a GitHub user based on their email address.

    Args:
        email (str): The email address of the GitHub user.

    Returns:
        tuple[str, str]: A tuple containing the email address and affiliation of the GitHub user.
            The first element of the tuple is the email address (str), and the second
            element is the affiliation (str). If the email address or affiliation cannot
            be determined, the corresponding element in the tuple will be None.
    """

    
    logger.info(f"deanonymizing github user for {email=}")

    if '@users.noreply.github.com' not in email:
        raise ValueError("The provided email address is not a valid GitHub noreply email.")


    if email in globals()['already_known_user_affiliations']:
        logger.info(f"Key {email=} already exists in the global dictionary. Not calling API")
        return globals()['already_known_user_affiliations'][email]
    
    
    GitHub_email = "Unknown-by-GitHub"
    GitHub_affiliation = "Unknown-by-GitHub" 
    
    
    # Extract the username from the email address
    try:
        if '+' in email:
            username = email.split('+')[1].split('@')[0]
        else:
            username = email.split('@')[0]
    except IndexError:
        raise ValueError("Unable to extract GitHub username from the email address.")


    # Make a GET request to the GitHub API to retrieve the user's public profile information
    response = requests.get(f'https://api.github.com/users/{username}',headers=git_hub_auth_headers)

    logger.debug(f'{response.status_code=}')

    user_data = response.json()
    
    # If the request was successful, extract the email, company, and organization from the response
    if response.status_code == 200:

        logger.debug(f"response for user {username} was successfull")
    
        
        print_GitHub_user_data(user_data)

        
        if "email" or "e-mail" not in user_data:
            logger.warning("email not in user_data for {username}")


        if "company" or "organization" or "affiliation " not in user_data:
            logger.warning("company not in user_data for {username}")
        

        if user_data['email'] != "None":
            GitHub_email = user_data['email']

        if user_data['company'] != "None":
            GitHub_affiliation = user_data['company']


        # We must also check organizations
        logger.info(f"check if the user {username=}is a member of one or more organizations")
        organizations = get_user_organizations(username)
        console.print(f"Organizations for {username}: {organizations}")

    
        
    elif response.status_code == 403:
        if "API rate limit exceeded" in user_data["message"] or "API rate limit exceeded" in user_data:
            logger.critical("API rate limit exceeded, enought for today.")
            sys.exit()
        else:
            logger.warning("Unexpected API message")
            logger.info(f'{user_data["message"]=}')
        
    else:
        console.print(json.dumps(response.json(), indent=4))
        logger.error(f"Failed to retrieve information for GitHub user: {username}")

    globals()['already_known_user_affiliations'][email]=(GitHub_email, GitHub_affiliation)
    return (GitHub_email, GitHub_affiliation)


def print_all_nodes(network: nx.Graph):
    """
    Print all nodes in a NetworkX graph along with their attributes using rich for pretty formatting.

    Parameters:
    network (nx.Graph): The NetworkX graph.
    """

    logger.info(f"Printing all nodes in network {network=}:")
    
    if not isinstance(network, nx.Graph):
        raise TypeError("The input must be a NetworkX graph.")

    console = Console()
    table = Table(title="Nodes and Attributes")

    # Add columns to the table
    table.add_column("Node ID", style="bold cyan")
    table.add_column("Attributes", style="bold magenta")

    # Iterate over the nodes and their attributes
    for node, attributes in network.nodes(data=True):
        attr_str = ", ".join(f"{key}: {value}" for key, value in attributes.items())
        table.add_row(str(node), attr_str if attr_str else "None")

    # Print the table
    console.print(table)


    
def read_graphml_with_progress(file_path: str) -> nx.Graph:
    """
    Read a GraphML file and display a progress bar using rich.

    Parameters:
    file_path (str): The path to the GraphML file.

    Returns:
    nx.Graph: The NetworkX graph.
    """

    # Get the total size of the file
    total_size = os.path.getsize(file_path)
    
    # Initialize the progress bar
    with Progress() as progress:
        task = progress.add_task("[cyan]Reading file...", total=total_size)
        
        # Open the file for reading
        with open(file_path, "rb") as file:
            content = b""
            while not progress.finished:
                # Read a chunk of the file
                chunk = file.read(1024)  # 1 KB chunks
                if not chunk:
                    break
                # Update the progress bar
                progress.update(task, advance=len(chunk))
                # Append chunk to content
                content += chunk

    # Load the graph from the content
    # Convert bytes content to string
    content_str = content.decode('utf-8')
    # Use networkx to read the GraphML data from the string
    graph = nx.parse_graphml(content_str)

    # Print basic info about the graph
    console.print(f"Graph loaded: {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges", style="bold green")

    return graph


def read_graphml_fast(file_path: str) -> nx.Graph:
    return nx.read_graphml(file_path)

    

def copy_graph_with_attributes(source_graph: nx.Graph) -> nx.Graph:
    """
    Copy nodes, edges, and their attributes from the source graph to a new target graph.
    Both node attributes and edge attributes 

    Parameters:
    source_graph (nx.Graph): The source graph.

    Returns:
    nx.Graph: The new target graph with copied nodes, edges, and attributes.
    """
    target_graph = nx.Graph()

    # Copy nodes with attributes
    for node, attributes in source_graph.nodes(data=True):
        target_graph.add_node(node, **attributes)

    # Copy edges with attributes
    for u, v, attributes in source_graph.edges(data=True):
        target_graph.add_edge(u, v, **attributes)

    return target_graph

    
def iterate_graph(input_file, output_file):
    logger.info(f"Iterating network in file graph({input_file=} to copy to {output_file=} with  deanonymized github user emails")
    

    if not check_file_exists(input_file):
        logger.error(f"The file '{input_file}' does not exist.")
        sys.exit()
    else:
        logger.info (f"The file '{input_file}' to be copied and deanonymize  exist.")
    

    #if is_valid_graphml(input_file):
    #    logger.info(f"The file '{input_file}' is a valid GraphML file.")
    #else:
    #    logger.error(f"The file '{input_file}' is an invalid GraphML file.")
    #    sys.exit()



    # Read the input GraphML file
    logger.info(f"Reading input GraphML file: {input_file}")


    
    try:
        # Option 1) With the facing progress 
        # G = read_graphml_with_progress(input_file)

        # Option 2) Without the facing progress 
        G = read_graphml_fast(input_file)
        
        console.print("[green]Graph read successfully![/green]")
        # You can now work with the graph
        print(f"Number of nodes: {graph.number_of_nodes()}")
        print(f"Number of edges: {graph.number_of_edges()}")
    except Exception as e:
        console.print(f"[red]Failed to read the graph: {e}[/red]")
        


    # Create a new directed graph for the output
    G_copy = nx.Graph()


    #print_all_nodes(G)
    

  # Retrieve nodes and attributes
    nodes_data = G.nodes(data=True)

    table = Table(title="Nodes and Attributes")

    # Add columns to the table
    table.add_column("Node ID", style="bold cyan")
    table.add_column("Attributes", style="bold magenta")
    
    # Create a Live display
    with Live(table, console=console, refresh_per_second=3) as live:
        # Iterate over the nodes and their attributes
        for node, attributes in nodes_data:
            attr_str = ", ".join(f"{key}: {value}" for key, value in attributes.items())
            table.add_row(str(node), attr_str if attr_str else "None")
            live.update(table)



    logger.info(f"Coping node {G=} to {G_copy=}")
    G_copy=copy_graph_with_attributes(G)

    console.rule("Replacing emails and affiliations for each node using GitHub REST API")

    logger.info("Looking for @users.noreply.github.com emails to call the API")
    
    for node, data in G_copy.nodes(data=True):
        logger.debug("iterating over {node=}")
        
        console.print(f"Checking {node=} with {data['e-mail']=} and {data['affiliation']=}")

        old_email = data['e-mail']

        if '@users.noreply.github.com' in old_email:
            new_email, new_affiliation = deanonymize_github_user_with_cache_andPyGuthub (old_email)
            logger.info(f"Updating {node=}) with API results {new_email=} and {new_affiliation=}")
            data['e-mail']= new_email
            data['affiliation']= new_affiliation
                    
            
    # Write the copied graph to the output GraphML file
    logger.info(f"Writing output GraphML file: {output_file}")
    nx.write_graphml(G_copy, output_file)

    console.print(f"[bold green]Successfully copied the graph to {output_file}[/bold green]")



def validate_input_file(input_file):
    # Check if the file has a .graphML extension
    if not input_file.lower().endswith('.graphml'):
        logger.error(f"Error: The input file '{input_file}' does not have a .graphML extension.")
        sys.exit(1)  # Exit the program with an error code
    
def main():

    #log_messages()
    #console_messages()
    #display_advanced_text()
    #display_emojis()
    #demonstrate_traceback_exceptions()
    #status_messages()
    #progress_bars_demo()
    
    parser = argparse.ArgumentParser(description="Creates a more correct GraphML file by  correcting e-mails and affiliations via the GitHub REST API.")




    # Add input file argument - a must one 
    parser.add_argument(
        'input', 
        type=str, 
        help='Path to the input GraphML file.'
    )
    
    # Add output file argument with default value 
    parser.add_argument(
        'output', 
        type=str, 
        nargs='?',  # This makes the argument optional
        default=None,  # Default is None, will be set based on input_file
        help='Path to the output file (default: input_file.out).'
    )
    
    args = parser.parse_args()

        # Validate input file
    validate_input_file(args.input)
    
    # Set default for output_file if not provided
    if args.output is None:
        # Generate default output file name
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}.out.graphML"

    # Call the function to copy and modify the graph
    iterate_graph(args.input, args.output)

if __name__ == "__main__":
    main()



