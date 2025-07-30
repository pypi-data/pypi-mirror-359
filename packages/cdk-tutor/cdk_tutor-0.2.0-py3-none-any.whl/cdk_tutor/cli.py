from pathlib import Path
from typing import Dict, List, Optional
from threading import Thread, Event

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from cdk_tutor.challenges import get_available_challenges
from cdk_tutor.grader import grade_challenge

app = typer.Typer(
    name="cdk-tutor",
    help="Interactive tutorial for learning AWS CDK",
    add_completion=False,
)

console = Console()
loading_stop_event = Event()


def _loading_animation(event: Event) -> None:
    """Simple loading animation."""
    while not event.is_set():
        for frame in "|/-\\":
            print(f"\rGrading {frame}", end="", flush=True)
            event.wait(0.1)
    print("\r", end="", flush=True)


@app.command()
def list_challenges() -> None:
    """List all available challenges."""
    challenges = get_available_challenges()

    if not challenges:
        console.print(
            Panel("No challenges found", title="CDK Tutor", border_style="red")
        )
        return

    console.print(
        Panel("Available Challenges", title="CDK Tutor", border_style="green")
    )

    for i, challenge in enumerate(challenges, 1):
        console.print(f"[bold]{i}.[/bold] {challenge.name}")
        console.print(f"   [dim]{challenge.description}[/dim]")
        console.print()


@app.command()
def start(
    challenge_name: Optional[str] = typer.Argument(
        None, help="Name of the challenge to start"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output-dir", "-o", help="Directory to create the challenge files in"
    ),
) -> None:
    """Start a specific challenge."""
    challenges = get_available_challenges()

    if not challenges:
        console.print(
            Panel("No challenges found", title="CDK Tutor", border_style="red")
        )
        return

    # If no challenge name is provided, list challenges and ask user to choose
    if not challenge_name:
        console.print(
            Panel("Available Challenges", title="CDK Tutor", border_style="green")
        )

        for i, challenge in enumerate(challenges, 1):
            console.print(f"[bold]{i}.[/bold] {challenge.name}")
            console.print(f"   [dim]{challenge.description}[/dim]")
            console.print()

        selection = Prompt.ask(
            "Select a challenge",
            choices=[str(i) for i in range(1, len(challenges) + 1)],
            default="1",
        )

        selected_challenge = challenges[int(selection) - 1]
    else:
        # Find challenge by name
        try:
            selected_challenge = next(
                c for c in challenges if c.name.lower() == challenge_name.lower()
            )
        except StopIteration:
            selected_challenge = None

        if not selected_challenge:
            console.print(
                Panel(
                    f"Challenge '{challenge_name}' not found",
                    title="CDK Tutor",
                    border_style="red",
                )
            )
            return

    # Check if we have a valid challenge
    if not selected_challenge:
        return

    # Determine the output directory
    if not output_dir:
        default_dir = selected_challenge.name.lower().replace(" ", "-")
        output_dir = Prompt.ask(
            "Enter output directory name",
            default=default_dir,
        )

    # Make sure output_dir is not None at this point
    if not output_dir:
        output_dir = selected_challenge.name.lower().replace(" ", "-")

    output_path = Path(output_dir)

    # Create the output directory if it doesn't exist
    if output_path.exists() and any(output_path.iterdir()):
        overwrite = Prompt.ask(
            f"Directory '{output_dir}' already exists and is not empty. Overwrite?",
            choices=["y", "n"],
            default="n",
        )

        if overwrite.lower() != "y":
            console.print("Aborted.")
            return

    output_path.mkdir(exist_ok=True, parents=True)

    # Extract the challenge files to the output directory
    selected_challenge.extract_to(output_path)

    console.print(
        Panel(
            f"Challenge '{selected_challenge.name}' started in '{output_path}'",
            title="CDK Tutor",
            border_style="green",
        )
    )
    console.print()
    console.print(selected_challenge.get_instructions())
    console.print()
    console.print(
        "When you're ready to check your solution, run:\n"
        f"[bold]cdk-tutor grade {output_dir}[/bold]"
    )


@app.command()
def grade(
    challenge_dir: str = typer.Argument(
        ..., help="Directory containing the challenge to grade"
    ),
) -> None:
    """Grade a completed challenge."""
    challenge_path = Path(challenge_dir)

    if not challenge_path.exists() or not challenge_path.is_dir():
        console.print(
            Panel(
                f"Directory '{challenge_dir}' not found",
                title="CDK Tutor",
                border_style="red",
            )
        )
        return

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task_id = progress.add_task(description="Grading...", total=None)
            result = grade_challenge(challenge_path, progress, task_id)

        if result.passed:
            console.print(
                Panel(
                    "Challenge completed successfully! 🎉",
                    title="CDK Tutor - Success",
                    border_style="green",
                )
            )

            if result.next_challenge:
                console.print(
                    f"\nReady for the next challenge? Try:\n"
                    f'[bold]cdk-tutor start "{result.next_challenge}"[/bold]'
                )
        else:
            console.print(
                Panel(
                    "Challenge not yet completed",
                    title="CDK Tutor - Feedback",
                    border_style="yellow",
                )
            )

            if result.resources_feedback:
                _render_table_feedback("Resources Feedback", result.resources_feedback)

            if result.output_feedback:
                _render_table_feedback("Outputs Feedback", result.output_feedback)

            if result.generic_feedback:
                console.print("\n[bold]Feedback:[/bold]")
                for item in result.generic_feedback:
                    console.print(f"- {item}")

            console.print(
                "\nYou need to make the generated output similar to the expected one. Keep going! 💪"
            )

    except Exception as e:
        console.print(
            Panel(
                f"Error grading challenge: {str(e)}",
                title="CDK Tutor - Error",
                border_style="red",
            )
        )
        console.print_exception()


def _render_table_feedback(title: str, feedback: Dict[str, List[str]]) -> None:
    """Render feedback in a table format."""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold magenta",
        expand=True,
        show_lines=True,
    )

    table.add_column("Resource", style="dim")
    table.add_column("Feedback", justify="left")

    for resource_id, resource_feedback in feedback.items():
        listed_feedback = "\n".join(map(lambda s: f"- {s}", resource_feedback))
        table.add_row(resource_id, listed_feedback)

    console.print(table)


if __name__ == "__main__":
    app()
