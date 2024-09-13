import sys
import subprocess
import logging
from datetime import datetime
from enum import Enum, auto

# Configure logging
log_filename = "logs.txt"
logging.basicConfig(filename=log_filename,
                    level=logging.INFO, format="%(message)s")


class AnsiColor(Enum):
    """Enum for ANSI escape sequences for colors."""
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


class MessageType(Enum):
    """Enum for types of messages."""
    SUCCESS = auto()
    WARNING = auto()
    FAILURE = auto()
    INFORMATION = auto()
    ERROR = auto()


class Messages(Enum):
    """Enum for terminal output messages."""
    SUCCESS_FILES_STAGED = (MessageType.SUCCESS,
                            "FILES ADDED TO STAGING AREA: OK")
    SUCCESS_COMMIT_CREATED = (MessageType.SUCCESS, "COMMIT CREATED: OK")
    SUCCESS_CHANGES_PUSHED = (MessageType.SUCCESS, "CHANGES PUSHED: OK")
    WARNING_DEFAULT_BRANCH_NAME_USED = (
        MessageType.WARNING, "USING DEFAULT BRANCH NAME: ")
    FAILURE_CHANGES_NOT_PUSHED = (
        MessageType.FAILURE, "CHANGES HAVE NOT BEEN PUSHED")
    FAILURE_KEYBOARD_INTERRUPT = (
        MessageType.FAILURE, "YOU PRESSED CTRL+C TO END SCRIPT EXECUTION")
    INFORMATION_TEXT = (MessageType.INFORMATION, "TRYING TO PUSH CHANGES...")
    ERROR_TEXT = (MessageType.ERROR, "ERROR: ")
    ERROR_COMMIT_MESSAGE_EMPTY = (
        MessageType.ERROR, "Commit message cannot be empty. Please, enter a valid commit message")
    ERROR_GIT_NOT_INSTALLED = (
        MessageType.ERROR, "Git is not installed or accessible. Please, install Git and try again.")

    def __init__(self, message_type, text):
        self.message_type = message_type
        self.text = text


def print_message(message: Messages, additional_text: str = ""):
    """Print a formatted message based on its type."""
    color = AnsiColor.RESET
    if message.message_type == MessageType.SUCCESS:
        color = AnsiColor.GREEN
    elif message.message_type == MessageType.WARNING:
        color = AnsiColor.YELLOW
    elif message.message_type in (MessageType.FAILURE, MessageType.ERROR):
        color = AnsiColor.RED

    print(f"{color.value}{message.text}{
          additional_text}{AnsiColor.RESET.value}")


def is_git_installed() -> bool:
    """Check if Git is installed and accessible."""
    try:
        subprocess.check_output(["git", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def set_commit_message() -> str:
    """Prompt the user to enter a commit message."""
    while True:
        commit_message = input("Please, enter some message for this commit: ")
        if commit_message:
            return commit_message
        else:
            print_message(Messages.ERROR_COMMIT_MESSAGE_EMPTY)


def set_branch_name(default_branch_name: str) -> str:
    """Prompt the user to enter a branch name, or use a default value."""
    branch_name = input(f"Please, enter the branch name ({
                        default_branch_name} if not specified): ")
    if branch_name:
        return branch_name
    else:
        print_message(Messages.WARNING_DEFAULT_BRANCH_NAME_USED,
                      f"'{default_branch_name}'")
        return default_branch_name


def run_git_command(command: list[str], command_name: str, commit_message: str, branch_name: str) -> str:
    """Run a git command and return the output."""
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        if "git add" in command_name:
            print_message(Messages.ERROR_TEXT,
                          "Error occurred during 'git add' operation.")
        elif "git commit" in command_name:
            print_message(Messages.ERROR_TEXT,
                          "Error occurred during 'git commit' operation.")
        elif "git push" in command_name:
            print_message(Messages.ERROR_TEXT,
                          "Error occurred during 'git push' operation.")

        error_message = e.output.strip()
        print_message(Messages.ERROR_TEXT, error_message)
        print_message(Messages.FAILURE_CHANGES_NOT_PUSHED)

        # Log the error and the failure
        date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{date_and_time} - Commit message: {commit_message} | Branch name: {
            branch_name} | Result: FAIL | Error: {error_message}"
        logging.error(log_entry)

        sys.exit(1)


def main() -> None:
    """Main function to handle user input and run Git commands."""
    if not is_git_installed():
        print_message(Messages.ERROR_GIT_NOT_INSTALLED)
        date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"{date_and_time} | {
                      Messages.ERROR_GIT_NOT_INSTALLED.text}")
        sys.exit(1)

    try:
        commit_message: str = set_commit_message()

        default_branch_name = "master"
        branch_name: str = set_branch_name(default_branch_name)

        print_message(Messages.INFORMATION_TEXT)

        # Step 1: Add all of the files to the staging area
        git_add_command = ["git", "add", "."]
        run_git_command(git_add_command, "git add",
                        commit_message, branch_name)
        print_message(Messages.SUCCESS_FILES_STAGED)

        # Step 2: Commit the changes with the specified message
        git_commit_command = ["git", "commit", "-m", commit_message]
        run_git_command(git_commit_command, "git commit",
                        commit_message, branch_name)
        print_message(Messages.SUCCESS_COMMIT_CREATED)

        # Step 3: Push the changes to the remote repository
        git_push_command = ["git", "push", "-u", "origin", branch_name]
        run_git_command(git_push_command, "git push",
                        commit_message, branch_name)

        # Log the success of the push operation
        date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{date_and_time} - Commit message: {
            commit_message} | Branch name: {branch_name} | Result: OK"
        logging.info(log_entry)
    except KeyboardInterrupt:
        print_message(Messages.FAILURE_KEYBOARD_INTERRUPT)
        print_message(Messages.FAILURE_CHANGES_NOT_PUSHED)

        # Log the keyboard interrupt and failure
        try:
            commit_message = commit_message
        except NameError:
            commit_message = "N/A"

        try:
            branch_name = branch_name
        except NameError:
            branch_name = "N/A"

        date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{date_and_time} - Commit message: {commit_message} | Branch name: {
            branch_name} | Result: FAIL | Error: {Messages.FAILURE_KEYBOARD_INTERRUPT.text}"
        logging.error(log_entry)

        sys.exit(1)

    print_message(Messages.SUCCESS_CHANGES_PUSHED)


if __name__ == "__main__":
    main()
