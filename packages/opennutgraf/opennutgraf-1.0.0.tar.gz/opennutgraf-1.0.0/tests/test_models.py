"""
Tests for OpenNutgraf models
"""

import pytest
from datetime import datetime
from opennutgraf.models import Article, Summary, SummaryOptions


class TestArticle:
    """Test Article model"""
    
    def test_article_creation(self):
        """Test creating an Article instance"""
        article = Article(
            url="https://example.com",
            title="Test Article",
            author="Test Author",
            content="Test content here",
            word_count=3
        )
        
        assert article.url == "https://example.com"
        assert article.title == "Test Article"
        assert article.author == "Test Author"
        assert article.content == "Test content here"
        assert article.word_count == 3
        assert article.is_paywalled is False
        assert article.error is None
    
    def test_article_to_dict(self):
        """Test Article to_dict method"""
        pub_date = datetime.now()
        article = Article(
            url="https://example.com",
            title="Test Article",
            publication_date=pub_date,
            content="Test content",
            word_count=2
        )
        
        result = article.to_dict()
        
        assert result['url'] == "https://example.com"
        assert result['title'] == "Test Article"
        assert result['publication_date'] == pub_date.isoformat()
        assert result['content'] == "Test content"
        assert result['word_count'] == 2


class TestSummary:
    """Test Summary model"""
    
    def test_summary_creation(self):
        """Test creating a Summary instance"""
        summary = Summary(
            text="This is a summary",
            word_count=4,
            settings={'model': 'gpt-3.5-turbo'}
        )
        
        assert summary.text == "This is a summary"
        assert summary.word_count == 4
        assert summary.settings == {'model': 'gpt-3.5-turbo'}
    
    def test_summary_to_dict(self):
        """Test Summary to_dict method"""
        summary = Summary(
            text="Summary text",
            word_count=2,
            settings={'tone': 'neutral'}
        )
        
        result = summary.to_dict()
        
        assert result['text'] == "Summary text"
        assert result['word_count'] == 2
        assert result['settings'] == {'tone': 'neutral'}


class TestSummaryOptions:
    """Test SummaryOptions model"""
    
    def test_summary_options_defaults(self):
        """Test SummaryOptions with default values"""
        options = SummaryOptions()
        
        assert options.length == 'standard'
        assert options.tone == 'neutral'
        assert options.format_type == 'prose'
        assert options.model == 'gpt-3.5-turbo'
        assert options.custom_word_count is None
    
    def test_summary_options_custom(self):
        """Test SummaryOptions with custom values"""
        options = SummaryOptions(
            length='brief',
            tone='conversational',
            format_type='bullets',
            model='gpt-4',
            custom_word_count=150
        )
        
        assert options.length == 'brief'
        assert options.tone == 'conversational'
        assert options.format_type == 'bullets'
        assert options.model == 'gpt-4'
        assert options.custom_word_count == 150
    
    def test_summary_options_to_dict(self):
        """Test SummaryOptions to_dict method"""
        options = SummaryOptions(
            length='in_depth',
            tone='professional',
            custom_word_count=300
        )
        
        result = options.to_dict()
        
        assert result['length'] == 'in_depth'
        assert result['tone'] == 'professional'
        assert result['format'] == 'prose'  # Note: format_type -> format
        assert result['model'] == 'gpt-3.5-turbo'
        assert result['custom_word_count'] == 300