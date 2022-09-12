import os
import os.path as path
import sys
import random
import datetime
from planning_experiments.constants import *
from planning_experiments.experiment_environment import Domain, ExperimentEnviorment, System
from planning_experiments.script_builder import ScriptBuilder
from planning_experiments.utils import *
from typing import List


class Executor:

    def __init__(self, environment: ExperimentEnviorment, short_name: str = '') -> None:
        self.environment = environment
        self.short_name = short_name
        self.script_folder = None
        self.results_folder = None
        self.systems_tmp_folder = None
        self.log_folder = None
    
    def run_experiments(self, test_run: bool = False):
        exp_id = self.short_name + str(datetime.datetime.now()).replace(' ', '_') + '_{}'.format(str(random.randint(0, sys.maxsize)))
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

        for planner in self.environment.run_dictionary.keys():
            for domain in self.environment.run_dictionary[planner][DOMAINS]:
                self._create_script(planner, domain, exp_id, script_list, test_run)
                
        return script_list
  
    def _create_script(self, planner: System, domain: Domain, exp_id: str, script_list: List[str], test_run: bool):
        planner_name = planner.get_name()
        solution_folder, results_file = create_results_folder(self.results_folder, exp_id, planner_name, domain.name)
        
        instances = collect_instances(domain.path)
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
            
            copy_planner_dst, planner_source = manage_planner_copy(
                self.systems_tmp_folder, self.environment.name, planner, domain, instance_name, exp_id)

            if domain.validation_path is None:
                val = NO_VALIDATION_PERFORMED
            else:
                path_to_domain4val = path.join(domain.validation_path, pddl_domain)
                path_to_instance4val = path.join(domain.validation_path, pddl_instance)
                val = '{}#{}'.format(path_to_domain4val, path_to_instance4val)

            collect_data_cmd = get_collect_cmd(self.environment, 
                                                solution_name, 
                                                solution_folder,
                                                domain.name, 
                                                instance_name, 
                                                stdo, 
                                                stde, 
                                                results_file, 
                                                planner_name, 
                                                val)

            builder = ScriptBuilder(self.environment, planner,
                                    system_dst=path.abspath(copy_planner_dst),
                                    time=str(self.environment.time), memory=str(self.environment.memory),
                                    system_exe=planner_exe, collect_data_cmd=collect_data_cmd, 
                                    stdo=stdo, stde=stde, script_name=script_name, script_folder=self.script_folder)
            
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
            for (script_name, script) in script_list:
                os.system(f'chmod +x {script}')
                os.system(script)