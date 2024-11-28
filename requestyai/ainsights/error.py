class AInsightsError(Exception):
    """Base exception class for AInsights-related errors."""

    pass


class AInsightsValueError(AInsightsError):
    """Exception raised when validation fails for AInsights capture parameters.

    Attributes:
        message: Explanation of the validation error
    """

    def __init__(self, message: str):
        super().__init__(message)
