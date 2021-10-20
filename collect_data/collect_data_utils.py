import re
import json
import fcntl
import os.path
import subprocess

import numpy as np

VALUE_VALIDATOR_REGEX = 'Value: [^\n ]*'

VALIDATED = "VALIDATED"

NO_MATCH = '#NOMATCH#'
INSTANCE = 'INSTANCE'
DOMAIN = 'DOMAIN'
SYSTEM = 'SYSTEM'
NO_SOLUTION = 'NO_SOLUTION'
NO_VALIDATION_PERFORMED = 'NoValidationPerformed'
VAL_COMMAND = 'validate -v {} {} {}'
SUCCESSFUL_PLAN = 'Successful plans:'
VALIDATOR_VALUE = "VALIDATOR_VALUE"
PLAN_LENGHT = "PLAN_LENGTH"

def get_data(args):
    system = args[1]
    results_file = args[2]
    solution_file = args[3]
    instance = args[4]
    domain = args[5]
    stdo = args[6]
    stde = args[7]
    val_info = args[8]

    if not os.path.exists(solution_file):
        solution_str = NO_SOLUTION
        plan_length = np.nan
        val_res = NO_VALIDATION_PERFORMED
        validator_value = np.nan
    else:
        with open(solution_file, 'r') as solution_read:
            solution_str = solution_read.read()
        plan_length = len(solution_str.strip().split('\n'))
        val_res, validator_value = validate(val_info, solution_file)

    with open(stdo, 'r') as stdo_read:
        stdo_str = stdo_read.read()

    with open(stde, 'r') as stde_read:
        stde_str = stde_read.read()

    return system, results_file, domain, instance, stdo_str, stde_str, solution_str, plan_length, val_res, validator_value


def validate(val_info, solution):
    if val_info == NO_VALIDATION_PERFORMED:
        val_res = NO_VALIDATION_PERFORMED
    else:
        domain4val = val_info.split('#')[0]
        instance4val = val_info.split('#')[1]
        print(VAL_COMMAND.format(domain4val, instance4val, solution))
        stdout, stderr = system_call(VAL_COMMAND.format(domain4val, instance4val, solution))
        # print stdout

        stdout = (stdout.decode('ascii'))
        print(stdout)
        val_res = SUCCESSFUL_PLAN in stdout
        if val_res:
            match = find_regex(VALUE_VALIDATOR_REGEX, stdout[stdout.find(SUCCESSFUL_PLAN):])
            assert len(match) == 1
            validator_value = int(match[0].split(':')[1].strip())
        else:
            validator_value = np.nan
    return str(val_res), validator_value


def find_regex(regex, string):
    matches = re.findall(regex, string, flags=re.DOTALL)
    return matches


def manage_no_solution(instance, domain, system):
    return {INSTANCE: instance, DOMAIN: domain, SYSTEM: system, 'SOLUTION': 'NO SOLUTION'}


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


def save_domain_instance_system_validation(results_dict, system, domain, instance, validated, plan_length, validator_value):
    results_dict[INSTANCE] = instance
    results_dict[DOMAIN] = domain
    results_dict[SYSTEM] = system
    results_dict[VALIDATED] = validated
    results_dict[VALIDATOR_VALUE] = validator_value
    results_dict[PLAN_LENGHT] = plan_length


def write_results(results_dict, results_file):
    string = json.dumps(results_dict)

    with open(results_file, 'a') as fout:
        fcntl.flock(fout, fcntl.LOCK_EX)
        fout.write(string + '\n')
        fcntl.flock(fout, fcntl.LOCK_UN)


def system_call(command):
    p = subprocess.Popen(
        [command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    return p.stdout.read(), p.stderr.read()
