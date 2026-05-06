import pandas as pd

# 仕訳出力ファイルを読む
df = pd.read_csv("data/output/journal_inout_output.csv")

# 借方科目ごとに借方金額を合計
debit_summary = df.groupby("借方科目", as_index=False)["借方金額"].sum()
debit_summary = debit_summary.rename(columns={"借方金額": "金額合計"})

# 貸方科目ごとに貸方金額を合計
credit_summary = df.groupby("貸方科目", as_index=False)["貸方金額"].sum()
credit_summary = credit_summary.rename(columns={
    "貸方科目": "勘定科目",
    "貸方金額": "金額合計"
})

# 借方側の列名も揃える
debit_summary = debit_summary.rename(columns={"借方科目": "勘定科目"})

# 借方・貸方の区分列を追加
debit_summary["区分"] = "借方"
credit_summary["区分"] = "貸方"

# 列順を揃える
debit_summary = debit_summary[["区分", "勘定科目", "金額合計"]]
credit_summary = credit_summary[["区分", "勘定科目", "金額合計"]]

# 縦に結合
trial_balance_df = pd.concat([debit_summary, credit_summary], ignore_index=True)

# 保存
trial_balance_df.to_csv("data/output/trial_balance_summary.csv", index=False, encoding="utf-8-sig")

print("=== 試算表集計 ===")
print(trial_balance_df)

print("\n保存完了:")
print("- data/output/trial_balance_summary.csv")