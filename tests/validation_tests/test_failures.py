from core.validation.failures import (
    InvalidEnumValueFailure,
    serialise_user_centered_failures,
)


def test_serialise_user_centered_failures():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure2 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="GIS Provided",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure3 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="GIS Provided",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failures = [failure1, failure2, failure3]
    output = serialise_user_centered_failures(failures)

    assert output
    assert "Project Admin" in output
    assert "Project Details" in output["Project Admin"]
    assert len(output["Project Admin"]["Project Details"]) == 3
    assert output["Project Admin"]["Project Details"]
    assert output == {
        "Project Admin": {
            "Project Details": [
                'For column "Does the project have a single location (e.g. one site) or multiple (e.g. multiple sites '
                'or across a number of post codes)?", you have entered "Value" which isn\'t correct. You must select '
                "an option from the list provided",
                'For column "Are you providing a GIS map (see guidance) with your return?", you have entered "Value" '
                "which isn't correct. You must select an option from the list provided",
                'For column "Are you providing a GIS map (see guidance) with your return?", you have entered "Value" '
                "which isn't correct. You must select an option from the list provided",
            ]
        }
    }
