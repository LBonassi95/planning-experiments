import os
import pandas as pd
import numpy as np
from planning_experiments.data_processor.utils import *


class LogsParser:
    
    def __init__(self, path):
        self.path = path
        self.log_processors = {
            SOL: SolutionExtractor(),
            RT: RTExtractor(),
            CT : ComptimeExtractor(),
            PL: PLExtractor(),
            f'{PL}_FF': PLExtractorFF(),
            UNSAT: UnsolvableExtractor(),
            'REAL_PL': RealPLExtractor(),
            EN: ENExtractor(),
            POL: PolicySizeExtractor(),
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
                    
                    extraction_params = {
                        OUT_LOG: system_log,
                        ERR_LOG: err_log,
                        D: domain, 
                        SYS: system,
                        I: f'{prob}',
                        PATH_TO_SOLUTIONS: path_to_solutions
                    }
                    for name, extractor in self.log_processors.items():
                        result = extractor.extract(extraction_params)
                        if result is not None:
                            record[name] = result
                    
                    records.append(record)
        df = pd.DataFrame.from_records(records)
        df.sort_values([SYS, I], inplace=True)
        return df