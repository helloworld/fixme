import openai
import subprocess
import re
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from fixme.prompts import gather_information_prompt, diagnose_issue_prompt

console = Console()
DEBUG = False

class Controller:
    def __init__(self, command, stdout, stderr):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.cwd = subprocess.check_output("pwd", shell=True).decode().strip()

    def _print_status(self, status):
        console.print(f"[bold blue]{status}[/bold blue]")

    def _print_prompt(self, prompt):
        console.print(
            Panel.fit(
                prompt,
                title="Prompt",
                border_style="blue",
            ),
        )

    def _print_response(self, response, header=None):
        if header:
            console.print(f"[bold green]{header}[/bold green]")

        console.print(
            Panel.fit(
                response,
                border_style="green",
            ),
        )

    def _request_completion(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )

        if DEBUG:
            console.print(
                Panel.fit(
                    Pretty(response),
                    title="Response",
                    border_style="red",
                ),
            )

        return response.choices[0].text.strip()

    def run(self):
        gathered_info = self.gather_information()
        diagnosed_issue = self.diagnose_issue(gathered_info)
        suggested_patch = self.generate_patch(diagnosed_issue)

    def gather_information(self):
        console.print("[bold blue]1. Figuring out what information to gather...[/bold blue]")

        gathered_info = []
        prompt = gather_information_prompt(
            self.command, self.stdout, self.stderr, self.cwd
        )
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        self._print_response(response, header="Information to gather:")

        for message in response.split("\n"):
            if "LIST_FILES_IN_DIRECTORY(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"ls -n {path}"
                console.print(f"[bold blue]Running command:[/bold blue] {command}")
                output = subprocess.check_output(command, shell=True).decode()
                gathered_info.append((message, output))
            elif "CAT_FILE(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"cat -n {path}"
                console.print(f"[bold blue]Running command:[/bold blue] {command}")
                output = subprocess.check_output(command, shell=True).decode()
                gathered_info.append((message, output))
            elif "GREP(" in message:
                path, search_string = (
                    re.search(r"\(([^)]+)", message).group(1).split(",")
                )
                command = f"grep -Rn {search_string} {path}"
                console.print(f"[bold blue]Running command:[/bold blue] {command}")
                output = subprocess.check_output(command, shell=True).decode()
                gathered_info.append((message, output))
            else:
                print("Invalid command received from AI.")
                break

        return gathered_info

    def diagnose_issue(self, gathered_info):
        console.print("[bold blue]2. Diagnosing issue...[/bold blue]")
        prompt = diagnose_issue_prompt(
            self.command, self.stdout, self.stderr, self.cwd, gathered_info
        )
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        self._print_response(response, header="Issue Diagnosis:")
        return response

    def generate_patch(self, issue_diagnosis):
        console.print("[bold blue]3. Generating patch...[/bold blue]")
        prompt = f"Here is the issue diagnosis:\n{issue_diagnosis}\n\nCan you provide a git patch that fixes the issue?g"
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        self._print_response(response, header="Potential Patch:")
        return response

    def validate_patch(self, patch, retries=0, max_retries=5):
        if retries > max_retries:
            console.print(
                Panel.fit(
                    "Maximum retries exceeded.",
                    title="Error",
                    border_style="red",
                ),
            )
            return

        console.print("[bold blue]4. Validating patch...[/bold blue]")
        try:
            subprocess.run(f"git apply {patch}", shell=True, check=True)
            console.print("[bold green]Patch applied successfully![/bold green]")
        except subprocess.CalledProcessError as e:
            console.print(
                Panel.fit(
                    str(e),
                    title="Error",
                    border_style="red",
                ),
            )
            console.print("[bold blue]Fixing patch...[/bold blue]")
            prompt = (
                f"Here is the issue with the patch:\n{str(e)}\n\nCan you fix the patch?"
            )
            self._print_prompt(prompt)
            response = self._request_completion(prompt)
            return self.validate_patch(
                response, retries=retries + 1, max_retries=max_retries
            )
