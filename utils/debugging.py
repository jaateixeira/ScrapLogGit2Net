from scrapLog import ProcessingState
from utils.unified_console import print_success



def ask_yes_or_no_question(question: str) -> bool:
    response = input(f"{question} (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']


def ask_continue() -> bool:
    response = input("Do you want to continue? (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']


def ask_inspect_processing_state() -> bool:
    response = input("Do you want to inspect processing state ? (y/n): ").strip().lower()
    return response in ['y', 'yes', 'Y', 'YES']


def handle_step_completion(state: ProcessingState, step_name: str) -> None:
    """
    Handle the completion of a processing step with optional inspection and continuation.

    Args:
        state: The current processing state
        step_name: Name of the step being completed (for logging)
    """
    # Format a generic success message from the step name

    print_success(f"{step_name} completed successfully ✓")

    if state.debug_mode:
        if _ask_inspect_processing_state():
            print_info(f"Inspecting state at stage {step_name}")
            console.print(f'state={inspect(state)}')

        if not _ask_continue():
            print_info(f"Aborted by user at stage {step_name}")
            sys.exit()
