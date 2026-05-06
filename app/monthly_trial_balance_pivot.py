import pandas as pd

# 仕訳出力ファイルを読む
df = pd.read_csv("data/output/journal_inout_output.csv")

# 日付を日付型に変換
df["日付"] = pd.to_datetime(df["日付"])

# 年月列を作る
df["年月"] = df["日付"].dt.strftime("%Y-%m")

# 月別 × 借方科目 のピボット集計
pivot_df = df.pivot_table(
    index="年月",
    columns="借方科目",
    values="借方金額",
    aggfunc="sum",
    fill_value=0
)

# 列名を通常列に戻す
pivot_df = pivot_df.reset_index()


pivot_df.columns.name = None

# 保存
pivot_df.to_csv("data/output/monthly_trial_balance_pivot.csv", index=False, encoding="utf-8-sig")

print("=== 月別試算表（ピボット） ===")
print(pivot_df)

print("\n保存完了:")
print("- data/output/monthly_trial_balance_pivot.csv")