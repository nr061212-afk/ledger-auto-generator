import pandas as pd

# === 読み込み ===
df = pd.read_csv("../data/iruka_card.csv")

# === 科目マッピング ===
CATEGORY_MAP = {
    "プ": "事業主貸",
    "事貸": "事業主貸",
    "消": "消耗品費",
    "交": "接待交際費",
    "福": "福利厚生費",
    "通": "通信費",
    "光": "水道光熱費",
    "燃料": "燃料費",
}

FOOD_KEYWORDS = ["ﾓｽﾊﾞ-ｶﾞ-", "ﾏｸﾄﾞﾅﾙﾄﾞ", "ﾖｼﾉﾔ", "ｱﾙ", "モスバーガー", "マクドナルド", "吉野家"]

def make_tekiyo(category, shop, date):
    month = pd.to_datetime(date).month

    if category in ["プ", "事貸"]:
        return "楽天カード　事業主"
    elif category == "消":
        return f"楽天カード　{shop}　雑貨代"
    elif category == "交":
        if "ｵ-ｸﾜ" in shop or "無印良品" in shop:
            return f"楽天カード　{shop}　贈答品"
        elif any(k in shop for k in FOOD_KEYWORDS):
            return f"楽天カード　{shop}　飲食代"
        else:
            return f"楽天カード　{shop}　飲食代"
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

# === 処理 ===
results = []

for _, row in df.iterrows():
    date = row["利用日"]
    shop = str(row["利用店名・商品名"]).strip()
    amount = int(row["利用金額"])
    category = str(row["支払内容"]).strip()

    debit = CATEGORY_MAP.get(category, "")
    credit = "未払金"

    tekiyo = make_tekiyo(category, shop, date)

    results.append({
        "date": date,
        "debit_account": debit,
        "credit_account": credit,
        "amount": amount,
        "shop": shop,
        "tekiyo": tekiyo,
        "status": "OK"
    })

# === CSV出力 ===
out_df = pd.DataFrame(results)
out_df.to_csv("../data/output/card_import.csv", index=False, encoding="utf-8-sig")

print("完成: data/output/card_import.csv")