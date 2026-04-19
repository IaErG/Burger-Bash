from Scraper import gather_burger_data
from SheetWriter import write_to_sheet

def main():
    # Get the burgers from burger bash, if the link has updated change the input
    print("Starting burger information gathering")
    data = gather_burger_data("https://burgerbash.ca/burger-lineup/#")

    print("Starting spreadsheet creation")
    # Write the burger data to the setup google sheet
    write_to_sheet(data, 'Test Sheet')

if __name__ == "__main__":
    main()
