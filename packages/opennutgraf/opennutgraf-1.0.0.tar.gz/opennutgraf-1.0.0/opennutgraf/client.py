"""
Main client for OpenNutgraf
"""

from typing import Optional, List, Dict, Any
from .article_extractor import ArticleExtractor
from .llm_service import LLMService
from .models import Article, Summary, SummaryOptions


class OpenNutgrafClient:
    """Main client for OpenNutgraf functionality"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        """
        Initialize OpenNutgraf client
        
        Args:
            openai_api_key: OpenAI API key for GPT models
            anthropic_api_key: Anthropic API key for Claude models
        """
        self.article_extractor = ArticleExtractor()
        self.llm_service = LLMService(openai_api_key, anthropic_api_key)
    
    def extract_article(self, url: str) -> Article:
        """
        Extract article content from a URL
        
        Args:
            url: The URL to extract content from
            
        Returns:
            Article object containing extracted content and metadata
        """
        return self.article_extractor.extract(url)
    
    def generate_summary(self, content: str, options: Optional[SummaryOptions] = None) -> Summary:
        """
        Generate a summary of the given content
        
        Args:
            content: The text content to summarize
            options: Summary generation options
            
        Returns:
            Summary object containing the generated summary
        """
        return self.llm_service.generate_summary(content, options)
    
    def extract_and_summarize(self, url: str, options: Optional[SummaryOptions] = None) -> Dict[str, Any]:
        """
        Extract article from URL and generate a summary
        
        Args:
            url: The URL to extract and summarize
            options: Summary generation options
            
        Returns:
            Dictionary containing both article and summary data
        """
        # Extract article
        article = self.extract_article(url)
        
        if article.error:
            return {
                'article': article.to_dict(),
                'summary': None,
                'error': article.error
            }
        
        if not article.content:
            return {
                'article': article.to_dict(),
                'summary': None,
                'error': 'No content available to summarize'
            }
        
        # Generate summary
        try:
            summary = self.generate_summary(article.content, options)
            return {
                'article': article.to_dict(),
                'summary': summary.to_dict(),
                'error': None
            }
        except Exception as e:
            return {
                'article': article.to_dict(),
                'summary': None,
                'error': str(e)
            }
    
    def summarize_text(self, text: str, options: Optional[SummaryOptions] = None) -> Summary:
        """
        Generate a summary of manually provided text
        
        Args:
            text: The text to summarize
            options: Summary generation options
            
        Returns:
            Summary object containing the generated summary
        """
        return self.generate_summary(text, options)
    
    def get_available_models(self) -> List[Dict[str, str]]:
        """
        Get list of available LLM models
        
        Returns:
            List of available models with their metadata
        """
        return self.llm_service.get_available_models()