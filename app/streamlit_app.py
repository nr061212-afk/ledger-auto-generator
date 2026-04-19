import streamlit as st
import pandas as pd
from processor import process_row

st.title("仕訳自動生成ツール")
st.caption("銀行明細CSVをアップロードすると仕訳を自動生成します")

# ファイルアップロード
input_file = st.file_uploader("銀行明細CSV", type="csv")
rule_file = st.file_uploader("ルールCSV", type="csv")

if input_file and rule_file:
    bank_df = pd.read_csv(input_file)
    rule_df = pd.read_csv(rule_file)

    st.subheader("読み込んだ明細データ")
    st.dataframe(bank_df)

    if st.button("仕訳を生成する"):
        journal_list = bank_df.apply(
            lambda row: process_row(row, rule_df), axis=1
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

        # 金額を絶対値に変換（renameの後なので「金額」で指定）
        ok_df["金額"] = ok_df["金額"].abs()
        unmatched_df["金額"] = unmatched_df["金額"].abs()

        st.subheader("仕訳結果")
        st.dataframe(ok_df)

        st.subheader("未判定データ")
        if unmatched_count > 0:
            st.warning(f"{unmatched_count}件が未判定です")
            st.dataframe(unmatched_df)
        else:
            st.success("未判定なし")

        # ダウンロードを2種類に分ける
        col_a, col_b = st.columns(2)

        with col_a:
            st.download_button(
                label="仕訳CSVをダウンロード",
                data=ok_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="journal.csv",
                mime="text/csv"
            )

        with col_b:
            st.download_button(
                label="未判定CSVをダウンロード",
                data=unmatched_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="unmatched.csv",
                mime="text/csv"
            )