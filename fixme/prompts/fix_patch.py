from fixme.prompts.helpers import gathered_context_message, preamble


def fix_patch_prompt(
    command, stdout, stderr, cwd, gathered_context, issue_diagnosis, patch
):
    return (
        f"{preamble(command, stdout, stderr, cwd)}\n\nHere is some extra information I"
        f" gathered:\n\n{gathered_context_message(gathered_context)}\n\nHere is the"
        f" issue diagnosis:\n\n{issue_diagnosis}\n\nI generated a patch file that fixes"
        f" the issue:\n\n{patch}\n"
    )
