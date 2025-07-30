"""
Test OpenNutgraf imports
"""

def test_main_imports():
    """Test that main exports can be imported"""
    from opennutgraf import OpenNutgrafClient
    from opennutgraf import ArticleExtractor  
    from opennutgraf import LLMService
    from opennutgraf import Summary
    from opennutgraf import Article
    from opennutgraf import SummaryOptions
    
    # Test that classes can be instantiated
    assert OpenNutgrafClient is not None
    assert ArticleExtractor is not None
    assert LLMService is not None
    assert Summary is not None
    assert Article is not None
    assert SummaryOptions is not None


def test_version_import():
    """Test that version can be imported"""
    import opennutgraf
    
    assert hasattr(opennutgraf, '__version__')
    assert isinstance(opennutgraf.__version__, str)
    assert len(opennutgraf.__version__) > 0


def test_all_exports():
    """Test that __all__ contains expected exports"""
    import opennutgraf
    
    expected_exports = [
        "OpenNutgrafClient", 
        "ArticleExtractor", 
        "LLMService", 
        "Summary", 
        "Article", 
        "SummaryOptions"
    ]
    
    assert hasattr(opennutgraf, '__all__')
    
    for export in expected_exports:
        assert export in opennutgraf.__all__
        assert hasattr(opennutgraf, export)