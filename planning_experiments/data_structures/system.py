from typing import List
import os

class RunContext:
    def __init__(self, domain_path: str, problem_path: str, solution_path: str, planner_path: str):
        self.domain_path = domain_path
        self.problem_path = problem_path
        self.solution_path = solution_path
        self.planner_path = planner_path

    def planner_command(self, launch_script: str, interpreter: str = None):
        """
        Given a launch_script, this function will build the command 
        to launch the planner from its sandbox
        """
        abs_script_path = os.path.join(self.planner_path, launch_script)

        if interpreter is None:
            return abs_script_path

        return f"{interpreter} {abs_script_path}"

class Planner:
    def __init__(self, name: str, planner_root: str, launch_script: str) -> None:
        self.name = name
        self.planner_root = planner_root
        self.launch_script = launch_script

    def get_cmd(self, ctx) -> List[str]:
        raise NotImplementedError
    
    def get_name(self) -> str:
        return self.name
    
    def get_path(self)-> str:
        return self.planner_root

    def __hash__(self) -> int:
        return hash((self.__class__, self.get_name()))
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Planner):
            return False
        return self.__hash__() == o.__hash__()
    
    def __repr__(self) -> str:
        return self.get_name()

# TODO: rethink how a PDDL compiler can be chained