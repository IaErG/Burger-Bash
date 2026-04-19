from Scraper import gather_burger_data
from SheetWriter import write_to_sheet
import sys

# Current year's link: https://burgerbash.ca/burger-lineup/#
def main(): 
    bbLink = sys.argv[1]
    sheet_name = sys.argv[2]
    
    # Get the burgers from burger bash, if the link has updated change the input
    print("Starting burger information gathering")
    data = gather_burger_data(bbLink)

    # Write the burger data to the setup google sheet
    print("Starting spreadsheet creation")
    write_to_sheet(data, sheet_name)

if __name__ == "__main__":
    main()
