import planning_experiments
from planning_experiments.experiment_environment import ExperimentEnviorment, MetaSystem, Domain
from planning_experiments.launch_experiments import Executor
import click
from os import path

BLOCKSWORLD_PATH = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/pddl_benchmarks/'
SYSTEMS_PATH = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/systems'


class FastPlanner(MetaSystem):

    def __init__(self) -> None:
        super().__init__()

    def name(self):
        return 'FastPlanner'

    def path(self):
        return path.join(SYSTEMS_PATH, 'system1')

    def get_cmd(self, domain, instance, solution, config):
        return f'launch.sh --domain {domain} --instance {instance} --solution {solution} --configuration {config}'


class SlowPlanner(MetaSystem):

    def __init__(self) -> None:
        super().__init__()

    def name(self):
        return 'SlowPlanner'

    def path(self):
        return path.join(SYSTEMS_PATH, 'system2')

    def get_cmd(self, domain, instance, solution, config):
        return f'launch.sh --d {domain} --p {instance} --sol {solution} -c {config}'


# @click.option('--short_name', '-n', default='')
def main():
    no_qsub = False
    planners_folder = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/systems'

    env = ExperimentEnviorment(planners_folder, name='TEST')

    system1 = FastPlanner()
    system2 = SlowPlanner()

    blocksworld_1 = Domain('blocksworld1', path.join(
        BLOCKSWORLD_PATH, 'blocksworld1'), path.join(BLOCKSWORLD_PATH, 'blocksworld1'))
    blocksworld_2 = Domain('blocksworld2', path.join(
        BLOCKSWORLD_PATH, 'blocksworld2'), path.join(BLOCKSWORLD_PATH, 'blocksworld2'))

    system1_configs = ["CONFIG1", "CONFIG2"]
    system2_configs = ["CONFIG1", "CONFIG3"]

    env.add_run(system1, system1_configs, [blocksworld_1])
    env.add_run(system2, system2_configs, [blocksworld_1, blocksworld_2])

    executor = Executor(env, short_name='')
    executor.run_experiments()

    # path_to_domains = cfg_dict[PATH_TO_DOMAINS]
    # memory = cfg_dict[MEMORY]
    # time = cfg_dict[TIME]

    # collect_runs(run_dict, path_to_domains)

    # script_list = create_scripts(
    #     name, exp_id, run_dict, memory, time, path_to_domains, short_name)

    # execute_scripts(name, script_list, cfg_dict[PPN], cfg_dict[PRIORITY], no_qsub)


if __name__ == "__main__":
    main()
