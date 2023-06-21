import os
import os.path as path
import sys
import random
import datetime
from planning_experiments.constants import *
from planning_experiments.data_structures.environment import Domain, Environment, System
from planning_experiments.script_builder import ScriptBuilder
from planning_experiments.utils import *
from typing import List
import json
import subprocess
import time
from multiprocessing import Pool
from tqdm import tqdm
from tabulate import tabulate
from planning_experiments.save_results import save_results

def run_script(script_info: Tuple[str, str]):
    script_name = script_info[0]
    script = script_info[1]
    subprocess.run(f'chmod +x {script}', shell=True)
    subprocess.run({script}, shell=True)
    return script_name


class Executor:

    def __init__(self, environment: Environment, short_name: str = '') -> None:
        self.environment = environment
        self.short_name = short_name
        self.script_folder = None
        self.results_folder = None
        self.systems_tmp_folder = None
        self.log_folder = None
    
    def show_info(self, run_folder: str):
        data = self.environment.get_info()
        data.append(['Results folder:', run_folder])
        print(LOGO)
        print(tabulate(data, headers=["Infos", ""], tablefmt="fancy_grid"))
    
    def run_experiments(self, test_run: bool = False):
        exp_id = self.short_name + str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
        self.define_paths(exp_id)

        if self.environment.clean_systems:
            delete_old_folder(self.systems_tmp_folder)
        if self.environment.clean_scripts:
            delete_old_folder(path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER))
        if self.environment.clean_logs:
            delete_old_folder(self.log_folder)

        run_folder = get_run_folder(self.results_folder, exp_id)
        self.show_info(run_folder)

        script_list, script2blob, blob_path = self.create_scripts(exp_id, run_folder, test_run)
        self.execute_scripts(script_list, script2blob, blob_path)
    
    def define_paths(self, exp_id):
        self.script_folder = path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER, self.environment.name, exp_id)
        self.results_folder = path.join(self.environment.experiments_folder, self.environment.RESULTS_FOLDER, self.environment.name)
        self.systems_tmp_folder = path.join(self.environment.experiments_folder, PLANNER_COPIES_FOLDER)
        self.log_folder = path.join(self.environment.experiments_folder, LOG_FOLDER, self.environment.name)
    
    def create_scripts(self, exp_id: str, run_folder: str,test_run: bool):
        script_list = []
        scripts_setup(self.script_folder)
        
        blob = {}
        blob_path = path.join(run_folder, 'blob.json')
        script2blob = {}

        for planner in self.environment.run_dictionary.keys():
            blob[planner.name] = {}
            for domain in self.environment.run_dictionary[planner][DOMAINS]:
                blob[planner.name][domain.name] = {}
                self._create_script(planner, domain, exp_id, run_folder, script_list, blob, blob_path, test_run, script2blob)

        with open(blob_path, 'w') as f:
            json.dump(blob, f, indent=4)
        
        # Make scripts executable
        subprocess.run(f'chmod +x {self.script_folder}/*', shell=True)
                
        return script_list, script2blob, blob_path
  
    def _create_script(self, planner: System, domain: Domain, exp_id: str, run_folder: str, script_list: List[str], blob: dict, blob_path: str, test_run: bool, script2blob: dict):
        planner_name = planner.get_name()
        
        instances = domain.instances
        if test_run:
            instances = instances[:2]

        for pddl_domain, pddl_instance in instances:

            instance_name = pddl_instance.replace(PDDL_EXTENSION, '')

            instance_folder = path.join(run_folder, planner_name, domain.name, instance_name)
            create_folder(instance_folder)

            solution_folder = path.join(instance_folder, SOLUTION_FOLDER)
            create_folder(solution_folder)

            solution_name = f'{domain.name}_{instance_name}.sol'
            script_name = f'{self.environment.name}_{planner_name}_{domain.name}_{instance_name}.sh'
            path2domain = path.join(domain.path, pddl_domain)
            path2instance = path.join(domain.path, pddl_instance)
            path2solution = path.join(solution_folder, solution_name)
            stde = path.abspath(path.join(instance_folder, f'err_{domain.name}_{instance_name}.txt'))
            stdo = path.abspath(path.join(instance_folder, f'out_{domain.name}_{instance_name}.txt'))
            planner_exe = planner.get_cmd(path2domain, path2instance, path2solution)

            # Collecting info #################
            blob[planner.name][domain.name][instance_name] = {}
            blob[planner.name][domain.name][instance_name][DOMAIN_PATH] = path2domain
            blob[planner.name][domain.name][instance_name][INSTANCE_PATH] = path2instance
            blob[planner.name][domain.name][instance_name][SOLUTION_PATH] = solution_folder
            blob[planner.name][domain.name][instance_name][STDE] = stde
            blob[planner.name][domain.name][instance_name][STDO] = stdo
            blob[planner.name][domain.name][instance_name][PLANNER_EXE] = planner_exe
            ###################################
            
            copy_planner_dst, planner_source = manage_planner_copy(
                self.systems_tmp_folder, self.environment.name, planner, domain, instance_name, exp_id)

            builder = ScriptBuilder(self.environment, 
                                    system=planner,
                                    domain_name=domain.name,
                                    instance_name=instance_name,
                                    results=blob_path,
                                    system_dst=path.abspath(copy_planner_dst),
                                    time=str(self.environment.time),
                                    memory=str(self.environment.memory),
                                    system_exe=planner_exe,
                                    stdo=stdo, 
                                    stde=stde, 
                                    script_name=script_name,
                                    info_dict_path=blob_path, 
                                    script_folder=self.script_folder)
            
            inner_script, outer_script = builder.get_script()
            write_script(inner_script, script_name, self.script_folder)
            write_script(outer_script, f'run_{script_name}', self.script_folder)
            script_list.append((script_name.replace('.sh', ''), path.join(self.script_folder, f'run_{script_name}')))
            script2blob[script_name.replace('.sh', '')] = (planner.name, domain.name, instance_name)


    
    def is_completed(self, job_infos: Tuple[str, str]):
        job_id = job_infos[0]
        output = subprocess.check_output(f'qstat -f {job_id}', shell=True, universal_newlines=True)
        if 'job_state = C' in output or 'Unknown Job Id' in output:
            return True
        else:
            return False

    
    def execute_scripts(self, script_list: List[str], script2blob: dict, blob_path: str):
        # Qsub logs setup
        os.makedirs(self.log_folder)
        #################

        if self.environment.qsub:
            
            job_infos = []

            for (script_name, script) in script_list:
                qsub_cmd = QSUB_TEMPLATE
                stdo = path.join(self.log_folder, 'log_{}'.format(script_name))
                stde = path.join(self.log_folder, 'err_{}'.format(script_name))
                qsub_cmd = qsub_cmd\
                    .replace(PPN_QSUB, str(self.environment.ppn))\
                    .replace(PRIORITY_QSUB, str(self.environment.priority))\
                    .replace(SCRIPT_QSUB, script)\
                    .replace(LOG_QSUB, stdo)\
                    .replace(ERR_QSUB, stde)
                job_id = subprocess.check_output(qsub_cmd, shell=True, universal_newlines=True)
                job_infos.append((job_id.strip(), script_name))
            

            running_jobs = set(job_infos)
            progress_bar = tqdm(total=len(running_jobs), desc="Progress", unit="iteration")
            while len(running_jobs) > 0:
                job_completed_so_far = filter(self.is_completed, running_jobs)
                job_completed_so_far = list(job_completed_so_far)
                running_jobs = running_jobs.difference(job_completed_so_far)
                if len(job_completed_so_far) > 0:
                    progress_bar.update(len(job_completed_so_far))

                    for job_id, script_name in job_completed_so_far:
                        planner, domain, instance = script2blob[script_name]
                        save_results(blob_path, planner, domain, instance)

                time.sleep(5)
            
            progress_bar.close()
            
        else:
            scripts_infos = [(script_name, script) for script_name, script in script_list]
            progress_bar = tqdm(total=len(scripts_infos), desc="Progress", unit="iteration")
            with Pool(self.environment.parallel_processes) as p:
                for script_name in p.imap_unordered(run_script, scripts_infos):
                    planner, domain, instance = script2blob[script_name]
                    save_results(blob_path, planner, domain, instance)
                    progress_bar.update(1)

                progress_bar.close()