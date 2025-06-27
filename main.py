#!/usr/bin/env python3
"""
Main script for web scraping books from books.toscrape.com

This script integrates the fetcher, parser, and saver modules to create
a complete web scraping workflow that:
1. Fetches HTML content from books.toscrape.com
2. Parses the HTML to extract book information
3. Saves the data to a CSV file
"""

import time
from typing import List, Dict
from fetcher import fetch_books_page, fetch_book_detail
from parser import parse_books_from_html, parse_book_details
from saver import save_books_to_csv, append_books_to_csv, get_csv_summary


def scrape_single_page(page_number: int = 1) -> List[Dict[str, str]]:
    """
    Scrape a single page of books from books.toscrape.com
    
    Args:
        page_number (int): Page number to scrape (default: 1)
    
    Returns:
        List[Dict[str, str]]: List of book dictionaries
    """
    print(f"Scraping page {page_number}...")
    
    # Fetch HTML content
    html_content = fetch_books_page(page_number)
    if not html_content:
        print(f"Failed to fetch page {page_number}")
        return []
    
    # Parse books from HTML
    books = parse_books_from_html(html_content)
    print(f"Found {len(books)} books on page {page_number}")
    
    return books


def scrape_multiple_pages(start_page: int = 1, num_pages: int = 5, delay: float = 1.0) -> List[Dict[str, str]]:
    """
    Scrape multiple pages of books from books.toscrape.com
    
    Args:
        start_page (int): Starting page number (default: 1)
        num_pages (int): Number of pages to scrape (default: 5)
        delay (float): Delay between requests in seconds (default: 1.0)
    
    Returns:
        List[Dict[str, str]]: Combined list of all books from all pages
    """
    all_books = []
    
    for page in range(start_page, start_page + num_pages):
        books = scrape_single_page(page)
        if books:
            all_books.extend(books)
            
            # Add delay between requests to be respectful to the server
            if page < start_page + num_pages - 1:  # Don't delay after the last page
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
        else:
            print(f"No more books found. Stopping at page {page}")
            break
    
    return all_books


def scrape_all_pages(start_page: int = 1, delay: float = 1.0) -> List[Dict[str, str]]:
    """
    Scrape ALL available pages from books.toscrape.com until 'Page not found'
    
    Args:
        start_page (int): Starting page number (default: 1)
        delay (float): Delay between requests in seconds (default: 1.0)
    
    Returns:
        List[Dict[str, str]]: Combined list of all books from all available pages
    """
    all_books = []
    page = start_page
    
    print(f"🔄 Starting to scrape all pages from page {start_page}...")
    
    while True:
        print(f"Scraping page {page}...")
        
        # Fetch HTML content
        html_content = fetch_books_page(page)
        
        # Check if page exists (contains book data or shows "Page not found")
        if not html_content:
            print(f"❌ Failed to fetch page {page}")
            break
        
        # Check for "Page not found" or similar indicators
        if is_page_not_found(html_content):
            print(f"📄 Page {page} not found - reached the end of available pages")
            break
        
        # Parse books from HTML
        books = parse_books_from_html(html_content)
        
        if not books:
            print(f"📭 No books found on page {page} - reached the end")
            break
        
        print(f"✅ Found {len(books)} books on page {page}")
        all_books.extend(books)
        
        # Add delay between requests to be respectful to the server
        print(f"⏳ Waiting {delay} seconds before next request...")
        time.sleep(delay)
        
        page += 1
    
    total_pages_scraped = page - start_page
    print(f"\n🎯 Scraping completed! Total pages scraped: {total_pages_scraped}")
    print(f"📚 Total books found: {len(all_books)}")
    
    return all_books


def is_page_not_found(html_content: str) -> bool:
    """
    Check if the HTML content indicates a 'Page not found' or similar error
    
    Args:
        html_content (str): HTML content to check
    
    Returns:
        bool: True if page not found, False otherwise
    """
    if not html_content:
        return True
    
    # Convert to lowercase for case-insensitive checking
    content_lower = html_content.lower()
    
    # More specific indicators of a "page not found" or error page
    not_found_indicators = [
        'page not found',
        '404 not found',
        'error 404',
        'sorry, no results found',
        'no results found'
    ]
    
    # Check if any indicator is present
    for indicator in not_found_indicators:
        if indicator in content_lower:
            return True
    
    # Check if the page has a very short body (likely an error page)
    # But be more lenient - only if it's extremely short
    if len(html_content.strip()) < 500:  # Much lower threshold
        return True
    
    # Check if page has "404" in title
    if '<title>' in content_lower and '404' in content_lower.split('<title>')[1].split('</title>')[0]:
        return True
    
    return False


def scrape_book_details(books: List[Dict[str, str]], max_details: int = 5) -> List[Dict[str, str]]:
    """
    Scrape detailed information for a subset of books
    
    Args:
        books (List[Dict[str, str]]): List of basic book information
        max_details (int): Maximum number of books to get details for (default: 5)
    
    Returns:
        List[Dict[str, str]]: List of books with detailed information
    """
    from parser import get_book_urls
    
    print(f"Scraping detailed information for up to {max_details} books...")
    detailed_books = []
    
    # Get book URLs from the first page (for demonstration)
    html_content = fetch_books_page(1)
    if html_content:
        book_urls = get_book_urls(html_content)
        
        for i, url in enumerate(book_urls[:max_details]):
            print(f"Getting details for book {i+1}/{min(len(book_urls), max_details)}...")
            
            detail_html = fetch_book_detail(url)
            if detail_html:
                book_details = parse_book_details(detail_html)
                if book_details:
                    detailed_books.append(book_details)
            
            # Small delay between detail requests
            time.sleep(0.5)
    
    return detailed_books


def main():
    """
    Main function that orchestrates the web scraping workflow
    """
    print("=" * 60)
    print("🕷️  Starting Books Web Scraping Project")
    print("=" * 60)
    
    # Configuration
    filename = "books.csv"
    request_delay = 1.0
    
    # Ask user for scraping preference
    print("\n🔧 Scraping Options:")
    print("1. Quick scrape (first 3 pages only)")
    print("2. Complete scrape (ALL available pages)")
    choice = input("Choose an option (1 or 2, default is 1): ").strip()
    
    try:
        if choice == "2":
            print(f"\n🌐 Starting COMPLETE scrape of ALL pages...")
            all_books = scrape_all_pages(start_page=1, delay=request_delay)
        else:
            print(f"\n📚 Starting QUICK scrape (3 pages)...")
            all_books = scrape_multiple_pages(
                start_page=1, 
                num_pages=3, 
                delay=request_delay
            )
        
        if all_books:
            print(f"\n✅ Successfully scraped {len(all_books)} books")
            
            # Save to CSV
            print(f"\n💾 Saving data to '{filename}'...")
            success = save_books_to_csv(all_books, filename)
            
            if success:
                # Display summary
                print(f"\n📊 Data Summary:")
                get_csv_summary(filename)
                
                # Option 2: Scrape detailed information for a few books (only for smaller datasets)
                if len(all_books) <= 100:  # Only get details if dataset is manageable
                    print(f"\n🔍 Getting detailed information for sample books...")
                    detailed_books = scrape_book_details(all_books, max_details=3)
                    
                    if detailed_books:
                        print(f"\n📋 Sample detailed book information:")
                        for i, book in enumerate(detailed_books, 1):
                            print(f"\n--- Book {i} Details ---")
                            for key, value in book.items():
                                if len(str(value)) > 100:  # Truncate long descriptions
                                    value = str(value)[:100] + "..."
                                print(f"{key}: {value}")
                else:
                    print(f"\n💡 Dataset is large ({len(all_books)} books), skipping detailed scraping")
                
            else:
                print("❌ Failed to save data to CSV")
        
        else:
            print("❌ No books were scraped")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    
    finally:
        print(f"\n🏁 Web scraping completed!")
        print("=" * 60)


def quick_demo():
    """
    Quick demonstration of the scraping workflow
    """
    print("🚀 Quick Demo: Scraping first page only...")
    
    # Scrape just the first page
    books = scrape_single_page(1)
    
    if books:
        # Save to a demo file
        demo_filename = "demo_books.csv"
        success = save_books_to_csv(books, demo_filename)
        
        if success:
            print(f"\n📊 Demo Results:")
            get_csv_summary(demo_filename)
            
            # Show first few books
            print(f"\n📚 Sample Books:")
            for i, book in enumerate(books[:3], 1):
                print(f"{i}. {book['Title']} - {book['Price']}")


def complete_scrape_demo():
    """
    Demonstration of complete scraping (all pages)
    """
    print("🚀 Complete Scrape Demo: Scraping ALL pages...")
    
    # Scrape all available pages
    all_books = scrape_all_pages(start_page=1, delay=0.5)  # Faster delay for demo
    
    if all_books:
        # Save to a complete demo file
        complete_filename = "complete_books.csv"
        success = save_books_to_csv(all_books, complete_filename)
        
        if success:
            print(f"\n📊 Complete Scrape Results:")
            get_csv_summary(complete_filename)
            
            # Show statistics
            print(f"\n📈 Scraping Statistics:")
            print(f"Total books scraped: {len(all_books)}")
            estimated_pages = len(all_books) // 20  # Assuming 20 books per page
            print(f"Estimated pages scraped: {estimated_pages}")
    else:
        print("No books found in complete scrape")


if __name__ == "__main__":
    # Uncomment one of the lines below for different demo modes:
    
    # quick_demo()                    # Demo: scrape first page only
    # complete_scrape_demo()          # Demo: scrape ALL pages automatically
    
    # Run the interactive main workflow (asks user for choice)
    main()