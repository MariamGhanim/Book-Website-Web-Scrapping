from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


def parse_books_from_html(html_content: str) -> List[Dict[str, str]]:
    """
    Parse HTML content and extract book information like title and price.
    
    Args:
        html_content (str): HTML content from books.toscrape.com
    
    Returns:
        List[Dict[str, str]]: List of dictionaries with 'Title' and 'Price' keys
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    
    # Find all book containers (articles with class 'product_pod')
    book_containers = soup.find_all('article', class_='product_pod')
    
    for book in book_containers:
        book_info = {}
        
        # Extract title - it's in the 'title' attribute of the <a> tag within h3
        title_element = book.find('h3').find('a')
        if title_element:
            book_info['Title'] = title_element.get('title', '').strip()
        
        # Extract price - it's in the <p> tag with class 'price_color'
        price_element = book.find('p', class_='price_color')
        if price_element:
            book_info['Price'] = price_element.text.strip()
        
        # Only add book if both title and price are found
        if 'Title' in book_info and 'Price' in book_info:
            books.append(book_info)
    
    return books


def parse_book_details(html_content: str) -> Dict[str, str]:
    """
    Parse detailed book information from a book's detail page.
    
    Args:
        html_content (str): HTML content from a book's detail page
    
    Returns:
        Dict[str, str]: Dictionary with detailed book information
    """
    if not html_content:
        return {}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    book_details = {}
    
    # Extract title
    title_element = soup.find('h1')
    if title_element:
        book_details['Title'] = title_element.text.strip()
    
    # Extract price
    price_element = soup.find('p', class_='price_color')
    if price_element:
        book_details['Price'] = price_element.text.strip()
    
    # Extract availability
    availability_element = soup.find('p', class_='instock availability')
    if availability_element:
        book_details['Availability'] = availability_element.text.strip()
    
    # Extract product information from the table
    product_table = soup.find('table', class_='table table-striped')
    if product_table:
        rows = product_table.find_all('tr')
        for row in rows:
            header = row.find('th')
            data = row.find('td')
            if header and data:
                key = header.text.strip()
                value = data.text.strip()
                book_details[key] = value
    
    # Extract description
    description_div = soup.find('div', id='product_description')
    if description_div:
        description_p = description_div.find_next_sibling('p')
        if description_p:
            book_details['Description'] = description_p.text.strip()
    
    # Extract rating
    rating_element = soup.find('p', class_=re.compile(r'star-rating'))
    if rating_element:
        rating_classes = rating_element.get('class', [])
        for class_name in rating_classes:
            if class_name in ['One', 'Two', 'Three', 'Four', 'Five']:
                book_details['Rating'] = class_name
                break
    
    return book_details


def clean_price(price_str: str) -> float:
    """
    Clean and convert price string to float.
    
    Args:
        price_str (str): Price string like '£51.77' or 'Â£51.77'
    
    Returns:
        float: Price as a float number
    """
    if not price_str:
        return 0.0
    
    # Remove currency symbols (including the special character Â) and whitespace
    cleaned = re.sub(r'[£$€¥Â]', '', price_str).strip()
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def get_book_urls(html_content: str) -> List[str]:
    """
    Extract book detail page URLs from the main listing page.
    
    Args:
        html_content (str): HTML content from books listing page
    
    Returns:
        List[str]: List of relative URLs to book detail pages
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    urls = []
    
    # Find all book links
    book_containers = soup.find_all('article', class_='product_pod')
    
    for book in book_containers:
        link_element = book.find('h3').find('a')
        if link_element:
            href = link_element.get('href', '')
            if href:
                urls.append(href)
    
    return urls


# Example usage and testing
if __name__ == "__main__":
    # Test with sample HTML (you would use fetcher.py to get real HTML)
    from fetcher import fetch_books_page
    
    print("Testing parser with live data from books.toscrape.com...")
    html_content = fetch_books_page()
    
    if html_content:
        books = parse_books_from_html(html_content)
        print(f"Found {len(books)} books:")
        
        # Display first 5 books
        for i, book in enumerate(books[:5], 1):
            print(f"{i}. {book['Title']} - {book['Price']}")
        
        # Test price cleaning
        if books:
            sample_price = books[0]['Price']
            cleaned_price = clean_price(sample_price)
            print(f"\nPrice cleaning test: '{sample_price}' -> {cleaned_price}")
        
        # Test URL extraction
        urls = get_book_urls(html_content)
        print(f"\nFound {len(urls)} book URLs")
        if urls:
            print(f"First URL: {urls[0]}")
    else:
        print("Failed to fetch HTML content for testing")