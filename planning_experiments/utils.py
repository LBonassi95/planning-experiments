import os
from os import path
from planning_experiments.constants import *
from planning_experiments.experiment_environment import Configuration, System


def add_configutation(base_cmd: str, configuration: Configuration):
    return ' '.join(base_cmd.split(' ') + configuration.parameters)


def scripts_setup(script_folder):
    # Clean old scripts with the same name
    # if path.isdir(script_folder):
    #    os.system(RM_CMD.format(script_folder))
    #######################################
    os.makedirs(script_folder)


def create_results_folder(results_folder: str, exp_id: str, planner: str, domain: str):
    if not path.isdir(results_folder):
        os.makedirs(results_folder)

    results_folder = path.join(
        results_folder, EXPERIMENT_RUN_FOLDER.format(exp_id))
    if not path.isdir(results_folder):
        os.mkdir(results_folder)

    results_folder_planner = path.join(
        results_folder, '{}'.format(planner))
    if not path.isdir(results_folder_planner):
        os.mkdir(results_folder_planner)

    results_file = path.join(results_folder, 'results.txt')
    if not path.exists(results_file):
        os.system('touch {}'.format(results_file))

    results_folder_planner_domain = path.join(results_folder_planner, domain)
    os.mkdir(results_folder_planner_domain)

    return path.abspath(results_folder_planner_domain), results_file


def manage_planner_copy(systems_tmp_folder: str, name: str, planner: System, domain: str, instance: str, exp_id: str) -> tuple[str, str]:
    if not path.isdir(systems_tmp_folder):
        os.makedirs(systems_tmp_folder)
    copy_planner_dst = path.join(systems_tmp_folder,
                                 'copy_{name}_{planner}_{domain}_{instance}_{exp_id}'
                                 .format(name=name, planner=planner.get_name(), domain=domain, instance=instance, exp_id=exp_id))
    planner_source = path.join(planner.get_path())
    return copy_planner_dst, planner_source


def collect_instances(instances_path):
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
            assert '-' in pddl_domains[i] or '_' in pddl_domains[i]
            if '-' in pddl_domains[i]:
                sep = '-'
            elif '_' in pddl_domains[i]:
                sep = '_'
            else:
                assert False, 'ABORTING!'
            test_soundness = pddl_domains[i].split(sep)[1]
            #assert test_soundness == pddl_instances[i]
            pairs.append((pddl_domains[i], pddl_instances[i]))
    return pairs


def write_script(shell_script, script_name, script_dst):
    script_path = path.join(script_dst, script_name)
    with open(script_path, 'w') as output_writer:
        output_writer.write(shell_script)


def delete_old_folder(folder: str):
    if path.isdir(folder):
        os.system(RM_CMD.format(folder))


"#COLLECT_DATA_SCRIPT# #SYSTEM# #RESULTS# #SOL_FILE# #SOL_INSTANCE# #SOL_DOMAIN# #STDO# #STDE# #DOMAIN4VAL#"
def get_collect_cmd(solution_name: str,
                    solution_folder: str,
                    domain_name: str,
                    instance_name: str,
                    stdo: str,
                    stde: str,
                    results_file: str,
                    system_name: str,
                    val: str):

    collect_data_path = path.abspath(
        path.join(COLLECT_DATA_FOLDER, "collect_data.py"))
    results_file_path = path.abspath(results_file)
    solution_path = path.join(solution_folder, solution_name)

    collect_data = [collect_data_path,
                    system_name,
                    results_file_path,
                    solution_path,
                    instance_name,
                    domain_name,
                    stdo,
                    stde,
                    val]

    return ' '.join(collect_data)
