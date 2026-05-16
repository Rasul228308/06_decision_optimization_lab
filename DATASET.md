# Kaggle Dataset

## Source

- Kaggle: `sawandikirby/supply-chain-shipment-pricing-data`
- URL: https://www.kaggle.com/datasets/sawandikirby/supply-chain-shipment-pricing-data
- Local files: `kaggle_raw/Raw_Data.csv`, `kaggle_raw/SCMS_Delivery_History_Raw_Data.xlsx`

## Portfolio Use

Use this for shipment-mode optimization, vendor performance, delivery-delay risk, cost per unit, and scenario planning. The value is not a predictive model alone. The stronger signal is a constrained decision system: service level, cost, lead time, destination risk, vendor concentration, and infeasible-plan handling.

The project excludes rows with unknown shipment mode and treats both `Air` and `Air Charter` as air-capacity consumers. It also repairs the common mojibake country-name artifact in generated reports while leaving the raw Kaggle files untouched.

## Scope And Ethics

This dataset is suitable for operations-research learning and logistics decision-support design. It is not enough for real procurement, humanitarian allocation, medical access, supplier approval, or route planning. The raw data lacks real-time demand, stockout impact, supplier capacity, cold-chain constraints, procurement law, anti-corruption review, sanctions screening, and clinical urgency.
