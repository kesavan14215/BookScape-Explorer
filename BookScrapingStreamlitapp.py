import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

import requests
import json

# Database connection
def get_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='k007', database='bookscape', auth_plugin='mysql_native_password'
    )
# Fetch data from database
def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df



# Add proxy settings if you're behind a corporate network
proxies = {
    'http': None,
    'https': None
}



def fetch_books(api_key, query, total_results=200):
    """Fetch book data from Google Books API using pagination."""
    books = []
    max_results_per_request = 40  # Google Books API limit per request
    
    for start in range(0, total_results, max_results_per_request):
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&startIndex={start}&maxResults={max_results_per_request}&key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                books.extend(data["items"])
        else:
            st.error(f"Failed to fetch books from API. Status Code: {response.status_code}")
            break  # Stop fetching if an error occurs
    
    return {"items": books}  # Return combined results



def insert_books(data, search_key):
    """Insert book data into the database."""
    connection = get_connection()
    
    cursor = connection.cursor()
    
    
    cursor.execute("DROP TABLE IF EXISTS books")
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




# Streamlit App
def main():
    st.title("📚 BookScape Explorer")
    st.sidebar.header("Search Books")
    
    query = st.sidebar.text_input("Enter a search query:", "Data Science")
    if st.sidebar.button("Fetch Books"):
        API_KEY = "AIzaSyCDitNpTzgdvJeEmcnfRLhIpDCmDNyEZnc"
        books_data = fetch_books(API_KEY, query, total_results=1000)  # Fetch 200 books
        if books_data:
            insert_books(books_data, query)
            #st.success("Books fetched and inserted successfully!")
            st.success("Books Details Updated")
    
    st.sidebar.header("Filters")

    queries = {
        "Availability of eBooks vs Physical Books": """
            SELECT CASE WHEN isEbook = TRUE THEN 'eBook' ELSE 'Physical Book' END AS book_format, COUNT(*) AS total_books
            FROM books GROUP BY book_format;
        """,
        "Publisher with Most Books": """
            SELECT publisher, COUNT(*) as book_count FROM books WHERE publisher != 'Unknown'
            GROUP BY publisher ORDER BY book_count DESC LIMIT 1;
        """,
        "Publisher with Highest Average Rating": """
            SELECT publisher, ROUND(AVG(averageRating), 2) as avg_rating, COUNT(*) as total_books FROM books
            WHERE publisher != 'Unknown' AND averageRating > 0 GROUP BY publisher HAVING COUNT(*) > 5
            ORDER BY avg_rating DESC LIMIT 1;
        """,
        "Top 5 Most Expensive Books": """
            SELECT book_title, amount_retailPrice FROM books WHERE amount_retailPrice IS NOT NULL
            ORDER BY amount_retailPrice DESC LIMIT 5;
        """,
        "Year with Highest Average Book Price": """
            SELECT year, AVG(amount_retailPrice) AS avg_price FROM books WHERE amount_retailPrice IS NOT NULL
            GROUP BY year ORDER BY avg_price DESC LIMIT 1;
        """,
        "Books with Discounts": """
            SELECT book_title, (amount_listPrice - amount_retailPrice) AS discount_amount FROM books
            WHERE amount_listPrice > amount_retailPrice ORDER BY discount_amount DESC LIMIT 10;
        """,
        "Average Page Count by Format": """
            SELECT CASE WHEN isEbook = TRUE THEN 'eBook' ELSE 'Physical Book' END as format, ROUND(AVG(pageCount), 0) as avg_pages
            FROM books WHERE pageCount > 0 GROUP BY format;
        """,
        "Top 3 Authors with Most Books": """
            SELECT book_authors, COUNT(*) as book_count FROM books WHERE book_authors != 'Unknown'
            GROUP BY book_authors ORDER BY book_count DESC LIMIT 3;
        """,
        "Publishers with More than 10 Books": """
            SELECT publisher, COUNT(*) as book_count FROM books WHERE publisher != 'Unknown'
            GROUP BY publisher HAVING COUNT(*) > 10 ORDER BY book_count DESC;
        """,
        "Average Page Count by Category": """
            SELECT categories, ROUND(AVG(pageCount), 0) as avg_pages, COUNT(*) as book_count FROM books
            WHERE categories != 'Unknown' GROUP BY categories ORDER BY avg_pages DESC;
        """,
        "Books with More than 3 Authors": """
            SELECT book_title, book_authors FROM books WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) > 2;
        """,
        "Books with Above Average Ratings Count": """
            WITH avg_ratings AS (SELECT AVG(ratingsCount) as avg_count FROM books WHERE ratingsCount > 0)
            SELECT book_title, ratingsCount, averageRating FROM books
            CROSS JOIN avg_ratings WHERE ratingsCount > avg_ratings.avg_count ORDER BY ratingsCount DESC;
        """
    }

    query_choice = st.sidebar.selectbox("Select Analysis", list(queries.keys()))
    df = fetch_data(queries[query_choice])
    st.subheader(query_choice)
    st.table(df)
    
    # Visualization
    if query_choice in ["Availability of eBooks vs Physical Books", "Average Page Count by Format"]:
        fig = px.pie(df, names=df.columns[0], values=df.columns[1], title=query_choice)
        st.plotly_chart(fig)
    elif query_choice in ["Publisher with Most Books", "Publisher with Highest Average Rating", "Top 5 Most Expensive Books", "Year with Highest Average Book Price", "Books with Discounts", "Top 3 Authors with Most Books", "Publishers with More than 10 Books", "Average Page Count by Category"]:
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=query_choice)
        st.plotly_chart(fig)
    elif query_choice == "Books with Above Average Ratings Count":
        fig = px.scatter(df, x='ratingsCount', y='averageRating', title=query_choice)
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
