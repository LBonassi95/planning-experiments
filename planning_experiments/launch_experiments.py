import os
import os.path as path
import datetime
from planning_experiments.constants import *
from planning_experiments.data_structures.environment import Domain, Environment, ScriptEnvironment
from planning_experiments.data_structures.system import *
from planning_experiments.script_builder import ScriptBuilder
from planning_experiments.utils import *
from typing import List
import json
import subprocess
import time
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from tabulate import tabulate
from planning_experiments.save_results import save_results
from planning_experiments.summary import create_summary, extract_float
from collections import defaultdict
import pandas as pd
import fcntl

def run_script(script_info: Tuple[str, str]):
    script_name = script_info[0]
    script = script_info[1]
    subprocess.run(f'chmod +x {script}', shell=True)
    subprocess.run(f'{script}', shell=True)
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

        if self.environment.clean_systems:
            delete_old_folder(self.systems_tmp_folder)
        if self.environment.clean_scripts:
            delete_old_folder(path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER))
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

            script_list, script2blob, blob_path = self.create_scripts(exp_id, run_folder, test_run, systems, batch_id)
            self.execute_scripts(script_list, run_folder, blob_path, script2blob, batch_id)
    
    def define_paths(self, exp_id):
        self.script_folder = path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER, self.environment.name, exp_id)
        self.results_folder = path.join(self.environment.experiments_folder, self.environment.RESULTS_FOLDER, self.environment.name)
        self.systems_tmp_folder = path.join(self.environment.experiments_folder, PLANNER_COPIES_FOLDER)
        self.log_folder = path.join(self.environment.experiments_folder, LOG_FOLDER, self.environment.name)
    
    def create_scripts(self, exp_id: str, run_folder: str, test_run: bool, systems: List[System], batch_id: str):
        script_list = []
        blob = {}
        blob_path = path.join(run_folder, f'blob_{batch_id}.json') if batch_id != '' else path.join(run_folder, f'blob.json')
        script2blob = {}

        for planner in systems:
            assert isinstance(planner, System)
            blob[planner.get_name()] = {}
            for domain in self.environment.run_dictionary[planner][DOMAINS]:
                blob[planner.get_name()][domain.name] = {}
                self._create_script(planner, domain, exp_id, run_folder, script_list, blob, blob_path, test_run, script2blob)

        with open(blob_path, 'w') as f:
            json.dump(blob, f, indent=4)
        
        # Make scripts executable
        subprocess.run(f'chmod -R +x {self.script_folder}', shell=True)
                
        return script_list, script2blob, blob_path
  
    def _create_script(self, planner: System, domain: Domain, exp_id: str, run_folder: str, script_list: List[str], blob: dict, blob_path: str, test_run: bool, script2blob: dict):
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
            script_name = f'{self.environment.name}_{planner_name}_{domain.name}_{instance_name}'
            path2solution = path.join(solution_folder, solution_name)
            stde = path.abspath(path.join(instance_folder, f'err_{domain.name}_{instance_name}.txt'))
            stdo = path.abspath(path.join(instance_folder, f'out_{domain.name}_{instance_name}.txt'))
            planner_exe = planner.get_cmd(pddl_domain_path, pddl_instance_path, path2solution)

            # Collecting info #################
            blob[planner_name][domain.name][instance_name] = {}
            blob[planner_name][domain.name][instance_name][DOMAIN_PATH] = pddl_domain_path
            blob[planner_name][domain.name][instance_name][INSTANCE_PATH] = pddl_instance_path
            blob[planner_name][domain.name][instance_name][SOLUTION_PATH] = solution_folder
            blob[planner_name][domain.name][instance_name][STDE] = stde
            blob[planner_name][domain.name][instance_name][STDO] = stdo
            blob[planner_name][domain.name][instance_name][PLANNER_EXE] = planner_exe
            ###################################
            
            copy_planner_dst, planner_source = manage_planner_copy(
                self.systems_tmp_folder, self.environment.name, planner, domain, instance_name, exp_id)

            builder = ScriptBuilder(self.environment, 
                                    system=planner,
                                    domain_name=domain.name,
                                    instance_name=instance_name,
                                    blob_path=blob_path,
                                    system_dst=path.abspath(copy_planner_dst),
                                    time=str(self.environment.time),
                                    memory=str(self.environment.memory),
                                    system_exe=planner_exe,
                                    stdo=stdo, 
                                    stde=stde, 
                                    script_name=script_name,
                                    script_folder=self.script_folder)
            
            inner_script, outer_script = builder.get_script()
            write_script(inner_script, f"{script_name}.sh", self.script_folder)
            write_script(outer_script, f'run_{script_name}.py', self.script_folder)
            script_list.append((script_name, path.join(self.script_folder, f'run_{script_name}.py')))
            script2blob[script_name] = {'planner': planner_name, 'domain': domain.name, 'instance': instance_name}


    
    def is_completed(self, job_info: Tuple[str, str]):
        job_id = job_info[0]
        try:
            output = subprocess.check_output(f'qstat -f {job_id}', shell=True, universal_newlines=True)
            if 'job_state = C' in output:
                return True
            else:
                return False
            
        except subprocess.CalledProcessError as e:
            return True
        
        
    
    def submit_job(self, args: Tuple[str, str]) -> str:

        script_name, script = args

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
        return job_id.strip(), script_name

    
    def execute_scripts(self, script_list: List[Tuple[str, str]], run_folder: str, blob_path: str, script2blob: dict, batch_id: str):
    
        print("Ready to launch experiments")
        print(f"Total number of runs: {len(script_list)}")

        if self.environment.qsub:

            pool_size = 16 if cpu_count() > 100 else cpu_count()

            start_time = time.time()
            with Pool(pool_size) as pool:
                results = pool.map(self.submit_job, [(script_name, script) for script_name, script in script_list])
            job_infos = [(job_id, script_name) for job_id, script_name in results]
            print(f"Time taken to submit all jobs: {time.time() - start_time:.2f} seconds")
                

            running_jobs = set(job_infos)
            progress_bar = tqdm(total=len(running_jobs), desc="Progress", unit="iteration", colour='green')
            while len(running_jobs) > 0:

                with Pool(pool_size) as pool:
                    completed_flags = pool.map(self.is_completed, running_jobs)

                job_completed_so_far = {job for job, completed in zip(running_jobs, completed_flags) if completed}
                running_jobs = running_jobs.difference(job_completed_so_far)
                if len(job_completed_so_far) > 0:
                    for _, script_name in job_completed_so_far:
                        save_results(blob_path, script2blob[script_name]["planner"], script2blob[script_name]["domain"], script2blob[script_name]["instance"])
                    progress_bar.update(len(job_completed_so_far))
                    
                time.sleep(5)
            
            progress_bar.close()
            
        else:
            scripts_infos = [(script_name, script) for script_name, script in script_list]
            progress_bar = tqdm(total=len(scripts_infos), desc="Progress", unit="iteration", colour='green')
            with Pool(self.environment.parallel_processes) as p:
                for script_name in p.imap_unordered(run_script, scripts_infos):
                    save_results(blob_path, script2blob[script_name]["planner"], script2blob[script_name]["domain"], script2blob[script_name]["instance"])
                    progress_bar.update(1)

                progress_bar.close()
        
        # Create summary
        summary_path = path.join(run_folder, f"summary_{batch_id}.csv") if batch_id != '' else path.join(run_folder, f"summary.csv")
        create_summary(blob_path, summary_path)


class ScriptExecutor(Executor):

    def __init__(self, environment: ScriptEnvironment, short_name: str = '') -> None:
        super().__init__(environment, short_name)
        if self.environment.qsub:
            raise ValueError(f"Qsub currently not supported by {__class__}")
    
    def create_scripts(self, exp_id: str, run_folder: str, test_run: bool, systems: List[ScriptSystem], batch_id: str):
        script_list = []
        blob = {}
        blob_path = path.join(run_folder, f'blob_{batch_id}.json') if batch_id != '' else path.join(run_folder, f'blob.json')
        script2blob = {}

        for system in systems:
            blob[system.get_name()] = {}
            for i in range(self.environment.run_dictionary[system][NRUNS]):
                blob[system.get_name()][f"run_{i}"] = {}
                self._create_script(system, i, run_folder, script_list, blob, script2blob)

        with open(blob_path, 'w') as f:
            json.dump(blob, f, indent=4)
        
        # Make scripts executable
        subprocess.run(f'chmod -R +x {self.script_folder}', shell=True)
                
        return script_list, script2blob, blob_path
    

    def _create_script(self, system: ScriptSystem, run: int, run_folder: str, script_list: List[str], blob: dict, script2blob: dict):
        system_name = system.get_name()
        run_id = f"run_{str(run)}"
        solution_folder = path.join(run_folder, system_name, run_id)
        create_folder(solution_folder)

        script_name = f'{self.environment.name}_{system_name}_{run_id}'
        out_path = path.join(solution_folder, f'{system_name}_{run_id}.sol')
        stde = path.abspath(path.join(solution_folder, f'err_{system_name}_{run_id}.txt'))
        stdo = path.abspath(path.join(solution_folder, f'out_{system_name}_{run_id}.txt'))
        system_exe = system.get_cmd(out_path)

        # Collecting info #################
        blob[system_name][run_id] = {}
        blob[system_name][run_id][SOLUTION_PATH] = solution_folder
        blob[system_name][run_id][STDE] = stde
        blob[system_name][run_id][STDO] = stdo
        blob[system_name][run_id][PLANNER_EXE] = system_exe
        ###################################

        memory = str(self.environment.memory)
        time = str(self.environment.time)

        launch_script = ['#!/bin/bash', f'cd {solution_folder}']
        if memory != 'None': launch_script.append(f'ulimit -Sv {memory}')

        if time != "None": exec_cmd = f'(time -p timeout --signal=HUP {time} {system_exe}) 2>> {stde} 1>> {stdo}'
        else: exec_cmd = f'(time -p {system_exe}) 2>> {stde} 1>> {stdo}'

        launch_script.append(exec_cmd)
        
        write_script("\n".join(launch_script), f"{script_name}.sh", self.script_folder)
        script_list.append((script_name, path.join(self.script_folder, f"{script_name}.sh")))
        script2blob[script_name] = {'planner': system_name, 'run_id': run_id}

    
    def execute_scripts(self, script_list: List[Tuple[str, str]], run_folder: str, blob_path: str, script2blob: dict, batch_id: str):
    
        print("Ready to launch experiments")
        print(f"Total number of runs: {len(script_list)}")

        scripts_infos = [(script_name, script) for script_name, script in script_list]
        progress_bar = tqdm(total=len(scripts_infos), desc="Progress", unit="iteration", colour='green')
        with Pool(self.environment.parallel_processes) as p:
            for script_name in p.imap_unordered(run_script, scripts_infos):
                self.save_results(blob_path, script2blob[script_name]["planner"], script2blob[script_name]["run_id"])
                progress_bar.update(1)

            progress_bar.close()

        
    
    def save_results(self, results_file, system, run_id):
        file = open(results_file, "r+")

        fcntl.flock(file, fcntl.LOCK_EX)

        json_data = json.load(file)

        try:
            stdo_path = json_data[system][run_id][STDO]
            stde_path = json_data[system][run_id][STDE]

            stdo_str = open(stdo_path, 'r').read()
            stde_str = open(stde_path, 'r').read()

            for sol_file in os.listdir(json_data[system][run_id][SOLUTION_PATH]):
                if '.sol' in sol_file:
                    json_data[system][run_id][SOLUTIONS] = open(os.path.join(json_data[system][run_id][SOLUTION_PATH], sol_file), 'r').read()
                    break

            json_data[system][run_id][STDO] = stdo_str
            json_data[system][run_id][STDE] = stde_str

            
            file.seek(0)
            file.truncate()
            json.dump(json_data, file, indent=4)
            fcntl.flock(file, fcntl.LOCK_UN)
            file.close()

        except Exception as e:
            json_data[system][run_id][SOLUTIONS] = []
            json_data[system][run_id][NUM_SOLUTIONS] = -1
            json_data[system][run_id][STDO] = "RUN SKIPPED DUE TO AN UNEXPECTED ERROR"
            json_data[system][run_id][STDE] = "RUN SKIPPED DUE TO AN UNEXPECTED ERROR"

            
            file.seek(0)
            file.truncate()
            json.dump(json_data, file, indent=4)
            fcntl.flock(file, fcntl.LOCK_UN)
            file.close()