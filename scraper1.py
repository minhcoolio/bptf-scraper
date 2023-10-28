from bs4 import BeautifulSoup
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time
import re

'''
listing class includes
data members:
- price
- type: buy or sell
- bot or human flag
member functions:
- constructor
    * initiate price, type, and bot/human flag

    
possibly make a key listing class that inherits some functionality
'''
class Listing:
    def __init__(self, listing):
        self.price = self.extract_price(listing)
        self.type = self.extract_type(listing)
        self.desc, self.is_spell = self.extract_desc(listing)
        
    def get_price(self):
        return self.price
    
    def extract_price(self, listing):
        data = listing.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        if data is None:
            data = listing.find(class_ = re.compile('item nocraft q-440*')) # used to catch noncraftable items
        temp = data.get('data-listing_price')
        return convert_price(temp)
    
    def extract_type(self, listing):
        data = listing.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        if data is None:
            data = listing.find(class_ = re.compile('item nocraft q-440*'))
        temp = data.get('data-listing_intent')
        return temp
    
    def extract_desc(self, listing):
        data = listing.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        if data is None:
            data = listing.find(class_ = re.compile('item nocraft q-440*'))
        desc = data.get('data-listing_comment')
        if desc is None:        # to catch listings without a desc
            return 'Empty', False 
        result = re.search(r"exo|exorcism|pumpkin|spells|spell|halloween|footstep|voices from below", desc, re.IGNORECASE) # need to ignore spell listings due to inflated price
        if result is None: # no keywords found, not a spell listing
            return desc, False
        else:                # keywords found, is a spell listing
            return desc, True
       
# this function pulls all bptf links of each item in tf2 and stores it in a text file
# run this function everyonce and a while to update the list when new items are added to the game
def init_item_list(soup):
    file = open("items.txt", "w")
    for i in soup.find_all("a", {"class": "qlink"}):
        file.write('https://backpack.tf' + i.get('href') + '\n') 
    file.close()

# this function takes in beautiful soup html and pulls bp.tf buy and sell listings from a webpage and returns them in a single list
def scrape(soup):
    listings = []
    for i in soup.find_all("li", {"class": "listing"}):
        listings.append( Listing(i) )
    return listings

# this function takes in a list of listings and sorts them into buy and sell lists
def sort_listings(listings):
    buy = []
    sell = []
    for inst in listings:
        if inst.is_spell == False: # used to ignore spell listings
            if inst.type == "buy":
                buy.append(inst)
            else:
                sell.append(inst)
    return buy, sell

def find_key_avg(driver):
    key_link = "https://backpack.tf/stats/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable"
    soup = get_url(driver, key_link)
    
    listings = soup.find_all("ul", {"class": "media-list"})
    buy, sell = sort_listings(listings)

    key_prices = extract_price(sell)
    key_avg = sum(key_prices)/len(key_prices)
    return key_avg
    
# this function takes in a str which contains the listings price and converts it to a float and price into ref (not keys)
def convert_price(ip, ref2key = 56.88):
    price_str = ip.split()
    key = ['key', 'keys', 'key,', 'keys,']
    ref = ['ref', 'refs', 'ref,' 'refs,']
    
    ### Price is either soley key or ref ###
    if len(price_str) == 2:
        if (price_str[1] in key):
            return float(price_str[0]) * ref2key
            #return {"key": float(price_str[0])}
        if (price_str[1] in ref):
            return float(price_str[0])
    ### Price is a combo of keys and ref ###
    if len(price_str) == 4:
        return float(price_str[0]) * ref2key + float(price_str[2]) 
        #return {"key": float(price_str[0]), "ref": float(price_str[2])}

# this function takes in a list of listings and extracts the price from them and returns a list of the prices
def extract_price(listings):
    price_list = []
    for inst in listings:
        price_list.append( inst.get_price() )
        #data = inst.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        #temp = data.get('data-listing_price')
        #price_list.append( convert_price(temp) )
    return price_list

# this function takes in a list of listings and finds the lowest price
# def find_low(listings):

# this function takes in a list of listings and finds the highest price
# def find_high(listings):    

# this funtion determines if the listing is a bot or a real person
# def bot_check():    

# this function compares buy list and a sell list and determines if there is arbitrage opportunity
def compare(listings, link):
    file = open("results.txt", "w")
    buy, sell = sort_listings(listings)
    buy_prices = list(filter(None, extract_price(buy))) # if price listed as dollar, it will appear as none, need to filter none out
    sell_prices = list(filter(None, extract_price(sell)))
    
    if (len(buy_prices) != 0) and (len(sell_prices) != 0): # if any of the lists are empty
        min_price = min(sell_prices)
        max_price = max(buy_prices)
        
        if max_price < min_price:
            file.write(link + '\n') # arbitrage found, write item link to results page
            print('Arbitrage found!')
    file.close()
    
# Initiates the driver    
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_argument('--log-level=3') # hides extra info printed to console. Only shows fatal messages
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    return driver

def kill_driver(driver):
    driver.quit()

# Takes in driver and link and returns html page as soup
def get_url(driver, link):
    #driver = init_driver()
    driver.get(link)
    element = WebDriverWait(driver=driver, timeout=5)
    html_src = driver.page_source
    soup = BeautifulSoup(html_src, 'html.parser') # consider adding try statement here since it fails sometimes
    return soup

'''
# configure webdriver
options = Options()
#options.headless = True  # hide GUI. If this line is enabled, cloudflare gives the wrong result
options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
options.add_argument("start-maximized")  # ensure window is full-screen
# configure chrome browser to not load images and javascript
'''
''' #driver

# configute webdriver
# need to use stealth version to operate in headless mode. Cloudflare stops normal version if operating in headless mode
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("--headless")
options.add_argument('--log-level=3') # hides extra info printed to console. Only shows fatal messages
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# driver '''
'''
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)
'''

''' X
key_link = "https://backpack.tf/stats/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable"
driver.get(key_link)
element = WebDriverWait(driver=driver, timeout=5)
html_src = driver.page_source
soup = BeautifulSoup(html_src, 'html.parser') # consider adding try statement here since it fails sometimes
temp = soup.find(class_ = "value").get_text() 
price = temp.partition("-")
print('hi')
print(price)
X '''

# Run these lines when you need to update the item list
#soup_items = get_url(driver, "https://backpack.tf/spreadsheet")
#init_item_list(soup_items)

file = open('items.txt', 'r')
items = file.readlines()
driver = init_driver()

itere = 1
for inst in items:
    soup1 = get_url(driver, inst)
    listings = scrape(soup1)
    compare(listings, inst)
    print("{}: {}\n".format(itere, inst))
    itere = itere + 1

kill_driver(driver)

#print(find_key_avg(driver))
'''#XXXX
temp = scrape(soup1)
print(len(temp))
test_listing = Listing(temp[8])
print(test_listing.price)
test_temp = test_listing.desc
result = re.search(r"exo\b|exorcism|pumpkin|spell|halloween|footprint", test_temp, re.IGNORECASE)
print(test_temp)
print(result)

testing = test_temp.split()
print(testing[1])
s = testing[1] #problem is some ads are in mathmetical alphanumeric which we need to convert to normal characters
print([ord(c) for c in s])
#XXXX'''

''' XXX
#driver = webdriver.Chrome(options=options)
link = "https://backpack.tf/stats/Unique/Team%20Spirit/Tradable/Craftable"
link2 = "https://backpack.tf/stats/Strange/Huntsman/Tradable/Craftable"
driver.get(key_link)
# wait for page to load
element = WebDriverWait(driver=driver, timeout=5)
html_src = driver.page_source

soup = BeautifulSoup(html_src, 'html.parser')
out = soup.find_all("ul", {"class": "media-list"})

listings = scrape(soup)
buy, sell = sort_listings(listings)

key_prices = extract_price(sell)
key_avg = sum(key_prices)/len(key_prices)

#print(find_key_avg())
XXX '''
''' XX
# Sort listings into buy or sell
buy = []
sell = []
for inst in listings:
    data = inst.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info WORKS
    #data = inst.find(class_="item q-440-11 q-440-border-11") # Gets <div> with the listing info WORKS
    #data = inst.find("div", {"class": "item q-440-6 q-440-border-6"}) # Gets <div> with the listing info DOESNT WORK
    if data.get('data-listing_intent') == "buy":
        buy.append(inst)
    else:
        sell.append(inst)

data = listings[5].find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info
temp1 = data.get('data-listing_intent')
temp2 = data.get('data-listing_price')

XX '''

#output = extract_price(temp2)

'''
# Find the search input element and enter a search query
search_box = driver.find_element_by_name("q")
search_query = "web scraping with Python"
search_box.send_keys(search_query)
search_box.send_keys(Keys.RETURN)

# Wait for a few seconds to let the search results load
time.sleep(5)

# Extract search results (in this case, the titles and URLs)
search_results = driver.find_elements_by_css_selector("h3")
for result in search_results:
    title = result.text
    url = result.find_element_by_xpath("..").get_attribute("href")
    print(f"Title: {title}")
    print(f"URL: {url}\n")
'''

# Close the web browser
#driver.quit()