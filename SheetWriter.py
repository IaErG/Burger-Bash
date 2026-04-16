import gspread
from google.oauth2.service_account import Credentials

def create_sheets_table(spreadsheet, sheet, sheet_name, start_row, start_col, num_rows, num_cols, table_name):
    spreadsheet.batch_update({
        "requests": [{
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet.id,
                    "title": sheet_name
                },
                "fields": "title"
            }
        },
            
        {
            "addTable": {
                "table": {
                    "name": table_name,
                    "range": {
                        "sheetId": sheet.id,
                        "startRowIndex": start_row,
                        "endRowIndex": start_row + num_rows,
                        "startColumnIndex": start_col,
                        "endColumnIndex": start_col + num_cols
                    },
                    "columnProperties": [
                        {
                            "columnIndex": 4,   # Mayo column
                            "columnName": "Mayo",
                            "columnType": "DROPDOWN",
                            "dataValidationRule": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [
                                        {"userEnteredValue": "Yes"},
                                        {"userEnteredValue": "No"}
                                    ]
                                }
                            }
                        },
                        {
                            "columnIndex": 5,   # Chicken column
                            "columnName": "Chicken",
                            "columnType": "DROPDOWN",
                            "dataValidationRule": {
                                "condition": {
                                    "type": "ONE_OF_LIST",
                                    "values": [
                                        {"userEnteredValue": "Yes"},
                                        {"userEnteredValue": "No"}
                                    ]
                                }
                            }
                        }
                    ]  
                }
            }
        }]
    })

def add_table_borders(spreadsheet, sheet, table_name):
    
    # Step 1 — Find the table's range
    spreadsheet_data = spreadsheet.fetch_sheet_metadata()
    sheets_data = spreadsheet_data.get("sheets", [])
    
    table_range = None
    for s in sheets_data:
        if s["properties"]["sheetId"] == sheet.id:
            for table in s.get("tables", []):
                if table.get("name") == table_name:
                    table_range = table["range"]
                    break

    if not table_range:
        print(f"Table '{table_name}' not found.")
        return

    border = {"style": "SOLID", "width": 1, "color": None}

    # Step 3 — Apply borders to the table range
    spreadsheet.batch_update({
        "requests": [{
            "updateBorders": {
                "range": {
                    "sheetId": sheet.id,
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
        }]
    })
    print(f"Borders applied to table '{table_name}'.")
    end_col_letter = chr(ord("A") + table_range["endColumnIndex"] - 1)  

    sheet.format(f"A1:{end_col_letter}1", {
        "textFormat": {
            "bold": True,
            "fontSize": 15,
            "foregroundColor": None
        },
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE"
    })

    sheet.format(f"A2:{end_col_letter}{table_range["endRowIndex"]}", {
        "verticalAlignment": "MIDDLE",
        "horizontalAlignment": "CENTER",
        "wrapStrategy": "WRAP"
    })



# # Define scopes
# scopes = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]

# # Authenticate
# creds = Credentials.from_service_account_file("token.json", scopes=scopes)
# client = gspread.authorize(creds)

# # Open your sheet (by name or URL)
# spreadsheet = client.open("Test Sheet")
# sheet = spreadsheet.worksheet("Elsewhere")
# sheet.clear()
# # Write the data first
# headers = ["Picture", "Location", "Name", "Description", "Mayo", "Chicken", "Price", "Donation $", "Donation %"]
# rows = [
#     ["", "Deerfield Pub\n\n40 Clubhouse Lane, Hammonds Plains b4b1t4", "Firecracker", "Double smash beef patties with Hellfire glaze...", "Yes", "No", "$24", "$1", "24%"],
#     ["", "Le Rouge Bold Grill & Cocktails\n\n15 Lakelands Boulevard, Halifax B3S 1G4", "The Butchers Board Burger", "Melty brie, sliced salami, red pepper jelly...", "No", "No", "$20", "$2", "1%"],
#     # ["True North Diner\n1658 Bedford Highway, Bedford B4A 2X9", "DADDY O COLA SMASH", "Two old school onion smash patties...", "Yes", "No", "$13", "$1"],
# ]

# sheet.update([headers] + rows, "A1")

# # Now create the official Sheets Table on top of it
# create_sheets_table(
#     spreadsheet=spreadsheet,
#     sheet=sheet,
#     sheet_name="Elsewhere",
#     start_row=0,    # row 1 (0-indexed)
#     start_col=0,    # column A
#     num_rows=3,     # 1 header + 3 data rows
#     num_cols=9,     # 7 columns
#     table_name="Elsewhere"
# )

# add_table_borders(spreadsheet, sheet, table_name="Elsewhere")


def write_to_sheet(data):
    # Define scopes
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authenticate
    creds = Credentials.from_service_account_file("token.json", scopes=scopes)
    client = gspread.authorize(creds)

    # Open your sheet (by name or URL)
    spreadsheet = client.open("Test Sheet")
    sheet = spreadsheet.get_worksheet(0)

    sheet.clear()
    # Write the data first
    headers = ["Picture", "Location", "Name", "Description", "Mayo", "Chicken", "Price", "Donation $", "Donation %"]
    mayo_keywords = ["mayo", "aoli", "mayonnaise"]
    locations = ["Halifax", "Dartmouth"]

    

