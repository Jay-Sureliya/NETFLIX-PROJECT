import pandas as pd
import numpy as np

# ---------------------------
# 1. Load Raw Data
# ---------------------------
try:
    data = pd.read_csv("netflix_titles.csv")
    print(f"✅ Data loaded successfully. Shape: {data.shape}")
except FileNotFoundError:
    print("❌ Error: netflix_titles.csv file not found!")
    exit()

# ---------------------------
# 2. Handle Missing Values
# ---------------------------
data["country"] = data["country"].fillna("Unknown")
data["director"] = data["director"].fillna("Unknown")
data["cast"] = data["cast"].fillna("Unknown")
data["rating"] = data["rating"].fillna("Unknown")
data["listed_in"] = data["listed_in"].fillna("")
data["duration"] = data["duration"].fillna("")

# ---------------------------
# 3. Convert Dates Safely
# ---------------------------
# First, let's see what date formats we have
print("🔍 Sample date_added values:")
print(data["date_added"].dropna().head(10).tolist())

# Try common Netflix date formats
def parse_netflix_dates(date_series):
    """Parse Netflix dates with multiple format attempts"""
    # Common Netflix date formats (updated based on your data format)
    formats_to_try = [
        "%d-%b-%y",       # "25-Sep-21" (your format!)
        "%d-%b-%Y",       # "25-Sep-2021" 
        "%B %d, %Y",      # "January 1, 2021"
        "%b %d, %Y",      # "Jan 1, 2021" 
        "%Y-%m-%d",       # "2021-01-01"
        "%m/%d/%Y",       # "1/1/2021"
        "%d/%m/%Y"        # "1/1/2021" (day first)
    ]
    
    parsed_dates = pd.Series(index=date_series.index, dtype='datetime64[ns]')
    
    for fmt in formats_to_try:
        # Find entries that haven't been parsed yet
        mask = parsed_dates.isna() & date_series.notna()
        if not mask.any():
            break
            
        try:
            # Try to parse remaining dates with current format
            temp_parsed = pd.to_datetime(date_series[mask], format=fmt, errors='coerce')
            parsed_dates[mask] = temp_parsed
            successfully_parsed = temp_parsed.notna().sum()
            if successfully_parsed > 0:
                print(f"✅ Parsed {successfully_parsed} dates with format: {fmt}")
        except:
            continue
    
    # For any remaining unparsed dates, use dateUtil as fallback (with explicit warning suppression)
    remaining_mask = parsed_dates.isna() & date_series.notna()
    if remaining_mask.any():
        print(f"🔄 Using dateUtil fallback for {remaining_mask.sum()} remaining dates...")
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            parsed_dates[remaining_mask] = pd.to_datetime(date_series[remaining_mask], errors='coerce')
    
    return parsed_dates

# Apply the safe date parsing
data["date_added"] = parse_netflix_dates(data["date_added"])

# Show parsing results
total_dates = data["date_added"].notna().sum()
print(f"✅ Successfully parsed {total_dates} out of {len(data)} total rows")

# ---------------------------
# 4. Clean Duration Column
# ---------------------------
# Create a more robust duration extraction
data["duration_clean"] = data["duration"].astype(str).str.strip()

# Extract duration number and type
duration_extracted = data["duration_clean"].str.extract(r'(\d+)\s*(\w+)', expand=True)
data["duration_int"] = pd.to_numeric(duration_extracted[0], errors="coerce")
data["duration_type"] = duration_extracted[1].fillna("Unknown").astype(str).str.strip()

# ---------------------------
# 5. Strip Extra Spaces
# ---------------------------
text_cols = ["title", "director", "cast", "country", "listed_in", "description", "rating", "duration_type"]
for col in text_cols:
    if col in data.columns:
        data[col] = data[col].astype(str).str.strip()

# ---------------------------
# 6. Remove Duplicates
# ---------------------------
initial_shape = data.shape[0]
data = data.drop_duplicates().reset_index(drop=True)
print(f"✅ Removed {initial_shape - data.shape[0]} duplicate rows")

# ---------------------------
# 7. Split Multi-value Columns into Lists (with better error handling)
# ---------------------------
def safe_split(x):
    """Safely split comma-separated values"""
    if pd.isna(x) or x == "" or x == "Unknown":
        return []
    try:
        return [item.strip() for item in str(x).split(",") if item.strip()]
    except:
        return []

data["cast_list"] = data["cast"].apply(safe_split)
data["genre_list"] = data["listed_in"].apply(safe_split)
data["country_list"] = data["country"].apply(safe_split)

# ---------------------------
# 8. Safe Explode Function
# ---------------------------
def safe_explode(df, col):
    """Safely explode a column containing lists"""
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Replace empty lists with ["Unknown"] to maintain rows
    df_copy[col] = df_copy[col].apply(lambda x: x if isinstance(x, list) and len(x) > 0 else ["Unknown"])
    
    # Explode and reset index
    try:
        return df_copy.explode(col).reset_index(drop=True)
    except Exception as e:
        print(f"❌ Error exploding column {col}: {e}")
        return df_copy

# Start with original data for exploding
data_exploded = data.copy()

# Explode one column at a time
print("🔄 Exploding cast...")
data_exploded = safe_explode(data_exploded, "cast_list")

print("🔄 Exploding genres...")
data_exploded = safe_explode(data_exploded, "genre_list")

print("🔄 Exploding countries...")
data_exploded = safe_explode(data_exploded, "country_list")

# ---------------------------
# 9. Rename Columns
# ---------------------------
data_exploded = data_exploded.rename(columns={
    "cast_list": "actor",
    "genre_list": "genre",
    "country_list": "country_exploded"
})

# ---------------------------
# 10. Clean Exploded Columns
# ---------------------------
for col in ["actor", "genre", "country_exploded"]:
    if col in data_exploded.columns:
        data_exploded[col] = data_exploded[col].astype(str).str.strip()
        # Replace 'nan' strings with 'Unknown'
        data_exploded[col] = data_exploded[col].replace(['nan', 'None', ''], 'Unknown')

# ---------------------------
# 11. Filter Out Truly Empty Entries (Optional)
# ---------------------------

initial_exploded_shape = data_exploded.shape[0]
data_exploded = data_exploded.loc[
    ~((data_exploded["actor"] == "Unknown") & 
      (data_exploded["genre"] == "Unknown") & 
      (data_exploded["country_exploded"] == "Unknown"))
].reset_index(drop=True)

print(f"✅ Removed {initial_exploded_shape - data_exploded.shape[0]} rows with all unknown values")

# ---------------------------
# 12. Save Cleaned Dataset
# ---------------------------
try:
    data_exploded.to_csv("netflix_titles_fully_cleaned.csv", index=False)
    print("✅ Fully cleaned and exploded dataset saved as 'netflix_titles_fully_cleaned.csv'")
except Exception as e:
    print(f"❌ Error saving file: {e}")

# ---------------------------
# 13. Preview and Summary
# ---------------------------
print(f"\n📊 Final dataset shape: {data_exploded.shape}")
print(f"📊 Columns: {list(data_exploded.columns)}")
print("\n🔍 First 10 rows:")
print(data_exploded.head(10))

# Show some basic statistics
print(f"\n📈 Summary Statistics:")
print(f"- Unique titles: {data_exploded['title'].nunique()}")
print(f"- Unique actors: {data_exploded['actor'].nunique()}")
print(f"- Unique genres: {data_exploded['genre'].nunique()}")
print(f"- Unique countries: {data_exploded['country_exploded'].nunique()}")