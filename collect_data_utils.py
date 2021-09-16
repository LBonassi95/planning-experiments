import re

NO_MATCH = '#NOMATCH#'


def get_data(args):
    results_file = args[1]
    solution_file = args[2]
    instance = args[3]
    domain = args[4]
    stdo = args[5]
    stde = args[6]

    with open(solution_file, 'r') as solution_read:
        solution_str = solution_read.read()

    with open(stdo, 'r') as stdo_read:
        stdo_str = stdo_read.read()

    with open(stde, 'r') as stde_read:
        stde_str = stde_read.read()

    return results_file, domain, instance, stdo_str, stde_str, solution_str


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
