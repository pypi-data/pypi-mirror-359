"""Markdown preprocessing utilities for Confluence conversion."""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def preprocess_toc_for_confluence(markdown_content: str) -> str:
    """
    Preprocess markdown content to convert Table of Contents to Confluence TOC macro.
    
    This function detects markdown TOC patterns and replaces them with a placeholder
    that will be converted to the Confluence TOC macro after md2cf processing.
    
    Args:
        markdown_content: The markdown content to preprocess
        
    Returns:
        The preprocessed markdown with TOC placeholders
    """
    if not markdown_content:
        return markdown_content
    
    # First check for [TOC] or [[TOC]] markers
    toc_marker_pattern = re.compile(r'^\s*\[{1,2}TOC\]{1,2}\s*$', re.MULTILINE | re.IGNORECASE)
    result = toc_marker_pattern.sub('[[TOC_PLACEHOLDER]]', markdown_content)
    
    # If we found a [TOC] marker, we're done
    if result != markdown_content:
        logger.info("Found [TOC] marker to convert to Confluence macro")
        return result
    
    # Pattern to match Table of Contents section with flexible spacing
    # This matches:
    # - A heading (any level) containing "Table of Contents" 
    # - Followed by any amount of whitespace/blank lines
    # - Then a list (bullet, numbered, or mixed) that may or may not have links
    toc_pattern = re.compile(
        r'(#{1,6}\s*Table\s+of\s+Contents\s*\n)'  # Heading
        r'(\s*\n)*'  # Optional blank lines
        r'((?:(?:\s*(?:[-*+•]|\d+\.)\s*(?:\[[^\]]+\]\([^)]+\)|[^\n]+))(?:\n|$))+)',  # List items (with or without links)
        re.IGNORECASE | re.MULTILINE
    )
    
    def replace_toc(match):
        """Replace matched TOC with placeholder."""
        logger.info("Found markdown TOC section to convert to Confluence macro")
        return '[[TOC_PLACEHOLDER]]\n'
    
    # Perform the replacement
    result = toc_pattern.sub(replace_toc, result)
    
    # Also handle case where someone just has a heading "Table of Contents" with no list
    # (Confluence will generate the TOC from headings anyway)
    simple_toc_pattern = re.compile(
        r'(#{1,6}\s*Table\s+of\s+Contents\s*\n)(?=\s*(?:#{1,6}|$))',  # Heading followed by another heading or end
        re.IGNORECASE | re.MULTILINE
    )
    
    result = simple_toc_pattern.sub('[[TOC_PLACEHOLDER]]\n', result)
    
    if result != markdown_content:
        logger.info("Marked TOC for conversion with placeholder")
    
    return result


def postprocess_confluence_content(confluence_content: str) -> str:
    """
    Postprocess Confluence content to replace TOC placeholders with actual macros.
    
    Args:
        confluence_content: The Confluence storage format content
        
    Returns:
        The postprocessed content with TOC macros
    """
    if not confluence_content:
        return confluence_content
        
    # Replace the placeholder with the actual Confluence TOC macro
    if '[[TOC_PLACEHOLDER]]' in confluence_content:
        logger.info("Replacing TOC placeholder with Confluence macro")
        # The placeholder might be wrapped in <p> tags by md2cf
        confluence_content = confluence_content.replace(
            '<p>[[TOC_PLACEHOLDER]]</p>',
            '<ac:structured-macro ac:name="toc" />'
        )
        # Also handle case where it's not wrapped
        confluence_content = confluence_content.replace(
            '[[TOC_PLACEHOLDER]]',
            '<ac:structured-macro ac:name="toc" />'
        )
    
    return confluence_content


def preprocess_markdown_for_confluence(markdown_content: str) -> str:
    """
    Main preprocessing function for markdown to Confluence conversion.
    
    This is the main entry point for all markdown preprocessing before
    passing content to md2cf for conversion.
    
    Args:
        markdown_content: The markdown content to preprocess
        
    Returns:
        The preprocessed markdown ready for md2cf conversion
    """
    # Apply TOC preprocessing
    processed = preprocess_toc_for_confluence(markdown_content)
    
    # Future preprocessing steps can be added here
    
    return processed