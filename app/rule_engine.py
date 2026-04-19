def apply_rule(tekiyo, rule_df):
    matched = rule_df[rule_df["keyword"].apply(lambda x: str(x) in tekiyo)]

   
    if not matched.empty:
        matched = matched.sort_values("priority")
        return matched.iloc[0].to_dict() 
    else:
        return None