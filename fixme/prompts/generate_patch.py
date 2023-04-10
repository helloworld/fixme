from fixme.prompts.helpers import (
    command_prompt,
    gathered_context_message,
    system_prompt,
)


def generate_patch_prompt(
    command, stdout, stderr, cwd, gathered_context, issue_diagnosis
):
    user_prompt = f"""{command_prompt(command, stdout, stderr, cwd)}

Here is some extra information I gathered:

{gathered_context_message(gathered_context)}

Here is the issue diagnosis:

{issue_diagnosis}

Generate a git patch file that fixes the issue and explain the patch in detail. I will save the patch file as "fix.patch" and directly apply the patch to the codebase. Put the explanation first.

IMPORTANT:
- Be very careful when generating the patch. The patch should only contain the changes that fix the issue.
- The patch should be generated from the current working directory.
- Be careful with file paths to make sure they are exact.

Wrap the patch in a code block like so:

```diff
(patch goes here)
```

Here is the explanation and patch:
"""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
