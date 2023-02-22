gather_information_prompt = (
    lambda command, stdout, stderr, cwd: f"""
I am a bot that can help you fix bugs. I am currently trying to fix the following command:
```
{command}
``  

I have run the command gathered the following outputs:
- stdout:
```
{stdout}
```

- stderr:
```
{stderr}
```

- current working directory:
```
{cwd}
``` 

I am now trying to gather more information to help me fix the bug.
I can run the following commands. Please provide a list of commands I should run to have sufficient context to fix the bug.
Each command should be on a new line, and must be in the following format:
1. LIST_FILES_IN_DIRECTORY(path_to_directory)
2. CAT_FILE(path_to_file)

I will run each command and gather the output. I will then use this information to fix the bug.

Here is an example response:

```
LIST_FILES_IN_DIRECTORY(/home/helloworld)
CAT_FILE(/home/helloworld/.bashrc)
```

Here are the commands to run:
"""
)
