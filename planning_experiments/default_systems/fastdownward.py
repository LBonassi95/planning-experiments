from planning_experiments.experiment_environment import Planner

class FDWrapper(Planner):

    def __init__(self, name: str, path: str, alias: str = None, search_params: str = None) -> None:
        super().__init__(name)
        self.name = name
        self.path = path
        self.alias = alias
        self.search_params = search_params
        if alias is None and search_params is None:
            raise Exception('Please select an alias or provide a search option')
        elif alias is not None and search_params is not None:
            raise Exception('...')

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def get_cmd(self, domain, instance, solution) -> list:
        
        if self.alias is not None:
            return [f'echo "python ./fast-downward/fast-downward.py --alias {self.alias} --plan-file {solution} {domain} {instance}"', f'python ./fast-downward/fast-downward.py --alias {self.alias} --plan-file {solution} {domain} {instance}']
        else:
            return [f'python ./fast-downward/fast-downward.py --plan-file {solution} {domain} {instance} {self.search_params}']