from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
import click
from os import path
import pkg_resources

PDDL_PATH = pkg_resources.resource_filename(__name__, 'pddl/')
MY_PLANNER_PATH = path.join(pkg_resources.resource_filename(__name__, 'systems/'), 'MyPlanner')


class MyPlannerWrapper(Planner):

    def __init__(self, name: str, planner_path: str) -> None:
        super().__init__(name, planner_path)

    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'enhsp {self.search_engine} {self.heuristic} {domain_path} {instance_path} {solution_path}'
    

def main():
    results_folder = pkg_resources.resource_filename(__name__, 'TEST_RESULT')
    params=["astar","hmax"]
    env = Environment(params,results_folder, name='TEST')
    
    my_planner = MyPlannerWrapper('my_planner', MY_PLANNER_PATH, search_engine="astar", heuristic="hmax")

    car_non_linear = Domain('car-non-linear', path.join(PDDL_PATH, 'car-non-linear'))

    env.add_run(system=my_planner, domains=[car_non_linear])
    env.set_time(None)
    env.set_memory(None)
    executor = Executor(env,search_engine="astar", heuristic="hmax")
    executor.run_experiments()

if __name__ == "__main__":
    main()
