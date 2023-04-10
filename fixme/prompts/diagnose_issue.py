from fixme.prompts.helpers import (
    command_prompt,
    gathered_context_message,
    system_prompt,
)


def diagnose_issue_prompt(command, stdout, stderr, cwd, gathered_context):
    user_prompt = f"""{command_prompt(command, stdout, stderr, cwd)}

Here is some extra information I gathered:

{gathered_context_message(gathered_context)}

Diagnose the issue based on the information I have gathered and explain the issue step by step in detail. Be as concise as possible.

Here is the issue diagnosis:"""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
