from planning_experiments.constants import *

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
    def __init__(self) -> None:
        pass

    def get_cmd(self, domain: str, instance: str, solution: str) -> str:
        raise NotImplementedError
    
    def get_name(self) -> str:
        raise NotImplementedError
    
    def get_path(self)-> str:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.get_name())
    
    def __repr__(self) -> str:
        return self.get_name()

class ExperimentEnviorment:

    SCRIPTS_FOLDER = 'scripts'
    RESULTS_FOLDER = 'results'

    def __init__(self, experiments_folder: str, name: str) -> None:
        self.experiments_folder = experiments_folder
        self.run_dictionary = {}
        self.name = name
        self.memory = DEFAULT_MEM
        self.time = DEFAULT_TIME

    def add_run(self, system: System, domains: list[Domain]):

        if self.run_dictionary.get(system, None) != None:
            raise Exception(ERROR_SYSTEM_ALREADY_ADDED.format(system))
        else:
            self.run_dictionary[system] = {}
            self.run_dictionary[system][DOMAINS] = domains
    
    def set_memory(self, memory: int):
        self.memory = memory
    
    def set_time(self, time: int):
        self.time = time
