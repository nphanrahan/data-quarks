📘 Ohio Injection Well Impact Analysis — Final Project Repository

This repository contains the full workflow, data preparation, spatial modeling, and risk-based evaluation of how Class II injection wells may affect nearby oil and gas production wells in Ohio. The project integrates spatial analytics, geologic context, and exploratory modeling to help identify at-risk wells, understand regional injection water flows, and provide actionable recommendations to Stonebridge Oilfield Solutions.

🔍 Project Overview

Ohio hosts thousands of active, inactive, and legacy oil and gas wells, along with a network of Class II injection wells used to dispose of brine and produced water. Communities and operators have raised concerns about whether injection activity could interfere with nearby production performance or accelerate well decline.

This project evaluates:

1. Production Changes Near Injection Wells

Does proximity to injection wells correlate with more rapid production decline or earlier cessation of production?

2. Source of Injected Water

Which operators and counties handle the highest disposal volumes, and how much injection activity appears tied to out-of-state wells (PA/WV)?

3. Directional Interference Patterns

Do production wells show patterns (distance × direction) that might reflect geologic pathways or directional effects from injection activity?

4. Well Risk Scoring

A composite scoring system identifies wells most likely to be vulnerable based on spatial, temporal, and operational indicators.

📂 Repository Structure
data/
    cleaned_wells.csv
    link_table.csv

notebooks/
    final-analysis/
        00_data_preparation.ipynb
        01_production_change_analysis.ipynb
        02_source_of_injected_water.ipynb
        03_directional_interference_analysis.ipynb
        04_scoring_risk_of_wells.ipynb
        primary-visualizations.ipynb
        FindNearbyWells.ipynb
        OilGas-exploration_update.ipynb

results/
    (generated figures, tables, and exports)

requirements.txt
README.md

⚙️ Methods Summary
Data Preparation (Notebook 00)

Cleaned and standardized all well attributes

Converted date fields and harmonized missing values

Validated surface coordinates and filtered unreliable bottom-hole coordinates

Classified wells into injection vs. production categories

Computed great-circle distances using Haversine geometry

Built a link table connecting each injection well to nearby production wells (≤ 7 miles)

Engineered features including well age, recency of production, and horizontal/vertical proxy

Cluster analysis of risk dimensions (proximity, age, recency)

📊 Analysis Components
1. Production Change Analysis (Notebook 01)

Evaluates whether production recency (years since last nonzero output) differs by distance band from injection wells.

Key output includes:

Boxplots of production recency by distance

Summary tables comparing median decline across bands

Interpretation of spatial patterns

2. Source-of-Water Analysis (Notebook 02)

Assesses which counties and operators manage the most Class II injection load.
Identifies regions likely receiving out-of-state brine from PA/WV operators.

3. Directional Interference Analysis (Notebook 03)

Evaluates potential geological flow patterns by mapping production change across compass bearings and distances relative to injection wells.

Outputs include:

Rose diagrams

Distance × direction heatmaps

Cluster-based interpretation of spatial groupings

4. Risk Scoring System (Notebook 04)

A weighted composite score integrates multiple indicators of concern:

Proximity risk (distance to injection wells)

Approval age risk (older wells more vulnerable)

Production recency risk (years since last production)

Scores are normalized and combined:

weighted_risk = 
    0.5 * proximity_risk +
    0.3 * approval_risk +
    0.2 * recency_risk


Wells are categorized using quantile classification:

Low

Elevated

High

Critical

Cluster analysis validates natural groupings across the risk dimensions.

🚨 Key Findings

Production recency varies widely, with no simple linear relationship to injection distance, but clusters reveal groups of wells with compounding vulnerabilities.

Injection activity is highly concentrated in a small number of counties, suggesting localized risk zones with potential cumulative impact.

Directional heatmaps show pockets of abnormal recency aligned with county-level geology and historical well density.

The risk model identifies ~2,680 wells classified as Critical, flagged for priority inspection or engineering review.

Full findings are detailed in the final written report.

🧭 Recommendations

The risk framework guides Stonebridge toward:

Prioritizing inspections on wells categorized as Critical

Focusing monitoring efforts in counties with both high injection activity and aging vertical well stock

Using directional patterns to guide subsurface modeling and water-flow assessment

Conducting follow-up engineering evaluations on high-risk clusters

Recommendations are expanded in the final report.

🛠️ How to Run the Project
1. Install dependencies
pip install -r requirements.txt

2. Open the notebooks

The entrypoint is:

notebooks/final-analysis/00_data_preparation.ipynb

3. Run notebooks in sequence

Each subsequent notebook reads outputs from the previous steps.