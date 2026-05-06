import streamlit as st
import pandas as pd
from processor import process_row, normalize_input_columns
from rule_engine import prepare_rules
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def read_csv_auto(file):
    try:
        return pd.read_csv(file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="shift-jis")

st.title("仕訳自動生成ツール")
st.caption("銀行明細CSVをアップロードすると仕訳を自動生成します")

# ファイルアップロード（複数対応）
input_files = st.file_uploader("銀行明細CSV", type="csv", accept_multiple_files=True)

# ルールは内部固定読み込み
rule_path = os.path.join(BASE_DIR, "data", "input", "rules.csv")
sample_rule_path = os.path.join(BASE_DIR, "data", "sample", "sample_rules.csv")

rule_df = pd.concat(
    [
        pd.read_csv(rule_path, encoding="utf-8-sig"),
        pd.read_csv(sample_rule_path, encoding="utf-8-sig")
    ],
    ignore_index=True
)

rule_df = prepare_rules(rule_df)

if input_files:
    # 複数ファイルを結合
    df_list = []
    for f in input_files:
        df = read_csv_auto(f)
        df = normalize_input_columns(df)  # ← ここを concat前に移動
        df["source_file"] = f.name  # どのファイル由来か記録
        df_list.append(df)
    bank_df = pd.concat(df_list, ignore_index=True)
    

    vendor_path = os.path.join(BASE_DIR, "data", "input", "vendor_master.csv")
    if os.path.exists(vendor_path):
        vendor_master_df = pd.read_csv(vendor_path)
    else:
        vendor_master_df = pd.DataFrame(columns=["raw_text", "normalized_text"])

    st.subheader("読み込んだ明細データ")
    st.dataframe(bank_df)

    if st.button("仕訳を生成する"):
        journal_list = bank_df.apply(
            lambda row: process_row(row, rule_df, vendor_master_df), axis=1
        ).dropna().tolist()

        journal_df = pd.DataFrame(journal_list)
        unmatched_df = journal_df[journal_df["status"] == "未判定"]
        ok_df = journal_df[journal_df["status"] == "OK"]

        # 集計
        total = len(journal_df)
        ok_count = len(ok_df)
        unmatched_count = len(unmatched_df)

        col1, col2, col3 = st.columns(3)
        col1.metric("総件数", total)
        col2.metric("OK", ok_count)
        col3.metric("未判定", unmatched_count)

        # 不要列を削除
        ok_df = ok_df.drop(columns=["source_file"], errors="ignore")
        unmatched_df = unmatched_df.drop(columns=["source_file"], errors="ignore")

        # 列名を日本語に変換
        column_names = {
            "date": "日付",
            "debit_account": "借方科目",
            "credit_account": "貸方科目",
            "amount": "金額",
            "description": "摘要",
            "tax_category": "税区分",
            "status": "ステータス"
        }
        ok_df = ok_df.rename(columns=column_names)
        unmatched_df = unmatched_df.rename(columns=column_names)

        # 金額を絶対値に変換
        ok_df["金額"] = ok_df["金額"].abs()
        unmatched_df["金額"] = unmatched_df["金額"].abs()

        st.subheader("仕訳結果")
        st.dataframe(ok_df)

        st.subheader("未判定データ")
        if unmatched_count > 0:
            st.warning(f"{unmatched_count}件が未判定です")
            st.info("未判定はルールCSVにキーワードを追加することで改善できます")
            st.dataframe(unmatched_df)
        else:
            st.success("未判定なし")

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                label="仕訳CSVをダウンロード",
                data=ok_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="journal_result.csv",
                mime="text/csv"
            )
        with col_b:
            st.download_button(
                label="未判定CSVをダウンロード",
                data=unmatched_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="unmatched_result.csv",
                mime="text/csv"
            )