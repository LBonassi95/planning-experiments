import os.path as path
import datetime
from planning_experiments.constants import *
from planning_experiments.data_structures.execution_backend import *
from planning_experiments.data_structures.system import RunContext
from planning_experiments.utils import *
from typing import List
import subprocess
from tabulate import tabulate

ERROR_SYSTEM_ALREADY_ADDED = '''
System "{system}" was already added to the environment.
If you want to run "{system}" multiple times, 
please create a new environment or assing different names to the system.
Example: define "{system}-1" and "{system}-2".
'''


class Executor:

    SCRIPTS_FOLDER = 'scripts'
    RESULTS_FOLDER = 'results'

    def __init__(self, execution_backend: ExecutionBackend, 
                       experiments_root: str, 
                       experiment_group: str = "run", 
                       short_name: str = None,
                       hard_copy: bool = False,
                       delete_old_scripts: bool = False) -> None:
        self.short_name = short_name
        self.script_folder = None
        self.results_folder = None
        self.execution_backend = execution_backend
        self.experiments_root = experiments_root
        self.hard_copy = hard_copy
        self.run_dictionary = {}
        self.experiment_group = experiment_group
        self.clean_scripts = delete_old_scripts

    def add_run(self, system: Planner, domains: List[Domain]):

        if self.run_dictionary.get(system, None) is not None:
            raise Exception(ERROR_SYSTEM_ALREADY_ADDED.format(system=system))
        else:
            self.run_dictionary[system] = {DOMAINS: domains}

    def get_nruns(self):
        nruns = 0
        for system in self.run_dictionary:
            for domain in self.run_dictionary[system][DOMAINS]:
                assert isinstance(domain, Domain)
                nruns += len(domain.instances)
        return nruns
    
    def show_info(self, run_folder: str):
        data = self.execution_backend.get_info()
        data.append(['Results folder:', run_folder])
        print(LOGO)
        print(tabulate(data, headers=["Infos", ""], tablefmt="fancy_grid"))

    def check_nruns(self):
        if self.get_nruns() == 0:
            raise Exception('No pddl instance provided')
    
    def run_experiments(self, test_run: bool = False):

        self.check_nruns()
        exp_id = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
       
        if self.short_name is not None:
            exp_id = f"{self.short_name}_{exp_id}"
        
        self.define_paths(exp_id)

        if self.clean_scripts:
            delete_old_folder(path.join(self.experiments_root, self.SCRIPTS_FOLDER))

        run_folder = get_run_folder(self.results_folder, exp_id)

        scripts_setup(self.script_folder)

        self.show_info(run_folder)

        systems = [_sys for _sys in self.run_dictionary.keys()]

        job_list = self.create_scripts(exp_id, run_folder, test_run, systems)
        self.execute_scripts(job_list)
    
    def define_paths(self, exp_id):
        self.script_folder = path.join(self.experiments_root, self.SCRIPTS_FOLDER, self.experiment_group, exp_id)
        self.results_folder = path.join(self.experiments_root, self.RESULTS_FOLDER, self.experiment_group)
    
    def create_scripts(self, exp_id: str, run_folder: str, test_run: bool, systems: List[Planner]):
        job_list = []

        for planner in systems:
            assert isinstance(planner, Planner)
            for domain in self.run_dictionary[planner][DOMAINS]:
                self._create_script(planner, domain, exp_id, run_folder, job_list, test_run)

        # Make scripts executable
        subprocess.run(f'chmod -R +x {self.script_folder}', shell=True)
                
        return job_list

  
    def _create_script(self, planner: Planner, domain: Domain, exp_id: str, run_folder: str, job_list: List[Job], test_run: bool):
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
            script_name = f'{self.experiment_group}_{planner_name}_{domain.name}_{instance_name}'
            path2solution = path.join(solution_folder, solution_name)
            stde = path.abspath(path.join(instance_folder, f'err_{domain.name}_{instance_name}.txt'))
            stdo = path.abspath(path.join(instance_folder, f'out_{domain.name}_{instance_name}.txt'))
            planner_path = path.join(instance_folder, SANDBOX_FOLDER)
            planner_exe = planner.get_cmd(RunContext(pddl_domain_path, pddl_instance_path, path2solution, planner_path))

            sandbox = manage_planner_copy(instance_folder, planner, self.hard_copy)

            script = self.execution_backend.create_script(cmd=planner_exe, sandbox=sandbox, stdout=stdo, stderr=stde)
            script_name = f"{script_name}.sh"

            write_script(script, script_name, self.script_folder)
            job_list.append(Job(script_name, 
                                path.join(self.script_folder, script_name), 
                                problem_result_folder=instance_folder))
    
    def execute_scripts(self, job_list: List[Job]):
        self.execution_backend.run(job_list)