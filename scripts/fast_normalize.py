import pandas as pd
print("Loading drug.parquet...")
df = pd.read_parquet("data/processed/faers_clean/drug.parquet")
print(f"Loaded {len(df):,} rows")
df["drugname_normalized"] = df["drugname"].str.upper().str.strip()
df["rxnorm_cui"] = None
df.to_parquet("data/processed/faers_clean/drug_normalized.parquet", index=False)
print(f"Unique drugs: {df['drugname_normalized'].nunique():,}")
print("FAST_NORM_DONE")
