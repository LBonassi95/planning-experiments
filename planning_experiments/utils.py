import os
from os import path
from planning_experiments.constants import *
from planning_experiments.data_structures import *
from typing import Tuple
import pkg_resources
import subprocess
import signal
import sys
import time

def scripts_setup(script_folder):
    # Clean old scripts with the same name
    # if path.isdir(script_folder):
    #    os.system(RM_CMD.format(script_folder))
    #######################################
    os.makedirs(script_folder)


def get_run_folder(results_folder: str, exp_id: str):
    create_folder(results_folder)

    results_folder = path.join(results_folder, EXPERIMENT_RUN_FOLDER.format(exp_id))
    create_folder(results_folder)

    return path.abspath(results_folder)


def create_folder(folder_path: str):
    if not path.isdir(folder_path):
        os.makedirs(folder_path)


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

def delete_old_folder(folder: str):
    if path.isdir(folder):
        subprocess.run(RM_CMD.format(folder), shell=True)


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def limited_time_execution(func, stde, args=(), kwargs={}, timeout=5):
    """
    Runs a function with a time limit.

    :param func: The function to run
    :param stde: The file to write the error output
    :param args: Arguments to pass to the function
    :param kwargs: Keyword arguments to pass to the function
    :param timeout: Time limit in seconds
    :return: The result of the function if it completes within the time limit
    :raises TimeoutException: If the function execution exceeds the time limit
    """
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)  # Set the alarm

    try:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Total time: {end_time - start_time:.2f}", file=open(stde, 'a'))
    except TimeoutException:
        print(f"Time out! Execution exceeded {timeout} seconds", file=open(stde, 'a'))
        os._exit(21)
    finally:
        signal.alarm(0)  # Disable the alarm

    return result