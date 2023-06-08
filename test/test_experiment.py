from distutils.command.config import config
import planning_experiments
from planning_experiments.experiment_environment import ExperimentEnviorment, System, Domain, Planner, Compiler
from planning_experiments.launch_experiments import Executor
import click
from os import path
from planning_experiments.utils import add_configutation
import pkg_resources

BLOCKSWORLD_PATH = pkg_resources.resource_filename(__name__, 'pddl_benchmarks/')
SYSTEMS_PATH = pkg_resources.resource_filename(__name__, 'systems/')


class FDWrapper(Planner):

    def __init__(self, name: str, fd_path: str, alias: str = None, search_params: str = None) -> None:
        super().__init__(name)
        self.name = name
        self.fd_path = fd_path
        self.alias = alias
        self.search_params = search_params
        if alias is None and search_params is None:
            raise Exception('Please select an alias or provide a search option')
        elif alias is not None and search_params is not None:
            raise Exception('...')

    def get_name(self):
        return self.name

    def get_path(self):
        return self.fd_path

    def get_cmd(self, domain, instance, solution):
        if self.alias is not None:
            return f'./fast-downward/fast-downward.py --alias {self.alias} --plan-file {solution} {domain} {instance}'
        else:
            return f'./fast-downward/fast-downward.py --plan-file {solution} {domain} {instance} {self.search_params}'


class TcoreWrapper(Compiler):

    def __init__(self, name: str, tcore_path: str, system: System) -> None:
        super().__init__(name, system)
        self.name = name
        self.tcore_path = tcore_path

    def get_path(self):
        return self.tcore_path

    def get_cmd(self, domain, instance, solution):
        return [f'python ./tcore/tcore/launch_tcore.py {domain} {instance} .', self.system.get_cmd("compiled_dom.pddl", "compiled_prob.pddl", solution)]


class TcoreInfoWrapper(Compiler):

    def __init__(self, name: str, tcore_path: str) -> None:
        super().__init__(name, None)
        self.name = name
        self.tcore_path = tcore_path

    def get_path(self):
        return self.tcore_path

    def get_cmd(self, domain, instance, solution):
        solution_filename = path.basename(solution).replace(".sol", "")
        solutions_dir = path.dirname(solution)
        return [f'python ./tcore/tcore/launch_tcore.py {domain} {instance} .',
                f'mv ./compiled_dom.pddl {path.join(solutions_dir, f"compiled_dom_{solution_filename}.pddl")}',
                f'mv ./compiled_prob.pddl {path.join(solutions_dir, f"compiled_prob_{solution_filename}.pddl")}']


# @click.option('--short_name', '-n', default='')
def main():
    fd_path = path.join(SYSTEMS_PATH, 'fast-downward')
    experiments_folder = pkg_resources.resource_filename(__name__, 'FIRST_TEST')

    env = ExperimentEnviorment(experiments_folder, name='TEST')

    system1 = FDWrapper('lama_first', fd_path, alias='lama-first')

    blocksworld_1 = Domain('blocksworld1', path.join(
        BLOCKSWORLD_PATH, 'blocksworld1'), path.join(BLOCKSWORLD_PATH, 'blocksworld1'))
    blocksworld_2 = Domain('blocksworld2', path.join(BLOCKSWORLD_PATH, 'blocksworld2'))

    for system in [system1]:
        env.add_run(system=system, domains=[blocksworld_1, blocksworld_2])

    env.set_qsub(False)
    env.set_conda_env('planning')

    executor = Executor(env, short_name='')
    executor.run_experiments()

if __name__ == "__main__":
    main()
