#!/usr/bin/env python3
"""Minimal logistics decision optimization dry run."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = {
    "Country",
    "Shipment Mode",
    "Vendor",
    "Product Group",
    "Line Item Value",
    "Weight (Kilograms)",
    "Freight Cost (USD)",
    "Scheduled Delivery Date",
    "Delivered to Client Date",
}


@dataclass(frozen=True)
class Record:
    country: str
    product_group: str
    mode: str
    vendor: str
    weight: float
    value: float
    freight: float
    late_days: int
    on_time: int


@dataclass(frozen=True)
class Candidate:
    country: str
    product_group: str
    mode: str
    vendor: str
    n: int
    demand_weight: float
    historical_weight: float
    total_value: float
    cost_per_kg: float
    avg_late_days: float
    on_time_rate: float


@dataclass
class Assignment:
    lane: tuple[str, str]
    candidate: Candidate
    demand_weight: float
    objective: float
    estimated_cost: float
    violation: str


@dataclass
class Plan:
    name: str
    assignments: list[Assignment]
    objective: float
    estimated_cost: float
    weighted_late_days: float
    weighted_on_time: float
    air_share: float
    largest_vendor_share: float
    violations: list[str]


def read_records(path: Path, max_rows: int | None = None) -> tuple[list[Record], list[str]]:
    errors: list[str] = []
    records: list[Record] = []
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [], ["CSV has no header row."]
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            errors.append(f"Missing columns: {', '.join(sorted(missing))}.")
        for index, row in enumerate(reader):
            if max_rows is not None and index >= max_rows:
                break
            record = parse_record(row)
            if record is not None:
                records.append(record)

    if not records:
        errors.append("No usable shipment records loaded.")
    return records, errors


def parse_record(row: dict[str, str]) -> Record | None:
    country = clean_text(row.get("Country", ""))
    product_group = clean_text(row.get("Product Group", ""))
    mode = clean_text(row.get("Shipment Mode", ""))
    vendor = clean_text(row.get("Vendor", ""))
    weight = parse_number(row.get("Weight (Kilograms)", ""))
    value = parse_number(row.get("Line Item Value", ""))
    freight = parse_number(row.get("Freight Cost (USD)", ""))
    scheduled = parse_date(row.get("Scheduled Delivery Date", ""))
    delivered = parse_date(row.get("Delivered to Client Date", ""))
    if not country or not product_group or not mode or not vendor:
        return None
    if mode.upper() in {"N/A", "NA", "UNKNOWN", "NOT CAPTURED"}:
        return None
    if weight is None or value is None or freight is None or weight <= 0 or freight <= 0:
        return None
    late_days = 0
    on_time = 1
    if scheduled and delivered:
        late_days = max(0, (delivered - scheduled).days)
        on_time = int(late_days == 0)
    return Record(country, product_group, mode, vendor, weight, value, freight, late_days, on_time)


def clean_text(value: str) -> str:
    text = str(value or "").strip()
    for _ in range(2):
        if "Ã" not in text and "Â" not in text:
            break
        try:
            repaired = text.encode("latin1").decode("utf-8")
        except UnicodeError:
            break
        if repaired == text:
            break
        text = repaired
    return " ".join(text.split())


def parse_number(value: str) -> float | None:
    text = str(value or "").strip().replace(",", "").replace("$", "")
    if not text or any(token in text.lower() for token in ["freight included", "separately", "not captured"]):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_date(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text or "not captured" in text.lower() or "pre-pq" in text.lower():
        return None
    for fmt in ["%d-%b-%y", "%d-%b-%Y", "%m/%d/%Y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def build_candidates(records: list[Record], min_history: int) -> list[Candidate]:
    grouped: dict[tuple[str, str, str, str], list[Record]] = defaultdict(list)
    for record in records:
        grouped[(record.country, record.product_group, record.mode, record.vendor)].append(record)

    candidates = []
    for (country, product_group, mode, vendor), rows in grouped.items():
        if len(rows) < min_history:
            continue
        total_weight = sum(row.weight for row in rows)
        if total_weight <= 0:
            continue
        candidates.append(
            Candidate(
                country=country,
                product_group=product_group,
                mode=mode,
                vendor=vendor,
                n=len(rows),
                demand_weight=total_weight,
                historical_weight=total_weight,
                total_value=sum(row.value for row in rows),
                cost_per_kg=sum(row.freight for row in rows) / total_weight,
                avg_late_days=statistics.mean(row.late_days for row in rows),
                on_time_rate=statistics.mean(row.on_time for row in rows),
            )
        )
    return candidates


def build_lanes(candidates: list[Candidate], max_lanes: int) -> list[tuple[tuple[str, str], float, float]]:
    lane_rows: dict[tuple[str, str], list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        lane_rows[(candidate.country, candidate.product_group)].append(candidate)
    lanes = []
    for lane, rows in lane_rows.items():
        lanes.append((lane, sum(row.historical_weight for row in rows), sum(row.total_value for row in rows)))
    return sorted(lanes, key=lambda item: item[2], reverse=True)[:max_lanes]


def candidate_objective(candidate: Candidate, demand_weight: float, late_penalty: float, reliability_penalty: float) -> float:
    cost = demand_weight * candidate.cost_per_kg
    late = demand_weight * candidate.avg_late_days * late_penalty
    unreliable = demand_weight * (1 - candidate.on_time_rate) * reliability_penalty
    return cost + late + unreliable


def choose_plan(
    name: str,
    lanes: list[tuple[tuple[str, str], float, float]],
    candidates: list[Candidate],
    strategy: str,
    vendor_cap: float,
    air_cap: float,
    late_penalty: float,
    reliability_penalty: float,
) -> Plan:
    candidates_by_lane: dict[tuple[str, str], list[Candidate]] = defaultdict(list)
    for candidate in candidates:
        candidates_by_lane[(candidate.country, candidate.product_group)].append(candidate)

    total_weight = sum(weight for _, weight, _ in lanes)
    vendor_load: Counter[str] = Counter()
    air_load = 0.0
    assignments: list[Assignment] = []
    violations: list[str] = []

    for lane, demand_weight, _ in sorted(lanes, key=lambda item: item[1], reverse=True):
        options = candidates_by_lane.get(lane, [])
        if not options:
            violations.append(f"No candidate for {lane[0]} / {lane[1]}.")
            continue
        ordered = sorted(
            options,
            key=lambda candidate: strategy_key(candidate, strategy, demand_weight, late_penalty, reliability_penalty),
        )
        chosen = None
        violation = ""
        for candidate in ordered:
            vendor_ok = vendor_load[candidate.vendor] + demand_weight <= total_weight * vendor_cap
            air_ok = not is_air_mode(candidate.mode) or air_load + demand_weight <= total_weight * air_cap
            if strategy != "constrained" or (vendor_ok and air_ok):
                chosen = candidate
                break
        if chosen is None:
            chosen = min(ordered, key=lambda candidate: violation_penalty(candidate, demand_weight, vendor_load, air_load, total_weight, vendor_cap, air_cap))
            parts = []
            if vendor_load[chosen.vendor] + demand_weight > total_weight * vendor_cap:
                parts.append("vendor-cap")
            if is_air_mode(chosen.mode) and air_load + demand_weight > total_weight * air_cap:
                parts.append("air-cap")
            violation = "+".join(parts) or "constraint-relaxed"
            violations.append(f"{lane[0]} / {lane[1]} required relaxed constraint: {violation}.")

        vendor_load[chosen.vendor] += demand_weight
        if is_air_mode(chosen.mode):
            air_load += demand_weight
        objective = candidate_objective(chosen, demand_weight, late_penalty, reliability_penalty)
        assignments.append(Assignment(lane, chosen, demand_weight, objective, demand_weight * chosen.cost_per_kg, violation))

    return summarize_plan(name, assignments, total_weight, violations)


def strategy_key(candidate: Candidate, strategy: str, demand_weight: float, late_penalty: float, reliability_penalty: float) -> tuple[float, float]:
    if strategy == "dominant":
        return (-candidate.n, candidate.cost_per_kg)
    if strategy == "cheapest":
        return (candidate.cost_per_kg, candidate.avg_late_days)
    return (candidate_objective(candidate, demand_weight, late_penalty, reliability_penalty), candidate.cost_per_kg)


def violation_penalty(
    candidate: Candidate,
    demand_weight: float,
    vendor_load: Counter[str],
    air_load: float,
    total_weight: float,
    vendor_cap: float,
    air_cap: float,
) -> float:
    vendor_excess = max(0.0, vendor_load[candidate.vendor] + demand_weight - total_weight * vendor_cap)
    air_excess = max(0.0, air_load + demand_weight - total_weight * air_cap) if is_air_mode(candidate.mode) else 0.0
    return vendor_excess * 2 + air_excess + candidate.cost_per_kg


def summarize_plan(name: str, assignments: list[Assignment], total_weight: float, violations: list[str]) -> Plan:
    objective = sum(item.objective for item in assignments)
    cost = sum(item.estimated_cost for item in assignments)
    weighted_late_days = safe_div(sum(item.demand_weight * item.candidate.avg_late_days for item in assignments), total_weight)
    weighted_on_time = safe_div(sum(item.demand_weight * item.candidate.on_time_rate for item in assignments), total_weight)
    air_share = safe_div(sum(item.demand_weight for item in assignments if is_air_mode(item.candidate.mode)), total_weight)
    vendor_weights: Counter[str] = Counter()
    for item in assignments:
        vendor_weights[item.candidate.vendor] += item.demand_weight
    largest_vendor_share = safe_div(max(vendor_weights.values()) if vendor_weights else 0.0, total_weight)
    return Plan(name, assignments, objective, cost, weighted_late_days, weighted_on_time, air_share, largest_vendor_share, violations)


def is_air_mode(mode: str) -> bool:
    return "air" in mode.lower()


def cap_flags(plan: Plan, vendor_cap: float, air_cap: float) -> list[str]:
    flags = []
    if plan.largest_vendor_share > vendor_cap:
        flags.append("vendor-cap")
    if plan.air_share > air_cap:
        flags.append("air-cap")
    return flags


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def fmt(value: float) -> str:
    return f"{value:,.2f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_report(
    records: list[Record],
    errors: list[str],
    min_history: int,
    max_lanes: int,
    vendor_cap: float,
    air_cap: float,
    stress_air_cap: float,
    late_penalty: float,
    reliability_penalty: float,
    top_rows: int,
) -> str:
    lines = ["# Decision Optimization Memo", ""]
    if errors:
        lines.extend(["## Input Validation", ""])
        lines.extend(f"- BREACH: {error}" for error in errors)
        return "\n".join(lines) + "\n"

    candidates = build_candidates(records, min_history)
    lanes = build_lanes(candidates, max_lanes)
    dominant = choose_plan("Historical dominant", lanes, candidates, "dominant", vendor_cap, air_cap, late_penalty, reliability_penalty)
    cheapest = choose_plan("Cheapest historical option", lanes, candidates, "cheapest", vendor_cap, air_cap, late_penalty, reliability_penalty)
    constrained = choose_plan("Constrained service-cost plan", lanes, candidates, "constrained", vendor_cap, air_cap, late_penalty, reliability_penalty)
    stress = choose_plan("Air-capacity stress plan", lanes, candidates, "constrained", vendor_cap, stress_air_cap, late_penalty, reliability_penalty)

    lines.extend(
        [
            "## Executive Summary",
            "",
            f"- Usable shipment records: {len(records):,}",
            f"- Candidate options: {len(candidates):,}",
            f"- Planned country/product lanes: {len(lanes)}",
            f"- Vendor concentration cap: {pct(vendor_cap)}",
            f"- Air capacity cap: {pct(air_cap)}",
            f"- Stress air capacity cap: {pct(stress_air_cap)}",
            "- Scope: practice dry run for portfolio learning, not a production procurement or humanitarian logistics system.",
            "",
            "## Input Validation",
            "",
            "- PASS: required shipment, vendor, mode, cost, weight, and delivery columns are present.",
            "- PASS: rows with unusable cost, weight, date, or unknown shipment-mode fields are excluded from candidate generation.",
            "- PASS: optimization uses historical aggregate candidates, not direct operational commitments.",
            "",
            "## Ethical And Operational Use",
            "",
            "- Use for learning, scenario planning, and decision-support design only.",
            "- Do not use to restrict medical access, deprioritize vulnerable countries, or hide supply disruption.",
            "- Do not bypass procurement rules, anti-corruption controls, sanctions screening, or supplier due diligence.",
            "- Do not optimize military or coercive logistics harm from this dry run.",
            "- Human review must override the objective when equity, safety, clinical urgency, or legal duties require it.",
            "",
            "## Objective And Constraints",
            "",
            "- Decision: choose one historical vendor/mode candidate for each country/product lane.",
            "- Objective: freight cost + late-delivery penalty + unreliable-service penalty.",
            "- Constraints: vendor concentration cap and air-shipment weight share cap.",
            "- Infeasibility handling: if no option satisfies constraints for a lane, the report marks the relaxed constraint.",
            "",
            "## Plan Comparison",
            "",
            "| Plan | Objective | Est. Freight Cost | Weighted Late Days | Weighted On-Time | Air Share | Largest Vendor Share | Relaxed Lanes | Cap Flags |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for plan in [dominant, cheapest, constrained, stress]:
        flags = ", ".join(cap_flags(plan, vendor_cap, stress_air_cap if plan is stress else air_cap)) or "-"
        lines.append(
            f"| {plan.name} | {fmt(plan.objective)} | {fmt(plan.estimated_cost)} | "
            f"{fmt(plan.weighted_late_days)} | {pct(plan.weighted_on_time)} | {pct(plan.air_share)} | "
            f"{pct(plan.largest_vendor_share)} | {len(plan.violations)} | {flags} |"
        )

    savings = dominant.estimated_cost - constrained.estimated_cost
    lines.extend(
        [
            "",
            "## Decision Read",
            "",
            f"- Estimated freight-cost delta vs historical dominant plan: {fmt(savings)}.",
            f"- Constrained-plan objective delta vs dominant: {fmt(dominant.objective - constrained.objective)}.",
            f"- Binding/relaxed constraints in constrained plan: {len(constrained.violations)}.",
            f"- Constrained aggregate cap flags: {', '.join(cap_flags(constrained, vendor_cap, air_cap)) or 'none'}.",
            f"- Stress plan adds {len(stress.violations) - len(constrained.violations)} additional relaxed constraints vs normal constrained plan.",
        ]
    )

    lines.extend(["", "## Recommended Plan", ""])
    lines.append(f"_Showing top {min(top_rows, len(constrained.assignments))} of {len(constrained.assignments)} lane decisions._")
    lines.extend(
        [
            "",
            "| Lane | Demand Kg | Mode | Vendor | Cost/Kg | Late Days | On-Time | Est. Cost | Violation |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for item in sorted(constrained.assignments, key=lambda assignment: assignment.estimated_cost, reverse=True)[:top_rows]:
        candidate = item.candidate
        lane = f"{candidate.country} / {candidate.product_group}"
        lines.append(
            f"| {lane} | {fmt(item.demand_weight)} | {candidate.mode} | {candidate.vendor} | "
            f"{fmt(candidate.cost_per_kg)} | {fmt(candidate.avg_late_days)} | {pct(candidate.on_time_rate)} | "
            f"{fmt(item.estimated_cost)} | {item.violation or '-'} |"
        )

    if constrained.violations or stress.violations:
        lines.extend(["", "## Constraint Notes", ""])
        lines.append("Normal constrained plan:")
        for note in constrained.violations[:8]:
            lines.append(f"- {note}")
        lines.append("")
        lines.append("Air-capacity stress plan:")
        for note in stress.violations[:8]:
            lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "## Analyst Actions",
            "",
            "- Review any lane with relaxed vendor or air-capacity constraints before accepting the plan.",
            "- Check clinical/humanitarian urgency before choosing a cheaper or slower mode.",
            "- Validate supplier eligibility, anti-corruption controls, sanctions screening, and cold-chain requirements outside this script.",
            "- Run stress scenarios before committing procurement or inventory policy.",
            "- Treat the output as a decision memo, not an autonomous optimizer.",
            "",
            "## Inherent Limits",
            "",
            "- This is a narrow practice dry run using historical SCMS shipment data.",
            "- The dataset does not contain real-time demand, stockouts, patient impact, procurement law, supplier capacity, cold-chain constraints, or route disruption data.",
            "- Historical lowest cost may encode bad service quality, missing context, or inequitable allocation.",
            "- The greedy constraint solver is transparent but not a full MILP/LP solver.",
            "- Good-looking cost savings here do not imply a safe, ethical, or legally valid logistics plan.",
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    records, errors = read_records(args.input, args.max_rows)
    report = build_report(
        records,
        errors,
        args.min_history,
        args.max_lanes,
        args.vendor_cap,
        args.air_cap,
        args.stress_air_cap,
        args.late_penalty,
        args.reliability_penalty,
        args.top_rows,
    )
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote {args.output}")
    if errors:
        print(f"Validation errors: {len(errors)}")
        return 2
    print(f"Usable shipment records: {len(records)}")
    print(f"Candidate options: {len(build_candidates(records, args.min_history))}")
    return 0


def self_test() -> int:
    rows = [
        Record("A", "ARV", "Air", "V1", 10, 100, 100, 0, 1),
        Record("A", "ARV", "Air", "V1", 10, 100, 110, 1, 0),
        Record("A", "ARV", "Sea", "V2", 10, 100, 30, 10, 0),
        Record("A", "ARV", "Sea", "V2", 10, 100, 35, 12, 0),
        Record("B", "HRDT", "Truck", "V3", 5, 50, 20, 0, 1),
        Record("B", "HRDT", "Truck", "V3", 5, 50, 25, 0, 1),
    ]
    candidates = build_candidates(rows, 2)
    assert len(candidates) == 3
    lanes = build_lanes(candidates, 5)
    plan = choose_plan("test", lanes, candidates, "constrained", 0.8, 0.8, 5, 20)
    assert plan.assignments
    assert plan.estimated_cost > 0
    assert parse_number("1,234.50") == 1234.5
    assert parse_date("2-Jun-06") is not None
    print("Self-tests passed.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a minimal logistics decision memo.")
    parser.add_argument("input", nargs="?", type=Path, default=Path("kaggle_raw/Raw_Data.csv"))
    parser.add_argument("--output", type=Path, default=Path("decision_memo.md"))
    parser.add_argument("--min-history", type=int, default=3)
    parser.add_argument("--max-lanes", type=int, default=18)
    parser.add_argument("--vendor-cap", type=float, default=0.35)
    parser.add_argument("--air-cap", type=float, default=0.45)
    parser.add_argument("--stress-air-cap", type=float, default=0.20)
    parser.add_argument("--late-penalty", type=float, default=2.0)
    parser.add_argument("--reliability-penalty", type=float, default=18.0)
    parser.add_argument("--top-rows", type=int, default=25)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        return self_test()
    if args.min_history <= 0 or args.max_lanes <= 0 or args.top_rows <= 0:
        print("--min-history, --max-lanes, and --top-rows must be positive", file=sys.stderr)
        return 2
    for name in ["vendor_cap", "air_cap", "stress_air_cap"]:
        value = getattr(args, name)
        if not 0 < value <= 1:
            print(f"--{name.replace('_', '-')} must be in (0, 1]", file=sys.stderr)
            return 2
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
