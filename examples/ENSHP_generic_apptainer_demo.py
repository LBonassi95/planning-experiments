from distutils.command.config import config
import planning_experiments
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
from planning_experiments.data_structures.parameters import *
import click
from os import path
import pkg_resources


PDDL_PATH = pkg_resources.resource_filename(__name__,'pddl/')


class ENSHP_PlannerWrapper(ApptainerPlanner):
    def __init__(self, name: str, params:ENSHP_Param, apptainer_planner_name: str) -> None:
        super().__init__(name, params, apptainer_planner_name)
    def get_cmd(self, domain_path, instance_path, solution_path):
        return f'apptainer run {self.apptainer_planner_name}  {domain_path} {instance_path} {solution_path} {self.params.get_parameters_cmd()}'
   # return f'apptainer run {self.apptainer_planner_name} domain.pddl p01.pddl sol get_parameters() 
  # get parameters ritornerà una stringa che ha tipo "-h euristica" "-s search_engine exx"

def main():
    results_folder = pkg_resources.resource_filename(__name__, 'Apptainer_ENHSP_TEST_RESULT')
    params = ENSHP_Param('gbfs','hadd','None')
    env = Environment (results_folder,name="ENHSP_TEST",planner_name='enhsp',recipe_name='Apptainer.enhsp_generic')

    planner = ENSHP_PlannerWrapper('my_ENSHP_planner',params,apptainer_planner_name='enhsp')
    #planner1 = ENSHP_PlannerWrapper('my_ENSHP_planner',ENSHP_PATH,params)
    fnCounters = Domain('fnCounters',path.join(PDDL_PATH,'fn-counters'))

    env.add_run(system=planner,  domains=[fnCounters] )
    #env.add_run(system=planner,  domains=[Depots_Numeric,fnCounters] )
    #env.add_run(system=planner1,  domains=[Depots_Numeric,fnCounters] )
    env.set_time(None)
    env.set_memory(None)
    executor = Executor(env,planner)
    executor.run_experiments()
    


if __name__ == "__main__":
    main()

