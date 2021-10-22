import sys
from collect_data_utils import *
import os

OVERHEAD_PAIRS = [('\[PRECONDITION-OVERHEAD\]: [^\n ]*', 'PRECONDITION-OVERHEAD'),
                  ('\[EFFECT-OVERHEAD\]: [^\n ]*', 'EFFECT-OVERHEAD'),
                  ('\[ATOMS-OVERHEAD\]: [^\n ]*', 'ATOMS-OVERHEAD')]

INFO_PAIRS = [('TOTAL-COMPILATION-RUNTIME: [^\n ]*', 'TOTAL-PCC-TCORE-RUNTIME'),
              ('PCC-TCORE-RUNTIME: [^\n ]*', 'PCC-TCORE-RUNTIME'),
              ('DONE-ACTION-ADDED: [^\n ]*', 'NUM-DONE-ACTION-ADDED'),
              ('DONE-ACTION-ADDED-IN: [^\n ]*', 'DONE-ACTION-RUNTIME'),
              ('PCC-RUNTIME: [^\n ]*', 'PCC-RUNTIME')]

STEPS_PARIS = [('Plan length: [^\n ]*', 'FD_PLAN_STEPS')]

STDE_PAIRS = [('Total Runtime: [^\n ]*', 'TOTALRUNTIME')]

SEARCH_TIME_PAIRS = [('Actual search time: [^\n ]*', 'LAMA_RUNTIME')]

MEMORY_ERROR = [('MemoryError', 'MEMORY-ERROR')]


# Actual search time: 50.5164s [t=51.095s]

def memory_error(string):
    return 'MEMORY-ERROR'


def clean_overhead(string):
    return float(string.split(':')[1].strip())


def clean_fd_search_time(string):
    return float(string.split(':')[1].split('s')[0].strip())


def clean_fd(string):
    return int(string.split(':')[1].split('step')[0].strip())


def clean_total_runtime(string):
    return float(string.split(':')[1].strip())


def get_solution_function(solution_path):
    if not os.path.exists(solution_path):
        return []

    with open(solution_path, 'r') as sol_in:
        sol_str = sol_in.read()

    splitted_sol = sol_str.split('\n')
    new_plan_actions = [action.replace('__', ' ') for action in splitted_sol]
    new_plan_actions = [a for a in new_plan_actions if 'o_copy' not in a and 'o_sync' not in a and 'o_world' not in a and 'o_goal' not in a]
    lifted_sol = '\n'.join(new_plan_actions)

    path_sol = os.path.dirname(solution_path)
    name_sol = os.path.basename(solution_path)

    lifted_path = os.path.join(path_sol, 'clean_{}'.format(name_sol))

    with open(lifted_path, 'w') as fout:
        fout.write(lifted_sol)

    return [(name_sol, lifted_sol, lifted_path)]


def collect(argv):
    data_array = get_data(argv, get_solution_function)
    assert len(data_array) == 1
    (system, results_file, domain, instance, stdo_str, stde_str, solution_str, sol_name, validated, validator_value) = data_array[0]
    if solution_str == NO_SOLUTION:
        results_dict = manage_no_solution(instance, domain, system)
        find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)
    else:
        results_dict = {}

        save_domain_instance_system_validation(results_dict, system, domain, instance, sol_name, validated, validator_value)

        find_and_save_from_regex_single_match(results_dict, stdo_str, OVERHEAD_PAIRS, cleanup_function=clean_overhead)
        find_and_save_from_regex_single_match(results_dict, stdo_str, INFO_PAIRS, cleanup_function=clean_overhead)
        find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)
        find_and_save_from_regex_single_match(results_dict, stdo_str, STEPS_PARIS, cleanup_function=clean_fd)
        find_and_save_from_regex_single_match(results_dict, stdo_str, SEARCH_TIME_PAIRS,
                                              cleanup_function=clean_fd_search_time)
        find_and_save_from_regex_single_match(results_dict, stdo_str, MEMORY_ERROR, cleanup_function=memory_error)

    write_results(results_dict, results_file)


if __name__ == '__main__':
    collect(sys.argv)
