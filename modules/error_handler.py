"""
Error handling module for EAI DealFlow Terminal.
Provides user-friendly error messages and centralized error management.
"""

from enum import Enum
from typing import Optional, Dict, Any, Callable
from functools import wraps


class ErrorCategory(Enum):
    """Categories of errors for user-friendly messaging."""
    DATA = "data"
    AI_SERVICE = "ai_service"
    PDF = "pdf"
    STORAGE = "storage"
    CONFIG = "config"
    NETWORK = "network"
    VALIDATION = "validation"


# User-friendly error messages mapped by category and error type
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "data": {
        "no_data_directory": (
            "Could not find the data folder. Please ensure the 'data' "
            "directory exists and contains CSV files."
        ),
        "no_csv_files": (
            "No transaction data found. Please add CSV files to the "
            "'data' folder to enable analysis."
        ),
        "csv_load_failed": (
            "Unable to load transaction data from '{filename}'. "
            "Please check the file format and try again."
        ),
        "invalid_data_format": (
            "The data format in '{filename}' is not recognized. "
            "Please ensure it matches the expected column structure."
        ),
        "no_peers_found": (
            "No comparable transactions found for this industry and revenue range. "
            "Try adjusting the filters or selecting a different industry."
        ),
    },
    "ai_service": {
        "api_key_missing": (
            "AI features are unavailable. Please configure your "
            "GEMINI_API_KEY in the environment settings."
        ),
        "api_connection_failed": (
            "Unable to connect to the AI service. Please check your "
            "internet connection and try again."
        ),
        "api_rate_limited": (
            "The AI service is temporarily busy. Please wait a moment "
            "and try again."
        ),
        "generation_failed": (
            "Unable to generate content. The AI service encountered "
            "an issue. Please try again."
        ),
        "website_scrape_failed": (
            "Could not analyze the website. The site may be unavailable "
            "or blocking automated access."
        ),
    },
    "pdf": {
        "generation_failed": (
            "Unable to create the PDF report. Please try again or "
            "contact support if the issue persists."
        ),
        "chart_export_failed": (
            "Could not include the chart in the PDF. The report will "
            "be generated without the visualization."
        ),
        "invalid_data": (
            "Some data is missing for the PDF report. Please ensure all "
            "required fields are filled in."
        ),
    },
    "storage": {
        "save_failed": (
            "Unable to save your data. Please check disk space and "
            "file permissions."
        ),
        "load_failed": (
            "Could not load saved data. The file may be corrupted. "
            "Starting with fresh data."
        ),
        "delete_failed": (
            "Unable to delete the selected entries. Please try again."
        ),
        "file_corrupted": (
            "The saved data file appears to be corrupted. "
            "Starting with fresh data."
        ),
    },
    "config": {
        "load_failed": (
            "Could not load your settings. Using default configuration."
        ),
        "save_failed": (
            "Unable to save your settings. Changes may not persist "
            "after restart."
        ),
        "invalid_format": (
            "Settings file has an invalid format. Using default configuration."
        ),
    },
    "network": {
        "connection_failed": (
            "Unable to connect to the internet. Please check your "
            "network connection."
        ),
        "timeout": (
            "The request took too long. Please check your connection "
            "and try again."
        ),
        "ssl_error": (
            "Secure connection could not be established. Please check "
            "your network settings."
        ),
    },
    "validation": {
        "invalid_company_name": (
            "Please enter a valid company name."
        ),
        "invalid_revenue": (
            "Please enter a valid revenue amount greater than zero."
        ),
        "invalid_industry": (
            "Please select an industry from the list or enter a custom one."
        ),
        "invalid_url": (
            "The website URL appears to be invalid. Please check the "
            "format and try again."
        ),
        "missing_required_fields": (
            "Please fill in all required fields: company name, industry, "
            "and revenue."
        ),
    },
}


def get_user_friendly_message(
    category: str,
    error_type: str,
    **kwargs: Any
) -> str:
    """
    Get a user-friendly error message for display.

    Args:
        category: Error category (data, ai_service, pdf, etc.)
        error_type: Specific error type within the category
        **kwargs: Optional parameters for message formatting

    Returns:
        User-friendly error message string
    """
    category_messages = ERROR_MESSAGES.get(category, {})
    message = category_messages.get(
        error_type,
        "An unexpected error occurred. Please try again."
    )

    # Format message with any provided parameters
    try:
        return message.format(**kwargs)
    except KeyError:
        return message


class DealFlowError(Exception):
    """Base exception class for DealFlow application errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.DATA,
        error_type: str = "unknown",
        technical_details: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Initialize a DealFlow error.

        Args:
            message: User-friendly error message
            category: Error category for classification
            error_type: Specific error type for lookup
            technical_details: Optional technical details for logging
            **kwargs: Additional context for the error
        """
        self.message = message
        self.category = category
        self.error_type = error_type
        self.technical_details = technical_details
        self.context = kwargs
        super().__init__(self.message)

    @classmethod
    def from_type(
        cls,
        category: ErrorCategory,
        error_type: str,
        technical_details: Optional[str] = None,
        **kwargs: Any
    ) -> "DealFlowError":
        """
        Create an error from category and type with auto-generated message.

        Args:
            category: Error category
            error_type: Specific error type
            technical_details: Optional technical details
            **kwargs: Parameters for message formatting

        Returns:
            DealFlowError instance with user-friendly message
        """
        message = get_user_friendly_message(category.value, error_type, **kwargs)
        return cls(
            message=message,
            category=category,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class DataError(DealFlowError):
    """Error related to data loading or processing."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("data", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.DATA,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class AIServiceError(DealFlowError):
    """Error related to AI/Gemini service."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("ai_service", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.AI_SERVICE,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class PDFError(DealFlowError):
    """Error related to PDF generation."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("pdf", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.PDF,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class StorageError(DealFlowError):
    """Error related to storage operations."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("storage", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.STORAGE,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class ConfigError(DealFlowError):
    """Error related to configuration."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("config", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIG,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


class ValidationError(DealFlowError):
    """Error related to input validation."""

    def __init__(self, error_type: str, technical_details: Optional[str] = None,
                 **kwargs: Any):
        message = get_user_friendly_message("validation", error_type, **kwargs)
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            error_type=error_type,
            technical_details=technical_details,
            **kwargs
        )


def handle_errors(
    category: ErrorCategory,
    default_error_type: str = "unknown",
    fallback_value: Any = None,
    reraise: bool = False
) -> Callable:
    """
    Decorator for handling errors with user-friendly messages.

    Args:
        category: Error category for this function
        default_error_type: Default error type if not specified
        fallback_value: Value to return on error (if not reraising)
        reraise: Whether to reraise as DealFlowError

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except DealFlowError:
                # Already a DealFlow error, re-raise or return fallback
                if reraise:
                    raise
                return fallback_value
            except Exception as e:
                error = DealFlowError.from_type(
                    category=category,
                    error_type=default_error_type,
                    technical_details=str(e)
                )
                if reraise:
                    raise error from e
                return fallback_value
        return wrapper
    return decorator


def validate_company_input(
    company_name: Optional[str],
    industry: Optional[str],
    revenue: Optional[float]
) -> Optional[str]:
    """
    Validate company input fields and return error message if invalid.

    Args:
        company_name: Company name input
        industry: Industry selection
        revenue: Revenue value

    Returns:
        Error message string if validation fails, None if valid
    """
    if not company_name or not company_name.strip():
        return get_user_friendly_message("validation", "invalid_company_name")

    if not industry or industry == "+ Add Custom":
        return get_user_friendly_message("validation", "invalid_industry")

    if revenue is None or revenue <= 0:
        return get_user_friendly_message("validation", "invalid_revenue")

    return None


def format_error_for_display(error: Exception) -> str:
    """
    Format any exception for user display.

    Args:
        error: The exception to format

    Returns:
        User-friendly error message
    """
    if isinstance(error, DealFlowError):
        return error.message

    # Map common Python exceptions to user-friendly messages
    error_type = type(error).__name__

    if error_type == "FileNotFoundError":
        return "The requested file could not be found. Please check the path."
    elif error_type == "PermissionError":
        return "Permission denied. Please check file access rights."
    elif error_type == "ConnectionError":
        return get_user_friendly_message("network", "connection_failed")
    elif error_type == "TimeoutError":
        return get_user_friendly_message("network", "timeout")
    elif error_type == "JSONDecodeError":
        return "Data file format is invalid. Please check the file."
    elif error_type == "ValueError":
        return "Invalid value provided. Please check your input."
    elif error_type == "KeyError":
        return "Required data is missing. Please ensure all fields are filled."

    return "An unexpected error occurred. Please try again."
