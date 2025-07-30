
class EsewaError(Exception):
    """Base exception for eSewa errors."""
    pass

class PaymentRequestError(EsewaError):
    """Raised when payment request fails."""
    pass

class StatusCheckError(EsewaError):
    """Raised when status check fails."""
    pass

class ValidationError(EsewaError):
    """Raised when input validation fails."""
    pass
