import sys
import subprocess
import logging
from datetime import datetime

# Configure logging
log_filename = "logs.txt"
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(message)s")


# Define constants for ANSI escape sequences for colors
class AnsiColor:
    """Constants for ANSI escape sequences for colors."""

    # Color definitions
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


# Define constants for terminal outputs
class Messages:
    """Constants for terminal output messages."""

    # Success
    SUCCESS_FILES_STAGED = "FILES ADDED TO STAGING AREA: OK"
    SUCCESS_COMMIT_CREATED = "COMMIT CREATED: OK"
    SUCCESS_CHANGES_PUSHED = "CHANGES PUSHED: OK"

    # Warnings
    WARNING_DEFAULT_BRANCH_NAME_USED = "USING DEFAULT BRANCH NAME: "

    # Failures
    FAILURE_CHANGES_NOT_PUSHED = "CHANGES HAVE NOT BEEN PUSHED"
    FAILURE_KEYBOARD_INTERRUPT = "YOU PRESSED CTRL+C TO END SCRIPT EXECUTION"

    # Information
    INFORMATION_TEXT = "TRYING TO PUSH CHANGES..."

    # Errors
    ERROR_TEXT = "ERROR: "
    ERROR_COMMIT_MESSAGE_EMPTY = (
        "Commit message cannot be empty. Please, enter a valid commit message"
    )
    ERROR_GIT_NOT_INSTALLED = (
        "Git is not installed or accessible. Please, install Git and try again."
    )


def is_git_installed() -> bool:
    """Check if Git is installed and accessible.

    This function checks if Git is installed and accessible in the current environment
    by attempting to execute the 'git --version' command. If the command executes
    successfully, it returns True, indicating that Git is installed and accessible.
    If the command fails (due to Git not being installed or not being accessible),
    it returns False.

    Returns:
        bool: True if Git is installed and accessible, False otherwise.
    """
    try:
        subprocess.check_output(["git", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_commit_message() -> str:
    """Prompt the user to enter a commit message.

    Returns:
        str: The commit message entered by the user.
    """
    while True:
        commit_message = input("Please, enter some message for this commit: ")
        if commit_message:
            return commit_message
        else:
            print(
                f"{AnsiColor.RED}{Messages.ERROR_COMMIT_MESSAGE_EMPTY}{AnsiColor.RESET}"
            )


def get_branch_name(default_branch_name: str) -> str:
    """Prompt the user to enter a branch name, or use a default value.

    Args:
        default_branch_name (str): The default branch name to use if none is specified.

    Returns:
        str: The branch name entered by the user, or the default branch name if none is specified.
    """
    branch_name = input(
        f"Please, enter the branch name ({default_branch_name} if not specified): "
    )
    if branch_name:
        return branch_name
    else:
        print(
            f"{AnsiColor.YELLOW}{Messages.WARNING_DEFAULT_BRANCH_NAME_USED}'{default_branch_name}'{AnsiColor.RESET}"
        )
        return default_branch_name


def run_git_command(command: list[str], command_name: str) -> str:
    """Run a git command and return the output.

    Args:
        command (list[str]): The git command to execute as a list of strings.
        command_name (str): The name of the git command for further error handling.

    Returns:
        str: The output of the executed git command.
    """
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        if "git add" in command_name:
            print(
                f"{AnsiColor.RED}Error occurred during 'git add' operation.{AnsiColor.RESET}"
            )
        elif "git commit" in command_name:
            print(
                f"{AnsiColor.RED}Error occurred during 'git commit' operation.{AnsiColor.RESET}"
            )
        elif "git push" in command_name:
            print(
                f"{AnsiColor.RED}Error occurred during 'git push' operation.{AnsiColor.RESET}"
            )

        error_message = e.output.strip()
        print(f"{AnsiColor.RED}{Messages.ERROR_TEXT}{error_message}{AnsiColor.RESET}")
        print(f"{AnsiColor.RED}{Messages.FAILURE_CHANGES_NOT_PUSHED}{AnsiColor.RESET}")

        # Log the error and the failure
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Commit message: {commit_message}, Branch name: {branch_name}, Result: FAIL, Error: {error_message}"
        logging.error(log_entry)

        sys.exit(1)


def main() -> None:
    """Main function to handle user input and run Git commands."""

    if not is_git_installed():
        print(f"{AnsiColor.RED}{Messages.ERROR_GIT_NOT_INSTALLED}{AnsiColor.RESET}")
        logging.error(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {Messages.ERROR_GIT_NOT_INSTALLED}"
        )
        sys.exit(1)

    default_branch_name = "master"

    try:
        commit_message: str = get_commit_message()
        branch_name: str = get_branch_name(default_branch_name)

        print(f"{AnsiColor.YELLOW}{Messages.INFORMATION_TEXT}{AnsiColor.RESET}")

        # Step 1: Add all of the files to the staging area
        git_add_command = ["git", "add", "."]
        run_git_command(git_add_command, "git add")
        print(f"{AnsiColor.GREEN}{Messages.SUCCESS_FILES_STAGED}{AnsiColor.RESET}")

        # Step 2: Commit the changes with the specified message
        git_commit_command = ["git", "commit", "-m", commit_message]
        run_git_command(git_commit_command, "git commit")
        print(f"{AnsiColor.GREEN}{Messages.SUCCESS_COMMIT_CREATED}{AnsiColor.RESET}")

        # Step 3: Push the changes to the remote repository
        git_push_command = ["git", "push", "-u", "origin", branch_name]
        run_git_command(git_push_command, "git push")

        # Log the success of the push operation
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Commit message: {commit_message}, Branch name: {branch_name}, Result: OK"
        logging.info(log_entry)
    except KeyboardInterrupt:
        print(
            f"{AnsiColor.RED}\n{Messages.FAILURE_KEYBOARD_INTERRUPT}{AnsiColor.RESET}"
        )
        print(f"{AnsiColor.RED}{Messages.FAILURE_CHANGES_NOT_PUSHED}{AnsiColor.RESET}")

        # Log the keyboard interrupt and failure
        log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Commit message: {commit_message}, Branch name: {branch_name}, Result: FAIL, Error: {Messages.FAILURE_KEYBOARD_INTERRUPT}"
        logging.error(log_entry)

        sys.exit(1)

    print(f"{AnsiColor.GREEN}{Messages.SUCCESS_CHANGES_PUSHED}{AnsiColor.RESET}")


if __name__ == "__main__":
    main()
