# life-expectancy

Exploring the wide geographic variation in life expectancy in the US.

# Background
## Variation in life expectancy by state
One of the most striking things about life expectancy in the US, is how much it varies depending on where you live.
Someone born today in Hawaii could expect to live to be 81. On the other hand, someone born in Mississippi would live to be just 72 on average.
9 years is a big difference between states.

In most developed countries the difference is much smaller. For example in Japan 🇯🇵, The difference between prefectures is just 2 years; 84 vs 82.
In the UK, the difference in LE by regions was only about 3 years: LE 77 Yrs in Scotland 🏴󠁧󠁢󠁳󠁣󠁴󠁿 and 80 in England 🏴󠁧󠁢󠁥󠁮󠁧󠁿.

If we imagine that each US state as a country we can compare them to world. 
Hawaii - with a life-expectancy of 82.3 years in 2019 - would be in 12th place worldwide, in between Spain 🇪🇸 and Sweden 🇸🇪.
On the other hand, West Virginia - with a life expectancy of 74.8 years - would be 77th place, just ahead of Columbia 🇨🇴 and behind Iran 🇮🇷.
It's even worse if we look at more recent data: In 2020, The life expectancy in Mississippi fell to 71.9. That would put Mississippi in 127th place worldwide, between Kyrgyzstan 🇰🇬 (71.95) & Tajikistan 🇹🇯(71.76)..

## Variation in life expectancy by county
The enormous heterogeneity in outcomes is even larger if we look at counties instead of states.
For example Summit County, Colorado has one of the highest LE at 86.83 years, better than Hong Kong 🇭🇰 (the best in the world; 85.5 yrs). Oglala Lakota County, South Dakota, has one of the shortest life expectancies at 66.81 years, which is slightly worse than Myanmar 🇲🇲 (171st place at 66.8 years).

![image](https://user-images.githubusercontent.com/48685552/233850467-1167d92b-96f5-4b90-9e61-e5081903e335.png)

## Why is life expectancy in the US so variable?


# Demo
You can interact with the site [here](https://nickmmark.github.io/life-expectancy/)


# ⚙️ Implementation
Interactive D3.js visualizations of U.S. life expectancy at birth (2010–2015) with county-level context and exploratory scatterplots versus demographics and election results.

## 💾 Data Sources
This app combines data from multiple sources:
* Life expectancy (2010-2015): [CDC/US Small-Area Life Expectancy Estimates](https://www.cdc.gov/nchs/nvss/usaleep/usaleep.html)
* Election results: [US County Level Election Results](https://github.com/tonmcg/US_County_Level_Election_Results_08-24)
* Economic/demographic data: [OpenIntro County Complete Data](https://www.openintro.org/data/?data=county_complete)
* County name/FIPS crosswalk: [Kieran Healy’s FIPS master](https://github.com/kjhealy/fips-codes) --> state_and_county_fips_master.csv or local fips_crosswalk.csv.
* Geometries: [us-atlas TopoJSON](https://github.com/topojson/us-atlas) (states-10m, counties-10m).

## 🛠️ Data wrangling
* Joining life expectancy to counties:
  * Use FIPS-keyed map (county_life_expectancy_by_fips.json) if present or derive from name-keyed CDC county data: normalize county/state strings (strip accents, convert “St.”→“Saint”, remove “County/Parish/City & Borough/Census Area/Municipality” suffixes, collapse whitespace) and join via crosswalk → FIPS.
* County metadata: Load OpenIntro file and map by zero-padded 5-digit FIPS; accept flexible column headers (robust matching to handle variants).
* Election margins: Parse 2016/2020 CSVs; compute margin = GOP% − DEM% in percentage points. Accept either % or proportions; auto-convert to pp.
* For Robustness: Flexible header detection for external CSVs; fallback name join if precomputed FIPS JSON is absent; manual fixes for a few CA county labels.

Notes & limitations
* LE values reflect 2010–2015 averages; demographic/economic fields are the latest available (often 2017) in OpenIntro.
* Some Alaska county-equivalents and independent cities use special naming rules; normalization covers common cases.
* Puerto Rico is excluded from some UI controls.

### 🗺️ Visualization:
* Maps (state & county): D3 + TopoJSON (geoAlbersUsa), sequential color (default Red→Blue for low→high LE), legend with numeric scale, tooltips with bold LE (years) and county extras.
* Scatterplots: Life expectancy (y) vs chosen x-variable (demographics or 2016/2020 margin). Each dot = county, radius ∝ population. Wheel/pinch zoom + pan, Reset zoom, optional OLS regression line + R² (checkbox), state filter (multi-select). Tooltips show county name, LE (years), x-value (with units), and population.

### 📁 Files
```
life-expectancy-web-app
├─ index.html
├─ state_life_expectancy.json
├─ county_life_expectancy_normalized.json
├─ county_life_expectancy_by_fips.json
├─ county_complete.csv
├─ 2016_US_County_Level_Presidential_Results.csv
├─ 2020_US_County_Level_Presidential_Results.csv
└─ fips_crosswalk.csv
```

# 📚️ References
* USALEEP
