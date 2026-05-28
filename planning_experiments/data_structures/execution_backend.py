
from dataclasses import dataclass
from typing import List, Tuple
import subprocess
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from os import path

@dataclass
class Job:
    name: str
    script_path: str

    def __repr__(self):
        return f"Job: {self.name}\nScript path: {self.script_path}"

class ExecutionBackend:

    def run(self, jobs: List[Job], **kwargs):
        raise NotImplementedError

    def get_info(self):
        return []



class SlurmBackend:

    def __init__(self, memory = "8GB"):
        self.memory = memory

    def run(self, jobs: List[Job], **kwargs):
        log_folder = kwargs["log_folder"]
        run_folder = kwargs["run_folder"]
        script_to_blob = kwargs["script_to_blob"]

        print("Command example")
        print(f"sbatch --mem={self.memory} --output=LOG.out --error=ERR.err --ntasks=1 --cpus-per-task=1 --threads-per-core=1 SCRIPT_PATH")

        for job in jobs:
            
            planner_name = script_to_blob[job.name]["planner"]
            domain_name = script_to_blob[job.name]["domain"]
            instance_name = script_to_blob[job.name]["instance"]

            instance_folder = path.join(run_folder, planner_name, domain_name, instance_name)

            cmd = f"sbatch --account=coml0970 --mem={self.memory} --output={instance_folder}/{job.name}.out --error={instance_folder}/{job.name}.err --ntasks=1 --cpus-per-task=1 --threads-per-core=1 {job.script_path}"
            subprocess.check_output(cmd, shell=True)

    def get_info(self):
        return [
            ["Slurm", "True"],
        ]


class PythonBackend:

    def __init__(self, parallel_jobs = 8):
        self.parallel_jobs = parallel_jobs

    def run(self, jobs: List[Job], **kwargs):
        progress_bar = tqdm(total=len(jobs), desc="Progress", unit="iteration", colour='green')
        with Pool(self.parallel_jobs) as p:
            for _ in p.imap_unordered(self.run_script, jobs):
                progress_bar.update(1)

            progress_bar.close()
    
        # Create summary
        # summary_path = path.join(run_folder, f"summary_{batch_id}.csv") if batch_id != '' else path.join(run_folder, f"summary.csv")
        # create_summary(blob_path, summary_path)

    def get_info(self):
        return [
            ["Multiprocessing", "True"],
            ["Parallel processes", self.parallel_jobs]
        ]
    
    @staticmethod
    def run_script(job: Job):
        script_name = job.name
        script = job.script_path
        subprocess.run(f'chmod +x {script}', shell=True)
        subprocess.run(f'{script}', shell=True)
        return script_name