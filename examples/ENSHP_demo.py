from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
import click
from os import path
import pkg_resources

ENSHP_PATH = "/Users/mattiatanchis/ENHSP-Public" #path of ENSHP
PDDL_PATH = pkg_resources.resource_filename(__name__,'pddl/')


class ENSHP_PlannerWrapper(Planner):
    def __init__(self, name: str, planner_path: str) -> None:
        super().__init__(name, planner_path)
    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'java -jar ./ENHSP-Public/enhsp.jar  -o {domain_path} -f {instance_path} -sp {solution_path}'

def main():
    results_folder = pkg_resources.resource_filename(__name__, 'ENSHP_TEST_RESULTS')
    params=["astar","hmax"]
    env = Environment (params,results_folder,name="ENSHP_TEST")

    planner = ENSHP_PlannerWrapper('my_ENSHP_planner',ENSHP_PATH)
    Depots_Numeric = Domain('Depots_Numeric',path.join(PDDL_PATH, 'Depots-Numeric'))

    env.add_run(system=planner, domains=Depots_Numeric )
    env.set_time(None)
    env.set_memory(None)
    
