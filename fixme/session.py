import os
import re
import subprocess
import tempfile

from rich.panel import Panel

from fixme.api import API, CommandContext
from fixme.console import console, mark_step
from fixme.utils import memoize_function_to_disk


class Session:
    def __init__(self, fixme_client, command, stdout, stderr, cwd):
        self._api_client: API = fixme_client
        self._command_context = CommandContext(
            command=command, stdout=stdout, stderr=stderr, cwd=cwd
        )

    def run(self):
        gathered_context = self.gather_context()
        issue_diagnosis = self.diagnose_issue(gathered_context=gathered_context)
        return self.generate_patch(
            gathered_context=gathered_context, issue_diagnosis=issue_diagnosis
        )

    def _run_subprocess_command(self, command):
        console.print(f"[bold green]Running command:[/bold green] {command}")
        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT
            ).decode()
            return True, output
        except subprocess.CalledProcessError as e:
            return False, e.output.decode()

    def _print_output(self, output, header):
        console.print(
            Panel.fit(
                output,
                title=header,
                border_style="green",
            ),
        )

    def _print_debug_information(self, response, header=""):
        def _print_prompt(prompt, header=""):
            relative_path = os.path.join(os.path.dirname(__file__), "prompts")
            os.makedirs(relative_path, exist_ok=True)
            file_path = os.path.join(relative_path, f"{header}.txt")
            with open(file_path, "w") as f:
                f.write(prompt["system_prompt"])
                f.write("\n")
                f.write(prompt["user_prompt"])

            console.print(f"[bold blue]Prompt {header}:[/bold blue]\n{prompt}")

        def _print_response(response, header):
            console.print(f"[bold green]Response {header}:[/bold green]\n{response}")

        if "debug" in response and response["debug"]:
            prompt = response["debug"]["prompt"]
            response = response["debug"]["response"]

            _print_prompt(prompt, header)
            _print_response(response, header)

    @memoize_function_to_disk
    def _gather_context_request(self):
        return self._api_client.gather_context(
            command_context=self._command_context,
        )

    def gather_context(self):
        mark_step("Gathering context...")
        response = self._gather_context_request()
        gather_context_commands = response.gather_context_commands

        gathered_context = []
        for message, command in gather_context_commands:
            success, output = self._run_subprocess_command(command)
            if "GREP(" in message and success and len(output) < 2000:
                gathered_context.append((message, output))
            else:
                gathered_context.append((message, output))

        console.print("\n")
        return gathered_context

    @memoize_function_to_disk
    def _diagnose_issue_request(self, gathered_context):
        return self._api_client.diagnose_issue(
            command_context=self._command_context,
            gathered_context=gathered_context,
        )

    def _parse_patch(self, patch):
        code_block = re.search(r"```diff(.*)```", patch, re.DOTALL)
        if code_block:
            patch = code_block.group(1).splitlines()[1:]
            patch = [line for line in patch if not re.match(r"index \w+\.\.\w+", line)]
            return "\n".join(patch)
        else:
            return None

    def _validate_patch(self, patch, retries=0, max_retries=5):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(patch)
            f.flush()
            patch_file = f.name

            mark_step("Validating patch...")
            try:
                subprocess.run(
                    f"git apply --check {patch_file}", shell=True, check=True
                )
                return True, patch

            except subprocess.CalledProcessError:
                return False, patch

    def diagnose_issue(self, gathered_context):
        mark_step("Diagnosing issue...")
        response = self._diagnose_issue_request(gathered_context=gathered_context)
        issue_diagnosis = response.issue_diagnosis
        self._print_output(issue_diagnosis, header="Issue Diagnosis")
        return issue_diagnosis

    def _generate_patch_request(self, gathered_context, issue_diagnosis):
        return self._api_client.generate_patch(
            command_context=self._command_context,
            gathered_context=gathered_context,
            issue_diagnosis=issue_diagnosis,
        )

    def generate_patch(
        self, gathered_context, issue_diagnosis, attempts=0, max_attempts=5
    ):
        if attempts > max_attempts:
            console.print(
                Panel.fit(
                    "Maximum retries exceeded.",
                    title="Error",
                    border_style="red",
                ),
            )
            return None

        mark_step("Generating patch...")
        response = self._generate_patch_request(
            gathered_context=gathered_context, issue_diagnosis=issue_diagnosis
        )
        patch = response.patch
        parsed_patch = self._parse_patch(patch)
        self._print_output(parsed_patch, header="Patch")

        is_patch_valid, patch = self._validate_patch(parsed_patch)
        if not is_patch_valid:
            console.print(
                Panel.fit(
                    (
                        "Patch is invalid. Trying again. Attempt"
                        f" {attempts + 1}/{max_attempts}."
                    ),
                    title="Error",
                    border_style="red",
                ),
            )

            return self.generate_patch(
                gathered_context=gathered_context,
                issue_diagnosis=issue_diagnosis,
                attempts=attempts + 1,
                max_attempts=max_attempts,
            )
        else:
            console.print(
                Panel.fit(
                    "Patch is valid!.",
                    title="Success",
                    border_style="green",
                ),
            )

        return patch

    def apply_patch(self, patch):
        mark_step("Applying patch...")
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(patch)
            f.flush()
            patch_file = f.name

            try:
                subprocess.run(f"git apply {patch_file}", shell=True, check=True)
                console.print(
                    Panel.fit(
                        "Patch applied successfully.",
                        title="Success",
                        border_style="green",
                    ),
                )
            except subprocess.CalledProcessError:
                console.print(
                    Panel.fit(
                        "Patch could not be applied.",
                        title="Error",
                        border_style="red",
                    ),
                )
