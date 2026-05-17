
from dataclasses import dataclass
from typing import List, Tuple
import subprocess
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

@dataclass
class Job:
    name: str
    script_path: str

    def __repr__(self):
        return f"Job: {self.name}\nScript path: {self.script_path}"

class ExecutionBackend:

    def run(self, jobs: List[Job], log_folder):
        raise NotImplementedError

    def get_info(self):
        return []



class SlurmBackend:

    def __init__(self, memory = "8GB"):
        self.memory = memory

    def run(self, jobs: List[Job], log_folder):

        print("Command example")
        print(f"sbatch --mem={self.memory} --output=LOG.out --error=ERR.err --cpus-per-task=1 SCRIPT_PATH")

        for job in jobs:
            cmd = f"sbatch --mem={self.memory} --output={log_folder}/{job.name}.out --error={log_folder}/{job.name}.err --cpus-per-task=1 {job.script_path}"
            subprocess.check_output(cmd, shell=True)

    def get_info(self):
        return [
            ["Slurm", "True"],
        ]
    
    @staticmethod
    def run_script(job: Job):
        script_name = job.name
        script = job.script_path
        subprocess.run(f'chmod +x {script}', shell=True)
        subprocess.run(f'{script}', shell=True)
        return script_name


class PythonBackend:

    def __init__(self, parallel_jobs = 8):
        self.parallel_jobs = parallel_jobs

    def run(self, jobs: List[Job], log_folder):
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