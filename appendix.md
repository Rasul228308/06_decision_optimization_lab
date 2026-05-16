# Appendix: Decision Optimization Decisions

This project is a compact logistics decision-optimization dry run. It is intentionally narrow: one historical SCMS shipment dataset, one script, one decision memo.

## Scope Decision

The goal is to show operations-research thinking, not to build a procurement platform.

This project demonstrates:

- candidate generation from historical lanes
- objective functions with cost, delay, and reliability
- vendor concentration constraints
- air-capacity constraints
- stress scenario comparison
- infeasibility/constraint-relaxation notes
- explicit ethical and humanitarian limits

It does not demonstrate full mixed-integer optimization, real-time demand planning, legal procurement governance, clinical prioritization, or end-to-end supply-chain execution.

## Methodology

Decision unit:

- one country/product lane
- one historical vendor/mode candidate chosen per lane

Objective:

`freight cost + late-delivery penalty + unreliable-service penalty`

Constraints:

- maximum share of plan weight from one vendor
- maximum share of plan weight shipped by air; `Air` and `Air Charter` are both treated as air modes

Baselines:

- historical dominant option
- cheapest historical option
- constrained service-cost option
- air-capacity stress option

The solver is a transparent greedy constrained assignment. That is intentional for a dry run: it makes tradeoffs and violations readable. A real implementation should move to linear/integer programming once the business rules are validated.

## Skills Reflected

| Skill Area | Where It Appears |
| --- | --- |
| Optimization | candidate assignment under capacity constraints |
| LP/ILP thinking | objective terms, decision variables, binding constraints |
| Scenario simulation | normal plan vs air-capacity stress plan |
| Business translation | cost, delay, reliability, concentration risk |
| Infeasibility handling | relaxed-constraint notes |
| Data cleaning | unusable cost/weight/date rows and unknown shipment modes excluded |
| Text normalization | common Latin-1/UTF-8 mojibake repaired in report output |
| Risk analytics | vendor concentration and mode dependence |
| Ethical review | humanitarian and procurement safeguards |

## Ethical Considerations

Recommended use:

- operations-research learning
- logistics scenario planning
- procurement analytics practice
- transparent decision-memo design

Not recommended:

- restricting access to medicines or diagnostics
- deprioritizing countries only because they are costly to serve
- bypassing procurement law or anti-corruption controls
- hiding stockout or delivery-risk information
- optimizing military/coercive logistics harm
- replacing humanitarian, clinical, or legal review

The dangerous failure mode is treating a cheaper plan as automatically better. In health and humanitarian logistics, cost optimization must be subordinate to patient access, equity, safety, legal obligations, and resilience.

## Inherent Limits

- SCMS data is historical and incomplete for operational planning.
- Some country names are mojibake in the raw Kaggle file; the script repairs the common case for readable reports, but this is not a full localization or master-data process.
- The dataset lacks real-time demand, inventory, supplier capacity, route disruption, cold-chain requirements, customs risk, and patient impact.
- Historical freight cost may include hidden procurement rules or exceptional circumstances.
- Greedy optimization is transparent but not globally optimal.
- This is a portfolio practice dry run, not an end product.

## Next Extensions

1. Replace greedy assignment with MILP/LP solver after business rules are stable.
2. Add supplier capacity and minimum-service constraints.
3. Add cold-chain and product criticality constraints.
4. Add equity constraints for countries with weak historical service.
5. Add stochastic disruption scenarios.
6. Add sensitivity analysis for late-delivery penalty and reliability penalty.
