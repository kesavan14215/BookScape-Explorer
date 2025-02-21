
"""

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='k007',
        database='bookscape',
        auth_plugin='mysql_native_password'
    )
    
    if connection.is_connected():
        print("Successfully connected to MySQL database")
        
        # Example query
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"You're connected to database: {db_name[0]}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
        
"""



import mysql.connector
import requests
import json

# Add proxy settings if you're behind a corporate network
proxies = {
    'http': None,
    'https': None
}

def fetch_books(api_key, query, max_results=40):
    """Fetch book data from Google Books API with error handling and proxies."""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key={api_key}"
        response = requests.get(url, proxies=proxies, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        print("Please check your internet connection and DNS settings")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    return None

def create_database():
    """Create SQL database and book table."""
    connection = mysql.connector.connect( 
                             host='localhost',
                             user='root',
                             password='k007',
                             #database='bookscape',
                             auth_plugin='mysql_native_password',
                             use_pure=True  # Force Python implementation instead of C extension
                             )
    
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS bookscape")
    cursor.execute("USE bookscape")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id VARCHAR(255) PRIMARY KEY,
            search_key VARCHAR(255),
            book_title TEXT,
            book_authors TEXT,
            book_description TEXT,
            industryIdentifiers TEXT,
            categories TEXT,
            language VARCHAR(10),
            averageRating DECIMAL(3,2),
            ratingsCount INT,
            pageCount INT,
            publisher TEXT,
            year TEXT,
            amount_listPrice DECIMAL(10,2),
            currencyCode_listPrice VARCHAR(10),
            amount_retailPrice DECIMAL(10,2),
            currencyCode_retailPrice VARCHAR(10),
            isEbook BOOLEAN
        )''')
    connection.commit()
    cursor.close()
    connection.close()
    print('Database & Table Created successfully ')
def insert_books(data, search_key):
    """Insert book data into the database."""
    connection = mysql.connector.connect( 
                             host='localhost',
                             user='root',
                             password='k007',
                             database='bookscape',
                             auth_plugin='mysql_native_password',
                             use_pure=True  # Force Python implementation instead of C extension
                             )
    
    cursor = connection.cursor()
    
    for item in data.get('items', []):
        book = item['volumeInfo']
        sale_info = item.get('saleInfo', {})
        book_id = item.get('id', 'Unknown')
        title = book.get('title', 'Unknown')
        authors = ', '.join(book.get('authors', []))
        description = book.get('description', 'No Description')
        identifiers = json.dumps(book.get('industryIdentifiers', []))
        categories = ', '.join(book.get('categories', [])) if 'categories' in book else 'Unknown'
        language = book.get('language', 'Unknown')
        avg_rating = book.get('averageRating', 0)
        ratings_count = book.get('ratingsCount', 0)
        page_count = book.get('pageCount', 0)
        publisher = book.get('publisher', 'Unknown')
        year = book.get('publishedDate', 'Unknown')
        list_price = sale_info.get('listPrice', {}).get('amount', 0.00)
        currency_list = sale_info.get('listPrice', {}).get('currencyCode', 'Unknown')
        retail_price = sale_info.get('retailPrice', {}).get('amount', 0.00)
        currency_retail = sale_info.get('retailPrice', {}).get('currencyCode', 'Unknown')
        is_ebook = book.get('readingModes', {}).get('text', False)
        
        cursor.execute('''
            INSERT INTO books (book_id, search_key, book_title, book_authors, book_description,
            industryIdentifiers, categories, language, averageRating, ratingsCount, pageCount, publisher, year,
            amount_listPrice, currencyCode_listPrice, amount_retailPrice, currencyCode_retailPrice, isEbook)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE book_title=VALUES(book_title)
        ''', (book_id, search_key, title, authors, description, identifiers, categories, language, avg_rating,
              ratings_count, page_count, publisher, year, list_price, currency_list, retail_price, currency_retail, is_ebook))
    
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    API_KEY = "AIzaSyCDitNpTzgdvJeEmcnfRLhIpDCmDNyEZnc"
    QUERY = "Data Science"
    
    create_database()
    books_data = fetch_books(API_KEY, QUERY)
    if books_data:
        insert_books(books_data, QUERY)
        print("Books inserted successfully!")



