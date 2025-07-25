"""
ArcanAgent Knowledge Management System

This package contains the knowledge management components:
- Markdown Parser: Parse and process markdown files with bidirectional links
- Link Analyzer: Analyze link density and relationships
- Note Manager: Manage individual notes and their metadata
- ZPD Analyzer: Analyze Zone of Proximal Development
"""

from .note_manager import NoteManager, NoteInfo
# from .markdown_parser import MarkdownParser
# from .link_analyzer import LinkAnalyzer
# from .zpd_analyzer import ZPDAnalyzer

__all__ = [
    "NoteManager",
    "NoteInfo",
    # "MarkdownParser", 
    # "LinkAnalyzer",
    # "ZPDAnalyzer"
]