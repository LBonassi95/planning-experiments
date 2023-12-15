from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
from planning_experiments.data_structures.parameters import *
import click
from os import path
import pkg_resources

ENSHP_PATH = "/Users/mattiatanchis/ENHSP-Public" #path of ENSHP
PDDL_PATH = pkg_resources.resource_filename(__name__,'pddl/')


class ENSHP_PlannerWrapper(ApptainerPlanner):
    def __init__(self, name: str, planner_path: str, params:ENSHP_Param) -> None:
        super().__init__(name, planner_path, params)
    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'java -jar ./ENHSP-Public/enhsp.jar -h {self.params.get_heuristics()} -s {self.params.get_search_engine()} -o {domain_path} -f {instance_path} -sp {solution_path}'
    def install_planner() -> str:
        return "enhsp.sif docker://enricos83/enhsp:latest"

def main():
    results_folder = pkg_resources.resource_filename(__name__, 'ENSHP_TEST_RESULTS')
    params = ENSHP_Param('gbfs','hadd',None)
    env = Environment (results_folder,name="ENSHP_TEST")

    planner = ENSHP_PlannerWrapper('my_ENSHP_planner',ENSHP_PATH,params)
    #planner1 = ENSHP_PlannerWrapper('my_ENSHP_planner',ENSHP_PATH,params)
    Depots_Numeric = Domain('Depots_Numeric',path.join(PDDL_PATH, 'Depots-Numeric'))
    fnCounters = Domain('fnCounters',path.join(PDDL_PATH,'fn-counters'))

    env.add_run(system=planner,  domains=[Depots_Numeric,fnCounters] )
    #env.add_run(system=planner,  domains=[Depots_Numeric,fnCounters] )
    #env.add_run(system=planner1,  domains=[Depots_Numeric,fnCounters] )
    env.set_time(None)
    env.set_memory(None)
    executor = Executor(env,planner)
    executor.run_experiments()
    


if __name__ == "__main__":
    main()

