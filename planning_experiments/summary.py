import json
import pandas as pd
import re
from planning_experiments.constants import STDE, NUM_SOLUTIONS, SOLUTIONS

SYS = 'planner'
DOM = 'domain'
PROB = 'problem'
RT = 'runtime'
EN = 'expanded'
CT = 'comptime'
SOL = 'solved'
PL = 'quality'
NA = 'n/a'


def extract_float(text: str, regex: str):
    match = re.search(regex, text)
    if match:
        return float(match.group(1))
    else:
        return NA
        

def create_summary(blob_path, output_path):

    with open(blob_path, 'r') as f:
        blob = json.load(f)
    records = []

    for planner in blob.keys():
        for domain in blob[planner].keys():
            for instance in blob[planner][domain].keys():
                record = {SYS: planner, DOM: domain, PROB: instance}
                record[RT] = extract_float(blob[planner][domain][instance][STDE], r'real (.*)\n')
                record[SOL] = False
                record[PL] = NA

                if blob[planner][domain][instance].get(NUM_SOLUTIONS) is None:
                    print(f"Error while creating the summary for {planner} {domain} {instance}. Skipping")
                    record[SOL] = "N/A"

                elif blob[planner][domain][instance][NUM_SOLUTIONS] > 0:
                    record[SOL] = True
                    assert len(blob[planner][domain][instance][SOLUTIONS]) == 1
                records.append(record)

    df = pd.DataFrame.from_records(records)

    return df.to_csv(output_path, index=False)