from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
import click
from os import path
import pkg_resources

PDDL_PATH = pkg_resources.resource_filename(__name__, 'pddl/')
FD_PATH = path.join(pkg_resources.resource_filename(__name__, 'systems/'), 'fast-downward')


class FDWrapper(Planner):

    def __init__(self, name: str, planner_path: str, search_params: str = None) -> None:
        super().__init__(name, planner_path)
        self.search_params = search_params

    def get_name(self):
        return self.name

    def get_cmd(self, domain, instance, solution):
        return f'./fast-downward/fast-downward.py --plan-file {solution} {domain} {instance} --search {self.search_params}'


def main():

    experiments_folder = pkg_resources.resource_filename(__name__, 'CLASSICAL_PLANNING_EXAMPLE')

    env = Environment(experiments_folder, name='TEST')

    astar_lmcut = FDWrapper('astar_lmcut', FD_PATH, search_params='"astar(lmcut())"')
    astar_add = FDWrapper('astar_add', FD_PATH, search_params='"astar(add())"')

    blocksworld = Domain('blocksworld', path.join(PDDL_PATH, 'blocksworld'))
    rovers = Domain('rovers', path.join(PDDL_PATH, 'rovers'))

    env.add_run(system=astar_lmcut, domains=[blocksworld, rovers])
    env.add_run(system=astar_add, domains=[blocksworld, rovers])

    executor = Executor(env)
    executor.run_experiments()

if __name__ == "__main__":
    main()
