import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def normalize_text(text):
    text = str(text)
    text = text.lower()
    text = text.replace("　", " ")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# 入力データを読む
bank_path = os.path.join(BASE_DIR, "data", "input", "bank.csv")
card_path = os.path.join(BASE_DIR, "data", "input", "card.csv")
rules_path = os.path.join(BASE_DIR, "data", "input", "rules.csv")
vendor_path = os.path.join(BASE_DIR, "data", "input", "vendor_master.csv")

bank_df = pd.read_csv(bank_path)
card_df = pd.read_csv(card_path)
rules = pd.read_csv(rules_path)
vendor_master = pd.read_csv(vendor_path)

rules["keyword_norm"] = rules["keyword"].apply(normalize_text)

# 通帳CSVとクレカCSVをまとめる
df = pd.concat([bank_df, card_df], ignore_index=True)

# 日付を日付型に変換
df["日付"] = pd.to_datetime(df["日付"], format="mixed", errors="coerce")
# 日付が変換できなかった行を未判定にする
df["日付エラー"] = df["日付"].isna()

# 出金・入金を数値化して空欄を0にする
df["出金"] = pd.to_numeric(df["出金"], errors="coerce").fillna(0)
df["入金"] = pd.to_numeric(df["入金"], errors="coerce").fillna(0)

# 整数にする
df["出金"] = df["出金"].astype(int)
df["入金"] = df["入金"].astype(int)

def get_prev_month(dt):
    if dt.month == 1:
        return 12
    return dt.month - 1

def get_month_by_rule(dt, month_rule):
    if month_rule == "prev":
        return get_prev_month(dt)
    elif month_rule == "current":
        return dt.month
    else:
        return None
    
def normalize_summary(summary):
    summary = str(summary)

    for _, row in vendor_master.iterrows():
        raw_text = str(row["raw_text"])
        normalized_text = str(row["normalized_text"])

        if raw_text in summary:
            return normalized_text

    return summary    

def apply_rule(row):
    raw_summary = row["摘要"]

    if pd.isna(raw_summary) or str(raw_summary).strip() == "":
         return pd.Series([
        "未判定","未判定","未判定","未判定",
        0,0,
        "摘要が空欄"
         ])

    raw_summary = str(raw_summary)
    summary = normalize_summary(raw_summary)
    summary_norm = normalize_text(summary)
    date = row["日付"]
    out_amount = row["出金"]
    in_amount = row["入金"]

    # 摘要が空
    if summary.strip() == "":
        return pd.Series([
            "未判定","未判定","未判定","未判定",
            0,0,
            "摘要が空欄"
        ])

    # 金額が0
    if out_amount == 0 and in_amount == 0:
        return pd.Series([
            "未判定","未判定","未判定","未判定",
            0,0,
            "金額が0"
        ])

    # 出金・入金両方ある（異常）
    if out_amount > 0 and in_amount > 0:
        amount = out_amount + in_amount
        return pd.Series([
            "未判定","未判定","未判定","未判定",
            amount,amount,
            "出金入金両方あり"
        ])

    for _, rule in rules.iterrows():
        keyword = str(rule["keyword_norm"])
        template = str(rule["template"])
        month_rule = str(rule["month_rule"])
        debit_account = str(rule["debit_account"])
        credit_account = str(rule["credit_account"])
        tax_code = str(rule["tax_code"])

        if keyword in summary_norm:
            month = get_month_by_rule(date, month_rule)

            if month is not None:
                application = template.replace("{month}", str(month))
            else:
                application = template

            if out_amount > 0:
                return pd.Series([
                    application,
                    debit_account,
                    credit_account,
                    tax_code,
                    int(out_amount),
                    int(out_amount),
                    ""
                ])

            elif in_amount > 0:
                return pd.Series([
                    application,
                    debit_account,
                    credit_account,
                    tax_code,
                    int(in_amount),
                    int(in_amount),
                    ""
                ])

    amount = out_amount if out_amount > 0 else in_amount

    return pd.Series([
        "未判定",
        "未判定",
        "未判定",
        "未判定",
        int(amount),
        int(amount),
        "ルール未登録"
    ])

df[["適用", "借方科目", "貸方科目", "税区分", "借方金額", "貸方金額", "未判定理由"]] = df.apply(apply_rule, axis=1)

# 列順を整える
df = df[["日付", "摘要", "出金", "入金", "適用", "借方科目", "借方金額", "貸方科目", "貸方金額", "税区分", "未判定理由"]]

df["摘要"] = df["摘要"].fillna("")


# 出力フォルダを作成
output_dir = os.path.join(BASE_DIR, "data", "output")
os.makedirs(output_dir, exist_ok=True)

# 出力ファイルのパス
journal_output_path = os.path.join(output_dir, "journal_inout_output.csv")
unmatched_output_path = os.path.join(output_dir, "unmatched_journal_inout_output.csv")

# 全件保存
df.to_csv(journal_output_path, index=False, encoding="utf-8-sig")

# 未判定だけ抽出
unmatched_df = df[
    (df["適用"] == "未判定") |
    (df["借方科目"] == "未判定") |
    (df["貸方科目"] == "未判定") |
    (df["税区分"] == "未判定")
]

# 未判定だけ保存
unmatched_df.to_csv(unmatched_output_path, index=False, encoding="utf-8-sig")

print("=== 全件データ ===")
print(df)

print("\n=== 未判定データ ===")
print(unmatched_df)

total_count = len(df)
matched_count = len(df) - len(unmatched_df)
unmatched_count = len(unmatched_df)

print("\n=== 集計 ===")
print(f"全件数: {total_count}件")
print(f"判定済み: {matched_count}件")
print(f"未判定: {unmatched_count}件")

print("\n保存完了:")
print("- data/output/journal_inout_output.csv")
print("- data/output/unmatched_journal_inout_output.csv")