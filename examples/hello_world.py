from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
from os import path
import pkg_resources

PDDL_PATH = pkg_resources.resource_filename(__name__, 'pddl/')
MY_PLANNER_PATH = path.join(pkg_resources.resource_filename(__name__, 'systems/'), 'MyPlanner')


class MyPlannerWrapper(Planner):

    def __init__(self, name: str, planner_path: str, search_engine: str, heuristic: str) -> None:
        super().__init__(name, planner_path)
        self.search_engine = search_engine
        self.heuristic = heuristic

    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'python ./MyPlanner/my_planner.py {self.search_engine} {self.heuristic} {domain_path} {instance_path} {solution_path}'
    

def main():

    results_folder = pkg_resources.resource_filename(__name__, 'HELLO_WORLD')
    env = Environment(results_folder, name='TEST')
    
    my_planner = MyPlannerWrapper('my_planner', MY_PLANNER_PATH, search_engine="astar", heuristic="hmax")

    blocksworld = Domain('blocksworld', path.join(PDDL_PATH, 'blocksworld'))
    rovers = Domain('rovers', path.join(PDDL_PATH, 'rovers'))

    env.add_run(system=my_planner, domains=[blocksworld, rovers])
    env.set_time(10)
    executor = Executor(env)
    executor.run_experiments()

if __name__ == "__main__":
    main()
