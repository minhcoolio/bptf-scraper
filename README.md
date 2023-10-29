# bptf-scraper
Python program that is designed to scrape the bp.tf website and find opportunities of arbitrage. I implemented this functionality with a Selenium webscraper. It targets the buying and selling listings of bots and compares the pricing data between them. From the same website, the program pulls a list of items from the game and searches through each one. I had to make sure to ignore listings that targeted spelled versions of items due to the inflated prices. 

I implemented this program using an OOP approach by parsing all necesssary info from the listings and categorizing the data into my own data type. This helped me keep organized and efficient code when working with many helper functions. 

Funtionality to implement:
- convert alphanumeric mathmatical numbers to normal letters in order
- sort results by amount of price difference achievable

