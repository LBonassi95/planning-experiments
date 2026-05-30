import argparse
import csv
import os
import json
from pathlib import Path

from planning_experiments.constants import *


def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return ""


def read_solutions(sol_dir):
    solutions = []
    if not os.path.exists(sol_dir):
        return solutions

    for f in os.listdir(sol_dir):
        if f.endswith(".sol"):
            try:
                with open(os.path.join(sol_dir, f), "r") as file:
                    solutions.append(file.read())
            except Exception:
                continue
    return solutions


def aggregate_results(results_root):
    results_root = Path(results_root)

    blob = {}

    for system_dir in results_root.iterdir():
        if not system_dir.is_dir():
            continue

        planner = system_dir.name
        blob[planner] = {}

        for domain_dir in system_dir.iterdir():
            if not domain_dir.is_dir():
                continue

            domain = domain_dir.name
            blob[planner][domain] = {}

            for instance_dir in domain_dir.iterdir():
                if not instance_dir.is_dir():
                    continue

                problem = instance_dir.name

                stdo_path = instance_dir / f"out_{domain}_{problem}.txt"
                stde_path = instance_dir / f"err_{domain}_{problem}.txt"
                sol_dir = instance_dir / "solutions"

                stdo = stdo_path.read_text() if stdo_path.exists() else ""
                stde = stde_path.read_text() if stde_path.exists() else ""

                solutions = []
                if sol_dir.exists():
                    for f in sol_dir.iterdir():
                        if f.suffix == ".sol":
                            solutions.append(f.read_text())

                blob[planner][domain][problem] = {
                    "solutions": solutions,
                    "num_solutions": len(solutions),
                    "stdo": stdo,
                    "stde": stde,
                }

    return blob


def compute_status(entry: dict):
    if entry.get("num_solutions", None) is None:
        return "pending"

    elif entry.get("num_solutions") > 0:
        return "true"
    else:
        assert entry.get("num_solutions") == 0
        return "false"


def write_summary(blob, output_csv):
    rows = []

    for planner, domains in blob.items():
        for domain, problems in domains.items():
            for problem, entry in problems.items():

                status = compute_status(entry)

                rows.append([
                    domain,
                    problem,
                    planner,
                    status
                ])

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "problem", "planner", "solved"])
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--output-summary", required=False)

    args = parser.parse_args()
    blob = aggregate_results(args.input)

    if args.output_summary:
        write_summary(blob, args.output_summary)

    import json
    Path(args.output).write_text(json.dumps(blob, indent=4))


if __name__ == "__main__":
    main()