import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

# スプレッドシートをURLで開く
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bBNNUWdgjooUDapQUZDA1ZF4auhCA2-e19nXb81pgd0/edit?gid=0#gid=0")

# CSVを読む
trial_df = pd.read_csv("data/output/monthly_trial_balance_full.csv")
unmatched_df = pd.read_csv("data/output/unmatched_journal_inout_output.csv")
rules_df = pd.read_csv("data/output/rule_suggestions.csv")

def get_or_create_worksheet(spreadsheet, sheet_name, rows=1000, cols=50):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=rows, cols=cols)
    return worksheet

# 1. 試算表タブ
trial_ws = get_or_create_worksheet(spreadsheet, "試算表")
trial_ws.clear()
set_with_dataframe(trial_ws, trial_df)

# 2. 未判定タブ
unmatched_ws = get_or_create_worksheet(spreadsheet, "未判定")
unmatched_ws.clear()
set_with_dataframe(unmatched_ws, unmatched_df)

# 3. ルール候補タブ
rules_ws = get_or_create_worksheet(spreadsheet, "ルール候補")
rules_ws.clear()
set_with_dataframe(rules_ws, rules_df)

print("Googleスプレッドシートに3タブ書き込み完了")