def normalize_summary(summary, vendor_master_df):
    summary = str(summary)

    for _, row in vendor_master_df.iterrows():
        raw_text = str(row["raw_text"])
        normalized_text = str(row["normalized_text"])

        if raw_text in summary:
            return normalized_text

    return summary