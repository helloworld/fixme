def output_message(stdout, stderr):
    output = ""
    if stdout:
        output += f"- stdout:\n```\n{stdout}```\n"
    if stderr:
        output += f"- stderr:\n```\n{stderr}```\n"

    return output


system_prompt = (
    "As an expert programming bot, you are capable of fixing programming bugs given the"
    " terminal output of a command. In order to do this, you need to gather context"
    " about the bug by running specific commands."
)


def command_prompt(command, stdout, stderr, cwd):
    return (
        f"For this task, a bug was caused by the command '{command}' in directory"
        f" '{cwd}'. The command produced the following"
        f" outputs:\n{output_message(stdout, stderr)}"
    )


def gathered_context_message(gathered_context):
    return "\n".join([f"{message}:\n{output}" for message, output in gathered_context])


def preamble():
    raise NotImplementedError()
