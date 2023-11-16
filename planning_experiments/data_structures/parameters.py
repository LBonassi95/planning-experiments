
class Parameters:
    def __init__(self ) -> None:
       self
    
    def get_parameters(self) -> str: 
        raise NotImplementedError
    
class ENSHP_Param(Parameters):
    def __init__(self, search_engine: str, heuristics: str, other_parameters: list[str]) -> None:
        super().__init__()
        self.search_engine = search_engine
        self.heuristics = heuristics
        self.other_parameters = other_parameters
    def get_heuristics(self) -> str :
        return self.heuristics    
    def get_others(self) -> str:
         if(self.other_parameters is not None):
            params = ", ".join(self.parameters)
            return params
         else:
             return ""

    def get_parameters(self) -> str:
        return "search_engine: " + self.search_engine +", heuristics: " + self.heuristics + ", others: " + self.get_others()
        