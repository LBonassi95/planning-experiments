import sys
from planning_experiments.constants import *


def save_results(results_file, system, domain, instance):
    import json
    import fcntl
    import os
    file = open(results_file, "r+")
    fcntl.flock(file, fcntl.LOCK_EX)
    json_data = json.load(file)

    try:
        stdo_path = json_data[system][domain][instance][STDO]
        stde_path = json_data[system][domain][instance][STDE]

        with open(stdo_path, 'r') as f:
            stdo_str = f.read()
        with open(stde_path, 'r') as f:
            stde_str = f.read()

        solutions = []
        for sol_file in os.listdir(json_data[system][domain][instance][SOLUTION_PATH]):
            if '.sol' in sol_file:
                with open(os.path.join(json_data[system][domain][instance][SOLUTION_PATH], sol_file), 'r') as f:
                    solutions.append(f.read())

        json_data[system][domain][instance][SOLUTIONS] = solutions
        json_data[system][domain][instance][NUM_SOLUTIONS] = len(solutions)
        json_data[system][domain][instance][STDO] = stdo_str
        json_data[system][domain][instance][STDE] = stde_str

    except Exception as e:
        json_data[system][domain][instance][SOLUTIONS] = []
        json_data[system][domain][instance][NUM_SOLUTIONS] = -1
        json_data[system][domain][instance][STDO] = "RUN SKIPPED DUE TO AN UNEXPECTED ERROR"
        json_data[system][domain][instance][STDE] = str(e)

    finally:
        file.seek(0)
        file.truncate()
        json.dump(json_data, file, indent=4)
        file.flush()
        fcntl.flock(file, fcntl.LOCK_UN)
        file.close()