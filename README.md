## git_push.py

This script automates the process of pushing all of the changes made to GitHub/GitLab via Git. 

### Process to be automated
Normally, this process involves the following steps:

1. Adding files to the staging area
    
    Command used to add all files to it: *git add .*

2. Commit changes using *git commit -m "some message"*

3. Finally, pushing changes using *git push -u origin master*

### How it works
This script requires user to input a commit message and a branch name. Afterward, if everything goes OK, all changes should be automatically pushed.

Code is capable of handling exceptions such as:

- KeyboardInterrupt: Stops script execution on Ctrl+C.
- subprocess.CalledProcessError: Deals with problems encountered during `subprocess.check_call()` execution. Related to problems that might occur when executing `git` commands.

**Notes:** 
- The script prompts for a commit message as a mandatory step.
- It also prompts for a branch name which is a non-mandatory step: In case there is no input for it, Python will assume **branch_name_by_default** variable value, defined in code, as the branch name to be used. Default value: master

### Running the script
```python 
py .\git_push.py
```
You will be asked to enter a commit message (mandatory) and a branch name (optional, defaults to master)

# Example output
Your execution should be outputting similiar as follows:

![alt text](success_output.png)

## Latest improvements

- Added logging support