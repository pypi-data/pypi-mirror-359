# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-30

### Added
- Initial release of OpenNutgraf
- Article extraction from URLs using readability and BeautifulSoup
- AI-powered summarization with OpenAI GPT models
- AI-powered summarization with Anthropic Claude models
- Flexible summary customization (length, tone, format)
- Paywall detection for articles
- Automatic chunking for long content
- Type hints throughout the codebase
- Comprehensive test suite
- Full documentation and examples

### Features
- `OpenNutgrafClient` - Main client interface
- `ArticleExtractor` - Smart article content extraction
- `LLMService` - Multi-provider LLM integration
- Support for multiple summary formats (prose, bullets)
- Support for multiple tones (neutral, conversational, professional)
- Support for multiple lengths (brief, standard, in-depth, custom)
- Error handling and validation
- Clean data models with serialization support

### Supported Models
- OpenAI: GPT-3.5 Turbo, GPT-4, GPT-4 Turbo, GPT-4o
- Anthropic: Claude 3 Haiku, Claude 3.5 Sonnet, Claude 3 Opus

[1.0.0]: https://github.com/nutgraf/opennutgraf/releases/tag/v1.0.0