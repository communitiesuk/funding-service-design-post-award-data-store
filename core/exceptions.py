class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures: list, active_project_ids=None):
        if active_project_ids is None:
            active_project_ids = []
        self.active_project_ids = active_project_ids
        self.validation_failures = validation_failures
