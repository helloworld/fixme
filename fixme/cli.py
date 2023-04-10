import subprocess
import tempfile
import textwrap
from typing import IO

import click

from fixme.api import OpenAIAPI
from fixme.console import console, mark_step
from fixme.session import Session
from fixme.utils import require_api_key

HELP_TEXT = textwrap.dedent(
    """\
Use AI to automatically fix bugs based on the output of a given command.

Examples:

  # Debug errors based on the output of a command or a stack trace

  > fixme python main.py

  # Debug errors based on test runner output

  > fixme pytest

  > fixme npm run test
"""
)


@click.command(
    name="fixme", context_settings=dict(ignore_unknown_options=True), help=HELP_TEXT
)
@click.version_option()
@click.argument(
    "full_command",
    nargs=-1,  # Accepts any number of arguments
    type=click.UNPROCESSED,  # Keeps the raw input format
    required=False,
)
@click.pass_context
@require_api_key
def cli(ctx: click.Context, full_command: str, openai_api_key: str):
    if not full_command:
        click.echo(ctx.get_help())
        ctx.exit()

    full_command_joined = " ".join(full_command)

    mark_step("Running command:", suffix=full_command_joined)

    stdout_contents: bytes = None
    stderr_contents: bytes = None

    def _process_output(stream: IO[bytes], file: IO, label: str):
        if stream:
            console.print("\n")
            if label:
                console.print("[bold green]stdout:[/bold green]")
            for line in iter(process.stdout.readline, b""):
                console.print(line.decode().strip())
                stdout.write(line)

            stdout.seek(0)
            console.print("\n")
            return stdout.read().decode()

    with tempfile.NamedTemporaryFile(
        delete=False
    ) as stdout, tempfile.NamedTemporaryFile(delete=False) as stderr:
        process = subprocess.Popen(
            full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        print_labels = False
        if process.stdout and process.stderr:
            print_labels = True

        if process.stdout:
            stdout_contents = _process_output(
                stream=process.stdout,
                file=stdout,
                label="stdout" if print_labels else None,
            )

        if process.stderr:
            stderr_contents = _process_output(
                stream=process.stderr,
                file=stderr,
                label="stderr" if print_labels else None,
            )

        process.wait()

    cwd = subprocess.check_output("pwd", shell=True).decode().strip()

    client = OpenAIAPI(api_key=openai_api_key)
    session = Session(
        fixme_client=client,
        command=full_command_joined,
        stdout=stdout_contents,
        stderr=stderr_contents,
        cwd=cwd,
    )
    patch = session.run()

    if patch:
        if click.confirm("Apply patch?"):
            session.apply_patch(patch=patch)
