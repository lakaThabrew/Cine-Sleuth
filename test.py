"""
Unit tests for CineSleuth application.
Run with: pytest test.py -v
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Import from main module
from main import (
    clean_output,
    load_api_key,
    configure_api,
    create_model,
    send_message_safely,
    get_yes_no_input,
    print_banner,
    CineSleuthError,
    APIKeyError,
    APIConnectionError,
    APIQuotaError,
)


class TestCleanOutput:
    def test_clean_output_removes_bold(self):
        assert clean_output("**bold text**") == "bold text"
        assert clean_output("This is **bold** word") == "This is bold word"

    def test_clean_output_removes_italic(self):
        assert clean_output("*italic text*") == "italic text"
        assert clean_output("_italic text_") == "italic text"

    def test_clean_output_removes_code_blocks(self):
        text = "Before ```python\nprint('hello')\n``` After"
        result = clean_output(text)
        assert "```" not in result
        assert "Before" in result
        assert "After" in result

    def test_clean_output_removes_inline_code(self):
        assert clean_output("Use `print()` function") == "Use print() function"

    def test_clean_output_removes_headers(self):
        assert clean_output("# Header") == "Header"
        assert clean_output("## Header 2") == "Header 2"
        assert clean_output("### Header 3") == "Header 3"

    def test_clean_output_removes_extra_newlines(self):
        text = "Line 1\n\n\n\nLine 2"
        result = clean_output(text)
        assert "\n\n\n" not in result

    def test_clean_output_strips_whitespace(self):
        assert clean_output("  text  ") == "text"
        assert clean_output("\n\ntext\n\n") == "text"

    def test_clean_output_empty_string(self):
        assert clean_output("") == ""

    def test_clean_output_plain_text(self):
        text = "This is a plain question about movies"
        assert clean_output(text) == text

    def test_clean_output_complex_markdown(self):
        text = "**Is the movie** a _comedy_ with `funny` scenes?"
        result = clean_output(text)
        assert "**" not in result
        assert "_" not in result
        assert "`" not in result
        assert "Is the movie" in result
        assert "comedy" in result
        assert "funny" in result

    def test_clean_output_type_error(self):
        with pytest.raises(TypeError):
            clean_output(123)
        with pytest.raises(TypeError):
            clean_output(None)
        with pytest.raises(TypeError):
            clean_output(['text'])


class TestLoadApiKey:
    def test_load_api_key_success(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}):
            key = load_api_key()
            assert key == "test-key-123"

    def test_load_api_key_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove GEMINI_API_KEY if it exists
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            with pytest.raises(APIKeyError):
                load_api_key()

    def test_load_api_key_empty(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with pytest.raises(APIKeyError):
                load_api_key()


class TestConfigureApi:
    @patch('main.genai')
    def test_configure_api_success(self, mock_genai):
        configure_api("test-key")
        mock_genai.configure.assert_called_once_with(api_key="test-key")

    @patch('main.genai')
    def test_configure_api_failure(self, mock_genai):
        """Test API configuration failure."""
        mock_genai.configure.side_effect = Exception("Config error")
        with pytest.raises(APIConnectionError):
            configure_api("test-key")


class TestCreateModel:
    @patch('main.genai')
    def test_create_model_success(self, mock_genai):
        """Test successful model creation."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = create_model('gemini-2.0-flash')
        
        assert result == mock_model
        mock_genai.GenerativeModel.assert_called_once_with('gemini-2.0-flash')

    @patch('main.genai')
    def test_create_model_failure(self, mock_genai):
        mock_genai.GenerativeModel.side_effect = Exception("Model error")
        with pytest.raises(APIConnectionError):
            create_model('invalid-model')


class TestSendMessageSafely:
    def test_send_message_success(self):
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_chat.send_message.return_value = mock_response
        
        result = send_message_safely(mock_chat, "Test prompt")
        
        assert result == mock_response
        mock_chat.send_message.assert_called_once_with("Test prompt")

    @patch('main.google_exceptions')
    def test_send_message_quota_exceeded(self, mock_exceptions):
        from google.api_core.exceptions import ResourceExhausted
        
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = ResourceExhausted("Quota exceeded")
        
        with pytest.raises(APIQuotaError):
            send_message_safely(mock_chat, "Test prompt")

    @patch('main.google_exceptions')
    def test_send_message_permission_denied(self, mock_exceptions):
        from google.api_core.exceptions import PermissionDenied
        
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = PermissionDenied("Invalid key")
        
        with pytest.raises(APIKeyError):
            send_message_safely(mock_chat, "Test prompt")

    @patch('main.google_exceptions')
    def test_send_message_service_unavailable(self, mock_exceptions):
        from google.api_core.exceptions import ServiceUnavailable
        
        mock_chat = MagicMock()
        mock_chat.send_message.side_effect = ServiceUnavailable("Service down")
        
        with pytest.raises(APIConnectionError):
            send_message_safely(mock_chat, "Test prompt")


class TestGetYesNoInput:
    def test_get_yes_no_input_yes(self):
        with patch('builtins.input', return_value='yes'):
            result = get_yes_no_input()
            assert result == 'yes'

    def test_get_yes_no_input_no(self):
        with patch('builtins.input', return_value='no'):
            result = get_yes_no_input()
            assert result == 'no'

    def test_get_yes_no_input_exit(self):
        with patch('builtins.input', return_value='exit'):
            result = get_yes_no_input()
            assert result == 'exit'

    def test_get_yes_no_input_case_insensitive(self):
        with patch('builtins.input', return_value='YES'):
            result = get_yes_no_input()
            assert result == 'yes'
        
        with patch('builtins.input', return_value='No'):
            result = get_yes_no_input()
            assert result == 'no'

    def test_get_yes_no_input_with_whitespace(self):
        with patch('builtins.input', return_value='  yes  '):
            result = get_yes_no_input()
            assert result == 'yes'

    def test_get_yes_no_input_eof(self):
        with patch('builtins.input', side_effect=EOFError):
            result = get_yes_no_input()
            assert result == 'exit'

    def test_get_yes_no_input_keyboard_interrupt(self):
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            result = get_yes_no_input()
            assert result == 'exit'


class TestExceptionHierarchy:
    def test_cinesleuth_error_is_exception(self):
        assert issubclass(CineSleuthError, Exception)

    def test_api_key_error_inherits_from_cinesleuth_error(self):
        assert issubclass(APIKeyError, CineSleuthError)

    def test_api_connection_error_inherits_from_cinesleuth_error(self):
        assert issubclass(APIConnectionError, CineSleuthError)

    def test_api_quota_error_inherits_from_cinesleuth_error(self):
        assert issubclass(APIQuotaError, CineSleuthError)

    def test_exception_message(self):
        msg = "Test error message"
        assert str(CineSleuthError(msg)) == msg
        assert str(APIKeyError(msg)) == msg
        assert str(APIConnectionError(msg)) == msg
        assert str(APIQuotaError(msg)) == msg


class TestPrintBanner:
    def test_print_banner_output(self, capsys):
        print_banner()
        captured = capsys.readouterr()
        assert "Welcome to Cine-Sleuth!" in captured.out
        assert "movie detector" in captured.out


class TestIntegration:
    @patch('main.create_model')
    @patch('main.configure_api')
    @patch('main.load_api_key')
    @patch('builtins.input')
    def test_game_exit_immediately(self, mock_input, mock_load, mock_configure, mock_create):
        mock_load.return_value = "test-key"
        mock_input.return_value = "exit"
        
        from main import main
        main()  # Should not raise any errors

    @patch('main.create_model')
    @patch('main.configure_api')
    @patch('main.load_api_key')
    @patch('builtins.input')
    def test_game_api_key_error(self, mock_input, mock_load, mock_configure, mock_create, capsys):
        mock_load.side_effect = APIKeyError("Missing API key")
        
        from main import main
        main()
        
        captured = capsys.readouterr()
        assert "API Key Error" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
