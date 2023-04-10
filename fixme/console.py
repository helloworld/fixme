from rich.console import Console
from rich.spinner import Spinner

console = Console()
spinner = Spinner("dots")

STEP_COUNT = 1


def mark_step(heading: str, suffix: str = ""):
    global STEP_COUNT
    suffix = f" {suffix}" if suffix else ""
    console.print(f"[bold blue]{STEP_COUNT}. {heading}[/bold blue]{suffix}")
    STEP_COUNT += 1
