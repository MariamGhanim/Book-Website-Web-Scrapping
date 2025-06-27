import pandas as pd
import os
from typing import List, Dict, Optional
from datetime import datetime


def save_to_csv(data: List[Dict[str, str]], filename: str, append: bool = False) -> bool:
    """
    Save the extracted data to a CSV file using pandas.
    
    Args:
        data (List[Dict[str, str]]): List of dictionaries containing book data
        filename (str): Name of the CSV file to save to
        append (bool): Whether to append to existing file or overwrite (default: False)
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    if not data:
        print("No data to save.")
        return False
    
    try:
        # Create DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
        
        # Determine the save mode
        mode = 'a' if append else 'w'
        header = not (append and os.path.exists(filename))
        
        # Save to CSV
        df.to_csv(filename, mode=mode, header=header, index=False, encoding='utf-8')
        
        print(f"Successfully saved {len(data)} records to '{filename}'")
        return True
        
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return False


def save_books_to_csv(books: List[Dict[str, str]], filename: str = "books.csv") -> bool:
    """
    Save book data to CSV with specific formatting for book information.
    
    Args:
        books (List[Dict[str, str]]): List of book dictionaries with Title and Price
        filename (str): CSV filename (default: "books.csv")
    
    Returns:
        bool: True if save was successful, False otherwise
    """
    if not books:
        print("No book data to save.")
        return False
    
    try:
        # Create DataFrame
        df = pd.DataFrame(books)
        
        # Clean and format the data
        if 'Price' in df.columns:
            # Import clean_price function from parser
            from parser import clean_price
            df['Price_Numeric'] = df['Price'].apply(clean_price)
        
        # Add timestamp
        df['Scraped_At'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"Successfully saved {len(books)} books to '{filename}'")
        print(f"Columns: {list(df.columns)}")
        return True
        
    except Exception as e:
        print(f"Error saving books to CSV: {e}")
        return False


def append_books_to_csv(books: List[Dict[str, str]], filename: str = "books.csv") -> bool:
    """
    Append new book data to an existing CSV file.
    
    Args:
        books (List[Dict[str, str]]): List of book dictionaries to append
        filename (str): CSV filename (default: "books.csv")
    
    Returns:
        bool: True if append was successful, False otherwise
    """
    return save_to_csv(books, filename, append=True)


def load_books_from_csv(filename: str = "books.csv") -> Optional[pd.DataFrame]:
    """
    Load book data from a CSV file.
    
    Args:
        filename (str): CSV filename to load from (default: "books.csv")
    
    Returns:
        Optional[pd.DataFrame]: DataFrame with book data, or None if load fails
    """
    try:
        if not os.path.exists(filename):
            print(f"File '{filename}' does not exist.")
            return None
        
        df = pd.read_csv(filename, encoding='utf-8')
        print(f"Successfully loaded {len(df)} records from '{filename}'")
        return df
        
    except Exception as e:
        print(f"Error loading data from CSV: {e}")
        return None


def get_csv_summary(filename: str = "books.csv") -> None:
    """
    Display a summary of the CSV file contents.
    
    Args:
        filename (str): CSV filename to analyze (default: "books.csv")
    """
    df = load_books_from_csv(filename)
    if df is not None:
        print(f"\n=== CSV Summary for '{filename}' ===")
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nData types:")
        print(df.dtypes)
        
        if 'Price_Numeric' in df.columns:
            print(f"\nPrice statistics:")
            print(df['Price_Numeric'].describe())
        
        print(f"\nFirst 5 records:")
        print(df.head())


# Example usage and testing
if __name__ == "__main__":
    # Test the saver module with sample data from the parser
    from fetcher import fetch_books_page
    from parser import parse_books_from_html
    
    print("Testing saver module with live data...")
    
    # Fetch and parse data
    html_content = fetch_books_page()
    if html_content:
        books = parse_books_from_html(html_content)
        
        if books:
            # Test saving to CSV
            success = save_books_to_csv(books, "test_books.csv")
            
            if success:
                # Test loading and displaying summary
                get_csv_summary("test_books.csv")
                
                # Test appending more data (simulate scraping page 2)
                print(f"\n--- Testing append functionality ---")
                html_content_page2 = fetch_books_page(2)
                if html_content_page2:
                    books_page2 = parse_books_from_html(html_content_page2)
                    if books_page2:
                        append_success = append_books_to_csv(books_page2, "test_books.csv")
                        if append_success:
                            get_csv_summary("test_books.csv")
        else:
            print("No books found to save")
    else:
        print("Failed to fetch data for testing")