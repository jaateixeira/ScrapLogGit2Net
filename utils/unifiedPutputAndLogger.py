#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from time import sleep

from loguru import logger
# Python data structures can be automatically pretty printed with syntax highlighting.
from rich import pretty
from rich import print

# You can then print strings or objects to the terminal in the usual way.
# Rich will do some basic syntax highlighting and format data structures to make them easier to read.
from rich import print as rprint
# Strings may contain Console Markup which can be used to insert color and styles in to the output.
from rich.markdown import Markdown
from rich import inspect
from rich.color import Color
# JSON gets easier to understand
from rich import print_json
from rich.json import JSON
# Rich has a Text class you can use to mark up strings with color and style attributes.
from rich.text import Text

# For configuring
from rich.traceback import install
from rich.traceback import Traceback

# Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the ‘task’, a progress bar, percentage complete, and estimated time remaining.
from rich.progress import Progress, TaskID



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






# Strings may contain Console Markup which can be used to insert color and styles in to the output.

pretty.install()

# Rich has an inspect() function which can generate a report on any Python object. It is a fantastic debug aid

# For complete control over terminal formatting, Rich offers a Console class.
# Most applications will require a single Console instance, so you may want to create one at the module level or as an attribute of your top-level object.
from rich.console import Console

# Initialize the console
console = Console()

# Rich supplies a logging handler which will format and colorize text written by Python’s logging module.
from rich.logging import RichHandler

# Add RichHandler to the loguru logger
logger.remove()  # Remove the default logger
logger.add(
    RichHandler(console=console, show_time=True, show_path=True, rich_tracebacks=True),
    format="{message}",  # You can customize this format as needed
    level="DEBUG",  # Set the desired logging level
    # level="INFO",  # Set the desired logging level
)

# Rich’s Table class offers a variety of ways to render tabular data to the terminal.

# Rich provides the Live  class to to animate parts of the terminal
# It's handy to annimate tables that grow row by row

# Rich provides the Align class to align rendable objects

# Rich can display continuously updated information regarding the progress of long running tasks / file copies etc. The information displayed is configurable, the default will display a description of the ‘task’, a progress bar, percentage complete, and estimated time remaining.

# Rich has a Text class you can use to mark up strings with color and style attributes.

# For configuring
from rich.traceback import install

# Install the Rich Traceback handler with custom options
install(
    show_locals=True,  # Show local variables in the traceback
    locals_max_length=10, locals_max_string=80, locals_hide_dunder=True, locals_hide_sunder=False,
    indent_guides=True,
    suppress=[__name__],
    # suppress=[your_module],  # Suppress tracebacks from specific modules
    # max_frames=3,  # Limit the number of frames shown
    max_frames=5,  # Limit the number of frames shown
    # width=50,  # Set the width of the traceback display
    width=100,  # Set the width of the traceback display
    extra_lines=3,  # Show extra lines of code around the error
    theme="solarized-dark",  # Use a different color theme
    word_wrap=True,  # Enable word wrapping for long lines
)

"""
This module  provides unified functions for stdout and a logger for all python scripts from the ScrapLogGit2Net family
"""


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
            # progress.console.print(f"Working on")
            progress.update(task2, advance=0.5)  # Update the second progress bar more slowly

    print("Counting to 100 and 200 completed!")


if __name__ == '__main__':
    print("Examples on how to use the unified functions and logger:")

    log_messages()
    console_messages()
    display_advanced_text()
    display_emojis()
    demonstrate_traceback_exceptions()
    status_messages()
    progress_bars_demo()

