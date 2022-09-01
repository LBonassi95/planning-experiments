#!/usr/bin/env python3

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

LTLexpINFO = [('Total No. of states = [^\n]*', 'LTL_EXP_STATES')]

LTLexpCOMP_TIME = [('CPU time: [^\n]*', 'LTL_EXP_COMP_TIME')]

LTLpolyCOMP_TIME_1 = [('Translation CPU time: [^\n]*', 'LTL_POLY_COMP_TIME_1')]
LTLpolyCOMP_TIME_2 = [('ToPddl CPU time: [^\n]*', 'LTL_POLY_COMP_TIME_2')]

FD_PREPROCESSOR_PAIRS = [('Done! [^\n]*', 'FD_PREPROCESSOR_RUNTIME')]

STEPS_PARIS = [('Plan length: [^\n ]*', 'FD_PLAN_STEPS')]

STDE_PAIRS = [('Total Runtime: [^\n ]*', 'TOTALRUNTIME'), ('Compilation Time: [^\n ]*', 'COMPILATION_TIME'), ('Total FD Time: [^\n ]*', 'TOTAL_FD_TIME')]

SEARCH_TIME_PAIRS = [('Total time: [^\n]*', 'FD_SEARCH_TIME')]

STATE_INFO_PAIRS = [('Expanded [^\n ]*', 'FD_EXPANDED_NODES')]

MEMORY_ERROR = [('MemoryError', 'MEMORY-ERROR')]


# Actual search time: 50.5164s [t=51.095s]

def memory_error(string):
    return 'MEMORY-ERROR'


def clean_overhead(string):
    return float(string.split(':')[1].strip())


def clean_fd_preprocessing_time(string):
    # Done! [0.030s CPU, 0.032s wall-clock]
    return float(string.split(',')[1].split('s')[0].strip())


def clean_fd_search_time(string):
    return float(string.split(':')[1].split('s')[0].strip())


def clean_fd_state_info(string):
    # Expanded 14 state(s).
    return int(string.replace('Expanded', '').replace('state(s).', ''))


def clean_fd(string):
    return int(string.split(':')[1].split('step')[0].strip())


def clean_total_runtime(string):
    return float(string.split(':')[1].strip())


def clean_ltlexp_states(string):
    return float(string.split('=')[1].strip())


def clean_ltlexp_comp_time(string):
    # CPU time: 0.797829657, Number of Inferences: 3502958
    return float(string.split(',')[0].split(':')[1].strip())


def sort_fd_sol(sol_name):
    return int(sol_name.split('.')[len(sol_name.split('.'))-1])


def get_solution_function(solution_path):
    solutions = []

    path_sol = os.path.dirname(solution_path)
    basename_sol = os.path.basename(solution_path)

    for file in os.listdir(path_sol):
        if file.startswith(basename_sol):
            solutions.append(file)

    solution_tuples = []
    if len(solutions) > 1:
        solutions.sort(key=sort_fd_sol)
    for solution in solutions:
        with open(os.path.join(path_sol, solution), 'r') as sol_in:
            sol_str = sol_in.read()

        splitted_sol = sol_str.split('\n')
        new_plan_actions = [action.replace('__', ' ') for action in splitted_sol]
        new_plan_actions = [a for a in new_plan_actions if 'o_copy' not in a and 'o_sync' not in a and 'o_world' not in a and 'o_goal' not in a and 'achieve-goal' not in a and 'sync' not in a and 'reach-goal' not in a]
        str_sol = '\n'.join(new_plan_actions)

        clean_path = os.path.join(path_sol, 'clean_{}'.format(solution))

        with open(clean_path, 'w') as fout:
            fout.write(str_sol)

        solution_tuples.append((solution, str_sol, clean_path))
    return solution_tuples


def collect(argv):
    data_array = get_data(argv, get_solution_function)

    n = 0
    for (system, results_file, domain, instance, stdo_str, stde_str, solution_str, sol_name, validated, validator_value) in data_array:
        if solution_str == NO_SOLUTION:
            results_dict = manage_no_solution(instance, domain, system)
            find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)
            if 'ltlexp' in system:
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLexpCOMP_TIME, cleanup_function=clean_ltlexp_comp_time)
            if 'ltlpoly' in system:
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLpolyCOMP_TIME_1, cleanup_function=clean_ltlexp_comp_time)
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLpolyCOMP_TIME_2, cleanup_function=clean_ltlexp_comp_time)
        else:
            results_dict = {}

            save_domain_instance_system_validation(results_dict, system, domain, instance, sol_name, validated, validator_value)

            find_and_save_from_regex_single_match(results_dict, stdo_str, OVERHEAD_PAIRS, cleanup_function=clean_overhead)
            find_and_save_from_regex_single_match(results_dict, stdo_str, INFO_PAIRS, cleanup_function=clean_overhead)
            find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)
            find_and_save_from_regex_single_match(results_dict, stdo_str, LTLexpINFO, cleanup_function=clean_ltlexp_states)
            if 'ltlexp' in system:
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLexpCOMP_TIME, cleanup_function=clean_ltlexp_comp_time)
            if 'ltlpoly' in system:
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLpolyCOMP_TIME_1, cleanup_function=clean_ltlexp_comp_time)
                find_and_save_from_regex_single_match(results_dict, stdo_str, LTLpolyCOMP_TIME_2, cleanup_function=clean_ltlexp_comp_time)
            find_and_save_from_regex_single_match(results_dict, stdo_str, FD_PREPROCESSOR_PAIRS,
                                                  cleanup_function=clean_fd_preprocessing_time)
            find_and_save_from_regex(results_dict, stdo_str, STEPS_PARIS, n, cleanup_function=clean_fd)
            find_and_save_from_regex(results_dict, stdo_str, SEARCH_TIME_PAIRS, n, cleanup_function=clean_fd_search_time)
            find_and_save_from_regex(results_dict, stdo_str, STATE_INFO_PAIRS, n,
                                     cleanup_function=clean_fd_state_info)
            find_and_save_from_regex_single_match(results_dict, stdo_str, MEMORY_ERROR, cleanup_function=memory_error)

        write_results(results_dict, results_file)
        n = n + 1


if __name__ == '__main__':
    collect(sys.argv)
