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
    
    # Pattern to match Table of Contents section
    # This matches:
    # - A heading (any level) containing "Table of Contents"
    # - Followed by a list of links with anchors
    toc_pattern = re.compile(
        r'(#{1,6}\s*Table\s+of\s+Contents\s*\n)'  # Heading
        r'((?:\s*(?:[-*+]|\d+\.)\s*\[[^\]]+\]\(#[^\)]+\)(?:\s*\n)?)+)',  # List items with links
        re.IGNORECASE | re.MULTILINE
    )
    
    def replace_toc(match):
        """Replace matched TOC with placeholder."""
        # Log that we found a TOC to convert
        logger.info("Found markdown TOC to convert to Confluence macro")
        
        # Return a placeholder that won't be escaped by md2cf
        return '[[TOC_PLACEHOLDER]]\n'
    
    # Perform the replacement
    result = toc_pattern.sub(replace_toc, markdown_content)
    
    # If we made any replacements, log it
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