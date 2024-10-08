from os import path
from planning_experiments.data_structures.environment import Environment, System
from planning_experiments.constants import *

class ScriptBuilder:

    # BASH = "#!/bin/bash"
    # PWD = "var=$PWD"

    def __init__(self, env: Environment,
                       system: System,
                       domain_name: str,
                       instance_name: str,
                       blob_path: str,
                       system_dst: str,
                       time: int,
                       system_exe: str,
                       stdo: str,
                       stde: str,
                       script_name: str,
                       script_folder: str,
                       memory: int = None) -> None:
        
        self.system = system
        self.enviorment = env
        self.inner_script = []
        self.outer_script = []
        self.memory = memory
        self.system_dst = system_dst
        self.time = time
        self.system_exe = system_exe
        self.stdo = stdo
        self.stde = stde
        self.script_name = script_name
        self.script_folder = script_folder
        self.domain_name = domain_name
        self.instance_name = instance_name
        self.blob_path = blob_path

    def get_script(self):

        self.outer_script = [
            '#!/usr/bin/env python3\n',
            f'import os',
            f'import shutil\n',
            # f'{SAVE_RESULTS_SCRIPT}',
            # f'blob_path = "{self.blob_path}"\n'
            # f'planner = "{self.system}"\n'
            # f'domain = "{self.domain_name}"\n'
            # f'instance = "{self.instance_name}"\n'
            f'working_dir = "{self.system_dst}"\n',
            f'stde_path = "{self.stde}"',
            f'stdo_path = "{self.stdo}"',
            f'time_limit = {self.time}\n',
            f'exec_str = "{path.join(self.script_folder, f"{self.script_name}.sh")} 2>> " + stde_path + " 1>> " + stdo_path\n',
        ]


        dependencies = set([dep for dep in self.system.get_dependencies()])
        for i, dep in enumerate(dependencies):
            dep_basename = path.basename(dep)
            self.outer_script.append(f'system_{i}_src = "{path.abspath(dep)}"')
            self.outer_script.append(f'system_{i}_dst = "{path.join(self.system_dst, dep_basename)}"')


        self.outer_script += [
            '\n'
            f'open(stdo_path, "w")',
            f'open(stde_path, "w")',
            f'os.makedirs(working_dir)',
            f'os.chdir(working_dir)\n\n'
            f'################## COPY ALL SRC TO DST ##################'
        ]

        for i, dep in enumerate(dependencies):
            self.outer_script.append(f'shutil.copytree(system_{i}_src, system_{i}_dst)')


        self.outer_script += [f'#########################################################\n']


        exec_cmd = f'os.system(exec)'

        if self.time != "None":
            exec_cmd = f'os.system("time -p timeout --signal=HUP {self.time} " + exec_str)'
            # exec_cmd = f'limited_time_execution(os.system, stde, args=[exec], timeout=time_limit)'

        self.outer_script.append(exec_cmd)
       
        ## INNER SCRIPT ##
        # self.inner_script.append(f'#!/usr/bin/env python3\n')
        # self.inner_script.append(f'import os')

        # if self.memory != 'None':
        #     self.inner_script.append(f'os.system("ulimit -Sv {self.memory}")')

        self.inner_script.append('#!/bin/bash')
        if self.memory != 'None':
            self.inner_script.append(f'ulimit -Sv {self.memory}')

        exe_list = self.manage_complex_cmd()
        self.inner_script += exe_list

        
        #################
        # self.outer_script.append(f'save_results(blob_path, planner, domain, instance)')

        if self.enviorment.delete_systems:
            self.outer_script.append(f'shutil.rmtree("{self.system_dst}")')
        
        # save_results_path = pkg_resources.resource_filename(__name__, f'./bin/save_results.py')
        # self.outer_script.append(f'python {save_results_path} {self.results} {self.system.name} {self.domain_name} {self.instance_name}')
        
        inner_script_str = '\n'.join(self.inner_script)
        outer_script_str = '\n'.join(self.outer_script)
        return inner_script_str, outer_script_str
    
    def set_memory(self, memory: int):
        self.memory = memory
    
    def manage_complex_cmd(self):
        if isinstance(self.system_exe, list):
            cmd_chain = []
            for cmd in self.system_exe:
                #cmd_chain.append(f'os.system({json.dumps(cmd)})')
                cmd_chain.append(cmd)
            return cmd_chain
        else:
            return [self.system_exe]