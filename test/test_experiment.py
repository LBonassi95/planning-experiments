from distutils.command.config import config
import planning_experiments
from planning_experiments.experiment_environment import ExperimentEnviorment, System, Domain, Configuration
from planning_experiments.launch_experiments import Executor
import click
from os import path
from planning_experiments.utils import add_configutation

BLOCKSWORLD_PATH = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/pddl_benchmarks/'
SYSTEMS_PATH = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/systems'


class FDWrapper(System):

    def __init__(self, name: str, fd_path: str, alias: str = None, search_params: str = None) -> None:
        super().__init__()
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
            return f'./fast-downward.py --alias {self.alias} --plan-file {solution} {domain} {instance}'
        else:
            return f'./fast-downward.py --plan-file {solution} {domain} {instance} {self.search_params}'


# @click.option('--short_name', '-n', default='')
def main():
    no_qsub = False
    fd_path = path.join(SYSTEMS_PATH, 'fast-downward')
    experiments_folder = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/FIRST_TEST'

    env = ExperimentEnviorment(experiments_folder, name='TEST')

    system1 = FDWrapper('lama_first', fd_path, alias='lama-first')
    system2 = FDWrapper('astar_hmax', fd_path, search_params='--search "astar(hmax)"')
    system3 = FDWrapper('astar_ff', fd_path, search_params='--search "astar(ff)"')

    blocksworld_1 = Domain('blocksworld1', path.join(
        BLOCKSWORLD_PATH, 'blocksworld1'), path.join(BLOCKSWORLD_PATH, 'blocksworld1'))
    #blocksworld_2 = Domain('blocksworld2', path.join(BLOCKSWORLD_PATH, 'blocksworld2'))

    for system in [system1]:
        env.add_run(system=system, domains=[blocksworld_1])

    executor = Executor(env, short_name='')
    executor.run_experiments()


if __name__ == "__main__":
    main()
