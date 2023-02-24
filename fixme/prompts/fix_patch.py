from fixme.prompts.helpers import preamble
from fixme.prompts.helpers import gathered_info_message

fix_patch_prompt = (
    lambda command, stdout, stderr, cwd, gathered_info, issue_diagnosis, patch: f"""{preamble(command, stdout, stderr, cwd)}

Here is some extra information I gathered:

{gathered_info_message(gathered_info)}

Here is the issue diagnosis:

{issue_diagnosis}

I generated a patch file that fixes the issue:

{patch}
"""
)
