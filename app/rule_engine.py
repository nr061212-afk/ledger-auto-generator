import re
import unicodedata

def normalize_text(text):
    text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def prepare_rules(rule_df):
    rule_df = rule_df.copy()
    rule_df["keyword_norm"] = rule_df["keyword"].apply(normalize_text)
    if "priority" not in rule_df.columns:
        rule_df["priority"] = 100

    return rule_df


def apply_rule(tekiyo, rule_df):
    tekiyo_norm = normalize_text(tekiyo)


    matched = rule_df[
        rule_df["keyword_norm"].apply(lambda x: str(x) in tekiyo_norm)
    ]

    if "keyword_norm" not in rule_df.columns:
        rule_df = prepare_rules(rule_df)

    matched = rule_df[
        rule_df["keyword_norm"].apply(lambda x: str(x) in tekiyo_norm)
    ].copy()

    if matched.empty:
        return {
            "status": "unmatched",
            "rule": None,
            "reason": "ルール未一致",
            "candidates": []
        }

    matched["keyword_length"] = matched["keyword_norm"].str.len()

    matched = matched.sort_values(
        by=["priority", "keyword_length"],
        ascending=[False, False]
    )

    if len(matched) > 1:
        top_priority = matched.iloc[0]["priority"]
        second_priority = matched.iloc[1]["priority"]

        if top_priority - second_priority < 5:
            return {
                "status": "multiple",
                "rule": None,
                "reason": "複数ルール該当",
                "candidates": matched["keyword"].tolist()
            }

    return {
        "status": "matched",
        "rule": matched.iloc[0].to_dict(),
        "reason": None,
        "candidates": matched["keyword"].tolist()
    }