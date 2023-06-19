import sys
import json
import fcntl
import os

def save_results(results_file, system, domain, instance):
    file = open(results_file, "r+")

    fcntl.flock(file, fcntl.LOCK_EX)

    json_data = json.load(file)

    stdo_path = json_data[system][domain][instance]['stdo']
    stde_path = json_data[system][domain][instance]['stde']

    stdo_str = open(stdo_path, 'r').read()
    stde_str = open(stde_path, 'r').read()

    # ACQUIRE SOLUTIONS
    n_solutuions = 0
    solutions = []
    for sol_file in os.listdir(json_data[system][domain][instance]['solution_path']):
        if '.sol' in sol_file:
            n_solutuions += 1
            solution_str = open(os.path.join(json_data[system][domain][instance]['solution_path'], sol_file), 'r').read()
            solutions.append(solution_str)

    json_data[system][domain][instance]['solutions'] = solutions
    json_data[system][domain][instance]['num_solutions'] = n_solutuions
    json_data[system][domain][instance]['stdo'] = stdo_str
    json_data[system][domain][instance]['stde'] = stde_str

    
    file.seek(0)
    file.truncate()
    json.dump(json_data, file, indent=4)
    fcntl.flock(file, fcntl.LOCK_UN)
    file.close()