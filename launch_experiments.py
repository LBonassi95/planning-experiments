import json
import os
import os.path as path
import sys
import random
import datetime

from constants import *


def collect_instances(path_to_domains, domain):
    instances_path = path.join(path_to_domains, domain)
    pddl_domains = []
    pddl_instances = []
    for file in os.listdir(instances_path):
        if PDDL_EXTENSION in file:
            if DOMAIN_STR_CONST in file:
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


def scripts_setup(name):
    # Clean old scripts with the same name
    script_folder = path.join(SCRIPTS_FOLDER, name)
    if path.isdir(script_folder):
        os.system(RM_CMD.format(script_folder))
    #######################################
    os.mkdir(script_folder)
    return script_folder


def create_results_folder(name, exp_id, planner, config, domain):
    top_level_folder = path.join(RESULTS_FOLDER, name)
    if not path.isdir(top_level_folder):
        os.mkdir(top_level_folder)

    results_folder = path.join(top_level_folder, EXPERIMENT_RUN_FOLDER.format(exp_id))
    if not path.isdir(results_folder):
        os.mkdir(results_folder)

    results_folder_planner = path.join(results_folder, '{}_{}'.format(planner, config))
    if not path.isdir(results_folder_planner):
        os.mkdir(results_folder_planner)

    results_folder_planner_domain = path.join(results_folder_planner, domain)
    os.mkdir(results_folder_planner_domain)

    return path.abspath(results_folder_planner_domain)


def manage_planner_copy(name, planner, config, domain, instance, exp_id, script_str):
    tmp_dir = path.join(PLANNERS_FOLDER, planner, PLANNER_COPIES_FOLDER)
    if not path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    copy_planner_dst = path.join(tmp_dir,
                                 'copy_{name}_{planner}_{config}_{domain}_{instance}_{exp_id}'
                                 .format(name=name, planner=planner, config=config, domain=domain, instance=instance, exp_id=exp_id))
    planner_source = path.join(PLANNERS_FOLDER, planner, PLANNER_SOURCE_FOLDER)
    script_str = script_str.replace(PLANNER_DESTINATION, path.abspath(copy_planner_dst))
    script_str = script_str.replace(PLANNER_SOURCE, path.abspath(planner_source))
    return script_str


def write_script(shell_script, script_name, script_dst):
    script_path = path.join(script_dst, script_name)
    with open(script_path, 'w') as output_writer:
        output_writer.write(shell_script)


def create_scripts(name, exp_id, run_dict, memory, time, path_to_domains):
    script_list = []
    script_folder = scripts_setup(name)

    for planner in run_dict.keys():
        cfg_path = path.join(PLANNERS_FOLDER, planner, CFG_MAP_PLANNER)
        if not path.isfile(cfg_path):
            raise Exception(CFG_PLANNER_ERROR1.format(planner))
        cfg_map = json.load(open(cfg_path,))
        for config in run_dict[planner][CONFIGS]:
            for domain in run_dict[planner][RUNS].keys():
                solution_folder = create_results_folder(name, exp_id, planner, config, domain)
                for pddl_domain, pddl_instance in run_dict[planner][RUNS][domain]:

                    instance_name = pddl_instance.replace(PDDL_EXTENSION, '')
                    solution_name = '{}_{}.sol'.format(domain, instance_name)
                    script_name = '{}_{}_{}_{}_{}.sh'.format(name, planner, config, domain, instance_name)
                    shell_script = SHELL_TEMPLATE

                    if config not in cfg_map:
                        raise Exception(CFG_PLANNER_ERROR2.format(config, planner))

                    path_to_pddl_domain = path.join(path_to_domains, domain, pddl_domain)
                    path_to_pddl_instance = path.join(path_to_domains, domain, pddl_instance)

                    command_template = cfg_map[config]
                    planner_exe = command_template.replace(PLANNER_EXE_DOMAIN, path_to_pddl_domain) \
                        .replace(PLANNER_EXE_INSTANCE, path_to_pddl_instance) \
                        .replace(PLANNER_EXE_SOLUTION, path.join(solution_folder, solution_name))

                    stde = '{}_err'.format(path.abspath(path.join(solution_folder, '{}_{}'.format(domain, instance_name))))
                    stdo = '{}_out'.format(path.abspath(path.join(solution_folder, '{}_{}'.format(domain, instance_name))))
                    planner_exe += " 2>>{} 1>>{}".format(stde, stdo)

                    shell_script = manage_planner_copy(name, planner, config, domain, instance_name, exp_id, shell_script)
                    shell_script = shell_script.replace(MEMORY_SHELL, str(memory))
                    shell_script = shell_script.replace(TIME_SHELL, str(time))
                    shell_script = shell_script.replace(PLANNER_EXE_SHELL, planner_exe)

                    write_script(shell_script, script_name, script_folder)
                    script_list.append((script_name.replace('.sh', ''), path.join(script_folder, script_name)))

    return script_list


def delete_old_planners(cfg_dict):
    for planner in cfg_dict.keys():
        copies_folder = path.join(PLANNERS_FOLDER, planner, PLANNER_COPIES_FOLDER)
        if path.isdir(copies_folder):
            os.system(RM_CMD.format(copies_folder))


def execute_scripts(name, script_list, ppn, priority):
    # Qsub logs setup
    log_dst = path.join(LOG_FOLDER, name)
    if path.isdir(log_dst):
        os.system(RM_CMD.format(log_dst))
    os.mkdir(log_dst)
    #################

    for (script_name, script) in script_list:
        qsub_cmd = QSUB_TEMPLATE
        stdo = path.join(LOG_FOLDER, name, 'log_{}'.format(script_name))
        stde = path.join(LOG_FOLDER, name, 'err_{}'.format(script_name))
        qsub_cmd = qsub_cmd\
            .replace(PPN_QSUB, str(ppn))\
            .replace(PRIORITY_QSUB, str(priority))\
            .replace(SCRIPT_QSUB, script)\
            .replace(LOG_QSUB, stdo)\
            .replace(ERR_QSUB, stde)
        print(qsub_cmd)


def main(args):
    cfg = args[1]
    cfg_dict = json.load(open(cfg, ))
    run_dict = cfg_dict[PLANNERS_X_DOMAINS]
    delete_old_planners(run_dict)
    name = cfg_dict[NAME]
    exp_id = str(datetime.datetime.now()).replace(' ', '_') + '_{}'.format(str(random.randint(0, sys.maxsize)))
    path_to_domains = cfg_dict[PATH_TO_DOMAINS]
    memory = cfg_dict[MEMORY]
    time = cfg_dict[TIME]

    collect_runs(run_dict, path_to_domains)

    script_list = create_scripts(name, exp_id, run_dict, memory, time, path_to_domains)

    execute_scripts(name, script_list, cfg_dict[PPN], cfg_dict[PRIORITY])


if __name__ == '__main__':
    main(sys.argv)
