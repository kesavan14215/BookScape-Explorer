select * from bookscape.books  ;

drop database bookscape;


-- 1. Check Availability of eBooks vs Physical bookscape.books
SELECT 
    CASE 
        WHEN isEbook = TRUE THEN 'eBook' 
        ELSE 'Physical Book' 
    END AS book_format, 
    COUNT(*) AS total_books
FROM bookscape.books
GROUP BY book_format;


-- 2. Publisher with Most bookscape.books
SELECT publisher, COUNT(*) as book_count
FROM bookscape.books
WHERE publisher != 'Unknown'
GROUP BY publisher
ORDER BY book_count DESC
LIMIT 1;

-- 3. Publisher with Highest Average Rating
SELECT 
    publisher,
    ROUND(AVG(averageRating), 2) as avg_rating,
    COUNT(*) as total_books
FROM bookscape.books
WHERE publisher != 'Unknown' AND averageRating > 0
GROUP BY publisher
HAVING COUNT(*) > 5
ORDER BY avg_rating DESC
LIMIT 1;

-- 4. Top 5 Most Expensive bookscape.books
SELECT book_title, book_authors, amount_retailPrice, currencyCode_retailPrice, year, publisher
FROM bookscape.books
WHERE amount_retailPrice IS NOT NULL
ORDER BY amount_retailPrice DESC
LIMIT 5;


-- 5. bookscape.books Published After 2010 with 500+ Pages
SELECT book_title, year, pageCount
FROM bookscape.books
WHERE SUBSTRING(year, 1, 4) > '2010' 
AND pageCount >= 500
ORDER BY pageCount DESC;

-- 6. bookscape.books with Discounts
SELECT book_title, book_authors, amount_listPrice, amount_retailPrice, 
       (amount_listPrice - amount_retailPrice) AS discount_amount, 
       ROUND(((amount_listPrice - amount_retailPrice) / amount_listPrice) * 100, 2) AS discount_percentage,
       currencyCode_listPrice, year, publisher
FROM bookscape.books
WHERE amount_listPrice IS NOT NULL 
AND amount_retailPrice IS NOT NULL 
AND amount_listPrice > amount_retailPrice
ORDER BY discount_percentage DESC;


-- 7. Average Page Count by Format
SELECT 
    CASE 
        WHEN industryIdentifiers LIKE '%EBOOK%' THEN 'eBook'
        ELSE 'Physical Book'
    END as format,
    ROUND(AVG(pageCount), 0) as avg_pages
FROM bookscape.books
WHERE pageCount > 0
GROUP BY 
    CASE 
        WHEN industryIdentifiers LIKE '%EBOOK%' THEN 'eBook'
        ELSE 'Physical Book'
    END;

-- 8. Top 3 Authors with Most bookscape.books
SELECT book_authors, COUNT(*) as book_count
FROM bookscape.books
WHERE book_authors != 'Unknown'
GROUP BY book_authors
ORDER BY book_count DESC
LIMIT 3;

-- 9. Publishers with More than 10 bookscape.books
SELECT publisher, COUNT(*) as book_count
FROM bookscape.books
WHERE publisher != 'Unknown'
GROUP BY publisher
HAVING COUNT(*) > 10
ORDER BY book_count DESC;

-- 10. Average Page Count by Category
SELECT 
    categories,
    ROUND(AVG(pageCount), 0) as avg_pages,
    COUNT(*) as book_count
FROM bookscape.books
WHERE categories != 'Unknown'
GROUP BY categories
ORDER BY avg_pages DESC;


-- 11. bookscape.books with More than 3 Authors
SELECT book_title, book_authors
FROM bookscape.books
WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) > 2;

-- 12. bookscape.books with Above Average Ratings Count
WITH avg_ratings AS (
    SELECT AVG(ratingsCount) as avg_count
    FROM bookscape.books
    WHERE ratingsCount > 0
)
SELECT 
    book_title,
    ratingsCount,
    averageRating
FROM bookscape.books
CROSS JOIN avg_ratings
WHERE ratingsCount > avg_ratings.avg_count
ORDER BY ratingsCount DESC;

-- 13. Same Author, Same Year Publications
SELECT DISTINCT a.book_authors, a.year, COUNT(*) as publications
FROM bookscape.books a
JOIN bookscape.books b ON a.book_authors = b.book_authors 
    AND a.year = b.year 
    AND a.book_id != b.book_id
GROUP BY a.book_authors, a.year
ORDER BY publications DESC;

-- 14. bookscape.books with Specific Keyword
SELECT book_title, book_authors, averageRating
FROM bookscape.books
WHERE LOWER(book_title) LIKE '%python%'
ORDER BY averageRating DESC;

-- 15. Year with Highest Average Book Price
SELECT year(year) AS year, AVG(amount_retailPrice) AS avg_price
FROM bookscape.books
WHERE amount_retailPrice IS NOT NULL
GROUP BY year(year)
ORDER BY avg_price DESC
LIMIT 1;


-- 16. Authors with 3 Consecutive Years
WITH consecutive_years AS (
    SELECT DISTINCT book_authors, SUBSTRING(year, 1, 4) as pub_year
    FROM bookscape.books
    WHERE book_authors != 'Unknown'
)
SELECT DISTINCT c1.book_authors
FROM consecutive_years c1
JOIN consecutive_years c2 ON c1.book_authors = c2.book_authors 
    AND c2.pub_year = c1.pub_year + 1
JOIN consecutive_years c3 ON c1.book_authors = c3.book_authors 
    AND c3.pub_year = c1.pub_year + 2;

-- 17. Authors with Multiple Publishers in Same Year
SELECT 
    book_authors,
    year,
    COUNT(DISTINCT publisher) as publisher_count,
    COUNT(*) as book_count
FROM bookscape.books
WHERE book_authors != 'Unknown'
GROUP BY book_authors, year
HAVING COUNT(DISTINCT publisher) > 1
ORDER BY book_count DESC;

-- 18. Average Retail Price by Format
SELECT 
    CASE 
        WHEN isEbook = TRUE THEN 'eBook'
        ELSE 'Physical Book' 
    END AS book_format, 
    AVG(amount_retailPrice) AS avg_retail_price
FROM bookscape.books
WHERE amount_retailPrice IS NOT NULL
GROUP BY book_format;

-- 19. Rating Outliers
WITH stats AS (
    SELECT 
        AVG(averageRating) as mean_rating,
        STDDEV(averageRating) as std_dev
    FROM bookscape.books
    WHERE averageRating > 0
)
SELECT 
    book_title,
    averageRating,
    ratingsCount
FROM bookscape.books
CROSS JOIN stats
WHERE ABS(averageRating - mean_rating) > 2 * std_dev
ORDER BY averageRating DESC;

-- 20. Best Rated High-Volume Publishers
SELECT 
    publisher,
    ROUND(AVG(averageRating), 2) as average_rating,
    COUNT(*) as total_books
FROM bookscape.books
WHERE publisher != 'Unknown'
AND averageRating > 0
GROUP BY publisher
HAVING COUNT(*) > 10
ORDER BY average_rating DESC
LIMIT 1;

