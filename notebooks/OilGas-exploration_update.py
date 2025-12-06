#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pathlib import Path
import pandas as pd

# Go up one level from /notebooks to the project root
PROJECT_ROOT = Path().resolve().parent

# Build the path to the data folder
file_path = PROJECT_ROOT / "data" / "Oil&GasWells.csv"

df = pd.read_csv(file_path)

df.info()
df.describe(include='all').T
df.isna().mean().sort_values(ascending=False).head(20)


# The dataset contains 24,174 wells with 58 attributes, spanning well characteristics, spatial coordinates, production metrics, operator information, and inspection history.
# The dataset shows a wide range of completeness:
# 
# Fully or near-fully populated fields
# County, Well Status, Well Latitude/Longitude, OBJ_ID, shale indicators
# (These provide a strong source for geospatial and categorical analysis.)
# 
# Moderately populated fields (~50–80% completeness)
# Well Date Complete, Total Depth, IP Oil/Gas, Producing Formation
# (Usable for modeling but require NA handling.)
# 
# Sparse or highly incomplete fields (>95% missing)
# Toe/Heel coordinates (likely only for horizontal wells)
# Well_BH_LAT/LONG (bottom-hole often missing)
# SecondProdFormation, Well_ProposedFormations
# Orphan Well Program Status
# (These should might want to be removed.)
# 
# Completely empty field
# OWPS Description is 100% null, drop from analysis.
# 
# High Missingness Features (Top 10)
# Feature	% Missing	Interpretation
# OWPS Description	100%	Drop
# Toe Latitude / Longitude	~99%	
# Heel Longitude / Latitude	~98%
# Well_BH_LAT/LONG	~98%
# SecondProdFormation	96%	
# Orphan Well Program Status	96%	
# Proposed Formations	86%	
# GeoPhysLogs	71%	
# 
# Conclusion:
# For the Stonebridge-style modeling, focus on latitude/longitude, depth, IP metrics, dates, formations, county, operator, and inspection dates, and avoid highly sparse fields.

# In[3]:


df[['Well_WH_LAT','Well_WH_LONG','Well Latitude','Well Longitude']].describe()


# In[4]:


df[(df['Well Latitude'] < 38) | (df['Well Latitude'] > 42)]
df[(df['Well Longitude'] > -80) | (df['Well Longitude'] < -85)]


# In[5]:


df['lat_delta'] = abs(df['Well Latitude'] - df['Bottom Hole Latitude'])
df['long_delta'] = abs(df['Well Longitude'] - df['Bottom Hole Longitude'])

df[['lat_delta','long_delta']].describe()


# Here’s what we found when looking at the different location fields in the dataset:
# 1. The main well coordinates look good
# The fields Well Latitude and Well Longitude have no missing values.
# Their ranges (lat ~38.4–42.0, long ~–84.8 to –80.5) match what we’d expect for wells located in Ohio.
# These should be our primary fields for mapping and spatial analysis.
# 
# 2. The wellhead coordinates (Well_WH_LAT / Well_WH_LONG) mostly match the main coordinates
# ~99% complete
# Values fall in the same Ohio range
# A few wells have zeros for latitude
# These fields are usable, but the main latitude/longitude fields are cleaner.
# 
# 3. Bottom-hole, toe, and heel coordinates are mostly missing
# Bottom-hole lat/long only exist for ~21K wells (out of 24K)
# Toe and heel coordinates exist for <1% of wells
# These fields can’t reliably be used to identify horizontal wells or measure lateral length.
# 
# 4. The “delta” calculations between surface and bottom-hole coordinates are not meaningful yet
# We calculated differences between wellhead and bottom-hole coordinates (lat_delta / long_delta).
# The deltas are way too large (mean of ~39° latitude difference), which isn’t physically possible.
# 
# This means:
# some wells have placeholder or incorrect bottom-hole coordinates
# or the fields were entered using a different coordinate system
# or missing values were coded as zeros/80s/etc.
# 
# So we shouldn’t use any of the delta calculations until we fix the coordinate inconsistencies.

# In[6]:


df['Well Type'].value_counts(dropna=False)



# In[7]:


df['Well Status'].value_counts(dropna=False)


# In[8]:


df['Producing Formation'].value_counts(dropna=False).head(20)


# In[9]:


df[['Utica_Shale','Marcellus_Shale']].describe()


# We examined the distributions of Well Type, Well Status, and Producing Formation to understand the overall structure of the well inventory and the geologic targets driving activity across the dataset. The Well Type breakdown shows a diverse mix of producing wells, dry holes, plugged wells, and wells with oil/gas shows, giving us an early sense of drilling outcomes and operational behavior. The Well Status distribution highlights that the largest groups are Producing and Plugged and Abandoned, which helps distinguish active infrastructure from legacy wells that may have different operational or environmental considerations. The Producing Formation summary identifies the Clinton Sand, Berea Sandstone, and related Clinton Group intervals as the dominant reservoirs in the dataset, providing context for where most historical and current production activity is concentrated. Finally, we looked at the Utica_Shale and Marcellus_Shale indicators because these two formations represent major unconventional shale targets in the region; tracking them separately helps us identify horizontal or deeper wells, which often differ in drilling practices, production behavior, and regulatory characteristics.

# In[10]:


date_cols = ['Well_Date_Approved','Well_Date_Complete','Well_Date_Plugged']
for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors='coerce')

df[date_cols].describe()


# 

# In[11]:


pd.set_option('display.max_rows', None)

df['Well_Date_Approved'] = pd.to_datetime(df['Well_Date_Approved'], errors='coerce')
df['Well_Date_Complete'] = pd.to_datetime(df['Well_Date_Complete'], errors='coerce')
df['Well_Date_Plugged'] = pd.to_datetime(df['Well_Date_Plugged'], errors='coerce')

approved = df.groupby(df['Well_Date_Approved'].dt.year).size()
completed = df.groupby(df['Well_Date_Complete'].dt.year).size()
plugged   = df.groupby(df['Well_Date_Plugged'].dt.year).size()

combined = pd.concat([approved, completed, plugged], axis=1)
combined.columns = ['Approved', 'Completed', 'Plugged']

combined = combined.fillna(0).astype(int)

combined = combined.sort_index()
combined


# The yearly trends show a long historical record of well activity, with data extending back to the early 1900s. Completion counts are extremely high from 1900–1950, which reflects the early conventional drilling boom in Ohio and the fact that many of these wells were drilled before modern permitting practices existed — this is also why approvals are sparse in the earliest years but completions appear in large numbers. From the 1960s through the mid-1980s, we see a steady rise in approvals and completions, peaking sharply around 1980–1985, which aligns with major development cycles in shallow sandstone formations like the Clinton and Berea. Plugging activity increases significantly starting in the 1950s and continues at a moderate pace through the modern era, indicating ongoing abandonment and remediation of older well stock. In the 2000s and 2010s, approvals and completions drop sharply as the industry shifts away from shallow vertical wells toward deeper unconventional drilling, which is less common in this dataset. The 2020–2025 values remain low but present, reflecting modern permitting and plugging activity but at a much smaller scale compared to historical drilling eras.

# In[12]:


df['Well_Total_Depth'].describe()


# In[13]:


df[['Well_IP_GAS','Well_IP_OIL']].describe()


# In[14]:


df[['Well_IP_GAS','Well_IP_OIL']].plot(kind='box')


# In[15]:


from scipy import stats
df['ip_gas_z'] = stats.zscore(df['Well_IP_GAS'].fillna(0))

df[df['ip_gas_z'] > 3][['Well Name','Well_IP_GAS','ip_gas_z']]


# The depth data shows a wide range of well types, with a median total depth of around 2,947 feet, but values extend from shallow vertical wells all the way to extremely deep wells exceeding 250,000 feet, indicating the presence of clear data-entry errors or placeholder values at the upper end. Initial production (IP) volumes have highly skewed distributions: gas IP has a median of only 30 Mcf, but a long tail of very high-producing wells reaching up to 50,000 Mcf, while oil IP values are generally low (median 1 barrel) with occasional large producers. The combination of high standard deviations and many zeros suggests a dataset dominated by older or non-producing wells, with a relatively small subset of modern high-volume wells. A Z-score analysis highlights a cluster of extreme gas-IP outliers,many with values above 10 standard deviations from the mean, which appear to be large horizontal shale wells rather than noise or random anomalies. These high-IP wells likely represent unconventional development and should be treated separately in modeling or further analysis due to their fundamentally different production behavior. Overall, the depth and IP statistics indicate a dataset with a very broad mix of legacy conventional wells and modern shale wells, requiring careful filtering of outliers and implausible depth values before performing trend or predictive modeling.

# In[16]:


df['County'].value_counts().head(15)
df.groupby('County')['Well_Total_Depth'].mean().sort_values(ascending=False).head()


# The depth-by-county breakdown shows clear geographic patterns in drilling behavior. Wells in Belmont, Harrison, Jefferson, Carroll, and Guernsey counties have the deepest average well depths, with Belmont leading at over 8,500 feet. These counties align with the core area of deep Appalachian Basin development, including both legacy Clinton/Berea wells and more recent Utica/Point Pleasant shale drilling. The strong clustering of deeper wells in a handful of eastern counties highlights the regional focus of high-intensity drilling activity within the dataset. This geographic variation is important for understanding differences in well construction, risk profiles, and production potential across the state.

# In[17]:


df['Orphan Well Program Status'].value_counts(dropna=False)


# In[18]:


df['Last_Inspection_Date'] = pd.to_datetime(df['Last_Inspection_Date'], errors='coerce')

df['days_since_inspection'] = (pd.Timestamp.today() - df['Last_Inspection_Date']).dt.days
df['days_since_inspection'].describe()


# The orphan well indicators show that nearly all wells (~96%) have no orphan status recorded, while a small but meaningful subset falls under categories such as Traditional Program Assessing, Referred, or Traditional Plugged, totaling a few hundred wells. These classifications help identify wells that may require remediation, monitoring, or state-funded plugging support. Inspection timing varies widely, with the dataset showing a median of 2,896 days (~8 years) since the last inspection among wells where inspection data exists. The presence of negative values suggests some records contain data-entry or timestamp errors and will need cleaning before further analysis. Overall, these fields help differentiate wells that are actively monitored from those potentially at higher environmental or operational risk due to age, lack of inspection, or unresolved orphan status.

# In[19]:


num_df = df.select_dtypes(include=['float64','int64'])
num_df.corr()


# The correlation matrix shows that the various latitude/longitude fields are strongly correlated with one another, which is expected since they all represent the same underlying location information. Beyond those obvious spatial correlations, several meaningful relationships appear in the operational and geological attributes. Well_Total_Depth has moderate positive correlations with Well_IP_GAS and the shale indicators, suggesting that deeper wells tend to be associated with higher gas output and are more likely to target formations such as the Utica. The shale indicators also show strong negative correlations with the lat_delta/long_delta fields, meaning shale wells tend to have cleaner and more consistent coordinate data, likely because they are newer, more modern wells. Last_Nonzero_Production_Year correlates positively with gas IP and depth, reinforcing the idea that more recent wells are deeper and more productive. Conversely, days_since_inspection correlates negatively with production and production year, meaning older wells (with more days since last inspection) generally have lower output and represent earlier drilling eras.

# In[20]:


df['is_horizontal'] = (df['lat_delta'] > 0.005).astype(int)

df['years_since_approved'] = (
    pd.Timestamp.today().year - df['Well_Date_Approved'].dt.year
)

df['age_category'] = pd.cut(
    df['years_since_approved'],
    bins=[0,5,10,20,40,100],
    labels=['0–5','6–10','11–20','21–40','40+']
)

# Quick summary output for engineered features

display("=== Horizontal vs Vertical Wells ===")
display(df['is_horizontal'].value_counts().rename({0: "Vertical", 1: "Horizontal"}))
display(df.groupby('is_horizontal')[['Well_Total_Depth','Well_IP_GAS']].mean())

display("=== Years Since Approved (Summary) ===")
display(df['years_since_approved'].describe()[['min','25%','50%','75%','max']])

display("=== Wells by Age Category ===")
display(df['age_category'].value_counts().sort_index())

display("=== Avg Depth & IP by Age Category ===")
display(df.groupby('age_category')[['Well_Total_Depth','Well_IP_GAS']].mean())

display("=== Horizontal % by Age Category ===")
display((pd.crosstab(df['age_category'], df['is_horizontal'], normalize='index') * 100)
        .rename(columns={0:'Vertical %',1:'Horizontal %'})
       )

display("=== Plugged Wells by Age Category ===")
display(df.groupby('age_category')['Well_Date_Plugged'].count())



# The is_horizontal flag uses the difference between surface and bottom-hole latitude to approximate whether a well is horizontal-useful because horizontal wells behave very differently from vertical wells in terms of production, depth, cost, and regulatory relevance. The years_since_approved field transforms raw approval dates into a simple numerical measure of well age, allowing us to explore how performance, inspection needs, or plugging likelihood change over time. Finally, the age_category bins help group wells into meaningful lifecycle ranges (0–5 years, 6–10, etc.), making it easier to compare younger vs. older wells without relying on raw date calculations. Together, these engineered features provide structure to the dataset, uncover patterns tied to well design and age, and enable clearer segmentation for exploration, visualization, and any downstream modeling or risk assessment.
# 
# The engineered variables reveal several clear structural patterns in the dataset. The majority of wells (~21,190) are classified as horizontal, with only ~2,984 vertical wells, reflecting the dominance of modern shale development across the dataset. Horizontal wells tend to be both deeper (average ~3,040 ft vs. 3,380 ft for vertical) and significantly higher-producing, with average gas IP more than double that of vertical wells. Age analysis shows that most wells fall into older categories, with the 40+ year group being the largest, while the youngest wells (0–5 years) represent the smallest share of the inventory.
# 
# Performance and depth vary dramatically by age group: the youngest wells (0–5 years) have extremely high average depths (~17,400 ft) and exceptional gas output (~8,010 Mcf), clearly identifying them as deep horizontal shale wells. Production declines sharply in older groups, which also contain a mix of legacy vertical wells and early conventional development. The horizontal well percentage also shifts by age: younger wells are overwhelmingly horizontal, while the 11–20 year group contains the highest share of vertical wells. Plugging activity is concentrated in older wells, with over 2,100 wells plugged in the 40+ category compared to only 28 in the 0–5 group.
# 
# Overall, these engineered fields highlight a strong lifecycle pattern: young, deep horizontal shale wells dominate modern development, while older, shallower vertical wells comprise most of the aging and plugged inventory. This segmentation is essential for analyzing performance, risk, inspection needs, and long-term infrastructure behavior in the dataset.

# In[21]:


from pathlib import Path
import numpy as np
from sklearn.neighbors import BallTree


df = df.dropna(subset=['Well Latitude', 'Well Longitude']).copy()
df['lat_rad'] = np.radians(df['Well Latitude'])
df['lon_rad'] = np.radians(df['Well Longitude'])

# Define Production and Injection Wells 

injection_mask = df['Well Type'].str.contains('Injection', case=False, na=False)

production_keywords = ['oil', 'gas', 'producing', 'plugged oil', 'plugged gas', 'final restoration']
production_mask = (
    df['Well Status'].str.contains('producing|plugged|final restoration', case=False, na=False) |
    df['Well Type'].str.contains('oil|gas', case=False, na=False)
)

injection_wells   = df[injection_mask].copy()
production_wells  = df[production_mask].copy()

print(f"\nInjection wells found  : {len(injection_wells):,}")
print(f"Production wells found : {len(production_wells):,}")

# BallTree Model 

coords_prod = production_wells[['lat_rad', 'lon_rad']].values
tree = BallTree(coords_prod, metric='haversine')   

R = 3958.8  # Earth's radius in miles
radius_miles = 7.0
radius_radians = radius_miles / R

# Link Table 

links = []

for idx, inj in injection_wells.iterrows():
    inj_coord = np.array([[inj['lat_rad'], inj['lon_rad']]])

    indices = tree.query_radius(inj_coord, r=radius_radians)[0]

    if len(indices) == 0:
        continue

    prods = production_wells.iloc[indices].copy()

    lat1 = inj['lat_rad']
    lon1 = inj['lon_rad']
    lat2 = prods['lat_rad'].values
    lon2 = prods['lon_rad'].values

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance_miles = R * c

    # Build link records
    for prod_idx, dist in zip(indices, distance_miles):
        links.append({
            'injection_OBJ_ID'      : inj['OBJ_ID'],
            'injection_API'         : inj['Permit number - API'],
            'injection_county'      : inj['County'],
            'injection_township'    : inj['Township'],
            'injection_well_name'   : f"{inj['Well Name'] or ''} {inj['Well Number'] or ''}".strip(),
            'injection_lat'         : inj['Well Latitude'],
            'injection_lon'         : inj['Well Longitude'],

            'production_OBJ_ID'    : production_wells.iloc[prod_idx]['OBJ_ID'],
            'production_API'        : production_wells.iloc[prod_idx]['Permit number - API'],
            'production_county'     : production_wells.iloc[prod_idx]['County'],
            'production_well_name'  : f"{production_wells.iloc[prod_idx]['Well Name'] or ''} {production_wells.iloc[prod_idx]['Well Number'] or ''}".strip(),
            'production_lat'        : production_wells.iloc[prod_idx]['Well Latitude'],
            'production_lon'        : production_wells.iloc[prod_idx]['Well Longitude'],
            'production_status'     : production_wells.iloc[prod_idx]['Well Status'],

            'distance_miles'        : round(dist, 3)
        })

link_df = pd.DataFrame(links)
link_df = link_df.sort_values(['injection_OBJ_ID', 'distance_miles'])


# In[22]:


link_df.head()


# In[23]:


# Spatial Analysis

# Descriptive Statistics 

link_df['distance_miles'].describe()

import matplotlib.pyplot as plt
plt.hist(link_df['distance_miles'], bins=30)
plt.xlabel("Distance (miles)")
plt.ylabel("Count")
plt.title("Distribution of Injection → Production Distances")
plt.show()


# In[25]:


# Number of Production Wells per Injection Well 

prod_counts = link_df.groupby('injection_API')['production_API'].nunique()
print(prod_counts.describe())

print("\nTop 10 injection wells with most production links:")
print(prod_counts.sort_values(ascending=False).head(10))


# In[27]:


# Nearest Production Well to each Injection Well 

nearest = link_df.groupby('injection_API').first().reset_index()
nearest[['injection_API','production_API','distance_miles']]


# In[28]:


# County-Level Summary (Injection County)

county_stats = link_df.groupby('injection_county')['distance_miles'].describe()
print(county_stats)


# In[29]:


# Aggregated Injection Summary 

inj_agg = link_df.groupby('injection_API').agg(
    n_productions=('production_API','nunique'),
    mean_distance=('distance_miles','mean'),
    median_distance=('distance_miles','median'),
    min_distance=('distance_miles','min'),
    max_distance=('distance_miles','max')
)

print(inj_agg.describe())


# In[24]:


# Heatmap of Injection to Production Density 

plt.scatter(link_df['production_lon'], link_df['production_lat'], s=5, alpha=0.4)
plt.scatter(link_df['injection_lon'], link_df['injection_lat'], s=5, alpha=0.4, color='red')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Injection (red) and Production (blue) Wells")
plt.show()

