from planning_experiments.experiment_environment import Compiler
from planning_experiments.experiment_environment import System


class TcoreWrapper(Compiler):

    def __init__(self, name: str, tcore_path: str, system: System, optimized = False, simplify_goal = False) -> None:
        super().__init__(name, system)
        self.name = name
        self.tcore_path = tcore_path
        self.optimized = optimized
        self.simplify_goal = simplify_goal

    def get_path(self):
        return self.tcore_path

    def get_cmd(self, domain, instance, solution):
        cmd = f'python ./bin/launch_tcore.py {domain} {instance} .'
        if self.optimized:
            cmd += ' --optimized'
        if self.simplify_goal:
            cmd += ' --simplify-goal'
        system_cmd = self.system.get_cmd("compiled_dom.pddl", "compiled_prob.pddl", solution)
        if isinstance(system_cmd, list):
            return [cmd] + system_cmd
        else:
            return [cmd, system_cmd]
