import os
from os import path
import shutil
from planning_experiments.constants import *
from planning_experiments.data_structures import *
import subprocess

def scripts_setup(script_folder):
    os.makedirs(script_folder)


def get_run_folder(results_folder: str, exp_id: str):
    create_folder(results_folder)

    results_folder = path.join(results_folder, exp_id)
    create_folder(results_folder)

    return path.abspath(results_folder)


def create_folder(folder_path: str):
    if not path.isdir(folder_path):
        os.makedirs(folder_path)


def manage_planner_copy(instance_folder: str, planner: Planner, hard_copy):
    sandbox = path.join(instance_folder, SANDBOX_FOLDER)
    planner_src = path.abspath(planner.get_path())

    if hard_copy:
        raise NotImplementedError("Hard copy of the full planner is not yet implemented!")
        shutil.copytree(planner_src, planner_dst)

    os.makedirs(sandbox, exist_ok=True)
    for entry in os.scandir(planner_src):
        if entry.is_file(follow_symlinks=False):
            os.symlink(entry.path, os.path.join(sandbox, entry.name))

    return sandbox

def write_script(shell_script, script_name, script_dst):
    script_path = path.join(script_dst, script_name)
    with open(script_path, 'w') as output_writer:
        output_writer.write(shell_script)

def delete_old_folder(folder: str):
    if path.isdir(folder):
        subprocess.run(RM_CMD.format(folder), shell=True)