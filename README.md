# 🎬 NETFLIX-PROJECT

## 📘 Overview
The **NETFLIX-PROJECT** focuses on cleaning, transforming, and organizing raw Netflix data for further data analysis or machine learning tasks.  
It performs **data preprocessing** on the `netflix_titles.csv` dataset, which includes movie and TV show metadata such as title, cast, country, director, duration, and genres.

This script ensures that the dataset is consistent, complete, and analysis-ready by handling missing values, standardizing date formats, splitting multi-value columns, and exporting a fully cleaned dataset.

---

## 🧠 Project Objective
To create a **robust and automated Netflix data cleaning pipeline** that:
- Handles incomplete or inconsistent data gracefully.
- Converts mixed-format dates into standard datetime objects.
- Splits multi-valued fields (like cast, genres, countries) into clean lists.
- Produces a fully cleaned and exploded dataset ready for analytics.

---

## 📂 Dataset Description
**Input file:** `netflix_titles.csv`  
**Output file:** `netflix_titles_fully_cleaned.csv`

| Column | Description |
|---------|-------------|
| `show_id` | Unique identifier for each Netflix title |
| `type` | Type of content — Movie or TV Show |
| `title` | Name of the title |
| `director` | Director’s name |
| `cast` | Cast members |
| `country` | Country of production |
| `date_added` | Date the title was added to Netflix |
| `release_year` | Year the title was released |
| `rating` | Content rating (e.g., PG, TV-MA) |
| `duration` | Duration in minutes or seasons |
| `listed_in` | Genre or category |
| `description` | Short summary of the title |

---

## ⚙️ Processing Steps

### 1. **Load Raw Data**
- Loads the original `netflix_titles.csv` safely.
- Displays dataset shape after successful load.
- Handles missing file errors gracefully.

### 2. **Handle Missing Values**
- Fills missing entries in key columns with `"Unknown"` or `""` (for empty lists).
- Ensures that no null entries break further processing.

### 3. **Parse and Standardize Dates**
- Parses the `date_added` column with multiple possible formats:
  - `25-Sep-21`, `25-Sep-2021`, `January 1, 2021`, etc.
- Uses a custom function `parse_netflix_dates()` to safely handle format inconsistencies.
- Falls back to flexible parsing for any unrecognized formats.

### 4. **Clean and Extract Duration**
- Cleans and separates the `duration` column into:
  - `duration_int` → numeric value  
  - `duration_type` → "min" or "season"

### 5. **Remove Duplicates and Extra Spaces**
- Trims extra spaces in all text-based columns.
- Removes duplicate rows from the dataset.

### 6. **Split Multi-Value Columns**
- Converts comma-separated columns (like cast, genres, countries) into **lists**:
  - `cast_list`, `genre_list`, `country_list`
- Handles missing or invalid entries using safe custom logic.

### 7. **Safe Exploding**
- Uses the custom `safe_explode()` function to expand list columns into multiple rows:
  - Each row corresponds to one actor, genre, and country.
- Replaces empty lists with `"Unknown"` to maintain row integrity.

### 8. **Column Renaming and Cleaning**
- Renames list columns for clarity:
  - `cast_list` → `actor`
  - `genre_list` → `genre`
  - `country_list` → `country_exploded`
- Cleans up text values and replaces `'nan'`, `'None'`, and blanks with `"Unknown"`.

### 9. **Final Cleaning**
- Removes rows where all key exploded columns are `"Unknown"`.
- Ensures the dataset is consistent and meaningful.

### 10. **Save and Export**
- Exports the final cleaned dataset as:
