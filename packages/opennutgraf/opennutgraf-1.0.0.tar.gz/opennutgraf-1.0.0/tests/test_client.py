"""
Tests for OpenNutgraf client
"""

import pytest
from unittest.mock import Mock, patch
from opennutgraf import OpenNutgrafClient, SummaryOptions
from opennutgraf.models import Article, Summary


class TestOpenNutgrafClient:
    """Test OpenNutgrafClient"""
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = OpenNutgrafClient()
        
        assert client.article_extractor is not None
        assert client.llm_service is not None
    
    def test_client_initialization_with_keys(self):
        """Test client initialization with API keys"""
        client = OpenNutgrafClient(
            openai_api_key="test-openai-key",
            anthropic_api_key="test-anthropic-key"
        )
        
        assert client.article_extractor is not None
        assert client.llm_service is not None
    
    @patch('opennutgraf.client.ArticleExtractor')
    def test_extract_article(self, mock_extractor):
        """Test article extraction"""
        # Mock the extractor
        mock_article = Article(
            url="https://example.com",
            title="Test Article",
            content="Test content",
            word_count=2
        )
        mock_extractor.return_value.extract.return_value = mock_article
        
        client = OpenNutgrafClient()
        result = client.extract_article("https://example.com")
        
        assert isinstance(result, Article)
        assert result.url == "https://example.com"
        assert result.title == "Test Article"
    
    @patch('opennutgraf.client.LLMService')
    def test_generate_summary(self, mock_llm_service):
        """Test summary generation"""
        # Mock the LLM service
        mock_summary = Summary(text="Test summary", word_count=2)
        mock_llm_service.return_value.generate_summary.return_value = mock_summary
        
        client = OpenNutgrafClient()
        options = SummaryOptions()
        result = client.generate_summary("Test content", options)
        
        assert isinstance(result, Summary)
        assert result.text == "Test summary"
        assert result.word_count == 2
    
    @patch('opennutgraf.client.ArticleExtractor')
    @patch('opennutgraf.client.LLMService')
    def test_extract_and_summarize_success(self, mock_llm_service, mock_extractor):
        """Test successful extract and summarize"""
        # Mock the extractor
        mock_article = Article(
            url="https://example.com",
            title="Test Article",
            content="Test content",
            word_count=2
        )
        mock_extractor.return_value.extract.return_value = mock_article
        
        # Mock the LLM service
        mock_summary = Summary(text="Test summary", word_count=2)
        mock_llm_service.return_value.generate_summary.return_value = mock_summary
        
        client = OpenNutgrafClient()
        result = client.extract_and_summarize("https://example.com")
        
        assert result['error'] is None
        assert result['article']['title'] == "Test Article"
        assert result['summary']['text'] == "Test summary"
    
    @patch('opennutgraf.client.ArticleExtractor')
    def test_extract_and_summarize_extraction_error(self, mock_extractor):
        """Test extract and summarize with extraction error"""
        # Mock the extractor to return an error
        mock_article = Article(
            url="https://example.com",
            error="Failed to extract"
        )
        mock_extractor.return_value.extract.return_value = mock_article
        
        client = OpenNutgrafClient()
        result = client.extract_and_summarize("https://example.com")
        
        assert result['error'] == "Failed to extract"
        assert result['summary'] is None
    
    @patch('opennutgraf.client.ArticleExtractor')
    def test_extract_and_summarize_no_content(self, mock_extractor):
        """Test extract and summarize with no content"""
        # Mock the extractor to return no content
        mock_article = Article(
            url="https://example.com",
            title="Test Article",
            content=None,
            word_count=0
        )
        mock_extractor.return_value.extract.return_value = mock_article
        
        client = OpenNutgrafClient()
        result = client.extract_and_summarize("https://example.com")
        
        assert result['error'] == "No content available to summarize"
        assert result['summary'] is None
    
    def test_summarize_text(self):
        """Test text summarization"""
        with patch.object(OpenNutgrafClient, 'generate_summary') as mock_generate:
            mock_summary = Summary(text="Summary", word_count=1)
            mock_generate.return_value = mock_summary
            
            client = OpenNutgrafClient()
            result = client.summarize_text("Test text")
            
            assert result == mock_summary
            mock_generate.assert_called_once()
    
    @patch('opennutgraf.client.LLMService')
    def test_get_available_models(self, mock_llm_service):
        """Test getting available models"""
        mock_models = [
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'provider': 'OpenAI'}
        ]
        mock_llm_service.return_value.get_available_models.return_value = mock_models
        
        client = OpenNutgrafClient()
        result = client.get_available_models()
        
        assert result == mock_models