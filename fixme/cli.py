import os
import subprocess
import tempfile
from typing import IO

import click

from fixme.api import OpenAIAPI
from fixme.console import console, mark_step
from fixme.session import Session


def require_api_key(func: callable):
    def wrapper(*args, **kwargs):
        if not os.environ.get("OPENAI_API_KEY"):
            console.print(
                "[bold red]"
                "Please set the OPENAI_API_KEY environment variable."
                "[/bold red]"
            )
            exit(1)

        return func(*args, **kwargs, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    return wrapper


@click.group()
@click.version_option()
def cli():
    """Use AI to automatically fix bugs."""


@cli.command(name="command")
@click.argument(
    "full_command",
)
@require_api_key
def fix_from_command(full_command: str, openai_api_key: str):
    """Fixes issues based on the output of the given command."""
    mark_step("Running command:", suffix=full_command)

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
        command=full_command,
        stdout=stdout_contents,
        stderr=stderr_contents,
        cwd=cwd,
    )
    patch = session.run()

    if patch:
        if click.confirm("Apply patch?"):
            session.apply_patch(patch=patch)
