import planning_experiments
from planning_experiments.experiment_environment import ExperimentEnviorment
from planning_experiments.launch_experiments import Executor
import click

# can be created programmatically
run_dictionary = {

    "system1": {
        "DOMAINS": ["blocksworld"],
        "CONFIGS": ["DEFAULT"],
        "COLLECT": "collect_data_fd_ff.py",
        "DOMAINS4VAL": {"blocksworld":  "blocksworld"}
      },

      "system2": {
        "DOMAINS": ["blocksworld"],
        "CONFIGS": ["DEFAULT"],
        "COLLECT": "collect_data_fd_ff.py",
        "DOMAINS4VAL": {"blocksworld":  "blocksworld"}
      }
}

@click.option('--short_name', '-n', default='')
def main(short_name):
    no_qsub = False
    planners_folder = '/home/luigi/Desktop/projects_coding/ExperimentsArchitecture/test/systems'
    env = ExperimentEnviorment(planners_folder, run_dictionary, name='TEST')
    executor = Executor(env, short_name)
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