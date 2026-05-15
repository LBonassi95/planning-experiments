from planning_experiments import RunContext
from planning_experiments.data_structures import *
from planning_experiments.launch_experiments import Executor
from pathlib import Path

PDDL_PATH = Path(__file__).parent /  "pddl"
MY_PLANNER_PATH = Path(__file__).parent / "systems" / "MyPlanner"


class MyPlannerWrapper(Planner):

    def __init__(self, name: str, planner_path: str, search_engine: str, heuristic: str) -> None:
        super().__init__(name=name, planner_root=planner_path, launch_script="my_planner.py")
        self.search_engine = search_engine
        self.heuristic = heuristic

    def get_cmd(self, ctx: RunContext) -> str:
        return f'python3.12 ./planner/{self.launch_script} {self.search_engine} {self.heuristic} {ctx.domain_path} {ctx.problem_path} {ctx.solution_path}'
    

def main():

    results_folder = Path(__file__).parent / 'HELLO_WORLD'
    env = Environment(experiments_root=str(results_folder), experiment_group="test")
    
    my_planner = MyPlannerWrapper('my_planner', str(MY_PLANNER_PATH), search_engine="astar", heuristic="hmax")

    blocksworld = Domain('blocksworld', str(PDDL_PATH / 'blocksworld'))
    rovers = Domain('rovers', str(PDDL_PATH / 'rovers'))

    env.add_run(system=my_planner, domains=[blocksworld, rovers])
    env.set_delete_systems(False)
    env.set_time(10)
    env.set_qsub(True)
    executor = Executor(env)
    executor.run_experiments()

if __name__ == "__main__":
    main()
