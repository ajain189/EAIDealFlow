"""
Tests for error_handler module.
Tests user-friendly error messages and error handling utilities.
"""

import pytest

from modules.error_handler import (
    ErrorCategory,
    ERROR_MESSAGES,
    get_user_friendly_message,
    DealFlowError,
    DataError,
    AIServiceError,
    PDFError,
    StorageError,
    ConfigError,
    ValidationError,
    handle_errors,
    validate_company_input,
    format_error_for_display,
)


class TestErrorMessages:
    """Tests for error message retrieval."""

    def test_get_message_for_valid_category_and_type(self):
        """Test retrieving a message with valid category and type."""
        message = get_user_friendly_message("data", "no_csv_files")
        assert message is not None
        assert len(message) > 0
        assert "CSV" in message or "data" in message.lower()

    def test_get_message_for_invalid_category(self):
        """Test retrieving a message with invalid category."""
        message = get_user_friendly_message("invalid_category", "some_type")
        assert message == "An unexpected error occurred. Please try again."

    def test_get_message_for_invalid_type(self):
        """Test retrieving a message with invalid type."""
        message = get_user_friendly_message("data", "invalid_type")
        assert message == "An unexpected error occurred. Please try again."

    def test_get_message_with_formatting(self):
        """Test message formatting with kwargs."""
        message = get_user_friendly_message(
            "data", "csv_load_failed", filename="test.csv"
        )
        assert "test.csv" in message

    def test_get_message_with_missing_format_key(self):
        """Test message formatting gracefully handles missing keys."""
        # Should not raise an exception
        message = get_user_friendly_message("data", "csv_load_failed")
        assert "{filename}" in message  # Unformatted placeholder

    def test_all_categories_have_messages(self):
        """Test that all error categories have at least one message."""
        for category in ErrorCategory:
            assert category.value in ERROR_MESSAGES
            assert len(ERROR_MESSAGES[category.value]) > 0


class TestErrorCategoryEnum:
    """Tests for ErrorCategory enum."""

    def test_data_category_exists(self):
        """Test DATA category exists."""
        assert ErrorCategory.DATA.value == "data"

    def test_ai_service_category_exists(self):
        """Test AI_SERVICE category exists."""
        assert ErrorCategory.AI_SERVICE.value == "ai_service"

    def test_pdf_category_exists(self):
        """Test PDF category exists."""
        assert ErrorCategory.PDF.value == "pdf"

    def test_storage_category_exists(self):
        """Test STORAGE category exists."""
        assert ErrorCategory.STORAGE.value == "storage"

    def test_config_category_exists(self):
        """Test CONFIG category exists."""
        assert ErrorCategory.CONFIG.value == "config"

    def test_network_category_exists(self):
        """Test NETWORK category exists."""
        assert ErrorCategory.NETWORK.value == "network"

    def test_validation_category_exists(self):
        """Test VALIDATION category exists."""
        assert ErrorCategory.VALIDATION.value == "validation"


class TestDealFlowError:
    """Tests for DealFlowError base class."""

    def test_create_error_with_message(self):
        """Test creating error with message."""
        error = DealFlowError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"

    def test_error_has_category(self):
        """Test error has category attribute."""
        error = DealFlowError("Test", category=ErrorCategory.DATA)
        assert error.category == ErrorCategory.DATA

    def test_error_has_error_type(self):
        """Test error has error_type attribute."""
        error = DealFlowError("Test", error_type="test_type")
        assert error.error_type == "test_type"

    def test_error_has_technical_details(self):
        """Test error stores technical details."""
        error = DealFlowError("Test", technical_details="Stack trace here")
        assert error.technical_details == "Stack trace here"

    def test_from_type_creates_correct_message(self):
        """Test from_type class method creates correct message."""
        error = DealFlowError.from_type(
            category=ErrorCategory.DATA,
            error_type="no_csv_files"
        )
        assert error.category == ErrorCategory.DATA
        assert error.error_type == "no_csv_files"
        assert "CSV" in error.message or "data" in error.message.lower()

    def test_from_type_with_formatting(self):
        """Test from_type with message formatting."""
        error = DealFlowError.from_type(
            category=ErrorCategory.DATA,
            error_type="csv_load_failed",
            filename="myfile.csv"
        )
        assert "myfile.csv" in error.message


class TestSpecificErrorClasses:
    """Tests for specific error subclasses."""

    def test_data_error_creation(self):
        """Test DataError creation."""
        error = DataError("no_csv_files")
        assert error.category == ErrorCategory.DATA
        assert "CSV" in error.message or "data" in error.message.lower()

    def test_ai_service_error_creation(self):
        """Test AIServiceError creation."""
        error = AIServiceError("api_key_missing")
        assert error.category == ErrorCategory.AI_SERVICE
        assert "GEMINI" in error.message or "AI" in error.message

    def test_pdf_error_creation(self):
        """Test PDFError creation."""
        error = PDFError("generation_failed")
        assert error.category == ErrorCategory.PDF
        assert "PDF" in error.message

    def test_storage_error_creation(self):
        """Test StorageError creation."""
        error = StorageError("save_failed")
        assert error.category == ErrorCategory.STORAGE
        assert "save" in error.message.lower()

    def test_config_error_creation(self):
        """Test ConfigError creation."""
        error = ConfigError("load_failed")
        assert error.category == ErrorCategory.CONFIG
        assert "settings" in error.message.lower()

    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        error = ValidationError("invalid_company_name")
        assert error.category == ErrorCategory.VALIDATION
        assert "company" in error.message.lower()


class TestHandleErrorsDecorator:
    """Tests for handle_errors decorator."""

    def test_decorator_passes_through_successful_call(self):
        """Test decorator allows successful function to return normally."""
        @handle_errors(ErrorCategory.DATA)
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    def test_decorator_returns_fallback_on_error(self):
        """Test decorator returns fallback value on error."""
        @handle_errors(ErrorCategory.DATA, fallback_value="fallback")
        def failing_func():
            raise ValueError("test error")

        result = failing_func()
        assert result == "fallback"

    def test_decorator_reraises_as_dealflow_error(self):
        """Test decorator can reraise as DealFlowError."""
        @handle_errors(ErrorCategory.DATA, reraise=True)
        def failing_func():
            raise ValueError("test error")

        with pytest.raises(DealFlowError):
            failing_func()

    def test_decorator_passes_through_dealflow_error(self):
        """Test decorator passes through existing DealFlowError."""
        @handle_errors(ErrorCategory.DATA, reraise=True)
        def func_with_dealflow_error():
            raise DataError("no_csv_files")

        with pytest.raises(DealFlowError):
            func_with_dealflow_error()

    def test_decorator_returns_none_as_default_fallback(self):
        """Test decorator returns None as default fallback."""
        @handle_errors(ErrorCategory.DATA)
        def failing_func():
            raise ValueError("test error")

        result = failing_func()
        assert result is None


class TestValidateCompanyInput:
    """Tests for validate_company_input function."""

    def test_valid_input_returns_none(self):
        """Test valid input returns None (no error)."""
        result = validate_company_input("Test Company", "HVAC", 1000000)
        assert result is None

    def test_empty_company_name_returns_error(self):
        """Test empty company name returns error message."""
        result = validate_company_input("", "HVAC", 1000000)
        assert result is not None
        assert "company" in result.lower()

    def test_whitespace_company_name_returns_error(self):
        """Test whitespace-only company name returns error message."""
        result = validate_company_input("   ", "HVAC", 1000000)
        assert result is not None

    def test_none_company_name_returns_error(self):
        """Test None company name returns error message."""
        result = validate_company_input(None, "HVAC", 1000000)
        assert result is not None

    def test_add_custom_industry_returns_error(self):
        """Test '+ Add Custom' industry returns error message."""
        result = validate_company_input("Test Company", "+ Add Custom", 1000000)
        assert result is not None
        assert "industry" in result.lower()

    def test_empty_industry_returns_error(self):
        """Test empty industry returns error message."""
        result = validate_company_input("Test Company", "", 1000000)
        assert result is not None

    def test_none_industry_returns_error(self):
        """Test None industry returns error message."""
        result = validate_company_input("Test Company", None, 1000000)
        assert result is not None

    def test_zero_revenue_returns_error(self):
        """Test zero revenue returns error message."""
        result = validate_company_input("Test Company", "HVAC", 0)
        assert result is not None
        assert "revenue" in result.lower()

    def test_negative_revenue_returns_error(self):
        """Test negative revenue returns error message."""
        result = validate_company_input("Test Company", "HVAC", -100)
        assert result is not None

    def test_none_revenue_returns_error(self):
        """Test None revenue returns error message."""
        result = validate_company_input("Test Company", "HVAC", None)
        assert result is not None


class TestFormatErrorForDisplay:
    """Tests for format_error_for_display function."""

    def test_dealflow_error_returns_message(self):
        """Test DealFlowError returns its message."""
        error = DataError("no_csv_files")
        result = format_error_for_display(error)
        assert result == error.message

    def test_file_not_found_error(self):
        """Test FileNotFoundError returns friendly message."""
        error = FileNotFoundError("file.txt")
        result = format_error_for_display(error)
        assert "file" in result.lower()
        assert "found" in result.lower()

    def test_permission_error(self):
        """Test PermissionError returns friendly message."""
        error = PermissionError("denied")
        result = format_error_for_display(error)
        assert "permission" in result.lower()

    def test_connection_error(self):
        """Test ConnectionError returns friendly message."""
        error = ConnectionError("failed")
        result = format_error_for_display(error)
        assert "connect" in result.lower() or "network" in result.lower()

    def test_timeout_error(self):
        """Test TimeoutError returns friendly message."""
        error = TimeoutError("timed out")
        result = format_error_for_display(error)
        assert "timeout" in result.lower() or "long" in result.lower()

    def test_value_error(self):
        """Test ValueError returns friendly message."""
        error = ValueError("invalid")
        result = format_error_for_display(error)
        assert "value" in result.lower() or "input" in result.lower()

    def test_key_error(self):
        """Test KeyError returns friendly message."""
        error = KeyError("missing")
        result = format_error_for_display(error)
        assert "missing" in result.lower() or "data" in result.lower()

    def test_unknown_error_returns_generic_message(self):
        """Test unknown error type returns generic message."""

        class CustomError(Exception):
            pass

        error = CustomError("something went wrong")
        result = format_error_for_display(error)
        assert "unexpected" in result.lower() or "error" in result.lower()


class TestErrorMessageContent:
    """Tests for specific error message content quality."""

    def test_data_messages_are_user_friendly(self):
        """Test data error messages are understandable."""
        for error_type in ERROR_MESSAGES["data"]:
            message = get_user_friendly_message("data", error_type)
            # Should not contain technical jargon
            assert "exception" not in message.lower()
            assert "traceback" not in message.lower()
            # Should provide actionable guidance
            assert len(message) > 20

    def test_ai_service_messages_are_user_friendly(self):
        """Test AI service error messages are understandable."""
        for error_type in ERROR_MESSAGES["ai_service"]:
            message = get_user_friendly_message("ai_service", error_type)
            assert "exception" not in message.lower()
            assert len(message) > 20

    def test_validation_messages_provide_guidance(self):
        """Test validation messages tell user what to do."""
        for error_type in ERROR_MESSAGES["validation"]:
            message = get_user_friendly_message("validation", error_type)
            # Should contain action words
            assert "please" in message.lower() or "enter" in message.lower() \
                or "select" in message.lower() or "fill" in message.lower()
