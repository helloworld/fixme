import openai
import subprocess
import re
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from fixme.prompts import (
    gather_information_prompt,
    diagnose_issue_prompt,
    generate_patch_prompt,
)
from fixme.utils import memoize_function_to_disk

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

    def _print_response(self, response, header):
        console.print(
            Panel.fit(
                response,
                title=header,
                border_style="green",
            ),
        )

    def _request_completion(self, prompt):
        def _request_completion(prompt):
            return openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.7,
            )

        response = _request_completion(prompt)

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
        suggested_patch = self.generate_patch(gathered_info, diagnosed_issue)
        # Save patch to file
        with open("patch.txt", "w") as f:
            f.write(suggested_patch)

    def _run_subprocess_command(self, command):
        console.print(f"[bold green]Running command:[/bold green] {command}")
        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT
            ).decode()
            return True, output
        except subprocess.CalledProcessError as e:
            return False, e.output.decode()

    def gather_information(self):
        console.print(
            "[bold blue]1. Figuring out what information to gather...[/bold blue]"
        )

        gathered_info = []
        prompt = gather_information_prompt(
            self.command, self.stdout, self.stderr, self.cwd
        )
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        self._print_response(response, header="Information to gather:")

        console.print("\n[bold blue]2. Gathering information...[/bold blue]")

        for message in response.split("\n"):
            if "LIST_FILES_IN_DIRECTORY(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"ls {path}"
                (_, output) = self._run_subprocess_command(command)
                gathered_info.append((message, output))
            elif "CAT_FILE(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"cat -n {path}"
                (_, output) = self._run_subprocess_command(command)
                gathered_info.append((message, output))
            elif "GREP(" in message:
                path, search_string = (
                    re.search(r"\(([^)]+)", message).group(1).split(",")
                )
                command = f"git grep -Rn {search_string} {path}"
                (success, output) = self._run_subprocess_command(command)
                if success and len(output) < 2000:
                    gathered_info.append((message, output))

        return gathered_info

    def diagnose_issue(self, gathered_info):
        console.print("[bold blue]3. Diagnosing issue...[/bold blue]")
        prompt = diagnose_issue_prompt(
            self.command, self.stdout, self.stderr, self.cwd, gathered_info
        )
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        self._print_response(response, header="Issue Diagnosis:")
        return response

    def _parse_patch_from_response(self, response):
        code_block = re.search(r"```diff(.*)```", response, re.DOTALL)
        if code_block:
            patch = code_block.group(1).splitlines()[1:]
            patch = [line for line in patch if not re.match(r"index \w+\.\.\w+", line)]
            return "\n".join(patch)
        else:
            return None

    def generate_patch(self, gathered_info, issue_diagnosis):
        console.print("[bold blue]4. Generating patch...[/bold blue]")
        prompt = generate_patch_prompt(
            self.command,
            self.stdout,
            self.stderr,
            self.cwd,
            gathered_info,
            issue_diagnosis,
        )
        self._print_prompt(prompt)
        response = self._request_completion(prompt)
        patch = self._parse_patch_from_response(response)
        self._print_response(response, header="Potential Patch:")
        self._print_response(patch, header="Parsed Patch:")
        return patch

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
