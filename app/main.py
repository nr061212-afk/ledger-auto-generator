import pandas as pd
import logging
import time
import os
from processor import process_row

# ===ログ設定===
os.makedirs("../logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("../logs/journal.log", encoding="utf-8"),
        logging.StreamHandler()  # コンソールにも出す
    ]
)
logger = logging.getLogger(__name__)

logger.info("=== 仕訳生成開始 ===")
start_time = time.time()

# 1. CSV読み込み
rule_df = pd.read_csv("../data/sample_rules.csv")
bank_df = pd.read_csv("../data/sample_input.csv")
logger.info(f"入力データ読み込み完了: {len(bank_df)}行")


# 2. 1行ずつ処理
def process_with_log(row):
    try:
        result = process_row(row, rule_df)
        if result is None:
            logger.warning(f"処理結果なし: {row.get('description', '不明')}")
            return None
        status = result.get("status", "不明")
        if status == "OK":
            logger.info(f"OK: {result.get('description')} → {result.get('debit_account')}")
        else:
            logger.warning(f"未判定: {result.get('description')} {result.get('amount')}円")
        return result
    except Exception as e:
        logger.error(f"処理失敗: {row.get('description', '不明')} | エラー: {e}")
        return None

journal_list = bank_df.apply(process_with_log, axis=1)
journal_list = journal_list.dropna().tolist()

# 3. DataFrame化
journal_df = pd.DataFrame(journal_list)

# 4. 未判定データ抽出
unmatched_df = journal_df[journal_df["status"] == "未判定"]

# 5. 集計
total_count = len(journal_df)
ok_count = len(journal_df[journal_df["status"] == "OK"])
unmatched_count = len(unmatched_df)

# 6. 集計ログ
elapsed = time.time() - start_time
logger.info(f"処理完了 | 総件数:{total_count} OK:{ok_count} 未判定:{unmatched_count} 処理時間:{elapsed:.2f}秒")

# 7. CSV出力
journal_df.to_csv("../data/journal_test.csv", index=False, encoding="utf-8-sig")
unmatched_df.to_csv("../data/unmatched.csv", index=False, encoding="utf-8-sig")
logger.info("CSV出力完了")