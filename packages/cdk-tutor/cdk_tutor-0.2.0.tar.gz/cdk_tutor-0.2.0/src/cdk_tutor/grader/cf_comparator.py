from collections import defaultdict
from typing import Any, Dict, List, Optional

from deepdiff import DeepDiff
from pydantic import BaseModel
from rich.console import Console

console = Console()


class ComparisonResult(BaseModel):
    """Result of comparing two CloudFormation templates."""

    resource_differences: Dict[str, List[str]]
    output_differences: Dict[str, List[str]]

    @property
    def is_match(self) -> bool:
        return len(self.resource_differences) == 0 and len(self.output_differences) == 0


class CfTemplateComparator:

    def __init__(
        self, expected_template: Dict[str, Any], user_template: Dict[str, Any]
    ):
        self.normalize_template(user_template)
        self.expected_template = expected_template
        self.user_template = user_template

    @property
    def user_resources(self) -> Dict[str, Any]:
        return self.user_template.get("Resources", {})

    @property
    def expected_resources(self) -> Dict[str, Any]:
        return self.expected_template.get("Resources", {})

    @property
    def user_output(self) -> Dict[str, Any]:
        return self.user_template.get("Outputs", {})

    @property
    def expected_output(self) -> Dict[str, Any]:
        return self.expected_template.get("Outputs", {})

    def compare(self) -> ComparisonResult:
        """
        Compare a user's CloudFormation template with the expected template.

        This function uses DeepDiff to compare the templates and format the differences
        in a human-readable way.
        """
        return ComparisonResult(
            resource_differences=self._clean_empty_diffs(self._compare_resources()),
            output_differences=self._clean_empty_diffs(self._compare_outputs()),
        )

    def _clean_empty_diffs(self, d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in d.items() if v}

    def _compare_resources(self) -> Dict[str, List[str]]:
        # Find differences in the resources section
        formatted_differences: Dict[str, List[str]] = defaultdict(list)
        for expected_resource_key, expected_resource in self.expected_resources.items():
            expected_resource_type = expected_resource.get("Type")
            user_resource = self.user_resources.get(expected_resource_key)
            if not user_resource:
                formatted_differences[expected_resource_key].append(
                    f"Missing resource (Type: {expected_resource_type})"
                )
                continue

            # Check resource type
            user_resource_type = user_resource.get("Type")
            if user_resource_type != expected_resource_type:
                formatted_differences[expected_resource_key].append(
                    f"Different resource type: expected [green]{expected_resource_type}[/green], got [red]{user_resource_type}[/red]",
                )
                continue

            # Check other properties
            resource_properties_diff = self._compare_item_properties(
                expected_resource, user_resource
            )
            formatted_differences[expected_resource_key].extend(
                resource_properties_diff
            )

        # Find extra unexpected resources
        for user_resource_key in self.user_resources:
            if user_resource_key not in self.expected_resources:
                formatted_differences[user_resource_key].append(
                    "Extra unexpected resource"
                )

        return formatted_differences

    def _compare_outputs(self) -> Dict[str, List[str]]:
        result = defaultdict(list)
        for expected_output_key, expected_output in self.expected_output.items():
            user_output = self.user_output.get(expected_output_key)
            if not user_output:
                result[expected_output_key].append("Missing output")
                continue

            # Check output properties
            output_properties_diff = self._compare_item_properties(
                expected_output, user_output
            )
            if output_properties_diff:
                result[expected_output_key].extend(output_properties_diff)

        # Find extra unexpected outputs
        for user_output_key in self.user_output:
            if user_output_key not in self.expected_output:
                result[user_output_key].append(
                    "Extra unexpected output"
                )

        return result

    def _compare_item_properties(
        self, expected_resource: Dict[str, Any], user_resource: Dict[str, Any]
    ) -> List[str]:
        differences: List[str] = []

        diff = DeepDiff(
            expected_resource,
            user_resource,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
        )
        if not diff:
            return differences

        # Handle missing resources
        if "dictionary_item_removed" in diff:
            for path in diff["dictionary_item_removed"]:
                differences.append(f"Missing item at {path}")

        # Handle extra resources
        if "dictionary_item_added" in diff:
            for path in diff["dictionary_item_added"]:
                differences.append(f"Extra item at {path}")

        # Handle value changes
        if "values_changed" in diff:
            for path, value_diff in diff["values_changed"].items():
                old_value = value_diff.get("old_value")
                new_value = value_diff.get("new_value")
                if old_value and new_value:
                    differences.append(
                        f"Different value at {path}: expected [green]{old_value}[/green], got [red]{new_value}[/red]"
                    )

        # Handle type changes
        if "type_changes" in diff:
            for path, type_diff in diff["type_changes"].items():
                old_type = type_diff.get("old_type")
                new_type = type_diff.get("new_type")
                old_value = type_diff.get("old_value")
                new_value = type_diff.get("new_value")

                if old_type and new_type:
                    differences.append(
                        f"Different type at {path}: expected [green]{old_type}[/green], got [red]{new_type}[/red]"
                    )

                if old_value and new_value:
                    differences.append(
                        f"Different value at {path}: expected [green]{old_value}[/green], got [red]{new_value}[/red]"
                    )

        # If no specific differences were formatted but diff exists
        if not differences and diff:
            differences.append(
                "Templates don't match, but the differences are complex. "
                "Check your implementation against the requirements."
            )

        return differences

    def _remove_key(self, key_path: str, template: Dict[str, Any]) -> None:
        """
        Remove a key from the template at the specified path.

        This function is a helper for removing keys from nested dictionaries.
        """
        keys = key_path.split(".")
        d = template
        for key in keys[:-1]:
            d = d.get(key, {})
        if keys[-1] in d:
            del d[keys[-1]]

    def _remove_key_recursively(
        self, key: str, template: Dict[str, Any] | list
    ) -> None:
        """
        Recursively remove a key from the template.

        This function is a helper for removing keys from nested dictionaries.
        """
        if isinstance(template, dict):
            for k in list(template.keys()):
                if k == key:
                    del template[k]
                else:
                    self._remove_key_recursively(key, template[k])
        elif isinstance(template, list):
            for item in template:
                self._remove_key_recursively(key, item)

    def normalize_template(self, template: Dict[str, Any]) -> None:
        """
        Normalize the CloudFormation template by removing unnecessary properties.

        This function removes properties that are not relevant for comparison,
        such as metadata and default values.
        """
        self._remove_key_recursively("Metadata", template)
        self._remove_key("Resources.CDKMetadata", template)
        self._remove_key("Conditions", template)
        self._remove_key("Parameters", template)
        self._remove_key("Rules", template)
