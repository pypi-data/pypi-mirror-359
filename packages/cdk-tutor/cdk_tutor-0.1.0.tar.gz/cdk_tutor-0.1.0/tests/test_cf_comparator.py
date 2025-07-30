import pytest
from cdk_tutor.grader.cf_comparator import CfTemplateComparator, ComparisonResult

@pytest.fixture
def expected_template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyQueue": {"Type": "AWS::SQS::Queue"},
        },
        "Outputs": {
            "BucketName": {"Value": {"Ref": "MyBucket"}},
        },
    }

@pytest.fixture
def user_template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyQueue": {"Type": "AWS::SNS::Topic"},  # Incorrect type
            "ExtraResource": {"Type": "AWS::DynamoDB::Table"},  # Extra resource
        },
        "Outputs": {
            "BucketName": {"Value": {"Ref": "MyBucket"}},
            "ExtraOutput": {"Value": "ExtraValue"},  # Extra output
        },
    }

def test_compare_resources(expected_template, user_template):
    comparator = CfTemplateComparator(expected_template, user_template)
    result = comparator.compare()

    assert isinstance(result, ComparisonResult)
    assert not result.is_match
    assert "MyQueue" in result.resource_differences
    assert "ExtraResource" in result.resource_differences
    assert "MyBucket" not in result.resource_differences

def test_compare_outputs(expected_template, user_template):
    comparator = CfTemplateComparator(expected_template, user_template)
    result = comparator.compare()

    assert isinstance(result, ComparisonResult)
    assert not result.is_match
    assert "ExtraOutput" in result.output_differences
    assert "BucketName" not in result.output_differences

def test_normalize_template():
    template = {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "CDKMetadata": {"Type": "AWS::CDK::Metadata"},
        },
        "Metadata": {"Info": "Some metadata"},
        "Conditions": {},
        "Parameters": {},
        "Rules": {},
    }
    comparator = CfTemplateComparator({}, template)
    comparator.normalize_template(template)

    assert "Metadata" not in template
    assert "CDKMetadata" not in template["Resources"]
    assert "Conditions" not in template
    assert "Parameters" not in template
    assert "Rules" not in template
