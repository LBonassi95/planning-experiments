import fcntl
import sys
import json
from collect_data_utils import *


OVERHEAD_PAIRS = [('\[PRECONDITION-OVERHEAD\]: [^\n ]*', 'PRECONDITION_OVERHEAD'),
                  ('\[EFFECT-OVERHEAD\]: [^\n ]*', 'EFFECT-OVERHEAD'),
                  ('\[ATOMS-OVERHEAD\]: [^\n ]*', 'ATOMS-OVERHEAD')]


def clean_overhead(string):
    return int(string.split(':')[1].strip())


def collect(argv):
    results_file, domain, instance, stdo_str, stde_str, solution_str = get_data(argv)

    results_dict = {}

    find_and_save_from_regex_single_match(results_dict, stdo_str, OVERHEAD_PAIRS, cleanup_function=clean_overhead)

    results_dict['INSTANCE'] = instance
    results_dict['DOMAIN'] = domain
    string = json.dumps(results_dict)

    with open(results_file, 'a') as fout:
        fcntl.flock(fout, fcntl.LOCK_EX)
        fout.write(string + '\n')
        fcntl.flock(fout, fcntl.LOCK_UN)


if __name__ == '__main__':
    collect(sys.argv)
