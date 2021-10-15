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

STEPS_PARIS = [('Plan length: [^\n ]*', 'PLAN_STEPS')]

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


def collect(argv):
    system, results_file, domain, instance, stdo_str, stde_str, solution_str, validated = get_data(argv)

    if solution_str == NO_SOLUTION:
        results_dict = manage_no_solution(instance, domain, system)
        find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)
    else:
        results_dict = {}

        save_domain_instance_system_validation(results_dict, system, domain, instance, validated)

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
