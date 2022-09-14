from planning_experiments.experiment_environment import Planner

class SingularityPlannerWrapper(Planner):

    def __init__(self, name: str, path: str) -> None:
        super().__init__(name)
        self.name = name
        self.fd_path = path

    def get_name(self):
        return self.name

    def get_path(self):
        return self.fd_path

    def get_cmd(self, domain, instance, solution):
        return f'./{self.name}.img {domain} {instance} {solution}'