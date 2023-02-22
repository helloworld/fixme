gathered_info_message = lambda gathered_info: "\n".join(
    [f"{message}:\n{output}" for message, output in gathered_info]
)

diagnose_issue_prompt = (
    lambda command, stdout, stderr, cwd, gathered_info: f"""
I am a bot is fixing a bug. I am currently trying to fix the following command:
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

I have also have the ability to run the following commands to gather more information:
1. LIST_FILES_IN_DIRECTORY(path_to_directory)
2. CAT_FILE(path_to_file)
3. GREP(path,search_string)

Here is the information I gathered:

{gathered_info_message(gathered_info)}

Can you diagnose the issue based on the information I have gathered and explain it step by step in detail?

Here is the issue diagnosis:
"""
)
