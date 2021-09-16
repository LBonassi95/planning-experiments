import fcntl
import sys
import json
from collect_data_utils import *


OVERHEAD_PAIRS = [('\[PRECONDITION-OVERHEAD\]: [^\n ]*', 'PRECONDITION_OVERHEAD'),
                  ('\[EFFECT-OVERHEAD\]: [^\n ]*', 'EFFECT-OVERHEAD'),
                  ('\[ATOMS-OVERHEAD\]: [^\n ]*', 'ATOMS-OVERHEAD')]

STDE_PAIRS = [('Total Runtime: [^\n ]*', 'TOTALRUNTIME')]


def clean_overhead(string):
    return int(string.split(':')[1].strip())


def clean_total_runtime(string):
    return float(string.split(':')[1].strip())


def collect(argv):
    results_file, domain, instance, stdo_str, stde_str, solution_str = get_data(argv)

    results_dict = {}

    save_domain_instance(results_dict, domain, instance)

    find_and_save_from_regex_single_match(results_dict, stdo_str, OVERHEAD_PAIRS, cleanup_function=clean_overhead)
    find_and_save_from_regex_single_match(results_dict, stde_str, STDE_PAIRS, cleanup_function=clean_total_runtime)

    write_results(results_dict, results_file)


if __name__ == '__main__':
    collect(sys.argv)
