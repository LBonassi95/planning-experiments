import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from planning_experiments.data_processor.utils import *

class TableManager:

    def __init__(self):
        pass
    
    def get_coverage(self, df) -> pd.DataFrame:
        df = df[df[SOL] == True]
        domains = get_col_domain(df, D)
        systems = get_col_domain(df, SYS)
        coverage_dict = {D: []}
        for system in systems:
            coverage_dict[system] = []

        for domain in domains:
            coverage_dict[D].append(domain)
            for system in systems:
                df_system_domain = df[
                    (df[SYS] == system) & (df[D] == domain)
                ]
                coverage = len(df_system_domain)
                coverage_dict[system].append(coverage)

        df_coverage = pd.DataFrame.from_dict(coverage_dict)
        total={D: 'TOTAL'}
        for system in systems:
            for index, row in df_coverage.iterrows():
                if system not in total.keys():
                    total[system] = 0
                total[system] += df_coverage.loc[index, system]
        df_coverage = df_coverage.append(total, ignore_index=True)
        return df_coverage

    def bold_max(self, df: pd.DataFrame, domains, precision=2, func='argmax'):
        df_copy = df.copy()
        for domain in domains:
            if func == 'argmax':
                idx = df.loc[domain].argmax()
            elif func == 'argmin':
                idx = df.loc[domain].argmin()
            else:
                raise Exception('func must be argmax or argmin')
            col = df.loc[domain].keys()[idx]
            if not np.isnan(df_copy.loc[domain, col]):
                df_copy.loc[domain, col] = r'\textbf{' + f"%.{precision}f" % df_copy.loc[domain, col] + '}'
        return df_copy