from fixme.prompts.helpers import preamble
from fixme.prompts.helpers import gathered_info_message

generate_patch_prompt = (
    lambda command, stdout, stderr, cwd, gathered_info, issue_diagnosis: f"""{preamble(command, stdout, stderr, cwd)}

Here is some extra information I gathered:

{gathered_info_message(gathered_info)}

Here is the issue diagnosis:

{issue_diagnosis}

Generate a git patch file that fixes the issue and explain the patch in detail. I will save the patch file as "fix.patch" and directly apply the patch to the codebase. Put the explanation first.
Wrap the patch in a code block like so:

```diff
(patch goes here)
```

Here is the explanation and patch:
"""
)
