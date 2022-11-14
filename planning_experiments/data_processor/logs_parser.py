import os
import pandas as pd
import numpy as np
from planning_experiments.data_processor.utils import *

def extract_runtime_from_log(err_log):
    try:
        assert 'Total Runtime' in err_log
        lines = [line for line in err_log.split('\n') if 'Total Runtime' in line]
        assert len(lines) == 1
        if 'ERROR: source_sink' in lines[0]:
            return float(1800)
        return float(lines[0].split(':')[1].strip())
    except:
        return None


def extract_comptime_from_log(system, system_log, err_log):
    try:
        if 'ltl' in system and 'Number of Inferences:' not in system_log:
            return None
        lines = [line for line in err_log.split('\n') if 'Compilation Time' in line]
        assert len(lines) == 1
        if 'ERROR: source_sink' in lines[0]:
            return float(1800)
        return float(lines[0].split(':')[1].strip())
    except:
        return None


def extract_plan_lenght_from_log(system_log):
    try:
        if 'Plan length:' not in system_log:
            return None
        start = system_log.find('Plan length:')
        steps = system_log[start:]
        return float(steps[:steps.find('step(s).')].split(':')[1].strip())
    except:
        return None


def extract_expanded_from_log(system_log):
    try:
        if 'Plan length:' not in system_log:
            return None
        start = system_log.find('Expanded')
        steps = system_log[start:]
        return float(steps[:steps.find('state(s).')].split('Expanded')[1].split('state(s).')[0].strip())
    except:
        return None

def extract_solution_found_log(system_log, *solution_found_strings):
    for s in solution_found_strings:
        if s in system_log:
            return True
    return False

def sort_fun(elem):
    return elem[1]


class InfoExtractor:

    def __init__(self, function, log: bool = False, err: bool = False, additional_args = None):
        self.function = function
        self.log = log
        self.err = err
        self.additional_args = additional_args

    def extract(self, log: str, err: str):
        params = []
        
        if self.log:
            params.append(log)
        if self.err:
            params.append(err)

        if params == []:
            return None

        if self.additional_args is not None:
            return self.function(*params, *self.additional_args)
        else:
            return self.function(*params)

class LogsParser:
    
    def __init__(self, path):
        self.path = path
        self.log_processors = {
            SOL: InfoExtractor(extract_solution_found_log, log=True, additional_args=DEFAULT_SOLUTION_FOUND_STRINGS),
            RT: InfoExtractor(extract_runtime_from_log, err=True),
            PL: InfoExtractor(extract_plan_lenght_from_log, log=True),
            EN: InfoExtractor(extract_expanded_from_log, log=True),
        }

    def logs2df(self):
        records = []

        systems = []
        sanity_check = False
        for elem in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, elem)):
                systems.append(elem)
            if elem == 'results.txt':
                sanity_check = True

        if not sanity_check:
            print(f'WARNING! No results.txt in {self.path}')

        for system in systems:
            system_path = os.path.join(self.path, system)
            for domain in os.listdir(system_path):

                path_to_solutions = os.path.join(system_path, domain)
                logs = []
                errs = []
                for file in os.listdir(path_to_solutions):
                    if file.startswith('out'):
                        logs.append((file, file.split(domain)[1].replace('_', '').replace('.txt', '')))
                    if file.startswith('err'):
                        errs.append((file, file.split(domain)[1].replace('_', '').replace('.txt', '')))

                results = []
                logs.sort(key=sort_fun)
                errs.sort(key=sort_fun)
                for i in range(len(logs)):
                    log, prob = logs[i]
                    err, prob_ = errs[i]
                    assert prob == prob_
                    system_log = open(os.path.join(path_to_solutions, log), 'r').read()
                    # if 'Search stopped' in system_log:
                    #     print(f'false->{log}')
                    # if 'Empty goal!' in system_log:
                    #     print(f'false->{log}')
                    # if 'Simplified to trivially false goal! Generating unsolvable' in system_log:
                    #     print(f'false->{log}')
                    err_log = open(os.path.join(path_to_solutions, err), 'r').read()

                    record = {
                        D: domain, SYS: system, I: f'{prob}'
                    }
                    
                    for name, extractor in self.log_processors.items():
                        result = extractor.extract(log=system_log, err=err_log)
                        if result is not None:
                            record[name] = result
                    
                    records.append(record)
        df = pd.DataFrame.from_records(records)
        return df