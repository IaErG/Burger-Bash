from Scraper import gather_burger_data

def main():
    data = gather_burger_data("https://burgerbash.ca/burger-lineup/#")

    print(data[12])

if __name__ == "__main__":
    main()
