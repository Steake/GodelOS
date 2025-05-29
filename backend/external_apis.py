"""
External API interfaces for knowledge ingestion.

Provides interfaces for Wikipedia, web scraping, and content processing.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class WikipediaAPI:
    """Wikipedia API interface."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize Wikipedia API."""
        logger.info("Initializing Wikipedia API...")
        self.initialized = True
        logger.info("Wikipedia API initialized")
    
    async def shutdown(self):
        """Shutdown Wikipedia API."""
        logger.info("Shutting down Wikipedia API...")
        self.initialized = False
        logger.info("Wikipedia API shutdown complete")
    
    async def get_page_content(self, title: str, language: str = "en") -> Dict[str, Any]:
        """Get Wikipedia page content."""
        # Mock implementation - would use actual Wikipedia API
        return {
            "title": title,
            "content": f"Mock Wikipedia content for: {title}",
            "url": f"https://{language}.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "language": language,
            "summary": f"This is a mock summary for {title}",
            "sections": ["Introduction", "History", "References"]
        }


class WebScraper:
    """Web scraping interface."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize web scraper."""
        logger.info("Initializing Web Scraper...")
        self.initialized = True
        logger.info("Web Scraper initialized")
    
    async def shutdown(self):
        """Shutdown web scraper."""
        logger.info("Shutting down Web Scraper...")
        self.initialized = False
        logger.info("Web Scraper shutdown complete")
    
    async def scrape_url(self, url: str, selectors: List[str] = None) -> Dict[str, Any]:
        """Scrape content from a URL."""
        # Mock implementation - would use actual web scraping
        return {
            "url": url,
            "title": f"Content from {url}",
            "content": f"Mock scraped content from {url}",
            "text_content": f"Extracted text content from {url}",
            "images": [],
            "links": [],
            "metadata": {
                "description": f"Mock description for {url}",
                "keywords": ["mock", "content", "scraping"]
            }
        }


class ContentProcessor:
    """Content processing utilities."""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?;:()-]', '', text)
        return text.strip()
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_content(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split content into chunks."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction - count word frequency
        words = re.findall(r'\b\w{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def detect_language(self, text: str) -> str:
        """Detect language of text content."""
        # Simple language detection - would use proper library in production
        if any(ord(char) > 127 for char in text):
            return "non-english"
        return "en"


# Global instances
wikipedia_api = WikipediaAPI()
web_scraper = WebScraper()
content_processor = ContentProcessor()