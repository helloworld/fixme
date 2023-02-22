def output_message(stdout, stderr):
    output = ""
    if stdout:
        output += f"- stdout:\n```\n{stdout}```\n"
    if stderr:
        output += f"- stderr:\n```\n{stderr}```\n"

    return output


def preamble(command, stdout, stderr, cwd):
    return f"""I am a bot that can help you fix bugs. The bug was the result of the following command: `{command}` in the current working directory: `{cwd}`.

I have run the command gathered the following outputs:
{output_message(stdout, stderr)}"""


gathered_info_message = lambda gathered_info: "\n".join(
    [f"{message}:\n{output}" for message, output in gathered_info]
)
