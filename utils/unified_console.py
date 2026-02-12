#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module  provides unified functions for stdout and a logger for all python scripts from the ScrapLogGit2Net family
"""


# TODO Implement function for the unused import statements
# TODO Fix status spinner

# To set some time delays
from time import sleep

# Rich has an inspect() function which can generate a report on any Python object.
# It is a fantastic debug aid
from rich import inspect
# Python data structures can be automatically pretty printed with syntax highlighting.
from rich import pretty
# Wth rprint, Rich will do some basic syntax highlighting and format data structures to make them easier to read.
from rich import print as rprint
from rich.color import Color
# For complete control over terminal formatting, Rich offers a Console class.
# Most applications will require a single Console instance, so you may want to create one at
# the module level or as an attribute of your top-level object.
from rich.console import Console
# JSON gets easier to understand
from rich.json import JSON
# Strings may contain Console Markup which can be used to insert color and styles in to the output.
from rich.markdown import Markdown

# Rich has a Text class you can use to mark up strings with color and style attributes.
from rich.text import Text

from rich.progress import Progress
from rich.progress import track

from rich import traceback



#from utils.unified_logger import logger

# Rich tables
from rich.table import Table


# TODO Document this import
# Rich can display continuously updated information regarding the progress of long executing tasks  file copies etc.
# The information displayed is configurable, the default will display a description of the ‘task’, a progress bar,
# percentage complete, and estimated time remaining.
# Rich’s Table class offers a variety of ways to render tabular data to the terminal.
# Rich provides the Live  class to animate parts of the terminal
# It's handy to animate tables that grow row by row

# Install the Rich Traceback handler with custom options
"""
traceback.install(
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
# Strings may contain Console Markup which can be used to insert color and styles in to the output.

pretty.install()

# Rich has an inspect() function which can generate a report on any Python object. It is a fantastic debug aid


# Initialize the console
console = Console()

# Rich provides the Live  class to  animate parts of the terminal
# It's handy to animate tables that grow row by row

# Rich provides the Align class to align renderable objects

# Rich can display continuously updated information regarding the progress of long-running tasks  / file copies etc.
# The information displayed is configurable, the default will display a description of the ‘task’,
# a progress bar, percentage complete, and estimated time remaining.



# For configuring
#from rich import traceback

# Install the Rich Traceback handler with custom options
"""
traceback.install(
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

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced console functions with rich formatting and emojis.
Pure message-based functions without exit codes.
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.box import ROUNDED, HEAVY, DOUBLE, SIMPLE

# Initialize the console
console = Console()


# ============================================================================
# MESSAGE TYPE FUNCTIONS WITH EMOJIS
# ============================================================================

def print_fatal_error(message: str, details: str = None) -> None:
    """
    Display a fatal error message.

    Args:
        message: The main error message
        details: Additional details (optional)
    """
    error_text = Text()
    error_text.append("💀 ", style="bold red")
    error_text.append("FATAL ERROR: ", style="bold white on red")
    error_text.append(message, style="bold red")

    if details:
        error_text.append("\n\n")
        error_text.append("Details: ", style="bold yellow")
        error_text.append(details, style="yellow")

    error_text.append("\n\n❌ ", style="bold red")
    error_text.append("Program cannot continue.", style="italic red")

    console.print("\n")
    console.print(Panel(
        error_text,
        title="[bold white]Critical Failure[/bold white]",
        border_style="red",
        box=HEAVY,
        padding=(1, 2)
    ))


def print_error(message: str, details: str = None) -> None:
    """
    Display an error message.

    Args:
        message: The main error message
        details: Additional details (optional)
    """
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append("Error: ", style="bold red")
    error_text.append(message, style="red")

    if details:
        error_text.append("\n")
        error_text.append("ℹ️  ", style="cyan")
        error_text.append(details, style="dim cyan")

    console.print("\n")
    console.print(Panel(
        error_text,
        border_style="red",
        box=ROUNDED,
        padding=(1, 1)
    ))


def print_warning(message: str, details: str = None, highlight: bool = False) -> None:
    """
    Display a warning message.

    Args:
        message: The main warning message
        details: Additional details (optional)
        highlight: If True, uses stronger styling (default: False)
    """
    warning_text = Text()

    if highlight:
        warning_text.append("🚨 ", style="bold yellow")
        warning_text.append("Important Warning: ", style="bold yellow")
        warning_text.append(message, style="bold yellow")

        if details:
            warning_text.append("\n")
            warning_text.append("📝 ", style="dim yellow")
            warning_text.append(details, style="dim yellow")

        console.print("\n")
        console.print(Panel(
            warning_text,
            title="[bold yellow]Attention Required[/bold yellow]",
            border_style="yellow",
            box=HEAVY,
            padding=(1, 2)
        ))
    else:
        warning_text.append("⚠️  ", style="yellow")
        warning_text.append("Warning: ", style="yellow")
        warning_text.append(message, style="yellow")

        if details:
            warning_text.append(" - ")
            warning_text.append(details, style="dim")

        console.print(warning_text)


def print_success(message: str, details: str = None, highlight: bool = False) -> None:
    """
    Display a success message.

    Args:
        message: The main success message
        details: Additional details (optional)
        highlight: If True, uses celebratory styling (default: False)
    """
    if highlight:
        success_text = Text()
        success_text.append("🎉 ", style="bold green")
        success_text.append("Success: ", style="bold green")
        success_text.append(message, style="bold green")

        if details:
            success_text.append("\n")
            success_text.append("✨ ", style="cyan")
            success_text.append(details, style="cyan")

        console.print("\n")
        console.print(Panel(
            success_text,
            title="[bold white]Achievement![/bold white]",
            border_style="green",
            box=DOUBLE,
            padding=(1, 2)
        ))
        console.print()
    else:
        success_text = Text()
        success_text.append("✅ ", style="green")
        success_text.append(message, style="green")

        if details:
            success_text.append(" - ")
            success_text.append(details, style="dim")

        console.print(success_text)


def print_key_action(message: str, symbol: str = "→", style: str = "bold blue") -> None:
    """
    Display a key action or step in a process.

    Args:
        message: The action description
        symbol: Symbol to use (default: →)
        style: Style for the message (default: bold blue)
    """
    action_text = Text()
    action_text.append(f"{symbol} ", style=style)
    action_text.append(message, style="bold")

    console.print(action_text)


def print_info(message: str, icon: str = "ℹ️", details: str = None) -> None:
    """
    Display an informational message.

    Args:
        message: The main info message
        icon: Icon to use (default: ℹ️)
        details: Additional details (optional)
    """
    info_text = Text()
    info_text.append(f"{icon} ", style="cyan")
    info_text.append(message, style="blue")

    if details:
        info_text.append("\n   ")
        info_text.append(details, style="dim")

    console.print(info_text)


def print_note(message: str, details: str = None) -> None:
    """
    Display a note message.

    Args:
        message: The main note
        details: Additional details (optional)
    """
    note_text = Text()
    note_text.append("📝 ", style="bold cyan")
    note_text.append("Note: ", style="bold cyan")
    note_text.append(message, style="cyan")

    if details:
        note_text.append("\n")
        note_text.append(details, style="dim")

    console.print(note_text)


def print_tip(message: str, details: str = None) -> None:
    """
    Display a helpful tip.

    Args:
        message: The main tip
        details: Additional details (optional)

    Returns:
        None: 
    """
    tip_text = Text()
    tip_text.append("💡 ", style="bold yellow")
    tip_text.append("Tip: ", style="bold yellow")
    tip_text.append(message, style="yellow")

    if details:
        tip_text.append("\n")
        tip_text.append(details, style="dim")

    console.print(tip_text)


def print_status(message: str, state: str = "processing") -> None:
    """
    Display a status message with appropriate emoji.

    Args:
        message: What's being done
        state: Current state (processing, done, waiting, etc.)
    """
    # Map states to emojis
    state_emojis = {
        "processing": "🔄",
        "working": "⚙️",
        "loading": "📥",
        "saving": "💾",
        "done": "✅",
        "complete": "✅",
        "ready": "✅",
        "waiting": "⏳",
        "paused": "⏸️",
        "stopped": "⏹️",
        "failed": "❌",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
    }

    emoji = state_emojis.get(state.lower(), "📌")

    status_text = Text()
    status_text.append(f"{emoji} ", style="bold")
    status_text.append(message, style="cyan")

    if state:
        status_text.append(f" [{state}]", style="dim")

    console.print(status_text)


def print_step(message: str, number: int = None, total: int = None) -> None:
    """
    Display a step in a process.

    Args:
        message: Step description
        number: Step number (optional)
        total: Total steps (optional)
    """
    step_text = Text()

    if number and total:
        step_text.append(f"Step {number}/{total}: ", style="bold magenta")
    elif number:
        step_text.append(f"Step {number}: ", style="bold magenta")
    else:
        step_text.append("• ", style="bold magenta")

    step_text.append(message, style="bold")

    console.print(step_text)


def print_header(title: str, emoji: str = "📌") -> None:
    """
    Display a section header.

    Args:
        title: Header title
        emoji: Leading emoji (default: 📌)
    """
    console.print()
    header_text = Text()
    header_text.append(f"{emoji} ", style="bold")
    header_text.append(title, style="bold white on blue")
    console.print(header_text)
    console.rule(style="blue")
    console.print()


def print_subheader(title: str, emoji: str = "↳") -> None:
    """
    Display a subheader.

    Args:
        title: Subheader title
        emoji: Leading symbol (default: ↳)
    """
    subheader_text = Text()
    subheader_text.append(f"{emoji} ", style="bold cyan")
    subheader_text.append(title, style="bold cyan underline")
    console.print(subheader_text)




def print_emoji_message(emoji: str, message: str, style: str = None) -> None:
    """
    Display a message with a custom emoji.

    Args:
        emoji: The emoji to use
        message: The message text
        style: Optional style (default: None)
    """
    message_text = Text()
    message_text.append(f"{emoji} ", style="bold")

    if style:
        message_text.append(message, style=style)
    else:
        message_text.append(message)

    console.print(message_text)




def console_messages() -> None:
    rprint("\n\t [green] Testing console messages:\n")

    markdown_text = Markdown("# This is a heading\n\n- This is a list item\n- Another item")
    console.print(markdown_text)

    console.print("\n [blue] Play with color and fonts \n")

    # An example of a styled message
    console.print("[bold blue]Welcome to [blink]Rich[/blink]![/bold blue]")
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.")
    console.print("[bold red]Error:[/bold red] Something went wrong. Please try again.")

    sleep(3)

    console.print("\n [blue] Play with underlines and backgrounds \n")

    # Other examples
    console.print([1, 2, 3])
    console.print("[blue underline]Looks like a link")

    console.print("FOO", style="white on blue")

    sleep(3)
    console.print("\n [blue]   console.print(locals()) \n")

    console.print(locals())
    sleep(3)
    console.print("\n [blue]   console.print(inspect(None, methods=True)) \n")
    console.print(inspect(None, methods=True))

    # Logging with time console.log("Hello, World!")

    sleep(3)

    console.print("\n [blue]   Use JSON format \n")
    # json and low level examples
    console.print_json('[false, true, null, "foo"]')
    console.log(JSON('["foo", "bar"]'))
    console.out("Locals", locals())

    sleep(3)
    console.print("\n [blue]   You can also add a rule \n")
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
            console.print(traceback.Traceback(), style="bold red")
            console.print(f"e={e}")  # Separator for clarity
            console.print("-" * 40)  # Separator for clarity


def status_messages():
    console.print("[blue] Counting started")
    # Create the status spinner and progress bar
    with console.status("[bold green]Processing... Counting to 100", spinner="dots") as status:
        # Loop from 1 to 100
        for i in range(1, 200):
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
            sleep(0.02)  # Simulate work being done
            progress.update(task1, advance=1)  # Update the first progress bar
            # progress.console.print(f"Working on")
            progress.update(task2, advance=0.5)  # Update the second progress bar more slowly

    print("Counting to 100 and 200 completed!")



def log_messages() -> None:
    rprint("\n\t [green] Testing logger messages:\n")

    # Log messages at different levels
    #logger.debug("This is a debug message.")
    #logger.info("This is an info message.")
    #logger.warning("This is a warning message.")
    #logger.error("This is an error message.")
    #logger.critical("This is a critical message.")
    rprint("\n")



if __name__ == '__main__':

    console.print("[bold blue]  How  about output to console/terminal")

    console_messages()
    console.print("[bold green]Success:[/bold green] Your saw many way to output. 😀\n")
    sleep(3)

    console.print("[bold blue] \n Displaying advanced text")
    display_advanced_text()
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.\n")
    sleep(3)

    console.print("[bold blue] \n Displaying emojis")
    display_emojis()
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.\n")
    sleep(3)

    demonstrate_traceback_exceptions()
    console.print("[bold blue] \n Displaying traceback exceptions")
    display_emojis()
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.\n")
    sleep(3)

    console.print("[bold blue] \n Displaying a status message with spinner")
    status_messages()
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.\n")
    sleep(3)

    console.print("[bold blue] \n Showing progress bars")
    progress_bars_demo()
    console.print("[bold green]Success:[/bold green] Your operation completed successfully.\n")


    console.print("[bold blue] \n You can log messages to terminal or separate log file")
    log_messages()
    console.print("[bold green]Success:[/bold green] You saw how to log  😀\n")
    sleep(3)

    console.print("[bold green]Success:[/bold green] Your saw many way to output. 😀\n")
    sleep(3)

    console.print("[bold blue] \n How  about inspecting objects")
    color = Color.parse("red")
    inspect(color, methods=True)

