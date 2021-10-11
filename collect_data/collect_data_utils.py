import re
import json
import fcntl
import os.path
import subprocess

TIME_SPENT_FF = 'time spent:'

STEP_FF = 'step'

VALIDATED = "VALIDATED"

NO_MATCH = '#NOMATCH#'
INSTANCE = 'INSTANCE'
DOMAIN = 'DOMAIN'
SYSTEM = 'SYSTEM'
NO_SOLUTION = 'NO_SOLUTION'
NO_VALIDATION_PERFORMED = 'NoValidationPerformed'
VAL_COMMAND = 'validate -v {} {} {}'
SUCCESSFUL_PLAN = 'Successful plans:'
FF = ['ff-x']


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
        val_res = NO_VALIDATION_PERFORMED
    else:
        with open(solution_file, 'r') as solution_read:
            solution_str = solution_read.read()

        if system in FF:
            solution_str = clean_ff_solution(solution_str)
            if solution_str != NO_SOLUTION:
                val_res = validate(val_info, solution_file)
            else:
                val_res = NO_VALIDATION_PERFORMED
        else:
            val_res = validate(val_info, solution_file)

    with open(stdo, 'r') as stdo_read:
        stdo_str = stdo_read.read()

    with open(stde, 'r') as stde_read:
        stde_str = stde_read.read()

    return system, results_file, domain, instance, stdo_str, stde_str, solution_str, val_res


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
        val_res = str(SUCCESSFUL_PLAN in stdout)
    return val_res


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


def save_domain_instance_system_validation(results_dict, system, domain, instance, validated):
    results_dict[INSTANCE] = instance
    results_dict[DOMAIN] = domain
    results_dict[SYSTEM] = system
    results_dict[VALIDATED] = validated


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


def clean_ff_solution(sol_str):
    if STEP_FF not in sol_str:
        return NO_SOLUTION
    else:
        start = sol_str.find(STEP_FF)
        end = sol_str.find(TIME_SPENT_FF)

        actions = sol_str[start:end]
        actions = actions.strip().split('\n')

        ok_actions = ['({})'.format(a.lower().replace('__', ' ').split(':')[1].strip()) for a in actions]
        return '\n'.join(ok_actions)

