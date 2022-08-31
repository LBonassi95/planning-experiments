from planning_experiments.constants import *

DEFAULT_MEM = 8000000
DEFAULT_TIME = 1800
DEFAULT_RESULTS_FOLDER = 'results'

ERROR_SYSTEM_ALREADY_ADDED = "System {} was already added to ExperimentEnviorment"

class Domain:
    def __init__(self, name: str, path2pddl: str, validation_path: str) -> None:
        self.name = name
        self.path = path2pddl
        self.validation_path = validation_path

class MetaSystem:
    def __init__(self) -> None:
        pass

    def get_cmd(self, domain, instance, solution):
        raise NotImplementedError
    
    def name(self):
        raise NotImplementedError
    
    def path(self):
        raise NotImplementedError
    
    def system_exe(self):
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.name())

class ExperimentEnviorment:

    def __init__(self, systems_folder: str, name: str) -> None:
        self.systems_folder = systems_folder
        self.run_dictionary = {}
        self.name = name
        self.memory = DEFAULT_MEM
        self.time = DEFAULT_TIME
        self.result_folder = DEFAULT_RESULTS_FOLDER

    def add_run(self, system: MetaSystem, configs: list[str], domains: list[Domain]):

        if self.run_dictionary.get(system, None) != None:
            raise Exception(ERROR_SYSTEM_ALREADY_ADDED.format(system))
        else:
            self.run_dictionary[system] = {}
            self.run_dictionary[system][DOMAINS] = domains
            self.run_dictionary[system][CONFIGS] = configs
    
    def set_memory(self, memory):
        self.memory = memory
    
    def set_time(self, time):
        self.time = time
    
    def set_results_folder(self, reuslts_folder):
        self.reuslts_folder = reuslts_folder

