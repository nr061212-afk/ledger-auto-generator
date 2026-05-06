import pandas as pd

# 仕訳出力ファイルを読む
df = pd.read_csv("data/output/journal_inout_output.csv")

# 日付を日付型に変換
df["日付"] = pd.to_datetime(df["日付"])

# 年月列を作る
df["年月"] = df["日付"].dt.strftime("%Y-%m")

# 借方科目ごとに年月別集計
monthly_debit = df.groupby(["年月", "借方科目"], as_index=False)["借方金額"].sum()
monthly_debit = monthly_debit.rename(columns={
    "借方科目": "勘定科目",
    "借方金額": "金額合計"
})

# 保存
monthly_debit.to_csv("data/output/monthly_debit_summary.csv", index=False, encoding="utf-8-sig")

print("=== 月別 借方科目集計 ===")
print(monthly_debit)

print("\n保存完了:")
print("- data/output/monthly_debit_summary.csv")