import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to scrape a single page of book data
def scrape_page(page_number):
    url = f"https://books.toscrape.com/catalogue/page-{page_number}.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    
    if soup.title.text == "404 Not Found":
        return None
    
    all_books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
    books = []
    
    for i in all_books:
        item = {}
        item['Title'] = i.find("img").attrs["alt"]
        item['Link'] = "https://books.toscrape.com/catalogue/" + i.find("a").attrs["href"]
        item['Price'] = float(i.find("p", class_="price_color").text[2:])
        item['Stock'] = i.find("p", class_= "instock availability").text.strip()
        books.append(item)
    
    return books

# Scrape data from multiple pages
def scrape_books():
    proceed = True
    current_page = 1
    all_books = []

    while proceed:
        print(f"Currently scraping page {current_page}")
        books = scrape_page(current_page)
        
        if books is None:
            proceed = False
        else:
            all_books.extend(books)
            current_page += 1

    return pd.DataFrame(all_books)

# Analyze the data
def analyze_data(df):
    # Descriptive statistics
    print("\nDescriptive Statistics:")
    print(df.describe())
    
    # Count the number of books in stock and out of stock
    df['In Stock'] = df['Stock'].apply(lambda x: 'In stock' in x)
    stock_counts = df['In Stock'].value_counts()
    print("\nStock Counts:")
    print(stock_counts)
    
    # Plot the data
    stock_counts.plot(kind='bar', color=['green', 'red'])
    plt.title('Number of Books In Stock vs. Out of Stock')
    plt.xlabel('Stock Status')
    plt.ylabel('Number of Books')
    plt.xticks([0, 1], ['In Stock', 'Out of Stock'], rotation=0)
    plt.show()

    # Price distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Price'], kde=True, bins=30)
    plt.title('Price Distribution of Books')
    plt.xlabel('Price (£)')
    plt.ylabel('Frequency')
    plt.show()

    # Boxplot for price distribution
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='In Stock', y='Price', data=df)
    plt.title('Price Distribution by Stock Status')
    plt.xlabel('Stock Status')
    plt.ylabel('Price (£)')
    plt.show()

# Search for a book
def search_books(df):
    while True:
        query = input("\nEnter the title of the book you want to search for (or type 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break
        results = df[df['Title'].str.contains(query, case=False, na=False)]
        if not results.empty:
            for index, row in results.iterrows():
                print(f"\nTitle: {row['Title']}\nPrice: £{row['Price']}\nStock: {row['Stock']}\nLink: {row['Link']}")
        else:
            print("No books found with that title. Please try again.")

# Main menu
def main_menu():
    print("Welcome to the Library Database!")
    
    df = None
    while True:
        print("\nPlease choose an option:")
        print("1. Scrape book data from the website")
        print("2. Analyze the book data")
        print("3. Search for a book in the database")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("Scraping book data from the website. Please wait...")
            df = scrape_books()
            df.dropna(inplace=True)
            df.to_csv("books.csv", index=False)
            print("Data scraping complete. The data has been saved to 'books.csv'.")
        
        elif choice == '2':
            if df is not None:
                analyze_data(df)
            else:
                print("Please scrape the book data first (Option 1).")
        
        elif choice == '3':
            if df is not None:
                search_books(df)
            else:
                print("Please scrape the book data first (Option 1).")
        
        elif choice == '4':
            print("Thank you for using the Library Database. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

# Main script
if __name__ == "__main__":
    main_menu()