import os
import os.path as path
import datetime
from planning_experiments.constants import *
from planning_experiments.data_structures.environment import Domain, Environment, Planner
from planning_experiments.data_structures.execution_backend import *
from planning_experiments.data_structures.system import RunContext
from planning_experiments.script_builder import ScriptBuilder
from planning_experiments.utils import *
from typing import List
import json
import subprocess
import time
from tqdm import tqdm
from tabulate import tabulate
from planning_experiments.save_results import save_results
from planning_experiments.summary import create_summary
from collections import defaultdict


class Executor:

    def __init__(self, environment: Environment, execution_backend: ExecutionBackend, short_name: str = '') -> None:
        self.environment = environment
        self.short_name = short_name
        self.script_folder = None
        self.results_folder = None
        self.log_folder = None
        self.execution_backend = execution_backend
    
    def show_info(self, run_folder: str):
        data = self.execution_backend.get_info()
        data.append(["Environment", self.environment.experiment_group])
        data.append(["Time", f'{self.environment.time}s'])
        data.append(["Memory", f'{self.environment.memory} KB'])
        data.append(['Results folder:', run_folder])
        print(LOGO)
        print(tabulate(data, headers=["Infos", ""], tablefmt="fancy_grid"))

    def check_nruns(self):
        if self.environment.get_nruns() == 0:
            raise Exception('No pddl instance provided')
    
    def run_experiments(self, test_run: bool = False):
        batch2systems = defaultdict(list)

        for system, details in self.environment.run_dictionary.items():
            batch_id = details.get(BATCH)
            if batch_id is not None:
                batch2systems[batch_id.strip()].append(system)

        self.check_nruns()
        exp_id = self.short_name + str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
        self.define_paths(exp_id)

        # if self.environment.clean_systems:
        #     delete_old_folder(self.systems_tmp_folder)
        if self.environment.clean_scripts:
            delete_old_folder(path.join(self.environment.experiments_root, self.environment.SCRIPTS_FOLDER))
        if self.environment.clean_logs:
            delete_old_folder(self.log_folder)

        run_folder = get_run_folder(self.results_folder, exp_id)

        scripts_setup(self.script_folder)
        # Qsub logs setup
        os.makedirs(self.log_folder)
        #################

        self.show_info(run_folder)

        for batch_id in batch2systems.keys():
            
            print(f"Running batch: {batch_id}")
            systems = batch2systems[batch_id]

            job_list, script2blob, blob_path = self.create_scripts(exp_id, run_folder, test_run, systems, batch_id)
            self.execute_scripts(job_list, run_folder, blob_path, script2blob, batch_id)
    
    def define_paths(self, exp_id):
        self.script_folder = path.join(self.environment.experiments_root, self.environment.SCRIPTS_FOLDER, self.environment.experiment_group, exp_id)
        self.results_folder = path.join(self.environment.experiments_root, self.environment.RESULTS_FOLDER, self.environment.experiment_group)
        # self.systems_tmp_folder = path.join(self.environment.experiments_root, PLANNER_COPIES_FOLDER)
        self.log_folder = path.join(self.environment.experiments_root, LOG_FOLDER, self.environment.experiment_group)
    
    def create_scripts(self, exp_id: str, run_folder: str, test_run: bool, systems: List[Planner], batch_id: str):
        job_list = []
        blob = {}
        blob_path = path.join(run_folder, f'blob_{batch_id}.json') if batch_id != '' else path.join(run_folder, f'blob.json')
        script2blob = {}

        for planner in systems:
            assert isinstance(planner, Planner)
            blob[planner.get_name()] = {}
            for domain in self.environment.run_dictionary[planner][DOMAINS]:
                blob[planner.get_name()][domain.name] = {}
                self._create_script(planner, domain, exp_id, run_folder, job_list, blob, blob_path, test_run, script2blob)

        with open(blob_path, 'w') as f:
            json.dump(blob, f, indent=4)
        
        # Make scripts executable
        subprocess.run(f'chmod -R +x {self.script_folder}', shell=True)
                
        return job_list, script2blob, blob_path
  
    def _create_script(self, planner: Planner, domain: Domain, exp_id: str, run_folder: str, job_list: List[Job], blob: dict, blob_path: str, test_run: bool, script2blob: dict):
        planner_name = planner.get_name()
        
        instances = domain.instances
        if test_run:
            instances = instances[:2]

        for pddl_domain_path, pddl_instance_path in instances:
            instance_name = path.basename(pddl_instance_path).replace(PDDL_EXTENSION, '')

            instance_folder = path.join(run_folder, planner_name, domain.name, instance_name)
            create_folder(instance_folder)

            solution_folder = path.join(instance_folder, SOLUTION_FOLDER)
            create_folder(solution_folder)

            solution_name = f'{domain.name}_{instance_name}.sol'
            script_name = f'{self.environment.experiment_group}_{planner_name}_{domain.name}_{instance_name}'
            path2solution = path.join(solution_folder, solution_name)
            stde = path.abspath(path.join(instance_folder, f'err_{domain.name}_{instance_name}.txt'))
            stdo = path.abspath(path.join(instance_folder, f'out_{domain.name}_{instance_name}.txt'))
            planner_path = path.join(instance_folder, SANDBOX_FOLDER)
            planner_exe = planner.get_cmd(RunContext(pddl_domain_path, pddl_instance_path, path2solution, planner_path))

            # Collecting info #################
            blob[planner_name][domain.name][instance_name] = {}
            blob[planner_name][domain.name][instance_name][DOMAIN_PATH] = pddl_domain_path
            blob[planner_name][domain.name][instance_name][INSTANCE_PATH] = pddl_instance_path
            blob[planner_name][domain.name][instance_name][SOLUTION_PATH] = solution_folder
            blob[planner_name][domain.name][instance_name][STDE] = stde
            blob[planner_name][domain.name][instance_name][STDO] = stdo
            blob[planner_name][domain.name][instance_name][PLANNER_EXE] = planner_exe
            ###################################
            
            # copy_planner_dst, planner_source = manage_planner_copy(
            #     self.systems_tmp_folder, self.environment.experiment_group, planner, domain, instance_name, exp_id)

            builder = ScriptBuilder(self.environment, 
                                    system=planner,
                                    domain_name=domain.name,
                                    instance_name=instance_name,
                                    blob_path=blob_path,
                                    # system_dst=path.abspath(copy_planner_dst),
                                    time=str(self.environment.time),
                                    memory=str(self.environment.memory),
                                    system_exe=planner_exe,
                                    instance_folder=instance_folder,
                                    stdo=stdo, 
                                    stde=stde, 
                                    script_name=script_name,
                                    script_folder=self.script_folder)
            
            inner_script, outer_script = builder.get_script()
            write_script(inner_script, f"{script_name}.sh", self.script_folder)
            write_script(outer_script, f'run_{script_name}.py', self.script_folder)
            job_list.append(Job(script_name, path.join(self.script_folder, f'run_{script_name}.py')))
            script2blob[script_name] = {'planner': planner_name, 'domain': domain.name, 'instance': instance_name}
    
    def execute_scripts(self, job_list: List[Job], run_folder: str, blob_path: str, script2blob: dict, batch_id: str):
    
        print("Ready to launch experiments")
        print(f"Total number of runs: {len(job_list)}")
        
        self.execution_backend.run(job_list, self.log_folder)