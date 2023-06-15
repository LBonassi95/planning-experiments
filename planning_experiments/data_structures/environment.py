from typing import List, Tuple
import os
from planning_experiments.constants import *
from planning_experiments.data_structures.system import System
from planning_experiments.data_structures.domain import Domain
import pkg_resources

DEFAULT_MEM = 8000000
DEFAULT_TIME = 1800

ERROR_SYSTEM_ALREADY_ADDED = "System {} was already added to the environment"


class Environment:

    SCRIPTS_FOLDER = 'scripts'
    RESULTS_FOLDER = 'results'

    def __init__(self, experiments_folder: str, name: str) -> None:
        self.experiments_folder = experiments_folder
        self.run_dictionary = {}
        self.name = name
        self.memory = DEFAULT_MEM
        self.time = DEFAULT_TIME
        self.delete_systems = True
        self.clean_logs = True
        self.clean_scripts = True
        self.clean_systems = True
        self.ppn = 2
        self.priority = 500
        self.qsub = False
        self.parallel_processes = 8

    def add_run(self, system: System, domains: List[Domain]):

        if self.run_dictionary.get(system, None) != None:
            raise Exception(ERROR_SYSTEM_ALREADY_ADDED.format(system))
        else:
            self.run_dictionary[system] = {}
            self.run_dictionary[system][DOMAINS] = domains
    
    def set_memory(self, memory: int):
        self.memory = memory
    
    def set_time(self, time: int):
        self.time = time

    def set_delete_systems(self, clean: bool):
        self.delete_systems = clean
    
    def set_clean_systems(self, clean: bool):
        self.clean_systems = clean
    
    def set_clean_scripts(self, clean: bool):
        self.clean_scripts = clean

    def set_clean_logs(self, clean: bool):
        self.clean_logs = clean
    
    def set_ppn(self, ppn: int):
        self.ppn = ppn
    
    def set_priority(self, priority: int):
        self.priority = priority 
    
    def set_qsub(self, qsub: bool):
        self.qsub = qsub

    def set_parallel_processes(self, parallel_processes: int):
        self.parallel_processes = parallel_processes