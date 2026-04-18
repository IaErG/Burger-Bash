from Scraper import gather_burger_data
from SheetWriter import write_to_sheet

def main():
    # Get the burgers from burger bash, if the link has updated change the input
    data = gather_burger_data("https://burgerbash.ca/burger-lineup/#")

    #print(data[:10])

    # Write the burger data to the setup google sheet
    write_to_sheet(data)

if __name__ == "__main__":
    main()
