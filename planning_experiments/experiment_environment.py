
class ExperimentEnviorment:

    def __init__(self, planners_folder: str, run_dictionary: dict, name: str) -> None:
        self.planners_folder = planners_folder
        self.run_dictionary = run_dictionary
        self.name = name