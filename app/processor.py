from rule_engine import apply_rule

def process_row(row, rule_df):
    tekiyo = str(row["description"])
    amount = row["amount"]
    date = row["date"]

    matched_rule = apply_rule(tekiyo, rule_df)

    if matched_rule is None:
        return {
            "date": date,
            "debit_account": "",
            "credit_account": "",
            "amount": amount,
            "description": tekiyo,
            "tax_category": "",
            "status": "未判定"
        }

    return {
        "date": date,
        "debit_account": matched_rule["debit_account"],
        "credit_account": matched_rule["credit_account"],
        "amount": amount,
        "description": tekiyo,
        "tax_category": matched_rule["tax_category"],
        "status": "OK"
    }