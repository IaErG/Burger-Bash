from Scraper import gather_burger_data
from SheetWriter import write_to_sheet

def main():
    data = gather_burger_data("https://burgerbash.ca/burger-lineup/#")


    #write_to_sheet(data)

if __name__ == "__main__":
    main()
