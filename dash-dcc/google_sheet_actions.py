import gspread
import pandas as pd

class GoogleSheetService:
    def __init__(self, file_name, document, sheet_name):
        self.gc = gspread.service_account(filename=file_name)
        self.sh = self.gc.open(document)
        self.sheet = self.sh.worksheet(sheet_name)
        
    def read_all_data(self):
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)