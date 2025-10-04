import pandas as pd
import os, glob, re, io

RAW_DIR = "data/raw"
CLEAN_DIR = "data/cleaned"
OUT_CSV = os.path.join(CLEAN_DIR, "all_parks_recreation_visits.csv")

os.makedirs(CLEAN_DIR, exist_ok=True)

expected = ["Park","Unit Code","Park Type","Region","State","Year","Month","Recreation Visits"]

# header canon mapping (very forgiving)
def canonicalize_columns(cols):
    out = []
    for c in cols:
        k = re.sub(r"\s+", " ", str(c)).strip().lower()
        k = k.replace("_", " ")
        if k in ["park", "park name", "park unit", "park unit name"]:
            out.append("Park")
        elif k in ["unit code","park code","code","unit"]:
            out.append("Unit Code")
        elif k in ["park type","type"]:
            out.append("Park Type")
        elif k in ["region","area"]:
            out.append("Region")
        elif k in ["state","st"]:
            out.append("State")
        elif k in ["year","yr"]:
            out.append("Year")
        elif k in ["month","mo"]:
            out.append("Month")
        elif k in ["recreation visits","visits","recreation_visits","recreation  visits","recreation visit"]:
            out.append("Recreation Visits")
        else:
            out.append(c)  # keep as-is; we’ll subset later
    return out

def try_read(file_path):
    """
    Try multiple strategies to read messy CSVs:
    - detect delimiter (comma/tab/semicolon/2+ spaces)
    - skip junk lines
    - python engine with on_bad_lines='skip'
    Returns a DataFrame or None.
    """
    # read raw text and normalize unicode spaces
    with open(file_path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", errors="ignore")
    text = text.replace("\ufeff", "")  # BOM
    text = re.sub(r"[ \t\xa0]+", lambda m: m.group(0).replace("\xa0"," "), text)

    # drop obvious junk header lines (title rows) until we hit something with many separators
    lines = [ln for ln in text.splitlines() if ln.strip() != ""]
    start = 0
    for i, ln in enumerate(lines[:10]):  # inspect first 10
        # heuristic: a real header should contain at least 4 tokens split by commas/tabs/2+ spaces
        tokens = re.split(r",|\t|;|\s{2,}", ln.strip())
        if len([t for t in tokens if t.strip()]) >= 4:
            start = i
            break
    text = "\n".join(lines[start:])

    # Try multiple delimiters
    seps = [
        r",",            # comma
        r"\t",           # tab
        r";",            # semicolon
        r"\s{2,}",       # 2+ spaces
        r",|\t|;|\s{2,}" # regex OR of all
    ]
    for sep in seps:
        try:
            df = pd.read_csv(
                io.StringIO(text),
                engine="python",
                sep=sep,
                on_bad_lines="skip",
                dtype=str,
                skip_blank_lines=True
            )
            if df.shape[1] < 4:  # too few columns, try next sep
                continue
            return df
        except Exception:
            continue
    return None

dfs = []
files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
print(f"Found {len(files)} CSV files to merge...")

for f in files:
    base = os.path.basename(f)
    df = try_read(f)
    if df is None:
        print(f"Could not parse {base}")
        continue

    # normalize headers
    df.columns = canonicalize_columns(df.columns)

    # if the expected columns aren’t all present, try to coerce by matching partials
    # (e.g., headers with extra spaces, case, etc., are already handled above)
    missing = [c for c in expected if c not in df.columns]
    if missing:
        print(f" {base}: missing columns {missing}. Attempting salvage…")
        # sometimes headers get duplicated or shifted; we can’t reliably infer—skip if still missing
        # keep only known columns
        df = df[[c for c in df.columns if c in expected]].copy()

    # ensure we end with exactly these columns (fill missing with NaN)
    for c in expected:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[expected].copy()

    # strip whitespace
    for c in expected:
        df[c] = df[c].astype(str).str.strip()

    # clean numbers like "4,63,710" or "1 23 456" → 463710 / 123456
    def clean_num(x):
        if x is None:
            return pd.NA
        s = str(x)
        # if it's clearly 0/empty
        if s.strip() in ["", "nan", "None", "-"]:
            return pd.NA
        # remove all non-digits
        digits = re.sub(r"[^0-9]", "", s)
        return pd.NA if digits == "" else int(digits)

    df["Recreation Visits"] = df["Recreation Visits"].apply(clean_num)
    df["Year"]  = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce").astype("Int64")

    # drop rows without essential fields
    df = df.dropna(subset=["Year","Month","Recreation Visits"])

    if len(df) == 0:
        print(f" {base}: no valid rows after cleaning, skipping.")
        continue

    dfs.append(df)

if not dfs:
    print(" No valid CSVs were processed!")
else:
    merged = pd.concat(dfs, ignore_index=True).drop_duplicates()
    merged.to_csv(OUT_CSV, index=False)
    print(f" Wrote {OUT_CSV} with {len(merged):,} rows from {len(dfs)} usable files.")

