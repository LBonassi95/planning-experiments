from typing import List

class System:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_cmd(self) -> List[str]:
        raise NotImplementedError
    
    def get_name(self) -> str:
        return self.name
    
    def get_path(self)-> str:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.get_name())
    
    def __repr__(self) -> str:
        return self.get_name()
    
    def get_dependencies(self) -> List[str]:
        raise NotImplementedError

class Planner(System):

    def __init__(self, name: str, planner_path: str) -> None:
        super().__init__(name)
        self.planner_path = planner_path

    def get_cmd(self, domain: str, instance: str, solution: str) -> List[str]:
        raise NotImplementedError
    
    def get_path(self) -> str:
        return self.planner_path
    
    def get_dependencies(self) -> List[str]:
        return [self.get_path()]

# FOR NOW, A COMPILER CAN BE CHAINED ONLY WITH A PLANNER (NOT ANOTHER COMPLIER!)
class Compiler(Planner):
    def __init__(self, name: str, compiler_path: str, system: System = None) -> None:
        super().__init__(name, compiler_path)
        self.system = system

    def get_cmd(self, domain: str, instance: str, solution: str) -> List[str]:
        return super().get_cmd()

    def get_name(self) -> str:
        if self.system is not None:
            return f'{self.name}_{self.system.get_name()}'
        else:
            return self.name
    
    def get_dependencies(self) -> List[str]:
        if self.system is not None:
            return [self.get_path()] + self.system.get_dependencies()
        else:
            return [self.get_path()]
        
    def make_shell_chain(self) -> str:
        raise NotImplementedError