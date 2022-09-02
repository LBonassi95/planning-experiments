from os import path
from planning_experiments.experiment_environment import ExperimentEnviorment, System


class ScriptBuilder:

    BASH = "#!/bin/bash"
    PWD = "var=$PWD"

    def __init__(self, env: ExperimentEnviorment, system: System, system_dst: str, time: int, 
                       system_exe: str, collect_data_cmd: str, stdo: str, stde: str, memory: int = None) -> None:
        self.system = system
        self.enviorment = env
        self.script = []
        self.memory = memory
        self.system_dst = system_dst
        self.time = time
        self.system_exe = system_exe
        self.collect_data_cmd = collect_data_cmd
        self.stdo = stdo
        self.stde = stde
        
    def get_script(self):
        self.script.append(self.BASH)
        self.script.append(self.PWD)

        if self.memory is not None:
            self.script.append(f'ulimit -v {self.memory}')

        self.script.append(f'mkdir {self.system_dst}')

        self.manage_dependencies()
        exe_str = self.manage_complex_cmd()

        self.script.append(f'cd {self.system_dst}')
        self.script.append(f'/usr/bin/time -f "Total Runtime: %e" timeout --signal=HUP {self.time} {exe_str}')
        self.script.append(self.collect_data_cmd)
        if self.enviorment.delete_systems:
            self.script.append(f'rm -r -f {self.system_dst}')
        
        return '\n'.join(self.script)
    
    def set_memory(self, memory: int):
        self.memory = memory

    def manage_dependencies(self):
        dependencies = set([dep for dep in self.system.get_dependencies()])
        for dep in dependencies:
            self.script.append(f'cp -r {path.abspath(dep)} {self.system_dst}')
    
    def manage_complex_cmd(self):
        if isinstance(self.system_exe, list):
            cmd_chain = []
            for cmd in self.system_exe:
                cmd_chain.append(cmd)
                cmd_chain.append(f"2>> {self.stde} 1>> {self.stdo};")
            return ' '.join(cmd_chain)
        else:
            exe_str = self.system_exe + f" 2>> {self.stde} 1>> {self.stdo}"
        return exe_str

