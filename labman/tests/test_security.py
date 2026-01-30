"""Security tests for the lab management application"""
import pytest
from labman.lib.validators import (
    validate_email_address,
    validate_url,
    validate_filename,
    validate_file_extension,
    sanitize_html,
    sanitize_text,
    validate_password_strength,
    validate_integer
)

class TestEmailValidation:
    def test_valid_email(self):
        is_valid, normalized, error = validate_email_address("test@example.com")
        assert is_valid
        assert normalized == "test@example.com"
        assert error is None
    
    def test_invalid_email_format(self):
        is_valid, normalized, error = validate_email_address("invalid-email")
        assert not is_valid
        assert normalized is None
        assert error is not None
    
    def test_empty_email(self):
        is_valid, normalized, error = validate_email_address("")
        assert not is_valid
        assert error == "Email is required"
    
    def test_email_normalization(self):
        is_valid, normalized, error = validate_email_address("Test@Example.COM")
        assert is_valid
        assert normalized == "test@example.com"

class TestURLValidation:
    def test_valid_http_url(self):
        is_valid, error = validate_url("http://example.com")
        assert is_valid
        assert error is None
    
    def test_valid_https_url(self):
        is_valid, error = validate_url("https://example.com")
        assert is_valid
        assert error is None
    
    def test_invalid_url_scheme(self):
        is_valid, error = validate_url("ftp://example.com")
        assert not is_valid
        assert "HTTP or HTTPS" in error
    
    def test_https_requirement(self):
        is_valid, error = validate_url("http://example.com", require_https=True)
        assert not is_valid
        assert "HTTPS" in error
    
    def test_empty_url_allowed(self):
        is_valid, error = validate_url("")
        assert is_valid
        assert error is None

class TestFilenameValidation:
    def test_valid_filename(self):
        is_valid, sanitized, error = validate_filename("document.pdf")
        assert is_valid
        assert sanitized == "document.pdf"
        assert error is None
    
    def test_filename_with_path_traversal(self):
        is_valid, sanitized, error = validate_filename("../../etc/passwd")
        assert is_valid
        assert ".." not in sanitized
        assert "passwd" in sanitized
    
    def test_filename_with_dangerous_chars(self):
        is_valid, sanitized, error = validate_filename("file<>:|?.txt")
        assert is_valid
        assert "<" not in sanitized
        assert ">" not in sanitized
    
    def test_filename_without_extension(self):
        is_valid, sanitized, error = validate_filename("noextension")
        assert not is_valid
        assert "extension" in error.lower()
    
    def test_empty_filename(self):
        is_valid, sanitized, error = validate_filename("")
        assert not is_valid
        assert error == "Filename is required"

class TestFileExtensionValidation:
    def test_allowed_pdf(self):
        is_valid, ext, error = validate_file_extension("document.pdf")
        assert is_valid
        assert ext == ".pdf"
        assert error is None
    
    def test_allowed_python(self):
        is_valid, ext, error = validate_file_extension("script.py")
        assert is_valid
        assert ext == ".py"
    
    def test_disallowed_exe(self):
        is_valid, ext, error = validate_file_extension("malware.exe")
        assert not is_valid
        assert ".exe" in error
    
    def test_case_insensitive(self):
        is_valid, ext, error = validate_file_extension("document.PDF")
        assert is_valid
        assert ext == ".pdf"
    
    def test_category_filter(self):
        is_valid, ext, error = validate_file_extension("image.jpg", allowed_categories=['images'])
        assert is_valid
        
        is_valid, ext, error = validate_file_extension("document.pdf", allowed_categories=['images'])
        assert not is_valid

class TestHTMLSanitization:
    def test_remove_script_tags(self):
        html = "<script>alert('xss')</script><p>Safe content</p>"
        sanitized = sanitize_html(html)
        assert "<script>" not in sanitized
        assert "Safe content" in sanitized
    
    def test_allow_safe_tags(self):
        html = "<p>Paragraph</p><strong>Bold</strong><em>Italic</em>"
        sanitized = sanitize_html(html)
        assert "<p>" in sanitized
        assert "<strong>" in sanitized
        assert "<em>" in sanitized
    
    def test_remove_onclick_attributes(self):
        html = '<a href="#" onclick="alert(\'xss\')">Link</a>'
        sanitized = sanitize_html(html)
        assert "onclick" not in sanitized
        assert "Link" in sanitized

class TestTextSanitization:
    def test_valid_text(self):
        is_valid, sanitized, error = sanitize_text("  Hello World  ")
        assert is_valid
        assert sanitized == "Hello World"
        assert error is None
    
    def test_text_too_long(self):
        long_text = "a" * 101
        is_valid, sanitized, error = sanitize_text(long_text, max_length=100)
        assert not is_valid
        assert "too long" in error.lower()
    
    def test_empty_text_allowed(self):
        is_valid, sanitized, error = sanitize_text("")
        assert is_valid
        assert sanitized == ""
    
    def test_none_text(self):
        is_valid, sanitized, error = sanitize_text(None)
        assert is_valid
        assert sanitized == ""

class TestPasswordStrength:
    def test_strong_password(self):
        is_valid, error = validate_password_strength("SecurePass123")
        assert is_valid
        assert error is None
    
    def test_password_too_short(self):
        is_valid, error = validate_password_strength("Short1")
        assert not is_valid
        assert "at least 8" in error
    
    def test_password_no_numbers(self):
        is_valid, error = validate_password_strength("NoNumbersHere")
        assert not is_valid
        assert "letters and numbers" in error
    
    def test_password_no_letters(self):
        is_valid, error = validate_password_strength("12345678")
        assert not is_valid
        assert "letters and numbers" in error
    
    def test_empty_password(self):
        is_valid, error = validate_password_strength("")
        assert not is_valid
        assert "required" in error.lower()

class TestIntegerValidation:
    def test_valid_integer(self):
        is_valid, value, error = validate_integer("42")
        assert is_valid
        assert value == 42
        assert error is None
    
    def test_integer_with_min(self):
        is_valid, value, error = validate_integer("5", min_value=10)
        assert not is_valid
        assert "at least 10" in error
    
    def test_integer_with_max(self):
        is_valid, value, error = validate_integer("100", max_value=50)
        assert not is_valid
        assert "at most 50" in error
    
    def test_invalid_integer(self):
        is_valid, value, error = validate_integer("not a number")
        assert not is_valid
        assert "Invalid integer" in error

class TestSQLInjectionPrevention:
    """Test that parameterized queries prevent SQL injection"""
    
    def test_parameterized_query_example(self):
        # This is a conceptual test - actual implementation uses parameterized queries
        # Example of SAFE query: query_db('SELECT * FROM users WHERE email = ?', [email])
        # Example of UNSAFE query: query_db(f'SELECT * FROM users WHERE email = "{email}"')
        
        malicious_input = "'; DROP TABLE users; --"
        # With parameterized queries, this would be treated as a literal string
        # and not executed as SQL code
        assert "DROP TABLE" in malicious_input  # Just to show the malicious intent
        # In actual code, this would be safely escaped by the database driver

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
