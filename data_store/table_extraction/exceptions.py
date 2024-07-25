class TableExtractionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TableProcessingError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
