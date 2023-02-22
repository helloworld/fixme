from fixme.prompts.helpers import preamble


gather_information_prompt = (
    lambda command, stdout, stderr, cwd: f"""{preamble(command, stdout, stderr, cwd)}

I am now trying to gather more information to help me fix the bug.
I can run the following commands. Provide a list of commands to run to gather context suffcient context.
Use the minimum number of commands to gather the information you need. Order the commands from most important to least important.
Be sure to only use paths and files you are sure exist and are relevant to the bug.
Each command should be on a new line, and must be in the following format:
1. LIST_FILES_IN_DIRECTORY(path_to_directory)
2. CAT_FILE(path_to_file)
3. GREP(path,search_string)

I will run each command and gather the output to help me fix the bug. 

First, explain why each command is important to gather context for the bug. Then, provide the commands to run.

Here is an example response:

```
LIST_FILES_IN_DIRECTORY(/home/helloworld)
CAT_FILE(/home/helloworld/.bashrc)
CAT_FILE(/home/helloworld/main.py)
GREP(/home/helloworld/.bashrc,hello)
```

Here are the commands to run:
"""
)
