import click
import openai
from rich.progress import track
from rich.console import Console
import subprocess
import os
from fixme.controller import Controller

console = Console()


def require_openai_api_key(func):
    def wrapper(*args, **kwargs):
        if not os.environ.get("OPENAI_API_KEY"):
            console.print(
                "[bold red]Please set the OPENAI_API_KEY environment variable.[/bold red]"
            )
            return

        openai.api_key = os.environ.get("OPENAI_API_KEY")
        return func(*args, **kwargs)

    return wrapper


@click.group()
@click.version_option()
def cli():
    "Use AI to automatically fix bugs"


@cli.command(name="command")
@click.argument(
    "full_command",
)
@require_openai_api_key
def command(full_command):
    "Fixes issues based on the output of the command"

    subprocess.call(
        full_command,
        shell=True,
        stdout=open("stdout.txt", "w"),
        stderr=open("stderr.txt", "w"),
    )

    with open("stdout.txt", "r") as f:
        stdout = f.read()
    with open("stderr.txt", "r") as f:
        stderr = f.read()

    controller = Controller(
        command=full_command,
        stdout=stdout,
        stderr=stderr,
    )

    controller.run()
