# Burger Bash
Python web scraper to get information about Burger Bash entries each year and write them to an easier to digest Google Sheet

Your will need 2 things to integrate your script with your Google Drive, both of which can be created via https://console.cloud.google.com/
1. Geocoding API key for Google Maps
2. Google Cloud Service Account for reading and writing to your Google Drive

To get started clone the repo locally and enter in your own API keys in the following spots:
- Geocoding API: Put in a **.env** file and set GOOGLE_MAPS_KEY=_YourAPIKey_
- Google Cloud Service Token: Save it as **token.json** and add to the directory

Also run this line to get all the dependencies needed to run this program:

_pip install beautifulsoup4 requests googlemaps python-dotenv gspread google-auth_

Make sure to open up your Google Drive and create a new Google Sheet.
Once you have, click on 'Share' and give editor access to the client_email in your token.json
This way the script that uses your token will be able to write to the sheet you made.

Once this setup has been finished run:

_python ./Main.py {Burger Bash Link} {Google Sheet Name}_
