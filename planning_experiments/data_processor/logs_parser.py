import os
import pandas as pd
import numpy as np
from planning_experiments.data_processor.utils import *
from planning_experiments.constants import *

DEFAULT_LOG_PROCESSORS = {
            SOL: SolutionExtractor(),
            RT: RTExtractor(),
            CT : ComptimeExtractor(),
            PL: PLExtractor(),
            EN: ENExtractor(),
        }

class LogsParser:
    
    def __init__(self, info: dict):
        self.info = info
        self.log_processors = DEFAULT_LOG_PROCESSORS

    def logs2df(self):
        records = []

        for system in self.info.keys():
            for domain in self.info[system].keys():
                for instance in self.info[system][domain].keys():
                    stdo = self.info[system][domain][instance][STDO]
                    stde = self.info[system][domain][instance][STDE]


                    system_log = open(stdo, 'r').read()
                    err_log = open(stde, 'r').read()

                    record = {
                        D: domain, SYS: system, I: f'{instance}'
                    }
                    
                    extraction_params = {
                        STDO: system_log,
                        STDE: err_log,
                        D: domain, 
                        SYS: system,
                        I: f'{instance}',
                        SOLUTION_PATH: self.info[system][domain][instance][STDE]
                    }

                    ##
                    # INSERT VALIDATION HERE
                    ##

                    for name, extractor in DEFAULT_LOG_PROCESSORS.items():
                        result = extractor.extract(extraction_params)
                        if result is not None:
                            record[name] = result
                    
                    records.append(record)
        df = pd.DataFrame.from_records(records)
        df.sort_values([SYS, I], inplace=True)
        return df
