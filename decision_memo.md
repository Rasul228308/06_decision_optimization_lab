# Decision Optimization Memo

## Executive Summary

- Usable shipment records: 5,963
- Candidate options: 222
- Planned country/product lanes: 18
- Vendor concentration cap: 35.0%
- Air capacity cap: 45.0%
- Stress air capacity cap: 20.0%
- Scope: practice dry run for portfolio learning, not a production procurement or humanitarian logistics system.

## Input Validation

- PASS: required shipment, vendor, mode, cost, weight, and delivery columns are present.
- PASS: rows with unusable cost, weight, date, or unknown shipment-mode fields are excluded from candidate generation.
- PASS: optimization uses historical aggregate candidates, not direct operational commitments.

## Ethical And Operational Use

- Use for learning, scenario planning, and decision-support design only.
- Do not use to restrict medical access, deprioritize vulnerable countries, or hide supply disruption.
- Do not bypass procurement rules, anti-corruption controls, sanctions screening, or supplier due diligence.
- Do not optimize military or coercive logistics harm from this dry run.
- Human review must override the objective when equity, safety, clinical urgency, or legal duties require it.

## Objective And Constraints

- Decision: choose one historical vendor/mode candidate for each country/product lane.
- Objective: freight cost + late-delivery penalty + unreliable-service penalty.
- Constraints: vendor concentration cap and air-shipment weight share cap.
- Infeasibility handling: if no option satisfies constraints for a lane, the report marks the relaxed constraint.

## Plan Comparison

| Plan | Objective | Est. Freight Cost | Weighted Late Days | Weighted On-Time | Air Share | Largest Vendor Share | Relaxed Lanes | Cap Flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Historical dominant | 290,181,622.57 | 80,154,089.23 | 3.67 | 80.6% | 54.1% | 75.1% | 0 | vendor-cap, air-cap |
| Cheapest historical option | 180,353,050.35 | 29,266,215.87 | 2.65 | 86.1% | 55.4% | 62.4% | 0 | vendor-cap, air-cap |
| Constrained service-cost plan | 94,257,493.60 | 50,880,589.40 | 0.72 | 95.6% | 56.8% | 29.8% | 7 | air-cap |
| Air-capacity stress plan | 134,429,221.89 | 37,139,311.55 | 1.73 | 91.3% | 40.6% | 34.5% | 8 | air-cap |

## Decision Read

- Estimated freight-cost delta vs historical dominant plan: 29,273,499.83.
- Constrained-plan objective delta vs dominant: 195,924,128.97.
- Binding/relaxed constraints in constrained plan: 7.
- Constrained aggregate cap flags: air-cap.
- Stress plan adds 1 additional relaxed constraints vs normal constrained plan.

## Recommended Plan

_Showing top 18 of 18 lane decisions._

| Lane | Demand Kg | Mode | Vendor | Cost/Kg | Late Days | On-Time | Est. Cost | Violation |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| Nigeria / ARV | 3,509,663.00 | Air | MERCK SHARP & DOHME IDEA GMBH (FORMALLY MERCK SHARP & DOHME B.V.) | 3.88 | 0.00 | 100.0% | 13,612,939.78 | - |
| Zambia / ARV | 2,261,924.00 | Air | MYLAN LABORATORIES LTD (FORMERLY MATRIX LABORATORIES) | 4.97 | 0.00 | 100.0% | 11,233,514.14 | - |
| Côte d'Ivoire / ARV | 1,364,359.00 | Truck | SCMS from RDC | 3.08 | 2.46 | 77.7% | 4,202,708.54 | - |
| Mozambique / ARV | 2,226,985.00 | Air | SCMS from RDC | 1.64 | 0.81 | 94.9% | 3,641,881.23 | - |
| Uganda / ARV | 1,183,563.00 | Ocean | STRIDES ARCOLAB LIMITED | 2.36 | 0.00 | 100.0% | 2,798,764.48 | - |
| Zimbabwe / ARV | 1,566,878.00 | Truck | SCMS from RDC | 1.57 | 3.38 | 79.0% | 2,466,580.24 | - |
| Tanzania / ARV | 1,155,152.00 | Ocean | MYLAN LABORATORIES LTD (FORMERLY MATRIX LABORATORIES) | 2.13 | 0.00 | 100.0% | 2,456,548.32 | - |
| Nigeria / HRDT | 322,308.00 | Air | Abbott GmbH & Co. KG | 7.04 | 9.60 | 80.0% | 2,269,273.70 | air-cap |
| South Africa / ARV | 1,674,083.00 | Ocean | GLAXOSMITHKLINE EXPORT LIMITED | 1.18 | 0.00 | 100.0% | 1,982,038.78 | - |
| Rwanda / ARV | 739,886.00 | Ocean | HETERO LABS LIMITED | 2.54 | 0.00 | 100.0% | 1,880,618.86 | - |
| Vietnam / ARV | 633,318.00 | Air | HETERO LABS LIMITED | 2.67 | 0.09 | 98.7% | 1,692,823.42 | air-cap |
| Cameroon / ARV | 194,483.00 | Air Charter | SCMS from RDC | 4.91 | 1.80 | 80.0% | 955,725.00 | air-cap |
| Haiti / ARV | 542,073.00 | Ocean | HETERO LABS LIMITED | 1.37 | 0.00 | 100.0% | 740,205.88 | - |
| Tanzania / HRDT | 170,738.00 | Air | SCMS from RDC | 3.59 | 0.00 | 100.0% | 613,387.26 | air-cap |
| Mozambique / HRDT | 107,718.00 | Air | SCMS from RDC | 2.14 | 0.00 | 100.0% | 230,535.24 | air-cap |
| Kenya / HRDT | 145,664.00 | Truck | SCMS from RDC | 0.54 | 0.00 | 100.0% | 78,471.14 | - |
| Zambia / HRDT | 987,380.00 | Air | Abbott GmbH & Co. KG | 0.02 | 0.00 | 100.0% | 16,138.67 | air-cap |
| Côte d'Ivoire / HRDT | 582,424.00 | Air | Abbott GmbH & Co. KG | 0.01 | 0.00 | 100.0% | 8,434.72 | air-cap |

## Constraint Notes

Normal constrained plan:
- Zambia / HRDT required relaxed constraint: air-cap.
- Vietnam / ARV required relaxed constraint: air-cap.
- Côte d'Ivoire / HRDT required relaxed constraint: air-cap.
- Nigeria / HRDT required relaxed constraint: air-cap.
- Cameroon / ARV required relaxed constraint: air-cap.
- Tanzania / HRDT required relaxed constraint: air-cap.
- Mozambique / HRDT required relaxed constraint: air-cap.

Air-capacity stress plan:
- Côte d'Ivoire / ARV required relaxed constraint: air-cap.
- Zambia / HRDT required relaxed constraint: air-cap.
- Vietnam / ARV required relaxed constraint: air-cap.
- Côte d'Ivoire / HRDT required relaxed constraint: air-cap.
- Nigeria / HRDT required relaxed constraint: air-cap.
- Cameroon / ARV required relaxed constraint: air-cap.
- Tanzania / HRDT required relaxed constraint: air-cap.
- Mozambique / HRDT required relaxed constraint: air-cap.

## Analyst Actions

- Review any lane with relaxed vendor or air-capacity constraints before accepting the plan.
- Check clinical/humanitarian urgency before choosing a cheaper or slower mode.
- Validate supplier eligibility, anti-corruption controls, sanctions screening, and cold-chain requirements outside this script.
- Run stress scenarios before committing procurement or inventory policy.
- Treat the output as a decision memo, not an autonomous optimizer.

## Inherent Limits

- This is a narrow practice dry run using historical SCMS shipment data.
- The dataset does not contain real-time demand, stockouts, patient impact, procurement law, supplier capacity, cold-chain constraints, or route disruption data.
- Historical lowest cost may encode bad service quality, missing context, or inequitable allocation.
- The greedy constraint solver is transparent but not a full MILP/LP solver.
- Good-looking cost savings here do not imply a safe, ethical, or legally valid logistics plan.
