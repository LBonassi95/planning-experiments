
class Parameters:
    def __init__(self, heuristics: str, search_engine: str , others: list ) -> None:
        self.heuristics = heuristics
        self.search_engine = search_engine
        self.others = others
    
    def get_heristics(self) -> str:
        return self.heuristics
    
    def get_search_engine(self) -> str:
        return self.search_engine
    
    def get_others(self) -> str:
         params = ", ".join(self.parameters)
         return params

    def get_parameters(self) -> str: 
        return "herustics: "+ self.heuristics + "search_enginge: " + self.search_engine + " others: " + self.get_others
    


   ##classe parameters generica con sottoclassi specifiche 