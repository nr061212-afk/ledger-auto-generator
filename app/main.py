import pandas as pd
import logging
import time
import os
from processor import process_row, normalize_input_columns
from rule_engine import apply_rule, prepare_rules

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# "sample"    = テスト用データ
# "input"     = 実務検証用データ（bank + card）
# "bank_only" = bank.csvだけ
# "card_only" = card.csvだけ
MODE = "input"




# === ログ設定 ===
log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "journal.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

logger.info("=== 仕訳生成開始 ===")
logger.info(f"実行モード: {MODE}")

start_time = time.time()


# 1. CSVパス設定
if MODE == "sample":
    rule_path = os.path.join(BASE_DIR, "data", "sample", "sample_rules.csv")
    input_paths = [
        os.path.join(BASE_DIR, "data", "sample", "sample_input.csv")
    ]

elif MODE == "input":
    rule_path = os.path.join(BASE_DIR, "data", "input", "rules.csv")
    input_paths = [
        os.path.join(BASE_DIR, "data", "input", "bank.csv"),
        os.path.join(BASE_DIR, "data", "input", "card.csv")
    ]

elif MODE == "bank_only":
    rule_path = os.path.join(BASE_DIR, "data", "input", "rules.csv")
    input_paths = [
        os.path.join(BASE_DIR, "data", "input", "bank.csv")
    ]

elif MODE == "card_only":
    rule_path = os.path.join(BASE_DIR, "data", "input", "rules.csv")
    input_paths = [
        os.path.join(BASE_DIR, "data", "input", "card.csv")
    ]

else:
    raise ValueError("MODE は 'sample', 'input', 'bank_only', 'card_only' のどれかにしてください")


# 2. CSV読み込み
rule_df = pd.read_csv(rule_path)
rule_df = prepare_rules(rule_df) 

input_df_list = []

for path in input_paths:
    temp_df = pd.read_csv(path)
    temp_df["source_file"] = os.path.basename(path)
    input_df_list.append(temp_df)

bank_df = pd.concat(input_df_list, ignore_index=True)

vendor_path = os.path.join(BASE_DIR, "data", "input", "vendor_master.csv")

if os.path.exists(vendor_path):
    vendor_master_df = pd.read_csv(vendor_path)
else:
    vendor_master_df = pd.DataFrame(columns=["raw_text", "normalized_text"])

# 3. 入力カラムを処理用に変換
bank_df = normalize_input_columns(bank_df)

logger.info(f"入力データ読み込み完了: {len(bank_df)}行")


# 4. 1行ずつ処理
def process_with_log(row):
    try:
        result = process_row(row, rule_df, vendor_master_df)

        if result is None:
            logger.warning(f"処理結果なし: {row.get('description', '不明')}")
            return None

        status = result.get("status", "不明")

        if status == "OK":
            logger.info(
                f"OK: {result.get('description')} → {result.get('debit_account')}"
            )
        else:
            logger.warning(
                f"未判定: {result.get('description')} | "
                f"理由: {result.get('reason')} | "
                f"候補: {result.get('candidates')}"
            )

        return result

    except Exception as e:
        logger.error(
            f"処理失敗: {row.get('description', '不明')} | エラー: {e}"
        )
        return None


journal_list = bank_df.apply(process_with_log, axis=1)
journal_list = journal_list.dropna().tolist()


# 5. DataFrame化
journal_df = pd.DataFrame(journal_list)


# 6. 出力列を分ける
ok_columns = [
    "date",
    "source_file",
    "debit_account",
    "credit_account",
    "amount",
    "description",
    "tax_category",
    "status"
]

unmatched_columns = [
    "date",
    "source_file",
    "amount",
    "description",
    "status",
    "reason",
    "candidates"
]

unmatched_df = journal_df[journal_df["status"] == "未判定"]


# 7. 集計
total_count = len(journal_df)
ok_count = len(journal_df[journal_df["status"] == "OK"])
unmatched_count = len(unmatched_df)


# 8. 集計ログ
elapsed = time.time() - start_time

logger.info(
    f"処理完了 | 総件数:{total_count} "
    f"OK:{ok_count} "
    f"未判定:{unmatched_count} "
    f"処理時間:{elapsed:.2f}秒"
)


# 9. CSV出力
output_dir = os.path.join(BASE_DIR, "data", "output", MODE)
os.makedirs(output_dir, exist_ok=True)

journal_output_path = os.path.join(output_dir, f"journal_test_{MODE}.csv")
unmatched_output_path = os.path.join(output_dir, f"unmatched_{MODE}.csv")

journal_df[journal_df["status"] == "OK"][ok_columns].to_csv(
    journal_output_path,
    index=False,
    encoding="utf-8-sig"
)

unmatched_df[unmatched_columns].to_csv(
    unmatched_output_path,
    index=False,
    encoding="utf-8-sig"
)

logger.info("CSV出力完了")