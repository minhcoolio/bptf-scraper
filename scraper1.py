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
        self.price = extract_price(listing)
        self.type = extract_type(listing)
        self.is_bot = True
    
    def extract_price(listing):
        data = listing.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        temp = data.get('data-listing_price')
        return convert_price(temp)
    
    def extract_type(listing):
        data = listing.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        temp = data.get('data-listing_intent')
        return temp
    
    def extract_desc(listing):
        pass



# this function takes in beautiful soup html and pulls bp.tf buy and sell listings from a webpage and returns them in a single list
def scrape(soup):
    listings = []
    for i in soup.find_all("li", {"class": "listing"}):
        listings.append(i)
    return listings

# this function takes in a list of listings and sorts them into buy and sell lists
def sort_listings(listings):
    buy = []
    sell = []
    for inst in listings:
        data = inst.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        if data.get('data-listing_intent') == "buy":
            buy.append(inst)
        else:
            sell.append(inst)
    return buy, sell

def find_key_avg():
    driver.get("https://backpack.tf/stats/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable")
    element = WebDriverWait(driver=driver, timeout=5)
    html_src = driver.page_source

    soup = BeautifulSoup(html_src, 'html.parser')
    out = soup.find_all("ul", {"class": "media-list"})
    listings = scrape(soup)
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
        data = inst.find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info. Wildcard makes it general
        temp = data.get('data-listing_price')
        price_list.append( convert_price(temp) )
    return price_list
    
# this function takes in a list of listings and finds the lowest price
# def find_low(listings):

# this function takes in a list of listings and finds the highest price
# def find_high(listings):    

# this funtion determines if the listing is a bot or a real person
# def bot_check():    

# this function compares buy list and a sell list and determines if there is arbitrage opportunity
def compare(listings):
    buy, sell = sort_listings(listings)
    buy_prices = extract_price(buy)
    sell_prices = extract_price(sell)
    
    min_price = min(sell_prices)
    max_price = max(buy_prices)
    
    if max_price < min_price:
        print('Arbitrage Found!')
    else:
        print('No arbitrage found :(')
    
    
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

def get_url(link):
    driver = init_driver()
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
'''
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)
'''
key_link = "https://backpack.tf/stats/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable"
driver.get(key_link)
element = WebDriverWait(driver=driver, timeout=5)
html_src = driver.page_source
soup = BeautifulSoup(html_src, 'html.parser') # consider adding try statement here since it fails sometimes
temp = soup.find(class_ = "value").get_text() 
price = temp.partition("-")
print('hi')
print(price)


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

'''
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
'''
data = listings[5].find(class_ = re.compile('item q-440*')) # Gets <div> with the listing info
temp1 = data.get('data-listing_intent')
temp2 = data.get('data-listing_price')



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