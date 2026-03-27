#!/usr/bin/env python3
"""
transaction_templates.py - Transaction template management and citation type mapping.

This module provides transaction payload templates for different citation types (journal articles,
books, chapters, theses, conference papers). It also maps user-provided citation types (from CSV
or RIS files) to standardized transaction types and ILLiad request/document types.

Templates are structured as nested dicts: the outer dict maps citation types to field mappings. 
Field mappings define how entry fields map to ILLiad transaction fields. If an entry lacks a value,
the template's field name is used as a fallback placeholder.

Notes:
- Citation type mapping uses both RIS types and Zotero types.
- Field mappings are case-sensitive and must match ILLiad field names exactly.
- Authors from RIS are converted to comma-separated strings for compatibility with ILLiad templates.

Author: Kristen Wilson, NC State Libraries, kmblake@ncsu.edu
Editor: Aditi Singh, NC State Libraries, asingh39@ncsu.edu
"""

import yaml
import logging
import os
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def map_citation_type(citation_type: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Map a citation type from user input to standardized transaction values.

    This function loads citation type mappings from a YAML file and matches the provided
    citation_type against both RIS types and Zotero types.
    Matching is case-insensitive to improve usability.

    Args:
        citation_type: Citation type string from a CSV or RIS file.

    Returns:
        Tuple (transaction_template, illiad_request_type, illiad_doc_type).
        - transaction_template: Standardized template type (e.g., 'JOUR', 'BOOK', 'CHAP').
        - illiad_request_type: ILLiad request type (e.g., 'Article', 'Loan').
        - illiad_doc_type: ILLiad document type (e.g., 'Book', 'Journal').
        Returns (None, None, None) if the citation type is not recognized.

    Notes:
        - Both RIS and Zotero types are checked for flexibility across citation sources.
        - Comparison is case-insensitive to accommodate various input formats.
    """
    try:
        # Load the citation type mappings from the YAML configuration file.
        with open(os.path.join(os.path.dirname(__file__), "citation_types.yaml"), "r", encoding="utf-8") as file:
            citation_types = yaml.safe_load(file)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logger.error("Failed to load citation_types.yaml: %s", str(e))
        return None, None, None
    
    # Normalize input to lowercase for case-insensitive comparison
    citation_type_lower = str.lower(citation_type)

    # Iterate through defined citation types to find a match
    for type in citation_types:
        ris_types = str.lower(type.get('ris_type', ''))
        zotero_types = str.lower(type.get ('zotero_type', ''))

        if str.lower(citation_type) in ris_types or str.lower(citation_type) in zotero_types:
            return type['transaction_template'], type['illiad_request_type'], type['illiad_doc_type']
            
    # No match found
    return None, None, None

def get_transaction_templates_csv(
    email: str, pickup: str, row: Dict, illiad_request_type: str, illiad_doc_type: str
) -> Dict[str, Dict[str, str]]:
    """
    Generate transaction templates for CSV-sourced citations.

    This function returns a dict of transaction templates keyed by citation type (e.g., 'JOUR', 'BOOK').
    Each template is a field mapping that defines how to populate ILLiad transaction fields from
    CSV row data. For each field in the template, the caller will use row.get(template_field, fallback)
    to populate the transaction, filling in from the entry if available.

    Args:
        email: User email (ExternalUserId for all transactions).
        pickup: Pickup location (required for loan/physical requests).
        row: Dict representing a single CSV row (column names as keys).
        illiad_request_type: ILLiad request type (e.g., 'Article', 'Loan') from citation type mapping.
        illiad_doc_type: ILLiad document type (e.g., 'Book', 'Journal') from citation type mapping.

    Returns:
        Dict of transaction templates by citation type.
        Each template is a dict mapping ILLiad field names to CSV column names (or fallback values).

    Notes:
        - Templates assume standard Zotero CSV column names (Title, Author, Publication Title, etc.).
        - Fields not present in a given row will use the template field name as a placeholder.
        - Pickup location (ItemInfo4) is only included for loan-type requests.
    """

    return {
        'JOUR': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'PhotoJournalTitle': row.get('Publication Title', ''),
            'PhotoArticleTitle': row.get('Title', ''),
            'PhotoArticleAuthor': row.get('Author', ''),
            'PhotoJournalVolume': row.get('Volume', ''),
            'PhotoJournalIssue': row.get('Issue', ''),
            'PhotoJournalYear': row.get('Publication Year', ''),    
            'PhotoJournalInclusivePages': row.get('Pages', ''),
            'DOI': row.get('DOI', ''),
            'ISSN': row.get('ISSN', '')
        },
        'BOOK': {
            'ExternalUserId': email,
            'ItemInfo4': pickup,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'LoanTitle': row.get('Title', ''),
            'LoanAuthor': row.get('Author', ''),
            'LoanDate': row.get('Publication Year', ''),
            'ISSN': row.get('ISBN', ''),
            'LoanPublisher': row.get('Publisher', ''),
        },
        'CHAP': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'PhotoJournalTitle': row.get('Publication Title', ''),
            'PhotoArticleTitle': row.get('Title', ''),
            'PhotoArticleAuthor': row.get('Author', ''),
            'PhotoJournalVolume': row.get('Volume', ''),
            'PhotoJournalIssue': row.get('Issue', ''),
            'PhotoJournalYear': row.get('Publication Year', ''),    
            'PhotoJournalInclusivePages': row.get('Pages', ''),
            'DOI': row.get('DOI', ''),
            'ISSN': row.get('ISBN', '')
        },
        'THES': {
            'ExternalUserId': email,
            'ItemInfo4': pickup,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'LoanTitle': row.get('Title', ''),
            'LoanAuthor': row.get('Author', ''),
            'LoanDate': row.get('Publication Year', ''),
            'ISSN': row.get('ISBN', ''),
            'LoanPublisher': row.get('Publisher', ''),
        },
        'CONF': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'PhotoJournalTitle': row.get('Conference Name', ''),
            'PhotoArticleTitle': row.get('Title', ''),
            'PhotoArticleAuthor': row.get('Author', ''),
            'PhotoJournalVolume': row.get('Volume', ''),
            'PhotoJournalIssue': row.get('Issue', ''),
            'PhotoJournalYear': row.get('Publication Year', ''),    
            'PhotoJournalInclusivePages': row.get('Pages', ''),
            'DOI': row.get('DOI', ''),
            'ISSN': row.get('ISSN', '')
        },
}

def get_transaction_templates_ris(
    email: str, pickup: str, entry: Dict, illiad_request_type: str, illiad_doc_type: str
) -> Dict[str, Dict[str, str]]:
    """
    Generate transaction templates for RIS-sourced citations.

    This function returns a dict of transaction templates keyed by citation type. Templates use
    RIS field names (mapped to standardized keys by rispy_mapping.py) to populate ILLiad fields.
    Unlike CSV templates, RIS author lists are converted to comma-separated strings for compatibility.

    Args:
        email: User email (ExternalUserId for all transactions).
        pickup: Pickup location (required for loan/physical requests).
        entry: Dict representing a single RIS entry (with standardized RIS field names).
        illiad_request_type: ILLiad request type (e.g., 'Article', 'Loan').
        illiad_doc_type: ILLiad document type (e.g., 'Book', 'Journal').

    Returns:
        Dict of transaction templates by citation type.
        Each template is a dict mapping ILLiad field names to RIS field names (or fallback values).

    Notes:
        - RIS entries have authors as a list; templates expect a comma-separated string.
        - Page ranges are constructed by concatenating start_page and end_page with a hyphen.
        - RIS field names are standardized by rispy_mapping.map_rispy() before reaching this function.
    """
    return {
        'JOUR': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'DocumentType': illiad_doc_type,
            'ProcessType': 'Borrowing',
            'PhotoJournalTitle': entry.get('secondary_title', ''),
            'PhotoArticleTitle': entry.get('primary_title', ''),
            'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
            'PhotoJournalYear': entry.get('year', ''),
            'PhotoJournalVolume': entry.get('volume', ''),
            'PhotoJournalIssue': entry.get('number', ''),
            'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
            'PhotoItemPublisher': entry.get('publisher', ''),
            'PhotoItemPlace': entry.get('place_published', ''),
            'DOI': entry.get('doi', ''),
            'ISSN': entry.get('issn', '')
        },
        'CHAP': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'DocumentType': illiad_doc_type,
            'ProcessType': 'Borrowing',
            'PhotoJournalTitle': entry.get('secondary_title', ''),
            'PhotoArticleTitle': entry.get('primary_title', ''),
            'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
            'PhotoJournalVolume': entry.get('volume', ''),
            'PhotoJournalIssue': entry.get('number', ''),  
            'PhotoJournalYear': entry.get('year', ''),   
            'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
            'PhotoItemPublisher': entry.get('publisher', ''),
            'PhotoItemPlace': entry.get('place_published', ''),
            'DOI': entry.get('doi', ''),
            'ISSN': entry.get('issn', ''),
        },
        'BOOK': {
            'ExternalUserId': email,
            'ItemInfo4': pickup,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'LoanTitle': entry.get('primary_title', ''),
            'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
            'LoanDate': entry.get('year', ''),
            'LoanPublisher': entry.get('publisher', ''),
            'ISSN': entry.get('issn', ''),
        },
        'THES': {
            'ExternalUserId': email,
            'ItemInfo4': pickup,
            'RequestType': illiad_request_type,
            'ProcessType': 'Borrowing',
            'DocumentType': illiad_doc_type,
            'LoanTitle': entry.get('primary_title', ''),
            'LoanAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
            'LoanDate': entry.get('year', ''),
            'LoanPublisher': entry.get('publisher', ''),
        },
        'CONF': {
            'ExternalUserId': email,
            'RequestType': illiad_request_type,
            'DocumentType': illiad_doc_type,
            'ProcessType': 'Borrowing',
            'PhotoJournalTitle': entry.get('secondary_title', ''),
            'PhotoArticleTitle': entry.get('primary_title', ''),
            'PhotoArticleAuthor': ', '.join(entry.get('authors', '')) if isinstance(entry.get('authors', ''), list) else entry.get('authors', ''),
            'PhotoJournalVolume': entry.get('volume', ''),
            'PhotoJournalIssue': entry.get('number', ''),
            'PhotoJournalYear': entry.get('year', ''),
            'PhotoJournalInclusivePages': entry.get('start_page', '') + '-' + entry.get('end_page', ''),
            'PhotoItemPublisher': entry.get('publisher', ''),
            'PhotoItemPlace': entry.get('place_published', ''),
            'DOI': entry.get('doi', ''),
            'ISSN': entry.get('issn', '')
        },
}