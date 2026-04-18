from bs4 import BeautifulSoup
import requests
from time import sleep

# Method to skip over urls that don't return a 200 status code
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

def gather_burger_data(url):
    # Website details for Burger Bash  
    response = safe_fetch(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get all listings on the website
    listings = soup.find_all("a", class_="listing-item-container")

    # Create an array for holding burger info dictionaries as well as a names array for filtering out duplicates
    burgers = []
    names = []
    skipped = []

    # Go through all listings on the website
    for l in listings:
        # Create a dictionary to store the details we want to add to the spreadsheet
        entry = {
            "picture" : '',
            "addresss" : '',
            "name" : '',
            "price" : 0,
            "restaurant" : '',
            "donation" : 0,
            "details" : '',
        }

        # Get/filter details from the listings as well as the link for the listing itself
        detailsResponse = safe_fetch(l['href'])
        # If the link is invalid skip it
        if detailsResponse is None:
            #print("Skipping link ::", l['href'])
            skipped.append(l['href'])
            continue

        # Get the information necessary on the details page
        burgerDetails = BeautifulSoup(detailsResponse.text, "html.parser")
        div_info = burgerDetails.find("div", class_="listing-section")
        img = burgerDetails.find("img", class_="attachment-post-thumbnail size-post-thumbnail wp-post-image")
        picture = img.get('src') if img else None
        paragraphs = div_info.find_all("p", recursive=False)

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
        entry['picture']    = picture
        entry['address']   = l['data-address']
        entry['name']       = name
        entry['price']      = price
        entry['restaurant'] = l.find("h3").text.strip()
        entry['details']    = '\n'.join(p.text.strip() for p in paragraphs)
        
        burgers.append(entry)
    
    # Output how many burgers we gathered as well as how many we had to skip
    print("Burgers:", len(burgers))
    print("Skipped:", len(skipped))
    # For the ones we skipped let the user know what they were
    for s in skipped:
        print(s['restaurant'], s['name'])

    # Return all the burgers that we got in a list
    return burgers


