import pandas as pd
import logging
import time
import os
from datetime import datetime

# ===設定===
INPUT_FILE = "../data/iruka_card.csv"
OUTPUT_JOURNAL = "../data/card_journal.csv"
OUTPUT_UNMATCHED = "../data/card_unmatched.csv"
LOG_FILE = "../logs/card_journal.log"

# ===科目マッピング===
CATEGORY_MAP = {
    "プ": "事業主貸",
    "事貸": "事業主貸",  # ← 追加
    "消": "消耗品費",
    "交": "接待交際費",
    "福": "福利厚生費",
    "通": "通信費",
    "光": "水道光熱費",
    "燃料": "燃料費",
}

# ===飲食店キーワード（交の摘要判定用）===
FOOD_KEYWORDS = ["ﾓｽﾊﾞ-ｶﾞ-", "ﾏｸﾄﾞﾅﾙﾄﾞ", "ﾖｼﾉﾔ", "ｱﾙ", "コメダ", "ローソン", "マクドナルド", "モスバーガー", "吉野家"]

# ===摘要生成===
def make_tekiyo(category, shop, date):
    month = pd.to_datetime(date).month
    if category == "プ":
        return "楽天カード　事業主"
    elif category == "消":
        return f"楽天カード　{shop}　雑貨代"
    elif category == "交":
        is_food = any(kw in shop for kw in FOOD_KEYWORDS)
        label = "飲食代" if is_food else "贈答品"
        return f"楽天カード　{shop}　{label}"
    elif category == "福":
        return f"楽天カード　{shop}　飲料代"
    elif category == "通":
        return f"楽天カード　{shop}　利用料"
    elif category == "光":
        return f"楽天カード　{shop}　電気代　{month}月分"
    elif category == "燃料":
        return f"楽天カード　{shop}　ガソリン代"
    else:
        return f"楽天カード　{shop}"

# ===1行処理===
def process_row(row):
    date = row["利用日"]
    shop = str(row["利用店名・商品名"]).strip()
    amount = row["利用金額"]
    category = str(row["支払内容"]).strip()

    debit = CATEGORY_MAP.get(category)

    if debit is None:
        return {
            "date": date,
            "debit_account": "",
            "credit_account": "",
            "amount": amount,
            "shop": shop,
            "tekiyo": "",
            "status": "未判定",
            "reason": f"支払内容未対応: {category}"
        }

    tekiyo = make_tekiyo(category, shop, date)

    return {
        "date": date,
        "debit_account": debit,
        "credit_account": "未払金",
        "amount": amount,
        "shop": shop,
        "tekiyo": tekiyo,
        "status": "OK"
    }

# ===メイン===
os.makedirs("../logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("=== カード明細仕訳生成開始 ===")
start_time = time.time()

df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
logger.info(f"入力データ読み込み完了: {len(df)}行")

results = []
for _, row in df.iterrows():
    try:
        result = process_row(row)
        if result["status"] == "OK":
            logger.info(f"OK: {result['shop']} → {result['debit_account']} | {result['tekiyo']}")
        else:
            logger.warning(f"未判定: {result['shop']} | 理由: {result['reason']}")
        results.append(result)
    except Exception as e:
        logger.error(f"処理失敗: {row.get('利用店名・商品名', '不明')} | エラー: {e}")

journal_df = pd.DataFrame(results)
ok_df = journal_df[journal_df["status"] == "OK"]
unmatched_df = journal_df[journal_df["status"] == "未判定"]

total = len(journal_df)
ok_count = len(ok_df)
unmatched_count = len(unmatched_df)

elapsed = time.time() - start_time
logger.info(f"処理完了 | 総件数:{total} OK:{ok_count} 未判定:{unmatched_count} 処理時間:{elapsed:.2f}秒")

ok_columns = ["date", "debit_account", "credit_account", "amount", "shop", "tekiyo", "status"]
unmatched_columns = ["date", "amount", "shop", "status", "reason"]

ok_df[ok_columns].to_csv(OUTPUT_JOURNAL, index=False, encoding="utf-8-sig")
unmatched_df[unmatched_columns].to_csv(OUTPUT_UNMATCHED, index=False, encoding="utf-8-sig")
logger.info("CSV出力完了")