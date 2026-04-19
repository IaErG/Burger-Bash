import gspread
from google.oauth2.service_account import Credentials

# Creates a table on the given sheet based on the amount of data for the burger list
def create_table(spreadsheet, sheet, burger_list):
    # Set the range for what columns I want conditional formatting on for yes/no values
    range_def = {
        "sheetId": sheet.id,
        "startRowIndex": 1,
        "endRowIndex": len(burger_list),
        "startColumnIndex": 4,
        "endColumnIndex": 6
    }

    # Send A request to the sheet to create a table and add yes/no formatting, also to give dimensions for the picture column
    spreadsheet.batch_update(
        {
            "requests": [
                {
                    "addTable": { # Create the table with rows and columns based on the inputted list
                        "table": {
                            "name": sheet.title,
                            "range": {
                                "sheetId": sheet.id,
                                "startRowIndex": 0,
                                "endRowIndex": len(burger_list),
                                "startColumnIndex": 0,
                                "endColumnIndex": len(burger_list[0])
                            },
                            "columnProperties": []
                        }
                    }
                },
                {
                    "addConditionalFormatRule": { # Rule to show the cell as green if the value is 'Yes'
                        "rule": {
                            "ranges": [range_def],
                            "booleanRule": {
                                "condition": {
                                    "type": "TEXT_EQ",
                                    "values": [{"userEnteredValue": "Yes"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.71, "green": 0.84, "blue": 0.71},
                                    "textFormat": {
                                        "foregroundColor": {"red": 0.0, "green": 0.39, "blue": 0.0}
                                    }
                                }
                            }
                        },
                        "index": 0
                    }
                },
                {
                    "addConditionalFormatRule": { # Rule to show the cell as red if the value is 'No'
                        "rule": {
                            "ranges": [range_def],
                            "booleanRule": {
                                "condition": {
                                    "type": "TEXT_EQ",
                                    "values": [{"userEnteredValue": "No"}]
                                },
                                "format": {
                                    "backgroundColor": {"red": 0.92, "green": 0.71, "blue": 0.71},
                                    "textFormat": {
                                        "foregroundColor": {"red": 0.60, "green": 0.0, "blue": 0.0}
                                    }
                                }
                            }
                        },
                        "index": 1
                    }
                },
                {
                    "updateDimensionProperties": { # Size adjustment for the picture width
                        "range": {
                            "sheetId": sheet.id,
                            "dimension": "ROWS",
                            "startIndex": 1,  # 1 to skip header
                            "endIndex": len(burger_list)
                        },
                        "properties": {"pixelSize": 150},
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": { # Size adjustment for the picture height
                        "range": {
                            "sheetId": sheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 1,  # 1 to skip header
                            "endIndex": 2 # Just the first column
                        },
                        "properties": {"pixelSize": 500},
                        "fields": "pixelSize"
                    }
                }
            ]
        }
    )


# Method to apply specific formatting to the sheets present in the given spreadsheet
def format_sheet(spreadsheet):
    # Get the metadata about the spreadsheet
    spreadsheet_data = spreadsheet.fetch_sheet_metadata()
    sheets_data = spreadsheet_data.get("sheets", [])

    # Set the border style for the cells and initialize a list of requests to change the sheet
    border = {"style": "SOLID", "width": 1, "color": None}
    requests = []

    # Go through each of the sheets found in the spreadsheet
    for s in sheets_data:
        sheet = spreadsheet.get_worksheet_by_id(s['properties']['sheetId'])
        # Dynamically get the table data found on the given sheet
        table_data = s.get("tables", [])[0]
        table_range = table_data['range']
        end_col_letter = chr(ord("A") + table_range["endColumnIndex"] - 1)

        # Format the header row in the sheet
        sheet.format(
            f"A1:{end_col_letter}1", 
            {
                "textFormat": {
                    "bold": True,
                    "fontSize": 15,
                    "foregroundColor": None
                },
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE"
            }
        )

        # Format the rest of the rows in the table
        sheet.format(
            f"A2:{end_col_letter}{table_range["endRowIndex"]}", 
            {
                "verticalAlignment": "MIDDLE",
                "horizontalAlignment": "CENTER",
                "wrapStrategy": "WRAP"
            }
        )

        # Add boarder update request for the given sheet to the requests array
        requests.append(
            {
                "updateBorders": {
                    "range": {
                        "sheetId": s["properties"]["sheetId"],
                        "startRowIndex":    table_range["startRowIndex"],
                        "endRowIndex":      table_range["endRowIndex"],
                        "startColumnIndex": table_range["startColumnIndex"],
                        "endColumnIndex":   table_range["endColumnIndex"]
                    },
                    "top":             border,
                    "bottom":          border,
                    "left":            border,
                    "right":           border,
                    "innerHorizontal": border,
                }
            }
        )

    # Send off border update for each of the sheets at once
    spreadsheet.batch_update({"requests": requests})


# Resets a given spreadsheet before writing to it
def reset_spreadsheet(spreadsheet):
    # Get the data of the spreadsheet entered and initialize an array for requests to send
    sheets_data = spreadsheet.fetch_sheet_metadata().get("sheets", [])
    requests = []

    # Check for tables on the sheets to delete and add the delete requests to the array
    for sheet in sheets_data:
        for table in sheet.get("tables", []):
            requests.append({
                "deleteTable": {
                    "tableId": table["tableId"]
                }
            })

    # Gather the sheets present, the first one needs to remain however
    sheets_data = spreadsheet.fetch_sheet_metadata().get("sheets", [])
    first_sheet_id = sheets_data[0]["properties"]["sheetId"]

    # Create a delete request for each sheet other than the first one 
    for sheet in sheets_data[1:]:
        requests.append({
            "deleteSheet": {
                "sheetId": sheet["properties"]["sheetId"]
            }
        })

    # Rename that first sheet back to 'Sheet1' as it was originally
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": first_sheet_id,
                "title": "Sheet1"
            },
            "fields": "title"
        }
    })

    # Send off our requests for removing sheets and tables
    if requests:
        spreadsheet.batch_update({"requests": requests})

    # Clear the content of the first sheet
    first_sheet = spreadsheet.get_worksheet(0)
    first_sheet.clear()

    # Clear whatever formatting rules were there as well
    try:
        spreadsheet.batch_update({
            "requests": [{
                "deleteConditionalFormatRule": {
                    "sheetId": first_sheet_id,
                    "index": 0
                }
            }]
        })
    except Exception:
        print("No formatting to clear")

    print("Spreadsheet cleaned")



# Method to organize all the data gathered into 3 location based arrays
def get_locations(headers, data):
    # Initialize the arrays with the header row as the first entry
    halifax = [headers]
    dartmouth = [headers]
    elsewhere = [headers]

    # Since mayo can be any one of these 3 I just made a list to help with validating if the burger has mayo in it
    mayo_keywords = ["mayo", "aioli", "mayonnaise"]

    # Go through all the burgers we got from the Burger Bash website
    for burger in data:
        # Determine if mayo is in the burger
        mayo = 'No'
        for s in mayo_keywords:
            if s in burger['details'].lower():
                mayo = 'Yes'

        # Determine if the burger is a chicken burger
        chicken = 'No'
        if 'chicken' in burger['details'].lower():
            chicken = 'Yes'

        # Create the row to add to the google sheet
        row = [
            burger['picture'], 
            burger['restaurant'] + '\n\n' + burger['address'],
            burger['name'],
            burger['details'],
            mayo,
            chicken,
            '$' + str(burger['price']),
            '$' + str(burger['donation']),
            str(round((burger['donation'] / burger['price']) * 100, 1)) + '%'
        ]

        # Depending on the location of the given entry, add it to the appropriate list
        if burger['city'] == 'Halifax':
            halifax.append(row)
        elif burger['city'] == 'Dartmouth':
            dartmouth.append(row)
        else:
            elsewhere.append(row)

    return halifax, dartmouth, elsewhere


# Write the burger bash data gathered from the website to the google sheet
def write_to_sheet(data, sheet_name):
    # Define scopes for using the api
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authenticate with the google drive
    creds = Credentials.from_service_account_file("token.json", scopes=scopes)
    client = gspread.authorize(creds)

    # Open the spreadsheet you gave edit access to by name and create the 3 location sheets
    spreadsheet = client.open(sheet_name)

    # If there's any data there delete it first before proceeding
    reset_spreadsheet(spreadsheet)

    # Update/add the sheets we will need for this list
    spreadsheet.get_worksheet(0).update_title("Halifax")
    spreadsheet.add_worksheet(title="Dartmouth", rows=100, cols=10)
    spreadsheet.add_worksheet(title="Elsewhere", rows=100, cols=10)
    
    # Store the sheets in variables to be used later
    halifax_sheet = spreadsheet.get_worksheet(0)
    dartmouth_sheet = spreadsheet.get_worksheet(1)
    elsewhere_sheet = spreadsheet.get_worksheet(2)

    # Setup a header row for each sheet as well as get the 3 location lists from inputted data
    headers = ["Picture", "Location", "Name", "Description", "Mayo", "Chicken", "Price", "Donation $", "Donation %"]
    halifax, dartmouth, elsewhere = get_locations(headers, data)
    print("Burger data sorted")

    # Create the tables to hold the burger data in each of the sheets made
    create_table(spreadsheet, halifax_sheet, halifax)
    create_table(spreadsheet, dartmouth_sheet, dartmouth)
    create_table(spreadsheet, elsewhere_sheet, elsewhere)
    print("Tables created")

    # Write the data to the sheets making sure to allow for the picture to show in column A1
    halifax_sheet.update(halifax, "A1", value_input_option="USER_ENTERED")
    dartmouth_sheet.update(dartmouth, "A1", value_input_option="USER_ENTERED")
    elsewhere_sheet.update(elsewhere, "A1", value_input_option="USER_ENTERED")
    print("Information added")

    # Appy formatting to all the sheets in the spreadsheet
    format_sheet(spreadsheet)
    print("Spreadsheet formatted")
