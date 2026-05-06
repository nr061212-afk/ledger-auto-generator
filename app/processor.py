from rule_engine import apply_rule
from vendor_master import normalize_summary

import pandas as pd


def normalize_input_columns(df):
    df = df.copy()

    if "日付" in df.columns:
        df = df.rename(columns={"日付": "date"})

    if "摘要" in df.columns:
        df = df.rename(columns={"摘要": "description"})

    if "出金" in df.columns and "入金" in df.columns:
        df["出金"] = pd.to_numeric(df["出金"], errors="coerce").fillna(0)
        df["入金"] = pd.to_numeric(df["入金"], errors="coerce").fillna(0)
        df["amount"] = df["入金"] - df["出金"]

    return df


def process_row(row, rule_df, vendor_master_df):
    raw_description = row.get("description", "")
    amount = row["amount"]
    date = row["date"]
    source_file = row.get("source_file", "")

    if pd.isna(raw_description) or str(raw_description).strip() == "":
        return {
            "date": date,
            "source_file": source_file,
            "debit_account": "",
            "credit_account": "",
            "amount": amount,
            "description": "",
            "tax_category": "",
            "status": "未判定",
            "reason": "摘要が空欄",
            "candidates": ""
        }

    display_description = str(raw_description)
    rule_description = normalize_summary(raw_description, vendor_master_df)

    if amount == 0:
        return {
            "date": date,
            "debit_account": "",
            "credit_account": "",
            "amount": amount,
            "description": display_description,
            "tax_category": "",
            "status": "未判定",
            "reason": "金額が0",
            "candidates": ""
        }

    result = apply_rule(rule_description, rule_df)

    if result["status"] == "matched":
        tax_category = result["rule"].get("tax_category", result["rule"].get("tax_code", ""))

        return {
            "date": date,
            "source_file": row.get("source_file", ""),
            "debit_account": result["rule"]["debit_account"],
            "credit_account": result["rule"]["credit_account"],
            "amount": amount,
            "description": display_description,
            "tax_category": tax_category,
            "status": "OK",
            "reason": "",
            "candidates": ""
        }
    else:
        return {
            "date": date,
            "source_file": row.get("source_file", ""),
            "debit_account": "",
            "credit_account": "",
            "amount": amount,
            "description": display_description,
            "tax_category": "",
            "status": "未判定",
            "reason": result["reason"],
            "candidates": ", ".join(result["candidates"])
        }