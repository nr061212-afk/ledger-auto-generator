import pandas as pd

# 仕訳出力ファイルを読む
df = pd.read_csv("data/output/journal_inout_output.csv")

# 日付を日付型に変換
df["日付"] = pd.to_datetime(df["日付"])

# 年月列を作る
df["年月"] = df["日付"].dt.strftime("%Y-%m")

# 借方ピボット
debit_pivot = df.pivot_table(
    index="年月",
    columns="借方科目",
    values="借方金額",
    aggfunc="sum",
    fill_value=0
)

# 貸方ピボット
credit_pivot = df.pivot_table(
    index="年月",
    columns="貸方科目",
    values="貸方金額",
    aggfunc="sum",
    fill_value=0
)

# 列名に prefix を付ける
debit_pivot = debit_pivot.add_prefix("借方_")
credit_pivot = credit_pivot.add_prefix("貸方_")

# 横結合
full_pivot = pd.concat([debit_pivot, credit_pivot], axis=1)

# 列名の軸名を消す
full_pivot.columns.name = None

# 通常列に戻す
full_pivot = full_pivot.reset_index()

# 保存
full_pivot.to_csv("data/output/monthly_trial_balance_full.csv", index=False, encoding="utf-8-sig")

print("=== 月別試算表（借方・貸方） ===")
print(full_pivot)

print("\n保存完了:")
print("- data/output/monthly_trial_balance_full.csv")