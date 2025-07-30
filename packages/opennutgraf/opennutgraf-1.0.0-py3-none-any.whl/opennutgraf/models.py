"""
Data models for OpenNutgraf
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Article:
    """Represents an extracted article"""
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    content: Optional[str] = None
    word_count: int = 0
    is_paywalled: bool = False
    error: Optional[str] = None
    paywall_warning: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'url': self.url,
            'title': self.title,
            'author': self.author,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'content': self.content,
            'word_count': self.word_count,
            'is_paywalled': self.is_paywalled,
            'error': self.error,
            'paywall_warning': self.paywall_warning
        }


@dataclass
class Summary:
    """Represents a generated summary"""
    text: str
    word_count: int
    settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'word_count': self.word_count,
            'settings': self.settings or {}
        }


@dataclass
class SummaryOptions:
    """Options for summary generation"""
    length: str = 'standard'  # brief, standard, in_depth, custom
    tone: str = 'neutral'  # neutral, conversational, professional
    format_type: str = 'prose'  # prose, bullets
    model: str = 'gpt-3.5-turbo'
    custom_word_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'length': self.length,
            'tone': self.tone,
            'format': self.format_type,
            'model': self.model,
            'custom_word_count': self.custom_word_count
        }