from typing import List
from planning_experiments.constants import *
import pkg_resources

DEFAULT_MEM = 8000000
DEFAULT_TIME = 1800

ERROR_SYSTEM_ALREADY_ADDED = "System {} was already added to ExperimentEnviorment"

class Domain:
    def __init__(self, name: str, path2pddl: str, validation_path: str = None) -> None:
        self.name = name
        self.path = path2pddl
        self.validation_path = validation_path
    
    def __repr__(self) -> str:
        return self.name


class Configuration:
    def __init__(self, name: str, parameters: list) -> None:
        self.name = name
        self.parameters = parameters
    
    def __repr__(self) -> str:
        return self.name
    

class System:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_cmd(self) -> List[str]:
        raise NotImplementedError
    
    def get_name(self) -> str:
        return self.name
    
    def get_path(self)-> str:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.get_name())
    
    def __repr__(self) -> str:
        return self.get_name()
    
    def get_dependencies(self) -> List[str]:
        raise NotImplementedError

class Planner(System):

    def __init__(self, name: str) -> None:
        super().__init__(name)

    def get_cmd(self, domain: str, instance: str, solution: str) -> List[str]:
        return super().get_cmd()
    
    def get_dependencies(self) -> List[str]:
        return [self.get_path()]

# FOR NOW, A COMPILER CAN BE CHAINED ONLY WITH A PLANNER (NOT ANOTHER COMPLIER!)
class Compiler(Planner):
    def __init__(self, name: str, system: System = None) -> None:
        super().__init__(name)
        self.system = system

    def get_cmd(self, domain: str, instance: str, solution: str) -> List[str]:
        return super().get_cmd()

    def get_name(self) -> str:
        if self.system is not None:
            return f'{self.name}_{self.system.get_name()}'
        else:
            return self.name
    
    def get_dependencies(self) -> List[str]:
        if self.system is not None:
            return [self.get_path()] + self.system.get_dependencies()
        else:
            return [self.get_path()]
        
    def make_shell_chain(self) -> str:
        raise NotImplementedError

class ExperimentEnviorment:

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
        self.qsub = True
        self.conda_env = None
        self.collect_data = pkg_resources.resource_filename(__name__, f'../{COLLECT_DATA_FOLDER}/collect_data.py')

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
    
    def set_conda_env(self, conda_env: str):
        self.conda_env = conda_env
    
    def set_collect_data(self, collect_data: str):
        self.collect_data = collect_data