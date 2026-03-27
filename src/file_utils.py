"""
file_utils.py - File validation and reading utilities.

This module handles validation and parsing of input files (CSV and RIS formats).
Functions raise domain exceptions (from exceptions.py) for callers to handle.
Logging is diagnostic-level only; user-facing messages are produced in main().

Notes:
- CSV files must contain an "Item Type" column to be valid.
- RIS files are identified by the "TY  -" tag on the first non-blank line.
- Empty files and unrecognized formats raise specific exceptions for clarity.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

import os
import csv
import logging

from typing import List, Tuple
from config import settings
from exceptions import (
    BillyFileNotFoundError,
    InvalidFileError,
    EmptyFileError,
)

logger = logging.getLogger(__name__)

# Columns that must be present in a CSV file for it to be valid.
REQUIRED_CSV_COLUMNS = {"Item Type"}


def validate_file(filename: str, messages: List[str]) -> Tuple[str, str, List[str]]:
    """
    Validate that an input file exists and determine its type (CSV or RIS).

    This function checks file existence, identifies the format by examining the
    first non-blank line, and validates format-specific requirements (e.g., CSV
    must have required columns). Empty files and unrecognized formats raise specific
    exceptions for clear error reporting.

    Args:
        filename: Name of the file to validate (located in DATA_FILES_DIR).
        messages: List to append human-readable status messages for the caller.

    Returns:
        Tuple (filepath, filetype, messages).
        - filepath: Absolute path to the validated file.
        - filetype: Either 'csv' or 'ris'.
        - messages: Updated messages list (for convenience).

    Raises:
        BillyFileNotFoundError: File not found or cannot be read (I/O error).
        EmptyFileError: File exists but contains no content.
        InvalidFileError: File format is unrecognized or missing required columns.
    """

    # Construct absolute filepath relative to the configured data directory
    filepath = os.path.join(settings.data_files_dir, filename)

    # Check if file exists before attempting to open
    if not os.path.isfile(filepath):
        logger.error("File not found: %s", filepath)
        raise BillyFileNotFoundError(f"The file {filepath} does not exist.")

    # Verify that the file is either a RIS or CSV file.
    filetype = None
    try:
        with open(filepath, 'r', encoding='utf-8') as file:

            # Read lines until we find a non-blank one (skip leading whitespace)
            first_line = ''
            while True:
                line = file.readline()
                if line == '':
                    # EOF reached without content
                    raise EmptyFileError(f"The file {filepath} is empty.")
                first_line = line.strip()
                if first_line:
                    break
            
            
            # Identify RIS file format by RIS type tag
            if 'TY  -' in first_line:
                filetype = 'ris'
                messages.append('RIS file confirmed.')
            
            # Identify CSV format by comma delimiter
            elif ',' in first_line:
                try:
                    # Reset file pointer to the beginning to re-read headers
                    file.seek(0)
                    reader = csv.DictReader(file)

                    # Validate that required columns are present in the header row
                    missing = REQUIRED_CSV_COLUMNS - set(reader.fieldnames or [])
                    if missing:
                        logger.error("Missing %s column in CSV: %s", ', '.join(sorted(missing)), filepath)
                        raise InvalidFileError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
                    
                    filetype = 'csv'
                    messages.append('CSV file confirmed.')
                
                # Catch CSV parsing errors
                except csv.Error as e:
                    logger.error("CSV parsing error: %s - %s", filepath, str(e))
                    raise InvalidFileError(f"The file {filepath} is not a valid CSV file: {str(e)}")
            
            # Unrecognized format: neither RIS nor CSV
            else:
                logger.error("Invalid file type: %s", filepath)
                raise InvalidFileError(f"The file {filename} is not a valid file type. Must be CSV or RIS.")
    
    # Catch file system errors
    except (OSError, IOError) as e:
        logger.error("I/O error reading file: %s - %s", filepath, str(e))
        raise InvalidFileError(f"Error reading file {filepath}: {str(e)}")
    return filepath, filetype, messages

def read_csv(filepath: str):
    """
    Generator that yields each row from a CSV file as a dict.

    Args:
        filepath: Absolute path to the CSV file to read.

    Yields:
        Dict representing each CSV row (column names as keys).

    Raises:
        OSError: If the file cannot be opened or read.
        csv.Error: If the CSV is malformed.
    """

    with open(filepath, 'r', encoding='utf-8-sig') as source_file:
        reader = csv.DictReader(source_file)
        for row in reader:
            yield row