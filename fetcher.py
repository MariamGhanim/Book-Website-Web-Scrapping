import requests
import time
from typing import Optional


def fetch_html(url: str, timeout: int = 30, retry_attempts: int = 3) -> Optional[str]:
    """
    Fetch HTML content from the given URL.
    
    Args:
        url (str): The URL to fetch HTML content from
        timeout (int): Request timeout in seconds (default: 30)
        retry_attempts (int): Number of retry attempts if request fails (default: 3)
    
    Returns:
        Optional[str]: HTML content as a string, or None if fetch fails
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retry_attempts):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retry_attempts - 1:
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"Failed to fetch {url} after {retry_attempts} attempts")
                return None


def fetch_books_page(page_number: int = 1) -> Optional[str]:
    """
    Fetch a specific page from books.toscrape.com
    
    Args:
        page_number (int): Page number to fetch (default: 1)
    
    Returns:
        Optional[str]: HTML content as a string, or None if fetch fails
    """
    if page_number == 1:
        url = "https://books.toscrape.com/"
    else:
        url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
    
    return fetch_html(url)


def fetch_book_detail(book_url: str) -> Optional[str]:
    """
    Fetch detailed information for a specific book.
    
    Args:
        book_url (str): Relative or absolute URL to the book detail page
    
    Returns:
        Optional[str]: HTML content as a string, or None if fetch fails
    """
    if not book_url.startswith('http'):
        # Handle relative URLs - remove leading '../' and add base URL
        base_url = "https://books.toscrape.com/"
        clean_url = book_url.lstrip('../')
        book_url = base_url + clean_url
    
    return fetch_html(book_url)


# Example usage
if __name__ == "__main__":
    # Test fetching the main page
    html_content = fetch_books_page()
    if html_content:
        print(f"Successfully fetched HTML content ({len(html_content)} characters)")
        print("First 200 characters:")
        print(html_content[:200])
    else:
        print("Failed to fetch HTML content")