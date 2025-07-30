from pathlib import Path
from typing import Dict, List, Optional

from rich.progress import Progress, TaskID
import yaml
from pydantic import BaseModel, Field

from cdk_tutor.grader.cf_comparator import CfTemplateComparator
from cdk_tutor.grader.cdk_runner import synthesize_cdk_template


class GradingResult(BaseModel):
    """Result of grading a challenge."""

    passed: bool
    generic_feedback: List[str] = Field(default_factory=list)
    resources_feedback: Dict[str, List[str]] = Field(default_factory=dict)
    output_feedback: Dict[str, List[str]] = Field(default_factory=dict)
    next_challenge: Optional[str] = None


def grade_challenge(challenge_dir: Path, progress: Progress, task_id: TaskID) -> GradingResult:
    """Grade a CDK challenge."""
    # Load challenge metadata
    try:
        with open(challenge_dir / ".cdk-tutor.yml", "r") as f:
            metadata = yaml.safe_load(f)
    except FileNotFoundError:
        return GradingResult(
            passed=False,
            generic_feedback=[
                "No challenge metadata found. Is this a valid challenge directory?"
            ],
        )

    challenge_name = metadata.get("challenge")

    if not challenge_name:
        return GradingResult(
            passed=False,
            generic_feedback=["Invalid challenge metadata: missing challenge name"],
        )

    # Find the corresponding challenge
    from cdk_tutor.challenges import get_available_challenges

    challenge = next(
        (c for c in get_available_challenges() if c.name == challenge_name),
        None,
    )

    if not challenge:
        return GradingResult(
            passed=False,
            generic_feedback=[
                f"Challenge '{challenge_name}' not found in available challenges"
            ],
        )

    progress.update(task_id, description="Synthesizing the CloudFormation template...")
    # Synthesize the CloudFormation template from the user's CDK code
    try:
        user_cf_template = synthesize_cdk_template(challenge_dir)
    except Exception as e:
        return GradingResult(
            passed=False,
            generic_feedback=[f"Error synthesizing CloudFormation template: {str(e)}"],
        )

    # Compare the user's template with the expected template
    progress.update(task_id, description="Comparing the result...")
    comparator = CfTemplateComparator(
        expected_template=challenge.expected_cf_template,
        user_template=user_cf_template,
    )
    comparison_result = comparator.compare()

    if comparison_result.is_match:
        return GradingResult(
            passed=True,
            generic_feedback=["All requirements completed successfully!"],
            next_challenge=challenge.next_challenge,
        )
    else:
        return GradingResult(
            passed=False,
            resources_feedback=comparison_result.resource_differences,
            output_feedback=comparison_result.output_differences,
        )

