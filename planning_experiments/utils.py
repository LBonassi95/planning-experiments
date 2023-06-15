import os
from os import path
from planning_experiments.constants import *
from planning_experiments.data_structures import *
from typing import Tuple
import pkg_resources


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

    results_folder_planner_domain = path.join(results_folder_planner, domain)
    os.mkdir(results_folder_planner_domain)

    return path.abspath(results_folder_planner_domain)


def manage_planner_copy(systems_tmp_folder: str, name: str, planner: System, domain: str, instance: str, exp_id: str) -> Tuple[str, str]:
    if not path.isdir(systems_tmp_folder):
        os.makedirs(systems_tmp_folder)
    copy_planner_dst = path.join(systems_tmp_folder,
                                 'copy_{name}_{planner}_{domain}_{instance}_{exp_id}'
                                 .format(name=name, planner=planner.get_name(), domain=domain, instance=instance, exp_id=exp_id))
    planner_source = path.join(planner.get_path())
    return copy_planner_dst, planner_source
    

def write_script(shell_script, script_name, script_dst):
    script_path = path.join(script_dst, script_name)
    with open(script_path, 'w') as output_writer:
        output_writer.write(shell_script)
    os.system(f'chmod +x {script_path}')


def delete_old_folder(folder: str):
    if path.isdir(folder):
        os.system(RM_CMD.format(folder))


"python #COLLECT_DATA_SCRIPT# #SYSTEM# #RESULTS# #SOL_FILE# #SOL_INSTANCE# #SOL_DOMAIN# #STDO# #STDE# #DOMAIN4VAL#"
def get_collect_cmd(envronment: Environment,
                    solution_name: str,
                    solution_folder: str,
                    domain_name: str,
                    instance_name: str,
                    stdo: str,
                    stde: str,
                    results_file: str,
                    system_name: str,
                    val: str):

    collect_data_path = envronment.collect_data
    results_file_path = path.abspath(results_file)
    solution_path = path.join(solution_folder, solution_name)

    collect_data = ["python", collect_data_path,
                    system_name,
                    results_file_path,
                    solution_path,
                    instance_name,
                    domain_name,
                    stdo,
                    stde,
                    val]

    return ' '.join(collect_data)
