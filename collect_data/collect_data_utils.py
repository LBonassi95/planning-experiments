import re
import json
import fcntl

NO_MATCH = '#NOMATCH#'
INSTANCE = 'INSTANCE'
DOMAIN = 'DOMAIN'
SYSTEM = 'SYSTEM'


def get_data(args):
    system = args[1]
    results_file = args[2]
    solution_file = args[3]
    instance = args[4]
    domain = args[5]
    stdo = args[6]
    stde = args[7]

    with open(solution_file, 'r') as solution_read:
        solution_str = solution_read.read()

    with open(stdo, 'r') as stdo_read:
        stdo_str = stdo_read.read()

    with open(stde, 'r') as stde_read:
        stde_str = stde_read.read()

    return system, results_file, domain, instance, stdo_str, stde_str, solution_str


def find_regex(regex, string):
    matches = re.findall(regex, string, flags=re.DOTALL)
    return matches


def find_and_save_from_regex_single_match(results_dict, string, regex_key_pairs, cleanup_function=None):
    for regex, dict_key in regex_key_pairs:
        match = find_regex(regex, string)
        if len(match) > 0:
            assert len(match) == 1
            if cleanup_function is None:
                results_dict[dict_key] = match
            else:
                match = cleanup_function(match[0])
                results_dict[dict_key] = match


def save_domain_instance_system(results_dict, system, domain, instance):
    results_dict[INSTANCE] = instance
    results_dict[DOMAIN] = domain
    results_dict[SYSTEM] = system


def write_results(results_dict, results_file):
    string = json.dumps(results_dict)

    with open(results_file, 'a') as fout:
        fcntl.flock(fout, fcntl.LOCK_EX)
        fout.write(string + '\n')
        fcntl.flock(fout, fcntl.LOCK_UN)