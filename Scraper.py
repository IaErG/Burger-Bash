from bs4 import BeautifulSoup
import requests
from time import sleep
import googlemaps
from dotenv import load_dotenv
import os

# Load in the google maps api key to use
load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_KEY"))

# Method to skip over urls that don't return a 200 status code or fail to load
def safe_fetch(url):
    try:
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return None
        if "504 Gateway Time-out" in r.text:
            return None
        return r
    except:
        return None
    

# Method to get the city name of the entry since sometimes the address section doesn't contain it
def get_city(address):
    try:
        res = gmaps.geocode(address)

        if not res:
            return None

        # Return the city the address is in
        for comp in res[0]['address_components']:
            if 'locality' in comp['types']:
                return comp['long_name']

        return None
    except Exception as e:
        print(f"Geocoding error for {address}: {e}")
        return None


# Scrape the inputted burger basg url for burger bash details
def gather_burger_data(url):
    # Website details for Burger Bash  
    response = safe_fetch(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Get all the listings on the website
    listings = soup.find_all("a", class_="listing-item-container")

    # Create an array for holding the burger info
    burgers = []
    # Names array for filtering duplicate burgers
    names = []
    # Skipped array for letting us know if any entries were unretrievable
    skipped = []

    # Go through all listings on the website
    for l in listings:
        # Create a dictionary to store the details we want to add to the spreadsheet
        entry = {
            "picture" : '',
            "addresss" : '',
            "city" : '',
            "name" : '',
            "price" : 0,
            "restaurant" : '',
            "donation" : 0,
            "details" : '',
        }

        # Get/filter details from the listings as well as the link for the listing itself
        detailsResponse = safe_fetch(l['href'])
        detailsResponse.encoding = "utf-8"
        # If the link is invalid skip it
        if detailsResponse is None:
            skipped.append(l['href'])
            continue

        # Load the page with the burger details
        burgerDetails = BeautifulSoup(detailsResponse.text, "html.parser")
        
        # Grab the description of the burger either from the header
        og_description = burgerDetails.find("meta", property="og:description")
        description = og_description["content"] if og_description else None
        # Or if the header cuts off the description, get it from the p tags
        if '[…]' in description:
            div_info = burgerDetails.find("div", class_="listing-section")
            paragraphs = div_info.find_all("p", recursive=False)
            description = '\n'.join(p.text.strip() for p in paragraphs)

        # Get the image for the given burger
        og_picture = burgerDetails.find("meta", property="og:image")
        picture = og_picture["content"] if og_picture else None
        
        # Name is in format 'name $price' so we can get both with that, sometimes has * character splitting it too
        nameDetails = l.find("h2", class_="burgername").text.strip().split("$")
        name = nameDetails[0].split("*")[0].strip()
        price = round(float(nameDetails[1]))
        
        # Name filter to see if the burger has been seen already
        if name in names:
            continue
        else:
            names.append(name)
        
        # Sometimes the details don't have a donation. This filters for that so program doesn't crash
        try:
            d = burgerDetails.find("span", class_='feednsamt').text.strip().split(' ')[0]
            if d:
                # Get just the number for the donation, don't need the $# format
                entry['donation'] = int(''.join(filter(str.isdigit, d)))
        except:
            entry['donation'] = 0

        # Fill out the rest of the information and add to the burgers list
        entry['picture']    = f'=IMAGE("{picture}")'
        entry['address']    = l['data-address']
        entry['city']       = get_city(l['data-address'])
        entry['name']       = name
        entry['price']      = price
        entry['restaurant'] = l.find("h3").text.strip()
        entry['details']    = description
        
        burgers.append(entry)
    
    # Output how many burgers we gathered as well as how many we had to skip
    print("Burgers:", len(burgers))
    print("Skipped:", len(skipped))
    # For the ones we skipped let the user know what they were
    for s in skipped:
        print(s['restaurant'], s['name'])

    # Return all the burgers that we got in a list
    return burgers


