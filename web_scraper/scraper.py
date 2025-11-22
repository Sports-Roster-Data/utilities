"""
Web scraper utility using newspaper4k to extract article text from URLs.

This module provides functionality to retrieve and extract text content from
web articles using the newspaper4k library.
"""

from typing import Optional, Dict
from newspaper import Article


def extract_article_text(
    url: str,
    download_timeout: int = 10,
    include_metadata: bool = False
) -> Dict[str, Optional[str]]:
    """
    Extract text content from a web article URL using newspaper4k.

    Args:
        url: The URL of the article to scrape
        download_timeout: Timeout in seconds for downloading the article (default: 10)
        include_metadata: If True, include additional metadata like title, authors,
                         publish date, and top image (default: False)

    Returns:
        A dictionary containing:
            - 'text': The extracted article text
            - 'title': Article title (if include_metadata=True)
            - 'authors': List of authors (if include_metadata=True)
            - 'publish_date': Publication date (if include_metadata=True)
            - 'top_image': URL of the top image (if include_metadata=True)
            - 'url': The original URL
            - 'error': Error message if extraction failed

    Example:
        >>> result = extract_article_text('https://example.com/article')
        >>> print(result['text'])

        >>> result = extract_article_text('https://example.com/article', include_metadata=True)
        >>> print(f"Title: {result['title']}")
        >>> print(f"Text: {result['text']}")
    """
    result = {'url': url, 'error': None}

    try:
        # Create an Article object
        article = Article(url)

        # Download the article
        article.download()

        # Parse the article
        article.parse()

        # Extract the text
        result['text'] = article.text

        # Include metadata if requested
        if include_metadata:
            result['title'] = article.title
            result['authors'] = article.authors
            result['publish_date'] = article.publish_date.isoformat() if article.publish_date else None
            result['top_image'] = article.top_image

    except Exception as e:
        result['error'] = str(e)
        result['text'] = None
        if include_metadata:
            result['title'] = None
            result['authors'] = None
            result['publish_date'] = None
            result['top_image'] = None

    return result


def extract_article_text_simple(url: str) -> Optional[str]:
    """
    Simple wrapper to extract just the text content from a URL.

    Args:
        url: The URL of the article to scrape

    Returns:
        The extracted article text, or None if extraction failed

    Example:
        >>> text = extract_article_text_simple('https://example.com/article')
        >>> if text:
        ...     print(text)
    """
    result = extract_article_text(url)
    return result.get('text')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scraper.py <url> [--metadata]")
        print("\nExample:")
        print("  python scraper.py https://example.com/article")
        print("  python scraper.py https://example.com/article --metadata")
        sys.exit(1)

    url = sys.argv[1]
    include_metadata = '--metadata' in sys.argv

    print(f"Extracting article from: {url}\n")

    result = extract_article_text(url, include_metadata=include_metadata)

    if result['error']:
        print(f"Error: {result['error']}")
        sys.exit(1)

    if include_metadata:
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Authors: {', '.join(result.get('authors', [])) if result.get('authors') else 'N/A'}")
        print(f"Publish Date: {result.get('publish_date', 'N/A')}")
        print(f"Top Image: {result.get('top_image', 'N/A')}")
        print("\n" + "="*80 + "\n")

    print("Article Text:")
    print(result['text'])
