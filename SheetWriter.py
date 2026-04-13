import gspread
from google.oauth2.service_account import Credentials

def create_sheets_table(spreadsheet, sheet, start_row, start_col, num_rows, num_cols, table_name):
    spreadsheet.batch_update({
        "requests": [{
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
                    "columnProperties": []   # empty = default column types
                }
            }
        }]
    })


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
sheet = spreadsheet.worksheet("Sheet1")
sheet.clear()
# Write the data first
headers = ["Picture", "Location", "Name", "Description", "Mayo", "Chicken", "Price", "Donation"]
rows = [
    ["Deerfield Pub\n40 Clubhouse Lane, Hammonds Plains b4b1t4", "Firecracker", "Double smash beef patties with Hellfire glaze...", "Yes", "No", "$24", "$1"],
    ["Le Rouge Bold Grill & Cocktails\n15 Lakelands Boulevard, Halifax B3S 1G4", "The Butchers Board Burger", "Melty brie, sliced salami, red pepper jelly...", "Yes", "No", "$20", "$2"],
    ["True North Diner\n1658 Bedford Highway, Bedford B4A 2X9", "DADDY O COLA SMASH", "Two old school onion smash patties...", "Yes", "No", "$13", "$1"],
]

sheet.update([headers] + rows, "A1")

# Now create the official Sheets Table on top of it
create_sheets_table(
    spreadsheet=spreadsheet,
    sheet=sheet,
    start_row=0,    # row 1 (0-indexed)
    start_col=0,    # column A
    num_rows=4,     # 1 header + 3 data rows
    num_cols=7,     # 7 columns
    table_name="BedfordTable"
)