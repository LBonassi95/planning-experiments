from os import path
import os
import planning_experiments
from planning_experiments.data_structures.environment import Environment, Planner, Planner
from planning_experiments.constants import *
import inspect


class ScriptBuilder:

    # BASH = "#!/bin/bash"
    # PWD = "var=$PWD"

    def __init__(self, env: Environment,
                       system: Planner,
                       domain_name: str,
                       instance_name: str,
                       blob_path: str,
                    #    system_dst: str,
                       time: int,
                       system_exe: str,
                       instance_folder: str,
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
        # self.system_dst = system_dst
        self.time = time
        self.system_exe = system_exe
        self.instance_folder = instance_folder
        self.stdo = stdo
        self.stde = stde
        self.script_name = script_name
        self.script_folder = script_folder
        self.domain_name = domain_name
        self.instance_name = instance_name
        self.blob_path = blob_path

    def get_script(self):
        
        assert isinstance(self.system, Planner)

        sandbox = path.join(self.instance_folder, SANDBOX_FOLDER)

        planner_src = path.abspath(self.system.get_path())
        planner_dst = path.join(sandbox)

        if self.enviorment.venv_path:
            python = os.path.join(self.enviorment.venv_path, 'bin', 'python3')
        else:
            python = '/usr/bin/env python3'

        self.outer_script = [
            f'#!{python}\n',
            f'import os',
            f'import shutil',
            f'from planning_experiments.save_results import *',
            f'sandbox = "{sandbox}"',
            f'blob_path = "{self.blob_path}"',
            f'planner_name = "{self.system.get_name()}"',
            f'domain_name = "{self.domain_name}"',
            f'instance_name = "{self.instance_name}"',
            f'stde_path = "{self.stde}"',
            f'stdo_path = "{self.stdo}"',
            f'time_limit = {self.time}\n',
            f'exec_str = "{path.join(self.script_folder, f"{self.script_name}.sh")} 2>> " + stde_path + " 1>> " + stdo_path\n',
        ]

        self.outer_script += [
            '\n\n'
            f'planner_src = "{planner_src}"',
            f'planner_dst = "{planner_dst}"',
        ]

        self.outer_script += [
            'open(stdo_path, "w")',
            'open(stde_path, "w")',
        ]

        if self.enviorment.hard_copy:
            self.outer_script += ['shutil.copytree(planner_src, planner_dst)']
        
        else:
            self.outer_script += [
            "os.makedirs(planner_dst, exist_ok=True)",
            "for entry in os.scandir(planner_src):",
            "    if entry.is_file(follow_symlinks=False):",
            "        os.symlink(entry.path, os.path.join(planner_dst, entry.name))",
        ]
            
        self.outer_script += ["os.chdir(sandbox)"]
        self.outer_script += [f'#########################################################\n']


        exec_cmd = f'os.system(exec)'

        if self.time != "None":
            exec_cmd = f'os.system("time -p timeout --signal=HUP {self.time} " + exec_str)'

        self.outer_script.append(exec_cmd)

        self.inner_script.append('#!/bin/bash')

        # if self.memory != 'None':
        #     self.inner_script.append(f'ulimit -Sv {self.memory}')

        exe_list = self.manage_complex_cmd()
        self.inner_script += exe_list

        if self.enviorment.delete_systems:
            self.outer_script.append(f'shutil.rmtree(sandbox)')
        
        self.outer_script.append(f'save_results(blob_path, planner_name, domain_name, instance_name)')

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