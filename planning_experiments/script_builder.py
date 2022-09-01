
class ScriptBuilder:

    BASH = "#!/bin/bash"
    PWD = "var=$PWD"

    def __init__(self, system_src: str, system_dst: str, time: int, system_exe, collect_data_cmd: str, memory: int = None) -> None:
        self.script = []
        self.memory = memory
        self.system_src = system_src
        self.system_dst = system_dst
        self.time = time
        self.system_exe = system_exe
        self.collect_data_cmd = collect_data_cmd
        
    def get_script(self):
        self.script.append(self.BASH)
        self.script.append(self.PWD)

        if self.memory is not None:
            self.script.append(f'ulimit -v {self.memory}')

        self.script.append(f'mkdir {self.system_dst}')
        self.script.append(f'cp -r {self.system_src}/* {self.system_dst}')
        self.script.append(f'cd {self.system_dst}')
        self.script.append(f'/usr/bin/time -f "Total Runtime: %e" timeout --signal=HUP {self.time} {self.system_exe}')
        self.script.append(f'rm -r -f {self.system_dst}')
        self.script.append(self.collect_data_cmd)
        return '\n'.join(self.script)
    
    def set_memory(self, memory: int):
        self.memory = memory

