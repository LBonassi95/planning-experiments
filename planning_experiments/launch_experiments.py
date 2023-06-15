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

from multiprocessing import Pool

def run_script(script: str):
    print(f'Running {script}')
    os.system(f'chmod +x {script}')
    os.system(script)


class Executor:

    def __init__(self, environment: Environment, short_name: str = '') -> None:
        self.environment = environment
        self.short_name = short_name
        self.script_folder = None
        self.results_folder = None
        self.systems_tmp_folder = None
        self.log_folder = None
    
    def run_experiments(self, test_run: bool = False):
        exp_id = self.short_name + str(datetime.datetime.now()).replace(' ', '_').split('.')[0]
        # + '_{}'.format(str(random.randint(0, sys.maxsize)))
        self.define_paths(exp_id)

        if self.environment.clean_systems:
            delete_old_folder(self.systems_tmp_folder)
        if self.environment.clean_scripts:
            delete_old_folder(path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER))
        if self.environment.clean_logs:
            delete_old_folder(self.log_folder)

        script_list = self.create_scripts(exp_id, test_run)
        self.execute_scripts(script_list)
    
    def define_paths(self, exp_id):
        self.script_folder = path.join(self.environment.experiments_folder, self.environment.SCRIPTS_FOLDER, self.environment.name, exp_id)
        self.results_folder = path.join(self.environment.experiments_folder, self.environment.RESULTS_FOLDER, self.environment.name)
        self.systems_tmp_folder = path.join(self.environment.experiments_folder, PLANNER_COPIES_FOLDER)
        self.log_folder = path.join(self.environment.experiments_folder, LOG_FOLDER, self.environment.name)
    
    def create_scripts(self, exp_id: str, test_run: bool):
        script_list = []
        scripts_setup(self.script_folder)
        
        info_dict = {}
        info_dict_path = path.join(self.results_folder, EXPERIMENT_RUN_FOLDER.format(exp_id), 'blob.json')

        for planner in self.environment.run_dictionary.keys():
            info_dict[planner.name] = {}
            for domain in self.environment.run_dictionary[planner][DOMAINS]:
                info_dict[planner.name][domain.name] = {}
                self._create_script(planner, domain, exp_id, script_list, info_dict, info_dict_path, test_run)

        with open(info_dict_path, 'w') as f:
            json.dump(info_dict, f, indent=4)
                
        return script_list
  
    def _create_script(self, planner: System, domain: Domain, exp_id: str, script_list: List[str], info_dict: dict, info_dict_path: str, test_run: bool):
        planner_name = planner.get_name()
        solution_folder = create_results_folder(self.results_folder, exp_id, planner_name, domain.name)
        
        instances = domain.instances
        if test_run:
            instances = instances[:2]

        for pddl_domain, pddl_instance in instances:

            instance_name = pddl_instance.replace(PDDL_EXTENSION, '')
            solution_name = f'{domain.name}_{instance_name}.sol'
            script_name = f'{self.environment.name}_{planner_name}_{domain.name}_{instance_name}.sh'
            path2domain = path.join(domain.path, pddl_domain)
            path2instance = path.join(domain.path, pddl_instance)
            path2solution = path.join(solution_folder, solution_name)
            stde = path.abspath(path.join(solution_folder, f'err_{domain.name}_{instance_name}.txt'))
            stdo = path.abspath(path.join(solution_folder, f'out_{domain.name}_{instance_name}.txt'))
            planner_exe = planner.get_cmd(path2domain, path2instance, path2solution)

            # Collecting info
            info_dict[planner.name][domain.name][instance_name] = {}
            info_dict[planner.name][domain.name][instance_name][DOMAIN_PATH] = path2domain
            info_dict[planner.name][domain.name][instance_name][INSTANCE_PATH] = path2instance
            info_dict[planner.name][domain.name][instance_name][SOLUTION_PATH] = path2solution
            info_dict[planner.name][domain.name][instance_name][STDE] = stde
            info_dict[planner.name][domain.name][instance_name][STDO] = stdo
            info_dict[planner.name][domain.name][instance_name][PLANNER_EXE] = planner_exe
            #################
            
            copy_planner_dst, planner_source = manage_planner_copy(
                self.systems_tmp_folder, self.environment.name, planner, domain, instance_name, exp_id)

            if domain.validation_path is None:
                val = NO_VALIDATION_PERFORMED
            else:
                path_to_domain4val = path.join(domain.validation_path, pddl_domain)
                path_to_instance4val = path.join(domain.validation_path, pddl_instance)
                val = '{}#{}'.format(path_to_domain4val, path_to_instance4val)
                info_dict[planner.name][domain.name][instance_name][VAL_DOMAIN_PATH] = path_to_domain4val
                info_dict[planner.name][domain.name][instance_name][VAL_INSTANCE_PATH] = path_to_instance4val
            
            info_dict[planner.name][domain.name][instance_name][VALIDATION] = val

            builder = ScriptBuilder(self.environment, 
                                    system=planner,
                                    domain_name=domain.name,
                                    instance_name=instance_name,
                                    results=info_dict_path,
                                    system_dst=path.abspath(copy_planner_dst),
                                    time=str(self.environment.time),
                                    memory=str(self.environment.memory),
                                    system_exe=planner_exe,
                                    stdo=stdo, 
                                    stde=stde, 
                                    script_name=script_name,
                                    info_dict_path=info_dict_path, 
                                    script_folder=self.script_folder)
            
            inner_script, outer_script = builder.get_script()
            write_script(inner_script, script_name, self.script_folder)
            write_script(outer_script, f'run_{script_name}', self.script_folder)
            script_list.append((script_name.replace('.sh', ''), path.join(self.script_folder, f'run_{script_name}')))

    
    def execute_scripts(self, script_list: List[str]):
        # Qsub logs setup
        os.makedirs(self.log_folder)
        #################

        if self.environment.qsub:

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
                print(qsub_cmd)
                os.system(qsub_cmd)
        else:
            scripts = [script for _, script in script_list]
            with Pool(self.environment.parallel_processes) as p:
                p.map(run_script, scripts)