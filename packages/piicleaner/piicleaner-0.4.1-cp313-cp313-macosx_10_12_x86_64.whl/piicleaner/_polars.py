"""Polars extensions for PII cleaning"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class PolarsCleanerMixin:
    """Mixin class to add Polars functionality to Cleaner"""

    def clean_dataframe(
        self,
        df: pl.DataFrame,
        column_name: str,
        cleaning: str,
        ignore_case: bool = True,
        new_column_name: str = None,
    ):
        """Clean PII in a Polars DataFrame column.

        Args:
            df (pl.DataFrame): Polars DataFrame.
            column_name (str): Name of the column to clean.
            cleaning (str): Cleaning method ("redact" or "replace").
            ignore_case (bool): Should we ignore case when detecting PII?
                Defaults to True.
            new_column_name (str | None): Name for the new cleaned column. If
                None, overwrites original. Defaults to None.

        Returns:
            pl.DataFrame: DataFrame with cleaned column.
        """
        if not POLARS_AVAILABLE:
            raise ImportError("polars is required for DataFrame operations")

        if not isinstance(df, pl.DataFrame):
            raise TypeError("df must be a polars DataFrame")

        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")

        # Use the clean_pii_list method which respects specific cleaners
        texts = df.get_column(column_name).to_list()
        # Handle null values - replace with empty strings for processing
        processed_texts = [
            str(text) if text is not None else "" for text in texts
        ]
        cleaned_texts = self.clean_pii_list(
            processed_texts, cleaning, ignore_case
        )

        # Restore null values in the results
        for i, original_text in enumerate(texts):
            if original_text is None:
                cleaned_texts[i] = None

        # Create new DataFrame with cleaned column
        if new_column_name is None:
            new_column_name = column_name

        result_df = df.with_columns(
            pl.Series(name=new_column_name, values=cleaned_texts)
        )

        return result_df

    def detect_dataframe(
        self,
        df: pl.DataFrame,
        column_name: str,
        ignore_case: bool = True,
        new_column_name: str = None,
    ):
        """Detect PII in a Polars DataFrame column.

        Args:
            df (pl.DataFrame): Polars DataFrame.
            column_name (str): Name of the column to analyse.
            ignore_case (bool): Should we ignore case when detecting PII?
                Defaults to True.
            new_column_name (str | None): Name for the new detection column. If
                None, uses "{column_name}_pii_detected". Defaults to None.

        Returns:
            pl.DataFrame: DataFrame with detection results added as a
                list column.
        """
        if not POLARS_AVAILABLE:
            raise ImportError("polars is required for DataFrame operations")

        if not isinstance(df, pl.DataFrame):
            raise TypeError("df must be a polars DataFrame")

        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")

        # Set default column name
        if new_column_name is None:
            new_column_name = f"{column_name}_pii_detected"

        # Get texts and use Cleaner's detect_pii_list method
        texts = df.get_column(column_name).to_list()
        # Handle null values - replace with empty strings for processing
        processed_texts = [
            str(text) if text is not None else "" for text in texts
        ]
        batch_results = self.detect_pii_list(processed_texts, ignore_case)

        # Set empty results for null values
        for i, original_text in enumerate(texts):
            if original_text is None:
                batch_results[i] = []

        # Convert to Polars list of structs format
        detection_results = []
        for matches in batch_results:
            # Convert each row's matches to list of dicts for Polars
            row_matches = [
                {
                    "start": match["start"],
                    "end": match["end"],
                    "text": match["text"],
                    "type": match["type"],
                }
                for match in matches
            ]
            detection_results.append(row_matches)

        # Add detection results as new column
        result_df = df.with_columns(
            pl.Series(
                name=new_column_name,
                values=detection_results,
                dtype=pl.List(
                    pl.Struct(
                        [
                            pl.Field("start", pl.Int64),
                            pl.Field("end", pl.Int64),
                            pl.Field("text", pl.String),
                            pl.Field("type", pl.String),
                        ]
                    )
                ),
            )
        )

        return result_df
