from fixme.prompts.helpers import command_prompt, system_prompt


def gather_information_prompt(command, stdout, stderr, cwd):
    user_prompt = f"""{command_prompt(command, stdout, stderr, cwd)}

To gather context for fixing the bug, you can run the following commands:
1. LS(path_to_directory) - List files in the directory to see if anything looks unusual or unexpected.
2. CAT(path_to_file) - View the contents of a specific file to see if it contains relevant information.
3. GREP(path, search_string) - Search for specific text within a file to find relevant information. Use sparingly as it can be resource-intensive.

When providing a list of commands for the bot to run, order the commands from most important to least important and use the minimum number of commands to gather the necessary information. Only use relevant and existing paths and files, and avoid using unnecessary commands that may not be relevant to the bug.

Here is an example response:

```
LIST_FILES_IN_DIRECTORY(/home/helloworld)
CAT_FILE(/home/helloworld/.bashrc)
CAT_FILE(/home/helloworld/main.py)
GREP(/home/helloworld/.bashrc,hello)
```

Here are the recommended commands:
"""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
