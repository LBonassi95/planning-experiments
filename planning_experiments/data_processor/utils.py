import pandas as pd
from planning_experiments.collect_data_utils import find_regex

RT = 'RT'
PL = 'PL'
EN = 'EN'
D = 'D'
SYS = 'SYS'
I = 'I'
SOL = 'SOL'
OUT_LOG = 'out_log'
ERR_LOG = 'err_log'
POL = 'POL'
DEFAULT_SOLUTION_FOUND_STRINGS = ['Strong cyclic plan found.', 'Policy successfully found.' , 'Solution found.', 'Plan found.']
SOLUTION_FOUND_STRINGS = 'solution_found_strings'


def get_col_domain(df: pd.DataFrame, col):
        domain = []
        for index, row in df.iterrows():
            if df.loc[index, col] not in domain:
                domain.append(df.loc[index, col])
        return domain

def sort_fun(elem):
    return elem[1]

class InfoExtractor:

    def __init__(self):
        pass

    def extract(self, params: dict):
        raise NotImplementedError

class SolutionExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> bool:
        solution_found_strings = params[SOLUTION_FOUND_STRINGS]
        system_log = params[OUT_LOG]
        for s in solution_found_strings:
            if s in system_log:
                return True
        return False

class RTExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> float:
        err_log = params[ERR_LOG]
        try:
            assert 'Total Runtime' in err_log
            lines = [line for line in err_log.split('\n') if 'Total Runtime' in line]
            assert len(lines) == 1
            if 'ERROR: source_sink' in lines[0]:
                return float(1800)
            return float(lines[0].split(':')[1].strip())
        except:
            return None

class ComptimeExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> float:
        err_log = params[ERR_LOG]
        system = params[SYS]
        system_log = params[OUT_LOG]
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

class PLExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> float:
        system_log = params[OUT_LOG]
        try:
            if 'Plan length:' not in system_log:
                return None
            start = system_log.find('Plan length:')
            steps = system_log[start:]
            return float(steps[:steps.find('step(s).')].split(':')[1].strip())
        except:
            return None

class ENExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> float:
        system_log = params[OUT_LOG]
        try:
            if 'Plan length:' not in system_log:
                return None
            start = system_log.find('Expanded')
            steps = system_log[start:]
            return float(steps[:steps.find('state(s).')].split('Expanded')[1].split('state(s).')[0].strip())
        except:
            return None



#PALADINUS ==> # Policy Size               = 10
#PRP ========> State-Action Pairs: 27
class PolicySizeExtractor(InfoExtractor):

    def __init__(self):
        super().__init__()

    def extract(self, params: dict) -> float:
        sys_log = params[OUT_LOG]
        system = params[SYS]
        
        if 'pal' in system or 'pltl_ax' in system:
            try:
                if '# Policy Size' not in sys_log:
                    return None
                match = find_regex('# Policy Size [^\n]*', sys_log)
                return float(match[0].split('=')[1].strip())
            except:
                return None

        elif 'prp' in system or 'pltl_ce' in system:
            try:
                if 'State-Action Pairs:' not in sys_log:
                    return None
                match = find_regex('State-Action Pairs: [^\n ]*', sys_log.replace("Forbidden State-Action Pairs:", "NOMATCH"))
                return float(match[0].split(':')[1].strip())
            except:
                return None
        else:
            return None