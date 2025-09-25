# build_fips_json.py  (robust version)
import csv, json, math, re
from statistics import mean

CDC_CSV = "U.S._Life_Expectancy_at_Birth_by_State_and_Census_Tract_-_2010-2015.csv"
XWALK  = "fips_crosswalk.csv"   # headers: fips,name,state (this can be full name or 2-letter)
OUT    = "county_life_expectancy_by_fips.json"

STATE_ABBR_TO_NAME = {
  "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut",
  "DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
  "IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts",
  "MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
  "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
  "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota",
  "TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
  "WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"
}
STATE_NAME_FROM_ABBR = {v:k for k,v in STATE_ABBR_TO_NAME.items()}

def strip_accents(s):
    try:
        import unicodedata
        return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")
    except Exception:
        return s

def norm_county_name(s):
    s = s or ""
    s = re.sub(r",\s*[A-Z]{2}$", "", s)  # drop trailing ", ST"
    s = re.sub(r" City and Borough| Borough| Census Area| Municipality| County| Parish", "", s, flags=re.I)
    s = re.sub(r"^St\.?\s+", "Saint ", s, flags=re.I)
    s = strip_accents(s)
    s = re.sub(r"[-']", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def norm_key(state_name, county_name):
    return (strip_accents(state_name).upper() + "|" + norm_county_name(county_name).upper())

# --- 1) Read crosswalk, build fips<->name maps ---
fips_to_name = {}
name_to_fips = {}
with open(XWALK, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        fips = (row.get("fips") or row.get("FIPS") or "").strip().zfill(5)
        state_field = (row.get("state") or row.get("STATE") or "").strip()
        county_field = (row.get("name") or row.get("NAME") or "").strip()
        if not (fips and state_field and county_field):
            continue
        # Accept either full state name or 2-letter abbr in crosswalk
        state_name = STATE_ABBR_TO_NAME.get(state_field.upper(), state_field)
        county_name = re.sub(r",\s*[A-Z]{2}$", "", county_field)
        fips_to_name[fips] = (state_name, county_name)
        name_to_fips[norm_key(state_name, county_name)] = fips

# --- 2) Scan CDC CSV, find columns robustly ---
def find_col(fieldnames, contains_all=(), contains_any=(), startswith_any=()):
    fl = [ (c, c.lower()) for c in fieldnames ]
    for c, cl in fl:
        if all(x in cl for x in contains_all) and (not contains_any or any(x in cl for x in contains_any)) \
           and (not startswith_any or any(cl.startswith(x) for x in startswith_any)):
            return c
    return None

with open(CDC_CSV, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    fns = r.fieldnames or []

    # Life expectancy column (e.g., "Life Expectancy", "life_expectancy")
    life_col = find_col(fns, contains_all=("life","expect"))
    if not life_col:
        raise RuntimeError("Couldn't find Life Expectancy column in CDC CSV.")

    # County column (e.g., "County", "County Name", "county_name", or even "Geographic Area Name")
    county_col = (find_col(fns, contains_any=("county",), startswith_any=())
                  or find_col(fns, contains_any=("geographic", "area", "name")))
    if not county_col:
        raise RuntimeError("Couldn't find a County/Area name column in CDC CSV.")

    # State column is OPTIONAL — we can derive from ", ST" at end of county if needed
    state_col = (find_col(fns, startswith_any=("state",))  # "State", "State Name", etc.
                 or find_col(fns, contains_any=("state",)))

    # --- 3) Aggregate LE by (STATE|COUNTY) ---
    by_key_values = {}
    total_rows = 0
    good_rows = 0
    for row in r:
        total_rows += 1
        le_raw = (row.get(life_col) or "").strip()
        try:
            le = float(le_raw)
        except ValueError:
            continue
        if math.isnan(le):
            continue

        county_field = (row.get(county_col) or "").strip()  # often like "Autauga County, AL"
        if not county_field:
            continue

        # Prefer explicit state if available, otherwise derive from county suffix ", ST"
        state_name = ""
        if state_col:
            st_val = (row.get(state_col) or "").strip()
            # If it's a 2-letter code, map to full; if it's already a full name, keep it.
            if len(st_val) == 2 and st_val.upper() in STATE_ABBR_TO_NAME:
                state_name = STATE_ABBR_TO_NAME[st_val.upper()]
            else:
                state_name = st_val

        if not state_name:
            m = re.search(r",\s*([A-Z]{2})$", county_field)
            st_abbr = m.group(1) if m else ""
            state_name = STATE_ABBR_TO_NAME.get(st_abbr, st_abbr)

        if not state_name:
            # As a last resort, skip; we need some state context
            continue

        county_name = norm_county_name(county_field)
        key = norm_key(state_name, county_name)
        by_key_values.setdefault(key, []).append(le)
        good_rows += 1

print(f"Read CDC rows: {total_rows}, usable rows: {good_rows}")

# --- 4) Map (STATE|COUNTY) -> FIPS, compute means, write JSON ---
fips_values = {}
matched = 0
for key, vals in by_key_values.items():
    fips = name_to_fips.get(key)
    if fips:
        matched += 1
        fips_values[fips] = round(mean(vals), 2)

print(f"Matched {matched} county name keys; writing {len(fips_values)} FIPS entries to {OUT}")
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(fips_values, f, indent=2)
print("Done.")
