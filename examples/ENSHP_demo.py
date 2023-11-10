from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
import click
from os import path
import pkg_resources

ENSHP_PATH = "/Users/mattiatanchis/ENHSP-Public" #path of ENSHP

class ENSHP_PlannerWrapper(Planner):
    def __init__(self, name: str, planner_path: str) -> None:
        super().__init__(name, planner_path)
    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'java -jar ./ENHSP-Public/enhsp.jar  -o {domain_path} -f {instance_path} -sp {solution_path}'

