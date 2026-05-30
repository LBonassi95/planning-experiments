
from dataclasses import dataclass
from typing import List, Tuple
import subprocess
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from pathlib import Path

@dataclass
class Job:
    name: str
    script_path: str
    problem_result_folder: str

    def __repr__(self):
        return f"Job: {self.name}\nScript path: {self.script_path}"

class ExecutionBackend:

    def run(self, jobs: List[Job]):
        raise NotImplementedError

    def create_script(self, cmd: str, sandbox: str, stdout: str, stderr: str):
        pass

    def get_info(self):
        return []



class SlurmBackend:

    def __init__(self, memory = "8GB", slurm_time = None, timeout = "1800", account = None):
        self.memory = memory
        self.timeout = timeout
        self.account = account
        self.slurm_time = slurm_time

    def run(self, jobs: List[Job]):
        print(f"Ready to dispatch with slurm! Total number of runs: {len(jobs)}")
        
        for job in tqdm(jobs, desc="Submitting jobs"):
            cmd = f"sbatch {job.script_path}"
            subprocess.check_output(cmd, shell=True)

    def get_info(self):
        return [
            ["Slurm", "True"],
            ["Memory", self.memory],
            ["Timeout", self.timeout],
            ["Slurm-time", self.slurm_time]
        ]


    def create_script(self, cmd: str, sandbox: str, stdout: str, stderr: str):

        lines = [
            "#!/bin/bash",
            "#SBATCH --cpus-per-task=1",
            f"#SBATCH --threads-per-core=1",
            f"#SBATCH --output={Path(stdout).parent / "slurm.out"}",
            f"#SBATCH --error={Path(stdout).parent / "slurm.err"}",
            f"#SBATCH --mem={self.memory}",
        ]

        if self.slurm_time is not None:
            lines += [f"#SBATCH --time={self.slurm_time}"]

        if self.account is not None:
            lines += [f"#SBATCH --account={self.account}"]

        lines += [f"cd {sandbox}",]
        
        exec_cmd = f"{cmd} > {stdout} 2> {stderr}"

        if self.timeout is not None:
            exec_cmd = f"timeout --signal=HUP {self.timeout} {exec_cmd}" 
        
        exec_cmd = f"/usr/bin/time -v {exec_cmd}"

        lines += [exec_cmd]

        return "\n".join(lines)


class PythonBackend:

    def __init__(self, parallel_jobs = 8, memory = "unlimited", time = "60"):
        self.parallel_jobs = parallel_jobs
        self.memory = memory
        self.time = time

    def run(self, jobs: List[Job]):
        progress_bar = tqdm(total=len(jobs), desc="Progress", unit="iteration", colour='green')
        with Pool(self.parallel_jobs) as p:
            for _ in p.imap_unordered(self.run_script, jobs):
                progress_bar.update(1)

            progress_bar.close()

    def get_info(self):
        return [
            ["Multiprocessing", "True"],
            ["Parallel processes", self.parallel_jobs],
            ["Memory", self.memory],
            ["Time", self.time]
        ]

    def create_script(self, cmd: str, sandbox: str, stdout: str, stderr: str):

        lines = [
            "#!/bin/bash",
            f"ulimit -v {self.memory}",
        ]
        lines += [
            f"cd {sandbox}",
            f"/usr/bin/time timeout --signal=HUP {self.time} {cmd} > {stdout} 2> {stderr}"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def run_script(job: Job):
        script_name = job.name
        script = job.script_path
        subprocess.run(f'chmod +x {script}', shell=True)
        subprocess.run(f'{script}', shell=True)
        return script_name