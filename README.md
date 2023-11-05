# bptf-scraper
Python program that is designed to scrape the bp.tf website and find opportunities of arbitrage. I implemented this functionality with a Selenium webscraper. It targets the buying and selling listings and compares the pricing data between them. From the same website, the program pulls a list of items from the game and searches through each one. The program outputs a results.txt file that stores all the links of items opportunities of arbitrage was found on.

I implemented this program using an OOP approach by parsing all necesssary info from the listings and categorizing the data into my own data type. This helped me keep organized and efficient code when working with many helper functions.

This code takes in a pre-created item list stored in items.txt in order to start sifting the listings. Be sure to run the `init_item_list()` function every time a new item is added to the game in order to update the items.txt file.

Funtionality to implement:
- convert alphanumeric mathmatical numbers to normal letters
- sort results by amount of price difference achievable

