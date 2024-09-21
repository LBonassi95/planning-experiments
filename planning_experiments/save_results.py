import sys
import json
import fcntl
import os
from planning_experiments.constants import *


def save_results(results_file, system, domain, instance):
    file = open(results_file, "r+")

    fcntl.flock(file, fcntl.LOCK_EX)

    json_data = json.load(file)

    try:
        stdo_path = json_data[system][domain][instance][STDO]
        stde_path = json_data[system][domain][instance][STDE]

        stdo_str = open(stdo_path, 'r').read()
        stde_str = open(stde_path, 'r').read()

        # ACQUIRE SOLUTIONS
        n_solutuions = 0
        solutions = []
        for sol_file in os.listdir(json_data[system][domain][instance][SOLUTION_PATH]):
            if '.sol' in sol_file:
                n_solutuions += 1
                solution_str = open(os.path.join(json_data[system][domain][instance][SOLUTION_PATH], sol_file), 'r').read()
                solutions.append(solution_str)

        json_data[system][domain][instance][SOLUTIONS] = solutions
        json_data[system][domain][instance][NUM_SOLUTIONS] = n_solutuions
        json_data[system][domain][instance][STDO] = stdo_str
        json_data[system][domain][instance][STDE] = stde_str

        
        file.seek(0)
        file.truncate()
        json.dump(json_data, file, indent=4)
        fcntl.flock(file, fcntl.LOCK_UN)
        file.close()

    except Exception as e:
        json_data[system][domain][instance][SOLUTIONS] = []
        json_data[system][domain][instance][NUM_SOLUTIONS] = -1
        json_data[system][domain][instance][STDO] = "RUN SKIPPED DUE TO AN UNEXPECTED ERROR"
        json_data[system][domain][instance][STDE] = "RUN SKIPPED DUE TO AN UNEXPECTED ERROR"

        
        file.seek(0)
        file.truncate()
        json.dump(json_data, file, indent=4)
        fcntl.flock(file, fcntl.LOCK_UN)
        file.close()