
class Parameters:
    def __init__(self ) -> None:
       self
    
    def get_parameters(self) -> str: 
        raise NotImplementedError
    
    def __eq__(self) -> bool:
        raise NotImplementedError
    
    def get_parameters_cmd(self) -> str:
        raise NotImplementedError


class ENSHP_Param(Parameters):
    def __init__(self, search_engine: str, heuristics: str, other_parameters: list[str]) -> None:
        super().__init__()
        self.search_engine = search_engine
        self.heuristics = heuristics
        self.other_parameters = other_parameters
        self.params = {'-h': self.heuristics, '-s': self.search_engine}#[('-h'), ('-g')]

    def get_heuristics(self) -> str :
        return self.heuristics    
    
    def get_search_engine(self) -> str:
        return self.search_engine
    
    def get_others(self) -> str:
         if(self.other_parameters is not None):
            params = ", ".join(self.parameters)
            return params
         else:
             return ""

    def get_parameters(self) -> str:
        return "search_engine: " + self.search_engine +", heuristics: " + self.heuristics + ", others: " + self.get_others()

    def get_parameters_cmd(self) -> str:
     items_as_strings = [f"{key}: {value}" for key, value in self.params.items()]
     return ''.join(items_as_strings)
    
    

        
    

