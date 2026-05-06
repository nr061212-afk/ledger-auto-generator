import pandas as pd

# 未判定ファイルを読む
unmatched_df = pd.read_csv("data/output/unmatched_journal_inout_output.csv")

# 摘要だけ取り出して重複削除
candidate_df = unmatched_df[["摘要"]].drop_duplicates()

# rules候補の形にする
candidate_df["keyword"] = candidate_df["摘要"]
candidate_df["template"] = "要確認"
candidate_df["month_rule"] = "none"
candidate_df["debit_account"] = "未判定"
candidate_df["credit_account"] = "普通預金"
candidate_df["tax_code"] = "未判定"

# 必要な列順に整える
candidate_df = candidate_df[[
    "keyword",
    "template",
    "month_rule",
    "debit_account",
    "credit_account",
    "tax_code"
]]

# 保存
candidate_df.to_csv("data/output/rule_suggestions.csv", index=False, encoding="utf-8-sig")

print("=== ルール候補 ===")
print(candidate_df)

print("\n保存完了:")
print("- data/output/rule_suggestions.csv")