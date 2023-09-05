from typing import List, Tuple
import os
from planning_experiments.constants import *
from planning_experiments.data_structures.system import System
from planning_experiments.data_structures.domain import Domain
import pkg_resources
from enum import Enum, auto

DEFAULT_MEM = 8000000
DEFAULT_TIME = 1800

class ExperimentMode(Enum):
    QSUB = auto()
    MULTIPROCESSING = auto()


MODALITIES = frozenset([
    ExperimentMode.QSUB,
    ExperimentMode.MULTIPROCESSING,
    ])
    

ERROR_SYSTEM_ALREADY_ADDED = '''
System "{system}" was already added to the environment.
If you want to run "{system}" multiple times, 
please create a new environment or assing different names to the system.
Example: define "{system}-1" and "{system}-2".
'''


class Environment:

    SCRIPTS_FOLDER = 'scripts'
    RESULTS_FOLDER = 'results'

    def __init__(self, experiments_folder: str, 
                name: str,
                memory: int = DEFAULT_MEM,
                timeout: int = DEFAULT_TIME,
                delete_temporary_systems: bool = True,
                qsub_ppn: int = 2,
                qsub_priority: int = 500,
                mode: Enum = ExperimentMode.MULTIPROCESSING,
                parallel_processes: int = 8
                ) -> None:
        self.experiments_folder = experiments_folder
        self.run_dictionary = {}
        self.name = name
        self.memory = memory
        self.timeout = timeout
        self.delete_temporary_systems = delete_temporary_systems
        self.qsub_ppn = qsub_ppn
        self.qsub_priority = qsub_priority
        self.mode = mode
        assert self.mode in MODALITIES
        self.parallel_processes = parallel_processes

    def add_run(self, system: System, domains: List[Domain]):

        if self.run_dictionary.get(system, None) is not None:
            raise Exception(ERROR_SYSTEM_ALREADY_ADDED.format(system=system))
        else:
            self.run_dictionary[system] = {}
            self.run_dictionary[system][DOMAINS] = domains

    def get_info(self):
        data = [
            ["Environment", self.name],
            ["Memory", f'{self.memory} KB'],
            ["Time", f'{self.timeout}s'],
        ]
        if self.mode == ExperimentMode.QSUB:
            data.append(["Qsub", "True"])
            data.append(["PPN", self.qsub_ppn])
            data.append(["Priority", self.qsub_priority])
        else:
            data.append(["Multiprocessing", "True"])
            data.append(["Parallel processes", self.parallel_processes])
        return data