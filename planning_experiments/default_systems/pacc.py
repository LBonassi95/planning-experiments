from planning_experiments.experiment_environment import Compiler
from planning_experiments.experiment_environment import System


class PACCWrapper(Compiler):

    def __init__(self, name: str, pacc_path: str, system: System, simplify_goal = False) -> None:
        super().__init__(name, system)
        self.name = name
        self.pacc_path = pacc_path
        self.simplify_goal = simplify_goal

    def get_path(self):
        return self.pacc_path

    def get_cmd(self, domain, instance, solution):
        cmd = f'python ./PAC-C/launch_PAC_C.py {domain} {instance} .'
        if self.simplify_goal:
            raise Exception('PACC does not support simplify-goal')
        return [cmd, self.system.get_cmd("compiled_dom.pddl", "compiled_prob.pddl", solution)]