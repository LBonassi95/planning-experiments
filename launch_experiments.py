import json
import os
import os.path as path
import sys
import random
import datetime

from constants import NAME, RUNS, PLANNERS_X_DOMAINS, PATH_TO_DOMAINS, DOMAINS, DOMAIN_INSTANCES_ERROR, PATH_TO_RESULTS, \
    TIME, MEMORY, COMPILER, SHELL_TEMPLATE, RM_CMD, CONFIGS, PLANNER_EXE_INSTANCE, PLANNER_EXE_SOLUTION, PLANNER_EXE_DOMAIN

CFG_PLANNER_ERROR1 = 'ERROR! configurations file for {} not found'
CFG_PLANNER_ERROR2 = 'ERROR! configuration {} for {} not found'


def collect_instances(path_to_domains, domain):
    instances_path = path.join(path_to_domains, domain)
    print(instances_path)
    pddl_domains = []
    pddl_instances = []
    for file in os.listdir(instances_path):
        if '.pddl' in file:
            if 'domain' in file:
                pddl_domains.append(file)
            else:
                pddl_instances.append(file)
    if len(pddl_domains) != 1 and len(pddl_domains) != len(pddl_instances):
        raise Exception(DOMAIN_INSTANCES_ERROR)
    pddl_instances.sort()
    pddl_domains.sort()
    pairs = []
    for i in range(len(pddl_instances)):
        if len(pddl_domains) == 1:
            pairs.append((pddl_domains[0], pddl_instances[i]))
        else:
            test_soundness = pddl_domains[i].split('-')[1]
            assert test_soundness == pddl_instances[i]
            pairs.append((pddl_domains[i], pddl_instances[i]))
    return pairs


def collect_runs(run_dict, path_to_domains):
    for planner in run_dict.keys():
        compiler = run_dict[planner][COMPILER]  # Ignored for now
        domains = run_dict[planner][DOMAINS]
        run_dict[planner][RUNS] = {}
        for domain in domains:
            runs = collect_instances(path_to_domains, domain)
            run_dict[planner][RUNS][domain] = runs


def old_scripts_cleanup(name):
    # Clean old scripts with the same name
    script_folder = path.join('scripts', name)
    if path.isdir(script_folder):
        os.system(RM_CMD.format(script_folder))
    os.mkdir(script_folder)
    #######################################


def create_results_folder(name, exp_id, planner, config, domain):
    top_level_folder = path.join('results', name)
    if not path.isdir(top_level_folder):
        os.mkdir(top_level_folder)

    results_folder = path.join(top_level_folder, "RUN_{}".format(exp_id))
    if not path.isdir(results_folder):
        os.mkdir(results_folder)

    results_folder_planner = path.join(results_folder, '{}_{}'.format(planner, config))
    if not path.isdir(results_folder_planner):
        os.mkdir(results_folder_planner)

    results_folder_planner_domain = path.join(results_folder_planner, domain)
    os.mkdir(results_folder_planner_domain)

    return results_folder_planner_domain


def create_scripts(name, exp_id, run_dict, memory, time):
    old_scripts_cleanup(name)

    for planner in run_dict.keys():
        cfg_path = path.join('planners', planner, 'cfg_map.json')
        if not path.isfile(cfg_path):
            raise Exception(CFG_PLANNER_ERROR1.format(planner))
        cfg_map = json.load(open(cfg_path,))
        for config in run_dict[planner][CONFIGS]:
            for domain in run_dict[planner][RUNS].keys():
                solution_folder = create_results_folder(name, exp_id, planner, config, domain)
                for pddl_domain, pddl_instance in run_dict[planner][RUNS][domain]:

                    script_name = '{}_{}_{}_{}_{}.sh'.format(name, planner, config, domain, pddl_instance.replace('.pddl', ''))
                    script_str = SHELL_TEMPLATE
                    if config not in cfg_map:
                        raise Exception(CFG_PLANNER_ERROR2.format(config, planner))
                    command_template = cfg_map[config]

                    solution_name = '{}_{}.sol'.format(domain, pddl_instance.replace('.pddl', ''))
                    planner_exe = command_template.replace(PLANNER_EXE_DOMAIN, pddl_domain)\
                        .replace(PLANNER_EXE_INSTANCE, pddl_instance)\
                        .replace(PLANNER_EXE_SOLUTION, path.join(solution_folder, solution_name))



                    script_str = script_str.format(memory=memory)
                    print(script_name)


def main(args):
    cfg = args[1]
    cfg_dict = json.load(open(cfg, ))
    name = cfg_dict[NAME]
    exp_id = str(datetime.datetime.now()).replace(' ', '_') + '_{}'.format(str(random.randint(0, sys.maxsize)))
    path_to_domains = cfg_dict[PATH_TO_DOMAINS]
    run_dict = cfg_dict[PLANNERS_X_DOMAINS]
    memory = cfg_dict[MEMORY]
    time = cfg_dict[TIME]

    collect_runs(run_dict, path_to_domains)

    create_scripts(name, exp_id, run_dict, memory, time)


if __name__ == '__main__':
    main(sys.argv)
