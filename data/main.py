import pandas as pd


def apply_rule(tekiyo, rule_df):
    matched = rule_df[rule_df["keyword"].apply(lambda x: str(x) in tekiyo)]

    if not matched.empty:
        return matched.iloc[0]
    else:
        return None


def process_row(row, rule_df):
    print("処理中:", row["摘要"])
    tekiyo = str(row["摘要"])
    rule = apply_rule(tekiyo, rule_df)

    if rule is None:
        return None

    date = row["日付"]
    out_amount = row["出金"]
    in_amount = row["入金"]

    if pd.notna(out_amount):
        amount = int(out_amount)
        transaction_type = "出金"
    elif pd.notna(in_amount):
        amount = int(in_amount)
        transaction_type = "入金"
    else:
        amount = 0
        transaction_type = "不明"

    month = pd.to_datetime(date).month
    journal_summary = str(rule["template"]).replace("{month}", str(month)).strip()

    return {
        "日付": date,
        "取引区分": transaction_type,
        "借方科目": rule["debit_account"],
        "貸方科目": rule["credit_account"],
        "金額": amount,
        "税区分": rule["tax_code"],
        "仕訳摘要": journal_summary,
        "元摘要": tekiyo
    }


rule_df = pd.read_csv("data/input/rules.csv")
bank_df = pd.read_csv("data/input/bank.csv")

print("=== 仕訳生成開始 ===")

journal_list = bank_df.apply(lambda row: process_row(row, rule_df), axis=1)

journal_list = journal_list.dropna().tolist()

journal_df = pd.DataFrame(journal_list)
journal_df.to_csv("data/output/journal_test.csv", index=False, encoding="utf-8-sig")

print("\n=== 完了 ===")
print(journal_df)
print("\ndata/output/journal_test.csv を出力しました")