from fixme.prompts.helpers import preamble
from fixme.prompts.helpers import gathered_info_message

diagnose_issue_prompt = (
    lambda command, stdout, stderr, cwd, gathered_info: f"""{preamble(command, stdout, stderr, cwd)}

Here is some extra information I gathered:

{gathered_info_message(gathered_info)}

Diagnose the issue based on the information I have gathered and explain the issue step by step in detail.

Here is the issue diagnosis:
"""
)
