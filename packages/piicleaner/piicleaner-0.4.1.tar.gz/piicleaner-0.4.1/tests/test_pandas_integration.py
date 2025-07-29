"""Tests for Pandas DataFrame integration functionality."""

import pytest

# Skip all tests if pandas is not available
pytest.importorskip("pandas")

import pandas as pd
from piicleaner import Cleaner


class TestPandasDataFrameMethods:
    """Test Cleaner class DataFrame methods."""

    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame with PII data for testing."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "text": [
                    "Contact john@example.com for help",
                    "My NINO is AB123456C",
                    "Call +44 20 7946 0958",
                    "No PII in this text",
                ],
                "category": ["email", "nino", "phone", "clean"],
            }
        )

    @pytest.fixture
    def cleaner(self):
        """Default cleaner instance."""
        return Cleaner()

    def test_clean_dataframe_redact(self, cleaner, sample_df):
        """Test cleaning DataFrame with redact method."""
        result = cleaner.clean_pandas_dataframe(
            sample_df, "text", "redact", new_column_name="cleaned_text"
        )

        assert result.shape == (4, 4)  # Original columns + new column
        assert "cleaned_text" in result.columns

        cleaned_texts = result["cleaned_text"].tolist()
        assert "john@example.com" not in cleaned_texts[0]
        assert "AB123456C" not in cleaned_texts[1]
        assert "+44 20 7946 0958" not in cleaned_texts[2]
        assert cleaned_texts[3] == "No PII in this text"  # No change

    def test_clean_dataframe_replace(self, cleaner, sample_df):
        """Test cleaning DataFrame with replace method."""
        result = cleaner.clean_pandas_dataframe(
            sample_df, "text", "replace", new_column_name="cleaned_text"
        )

        assert result.shape == (4, 4)
        cleaned_texts = result["cleaned_text"].tolist()

        # Replace method should change entire string if PII found
        assert cleaned_texts[0] != "Contact john@example.com for help"
        assert cleaned_texts[1] != "My NINO is AB123456C"
        assert cleaned_texts[2] != "Call +44 20 7946 0958"
        assert cleaned_texts[3] == "No PII in this text"  # No change

    def test_clean_dataframe_overwrite_column(self, cleaner, sample_df):
        """Test cleaning DataFrame by overwriting original column."""
        original_texts = sample_df["text"].tolist()
        result = cleaner.clean_pandas_dataframe(sample_df, "text", "redact")

        assert result.shape == sample_df.shape
        assert "text" in result.columns

        new_texts = result["text"].tolist()
        assert new_texts != original_texts
        assert "john@example.com" not in new_texts[0]

    def test_detect_dataframe(self, cleaner, sample_df):
        """Test PII detection in DataFrame."""
        result = cleaner.detect_pandas_dataframe(sample_df, "text")

        assert isinstance(result, pd.DataFrame)
        assert "id" in result.columns
        assert "text" in result.columns
        assert "category" in result.columns
        assert "text_pii_detected" in result.columns

        # Should detect PII in rows 0, 1, 2 but not 3
        pii_lengths = [len(matches) for matches in result["text_pii_detected"]]

        # First three results should all be > 0, i.e. something detected
        assert all(x > 0 for x in pii_lengths[:3])
        # Final result should be 0, i.e. no PII detected
        assert pii_lengths[3] == 0

        pii_texts = result["text"].tolist()
        assert any("john@example.com" in text for text in pii_texts)
        assert any("AB123456C" in text for text in pii_texts)
        assert any("+44 20 7946 0958" in text for text in pii_texts)

    def test_clean_dataframe_invalid_column(self, cleaner, sample_df):
        """Test error when column doesn't exist."""
        with pytest.raises(ValueError, match="Column 'nonexistent' not found"):
            cleaner.clean_pandas_dataframe(sample_df, "nonexistent", "redact")

    def test_detect_dataframe_invalid_column(self, cleaner, sample_df):
        """Test error when column doesn't exist."""
        with pytest.raises(ValueError, match="Column 'nonexistent' not found"):
            cleaner.detect_pandas_dataframe(sample_df, "nonexistent")

    def test_clean_dataframe_invalid_df_type(self, cleaner):
        """Test error with non-DataFrame input."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            cleaner.clean_pandas_dataframe(
                ["not", "a", "dataframe"], "text", "redact"
            )

    def test_detect_dataframe_invalid_df_type(self, cleaner):
        """Test error with non-DataFrame input."""
        with pytest.raises(TypeError, match="df must be a pandas DataFrame"):
            cleaner.detect_pandas_dataframe({"not": "a dataframe"}, "text")


class TestPandasSeriesAccessor:
    """Test Pandas Series accessor API (.pii.* methods)."""

    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame for accessor testing."""
        return pd.DataFrame(
            {
                "text": [
                    "Email: alice@company.com",
                    "Phone: +44 20 1234 5678",
                    "NINO: JK987654D",
                    "Clean text here",
                ]
            }
        )

    def test_accessor_clean_pii_redact(self, sample_df):
        """Test accessor .pii.clean_pii() with redact."""
        result = sample_df["text"].pii.clean_pii("redact")

        assert isinstance(result, pd.Series)
        assert len(result) == 4

        cleaned_texts = result.tolist()
        assert "alice@company.com" not in cleaned_texts[0]
        assert "+44 20 1234 5678" not in cleaned_texts[1]
        assert "JK987654D" not in cleaned_texts[2]
        assert cleaned_texts[3] == "Clean text here"

    def test_accessor_clean_pii_replace(self, sample_df):
        """Test accessor .pii.clean_pii() with replace."""
        result = sample_df["text"].pii.clean_pii("replace")

        cleaned_texts = result.tolist()
        original_texts = sample_df["text"].tolist()

        # Should change strings with PII
        assert cleaned_texts[0] != original_texts[0]
        assert cleaned_texts[1] != original_texts[1]
        assert cleaned_texts[2] != original_texts[2]
        assert cleaned_texts[3] == original_texts[3]  # No change

    def test_accessor_detect_pii(self, sample_df):
        """Test accessor .pii.detect_pii()."""
        result = sample_df["text"].pii.detect_pii()

        assert isinstance(result, pd.Series)
        assert len(result) == 4

        matches = result.tolist()

        # Check that matches are returned as list of dicts
        assert isinstance(matches[0], list)  # Email row should have matches
        assert isinstance(matches[1], list)  # Phone row should have matches
        assert isinstance(matches[2], list)  # NINO row should have matches
        assert matches[3] == []  # Clean text should have no matches

        # Check structure of matches
        if matches[0]:  # If email matches found
            match = matches[0][0]
            assert "start" in match
            assert "end" in match
            assert "text" in match
            assert "type" in match

    def test_accessor_detect_pii_with_cleaners(self, sample_df):
        """Test accessor .pii.detect_pii() with specific cleaners."""
        result = sample_df["text"].pii.detect_pii(["email"])

        matches = result.tolist()

        # Should only detect email, not phone or NINO
        assert len(matches[0]) >= 1  # Email row should have matches
        # Other rows might have no matches or fewer matches

        # Check that detected text contains email
        if matches[0]:
            email_match_text = matches[0][0]["text"]
            assert "@" in email_match_text

    def test_accessor_with_null_values(self):
        """Test accessor API handles null values correctly."""
        df = pd.DataFrame(
            {"text": ["Email: test@example.com", None, "Clean text"]}
        )

        cleaned = df["text"].pii.clean_pii("redact")
        detected = df["text"].pii.detect_pii()

        assert pd.isna(cleaned.iloc[1])  # Null should remain null
        assert detected.iloc[1] == []  # Null should return empty list

        assert "test@example.com" not in cleaned.iloc[0]
        assert cleaned.iloc[2] == "Clean text"


class TestPandasEdgeCases:
    """Test edge cases and error conditions for Pandas integration."""

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        cleaner = Cleaner()
        empty_df = pd.DataFrame({"text": []})

        cleaned = cleaner.clean_pandas_dataframe(empty_df, "text", "redact")
        detected = cleaner.detect_pandas_dataframe(empty_df, "text")

        assert cleaned.shape == (0, 1)
        assert detected.shape[0] == 0  # No rows

    def test_vectorised_batch_processing(self):
        """Test vectorised DataFrame operations with larger dataset."""
        cleaner = Cleaner()
        # Test with larger dataset to ensure vectorisation works
        batch_data = ["Email: test@example.com"] * 200 + ["No PII"] * 200
        batch_df = pd.DataFrame({"text": batch_data})

        cleaned = cleaner.clean_pandas_dataframe(
            batch_df, "text", "redact", new_column_name="cleaned"
        )
        detected = cleaner.detect_pandas_dataframe(batch_df, "text")

        assert cleaned.shape == (400, 2)
        assert detected.shape[0] >= 200  # Should detect PII in first 200 rows

        cleaned_texts = cleaned["cleaned"].tolist()
        # First 200 should be cleaned, last 200 unchanged
        assert "test@example.com" not in cleaned_texts[0]
        assert cleaned_texts[399] == "No PII"

    def test_multiple_columns_cleaning(self):
        """Test cleaning multiple columns."""
        df = pd.DataFrame(
            {
                "emails": ["Contact alice@test.com", "No email here"],
                "phones": ["Call +44 20 1234 5678", "No phone here"],
            }
        )

        # Clean both columns using accessor
        df["clean_emails"] = df["emails"].pii.clean_pii("redact")
        df["clean_phones"] = df["phones"].pii.clean_pii("redact")

        assert df.shape == (2, 4)
        clean_emails = df["clean_emails"].tolist()
        clean_phones = df["clean_phones"].tolist()

        assert "alice@test.com" not in clean_emails[0]
        assert "+44 20 1234 5678" not in clean_phones[0]
        assert clean_emails[1] == "No email here"
        assert clean_phones[1] == "No phone here"

    def test_specific_cleaners_dataframe(self):
        """Test DataFrame methods with specific cleaners."""
        email_cleaner = Cleaner(["email"])
        df = pd.DataFrame(
            {
                "text": [
                    "Email alice@test.com and call +44 20 1234 5678",
                    "NINO: AB123456C",
                ]
            }
        )

        cleaned = email_cleaner.clean_pandas_dataframe(
            df, "text", "redact", new_column_name="cleaned"
        )
        detected = email_cleaner.detect_pandas_dataframe(df, "text")

        cleaned_texts = cleaned["cleaned"].tolist()

        # Should only clean/detect emails
        assert "alice@test.com" not in cleaned_texts[0]
        assert "+44 20 1234 5678" in cleaned_texts[0]  # Phone should remain
        assert cleaned_texts[1] == "NINO: AB123456C"  # NINO should remain

        # Detection should only find emails - check detection results column
        detection_results = detected["text_pii_detected"].tolist()

        # First row should have email detection
        assert len(detection_results[0]) > 0, "Should detect email in 1st row"
        detected_texts_row1 = [match["text"] for match in detection_results[0]]
        assert "alice@test.com" in detected_texts_row1
        assert "+44 20 1234 5678" not in detected_texts_row1

        # Second row should have no detections (no email)
        assert len(detection_results[1]) == 0, "Should not detect anything"

    def test_custom_replacement_string(self):
        """Test custom replacement string functionality."""
        custom_cleaner = Cleaner(replace_string="[REDACTED]")
        df = pd.DataFrame(
            {
                "text": [
                    "Email: test@example.com",
                    "No PII here",
                ]
            }
        )

        result = custom_cleaner.clean_pandas_dataframe(df, "text", "replace")
        cleaned_texts = result["text"].tolist()

        # Row with PII should use custom replacement string
        assert cleaned_texts[0] == "[REDACTED]"
        assert cleaned_texts[1] == "No PII here"  # No PII unchanged

        # Test with Series accessor
        series_result = df["text"].pii.clean_pii(
            "replace", replace_string="***REMOVED***"
        )
        assert series_result.iloc[0] == "***REMOVED***"
        assert series_result.iloc[1] == "No PII here"
