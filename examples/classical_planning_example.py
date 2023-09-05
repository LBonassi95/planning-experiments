from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
import click
from os import path
import pkg_resources


class FDWrapper(Planner):

    def __init__(self, name: str, src_path: str, search_params: str = None) -> None:
        super().__init__(name, src_path)
        self.search_params = search_params

    def get_cmd(self, 
                tmp_planner_path, # PATH TO THE FOLDER CONTAINING THE PLANNER
                domain_path, # PATH TO THE DOMAIN FILE
                instance_path, # PATH TO THE INSTANCE FILE
                solution_path # PATH POINTING TO THE SOLUTIION FOLDER
                ):
        return f'{tmp_planner_path}/fast-downward.py --plan-file {solution_path} {domain_path} {instance_path} --search {self.search_params}'
    

class LamaWrapper(Planner):

    def __init__(self, name: str, src_path: str) -> None:
        super().__init__(name, src_path)

    def get_cmd(self, tmp_planner_path, domain_path, instance_path, solution_path):
        return f'{tmp_planner_path}/fast-downward.py --alias lama --plan-file {solution_path} {domain_path} {instance_path}'


def main():

    experiments_folder = pkg_resources.resource_filename(__name__, 'RESULTS') # FOLDER CONTAINING RESULTS AND BOOKEEPING DATA

    env = Environment(experiments_folder=experiments_folder, 
                      name = 'CLASSICAL_PLANNING_TEST', # NAME OF THIS EXPERIMENT
                      timeout = 20, # MAXIMUM RUNTIME IN SEC
                      memory = 8000000, # MAXIMUM MEMORY IN KB
                      delete_temporary_systems=True, # AUTOMATICALLY DELETE COPIES OF THE SYSTEMS
                      parallel_processes = 8, # NUMBER OF PARALLEL PROCESSES FOR THIS EXPERIMENT
                      mode = ExperimentMode.MULTIPROCESSING # USE PYTHON MULTIPROCESSING TO HANDLE THE PARALLEL PROCESSES
                      ) 
    
    pddl_path = pkg_resources.resource_filename(__name__, 'pddl/')
    fast_downward_src_folder = path.join(pkg_resources.resource_filename(__name__, 'systems/'), 'fast-downward')
    
    # INSTANTIATE THE PLANNERS
    astar_lmcut = FDWrapper('astar_lmcut', fast_downward_src_folder, search_params='"astar(lmcut())"')
    lama = LamaWrapper('lama', fast_downward_src_folder)

    # INSTAINTIATE THE OBJECTS REPRESENTING THE PDDL DOMAINS
    # THE LIBRARY ASSUMES THAT THE PDDL FILES ARE ORGANIZED AS FOLLOWS:
    # domain_folder/
    #   - domain.pddl
    #   - {INSTANCE_X}.pddl
    #   - {INSTANCE_Y}.pddl
    #   - etc ...
    blocksworld = Domain('blocksworld', path.join(pddl_path, 'blocksworld'))
    rovers = Domain('rovers', path.join(pddl_path, 'rovers'))

    # ADD THE RUN TO THE ENVIRONMENT
    env.add_run(system=astar_lmcut, domains=[blocksworld, rovers])
    env.add_run(system=lama, domains=[blocksworld, rovers])

    # RUN THE EXPERIMENTS
    executor = Executor(env)
    executor.run_experiments()

if __name__ == "__main__":
    main()
