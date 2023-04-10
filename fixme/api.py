import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Tuple

import openai
from pydantic import BaseModel

from fixme.prompts.diagnose_issue import diagnose_issue_prompt
from fixme.prompts.gather_information import gather_information_prompt
from fixme.prompts.generate_patch import generate_patch_prompt


class DebugInformation(BaseModel):
    prompt: Dict[str, str]
    response: Optional[str]


class CommandContext(BaseModel):
    command: Optional[str]
    stdout: Optional[str]
    stderr: Optional[str]
    cwd: Optional[str]


class GatherContextResponse(BaseModel):
    debug: Optional[DebugInformation]
    gather_context_commands: List[Tuple[str, str]]


class DiagnoseIssueResponse(BaseModel):
    debug: Optional[DebugInformation]
    issue_diagnosis: str


class GeneratePatchResponse(BaseModel):
    debug: Optional[DebugInformation]
    patch: str


class Mode(Enum):
    CHAT = "chat"
    COMPLETION = "completion"


MODE: Mode = Mode.CHAT


class API(ABC):
    @abstractmethod
    def request_completion(self, prompt: str, max_tokens: int = 1024) -> str:
        pass

    @abstractmethod
    def gather_context(
        self,
        command_context: CommandContext,
    ) -> GatherContextResponse:
        pass

    @abstractmethod
    def diagnose_issue(
        self, command_context: CommandContext, gathered_context: List[Tuple[str, str]]
    ) -> DiagnoseIssueResponse:
        pass

    @abstractmethod
    def generate_patch(
        self,
        command_context: CommandContext,
        gathered_context: List[Tuple[str, str]],
        issue_diagnosis: str,
    ) -> GeneratePatchResponse:
        pass


class OpenAIAPI(API):
    def __init__(self, api_key):
        self._api_key = api_key

    def request_completion(self, prompt, max_tokens=1024, print_prompt=False):
        def _request_chatgpt(prompt):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": prompt["system_prompt"],
                    },
                    {"role": "user", "content": prompt["user_prompt"]},
                ],
            )

            return response.choices[0]["message"]["content"].strip()

        def _request_davinci(prompt):
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                n=1,
                stop=None,
                temperature=0.7,
            )

            return response.choices[0].text.strip()

        if MODE == Mode.CHAT:
            return _request_chatgpt(prompt)
        elif MODE == Mode.COMPLETION:
            return _request_davinci(prompt)
        else:
            raise ValueError(f"Unknown mode for request_completion: {MODE}")

    def gather_context(
        self,
        command_context: CommandContext,
    ) -> GatherContextResponse:
        debug = True

        prompt = gather_information_prompt(
            command=command_context.command,
            stdout=command_context.stdout,
            stderr=command_context.stderr,
            cwd=command_context.cwd,
        )
        response = self.request_completion(prompt)

        gather_context_commands = []
        for message in response.split("\n"):
            if "LS(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"ls {path}"
                gather_context_commands.append((message, command))
            elif "CAT(" in message:
                path = re.search(r"\(([^)]+)", message).group(1)
                command = f"cat -n {path}"
                gather_context_commands.append((message, command))
            elif "GREP(" in message:
                path, search_string = (
                    re.search(r"\(([^)]+)", message).group(1).split(",")
                )
                command = f"git grep -Rn {search_string} {path}"
                gather_context_commands.append((message, command))

        return GatherContextResponse(
            gather_context_commands=gather_context_commands,
            debug=DebugInformation(prompt=prompt, response=response) if debug else None,
        )

    def diagnose_issue(
        self, command_context: CommandContext, gathered_context: List[Tuple[str, str]]
    ) -> DiagnoseIssueResponse:
        debug = True

        prompt = diagnose_issue_prompt(
            command=command_context.command,
            stdout=command_context.stdout,
            stderr=command_context.stderr,
            cwd=command_context.cwd,
            gathered_context=gathered_context,
        )
        issue_diagnosis = self.request_completion(prompt)

        return DiagnoseIssueResponse(
            issue_diagnosis=issue_diagnosis,
            debug=(
                DebugInformation(prompt=prompt, response=issue_diagnosis)
                if debug
                else None
            ),
        )

    def generate_patch(
        self,
        command_context: CommandContext,
        gathered_context: List[Tuple[str, str]],
        issue_diagnosis: str,
    ) -> GeneratePatchResponse:
        debug = True

        prompt = generate_patch_prompt(
            command=command_context.command,
            stdout=command_context.stdout,
            stderr=command_context.stderr,
            cwd=command_context.cwd,
            gathered_context=gathered_context,
            issue_diagnosis=issue_diagnosis,
        )
        patch = self.request_completion(prompt)

        return GeneratePatchResponse(
            patch=patch,
            debug=DebugInformation(prompt=prompt, response=patch) if debug else None,
        )
